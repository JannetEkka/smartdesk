"""Pluggable embedding providers.

SmartDesk runs against AlloyDB in production and plain Postgres + pgvector in
development. The original ``search_notes`` called AlloyDB's in-database
``embedding('text-embedding-005', ...)`` function, which does not exist on
stock Postgres. Computing embeddings client-side instead keeps one code path
for both databases: the vector is passed as a bound parameter and cast with
``::vector``, which AlloyDB and pgvector both understand.

Two providers:

* ``VertexEmbedder``  — text-embedding-005 via Vertex AI, 768 dimensions.
                        This is the production path and matches the existing
                        ``VECTOR(768)`` column.
* ``LocalEmbedder``   — sentence-transformers all-MiniLM-L6-v2, 384 dimensions.
                        CPU-only, ~90 MB, for development without cloud
                        credentials or spend.

Select with the ``SMARTDESK_EMBEDDER`` environment variable (``vertex`` or
``local``). Because the two produce different dimensionalities, the schema
helpers take the dimension from the active embedder rather than hard-coding
768 — see ``rag/db.py``.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Protocol, Sequence

logger = logging.getLogger(__name__)


class Embedder(Protocol):
    """Minimal interface every embedding provider implements.

    Queries and documents are embedded through separate methods because
    several models (text-embedding-005 among them) are trained with distinct
    task types for each side of the retrieval pair.
    """

    name: str
    dimension: int

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed texts that will be stored and searched over."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query."""
        ...

    def embed_queries(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed several queries in as few round trips as possible.

        The eval harness embeds every question up front. Doing that one call
        at a time is dozens of sequential network round trips with no output,
        which looks indistinguishable from a hang.
        """
        ...


class VertexEmbedder:
    """text-embedding-005 through Vertex AI.

    Requires application default credentials and ``GOOGLE_CLOUD_PROJECT``.
    Uses the google-genai client that google-adk already depends on, so this
    adds no new package to requirements.txt.
    """

    name = "text-embedding-005"
    dimension = 768

    #: Vertex rejects oversized batches; 250 is the documented per-request cap
    #: for this model family, and we stay well under it.
    BATCH_SIZE = 100

    def __init__(
        self,
        model: str = "text-embedding-005",
        project: str | None = None,
        location: str | None = None,
    ) -> None:
        self.name = model
        self._project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self._location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        if not self._project:
            raise RuntimeError(
                "VertexEmbedder needs GOOGLE_CLOUD_PROJECT set (and application "
                "default credentials). Set SMARTDESK_EMBEDDER=local to develop "
                "without cloud access."
            )
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(
                vertexai=True, project=self._project, location=self._location
            )
        return self._client

    def _embed(self, texts: Sequence[str], task_type: str) -> list[list[float]]:
        from google.genai import types

        client = self._get_client()
        out: list[list[float]] = []
        for start in range(0, len(texts), self.BATCH_SIZE):
            batch = list(texts[start : start + self.BATCH_SIZE])
            response = client.models.embed_content(
                model=self.name,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.dimension,
                ),
            )
            out.extend([list(e.values) for e in response.embeddings])
        return out

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def embed_queries(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, "RETRIEVAL_QUERY")


class GeminiAPIEmbedder:
    """gemini-embedding-001 through the Gemini API (AI Studio), not Vertex.

    Exists to remove the Vertex billing dependency: the Gemini API has a free
    tier covering this model, and it needs only ``GOOGLE_API_KEY`` rather than
    a billed GCP project with application default credentials.

    ``output_dimensionality`` is pinned to 768 so the existing
    ``VECTOR(768)`` column works unchanged — no migration, no re-declaring the
    schema. Note that this model natively produces a larger vector and
    truncates to the requested size, so Google's guidance is to re-normalise
    after truncation, which this does.

    Free-tier rate limits apply. Ingesting a large corpus may need throttling.
    """

    name = "gemini-embedding-001"
    dimension = 768
    BATCH_SIZE = 100

    def __init__(
        self, model: str = "gemini-embedding-001", api_key: str | None = None
    ) -> None:
        self.name = model
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self._api_key:
            raise RuntimeError(
                "GeminiAPIEmbedder needs GOOGLE_API_KEY (create one at "
                "https://aistudio.google.com/apikey). Use SMARTDESK_EMBEDDER=local "
                "to develop with no API access at all."
            )
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    @staticmethod
    def _normalise(vector: list[float]) -> list[float]:
        """Re-normalise to unit length after dimensionality truncation."""
        norm = sum(x * x for x in vector) ** 0.5
        return [x / norm for x in vector] if norm else vector

    def _embed(self, texts: Sequence[str], task_type: str) -> list[list[float]]:
        from google.genai import types

        client = self._get_client()
        out: list[list[float]] = []
        for start in range(0, len(texts), self.BATCH_SIZE):
            batch = list(texts[start : start + self.BATCH_SIZE])
            response = client.models.embed_content(
                model=self.name,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.dimension,
                ),
            )
            out.extend(self._normalise(list(e.values)) for e in response.embeddings)
        return out

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def embed_queries(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed(texts, "RETRIEVAL_QUERY")


class LocalEmbedder:
    """all-MiniLM-L6-v2 on CPU, for development.

    Normalised output, so cosine distance and inner product agree. Chosen
    because it is small enough (~90 MB, 22M parameters) to run on a laptop
    with no GPU, which is the stated development constraint.
    """

    name = "all-MiniLM-L6-v2"
    dimension = 384

    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.name = model.split("/")[-1]
        self._model_id = model
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading local embedding model %s", self._model_id)
            self._model = SentenceTransformer(self._model_id, device="cpu")
            # Renamed in sentence-transformers 5.x; support both.
            getter = getattr(
                self._model,
                "get_embedding_dimension",
                getattr(self._model, "get_sentence_embedding_dimension", None),
            )
            if getter is not None:
                self.dimension = getter()
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        vectors = model.encode(
            list(texts),
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def embed_queries(self, texts: Sequence[str]) -> list[list[float]]:
        return self.embed_documents(texts)


@lru_cache(maxsize=None)
def get_embedder(kind: str | None = None) -> Embedder:
    """Return the configured embedder.

    Cached so the local model is loaded from disk only once per process.
    """
    kind = (kind or os.getenv("SMARTDESK_EMBEDDER", "vertex")).lower()
    if kind == "vertex":
        return VertexEmbedder()
    if kind == "gemini":
        return GeminiAPIEmbedder()
    if kind == "local":
        return LocalEmbedder()
    raise ValueError(
        f"Unknown embedder {kind!r}; expected 'vertex', 'gemini', or 'local'."
    )


def to_pgvector(vector: Sequence[float]) -> str:
    """Format a vector as a pgvector literal.

    Both AlloyDB and pgvector parse ``'[1,2,3]'::vector``, so this is the
    portable way to bind an embedding as a query parameter.
    """
    return "[" + ",".join(f"{x:.8f}" for x in vector) + "]"
