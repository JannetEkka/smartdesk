"""Reranking strategies.

Dense retrieval gives a ranking from one bi-encoder similarity score. A
reranker takes a wider candidate set and reorders it using a signal the
retriever did not have.

Three implementations, spanning the cost/accuracy range:

``RRFReranker``
    Free. Scores candidates with BM25 and fuses that ranking with the dense
    ranking using reciprocal rank fusion. Complements dense retrieval on rare
    exact terms — names, error strings, product nouns — which is where
    embeddings are weakest. No model call, no network.

``CrossEncoderReranker``
    Cheap. A real cross-encoder (ms-marco-MiniLM-L-6-v2) that scores query and
    document jointly rather than comparing two independent vectors. Runs on
    CPU. Far more accurate than bi-encoder similarity in the general case, at
    the cost of one forward pass per candidate.

``GeminiReranker``
    Most expensive. Uses Gemini as a cross-encoder by asking it to score each
    candidate's relevance. Highest ceiling, but adds a network round trip and
    real per-query cost.

BM25 is implemented here rather than pulled in as a dependency: it is twenty
lines, and the point of this pipeline is that the mechanics stay legible.
"""

from __future__ import annotations

import logging
import math
import os
import re
from collections import Counter
from typing import Callable, Sequence

from .retrieval import RetrievedNote

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Common words carry no discriminative signal and inflate BM25 scores for
# long documents. A small stoplist is enough for this corpus.
_STOPWORDS = frozenset(
    """a an and are as at be by did do does for from had has have how i if in
    is it its of on or our that the their there they this to too was we were
    what when where which who why will with you your""".split()
)


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def bm25_scores(
    query: str, documents: Sequence[str], k1: float = 1.5, b: float = 0.75
) -> list[float]:
    """Score documents against a query with Okapi BM25.

    IDF is computed over the candidate set rather than the whole corpus. That
    is the standard approximation when reranking: it costs nothing, and within
    a candidate set the relative ordering is what matters.
    """
    docs = [_tokenize(d) for d in documents]
    if not docs:
        return []
    n = len(docs)
    avgdl = sum(len(d) for d in docs) / n or 1.0

    doc_freq: Counter[str] = Counter()
    for d in docs:
        doc_freq.update(set(d))

    q_terms = _tokenize(query)
    scores = []
    for d in docs:
        tf = Counter(d)
        dl = len(d)
        score = 0.0
        for term in q_terms:
            if term not in tf:
                continue
            df = doc_freq[term]
            # +0.5 smoothing keeps IDF positive when a term is in every doc.
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
            freq = tf[term]
            score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * dl / avgdl))
        scores.append(score)
    return scores


def _rrf(rank: int, k: int = 60) -> float:
    """Reciprocal rank fusion weight for a 1-indexed rank."""
    return 1.0 / (k + rank)


class RRFReranker:
    """Fuse the dense ranking with a BM25 ranking.

    Reciprocal rank fusion combines rankings without needing the two score
    scales to be comparable, which is what makes it robust: cosine similarity
    and BM25 are not on the same scale and calibrating them is fiddly.
    """

    name = "rrf"
    #: No model call, so cost is zero and latency is microseconds.
    cost_per_query_usd = 0.0

    def __init__(self, k: int = 60) -> None:
        self._k = k

    def rerank(
        self, query: str, candidates: Sequence[RetrievedNote], top_k: int = 5
    ) -> list[RetrievedNote]:
        if not candidates:
            return []
        # Dense ranking is the order the retriever returned.
        dense_rank = {c.note_id: i + 1 for i, c in enumerate(candidates)}

        texts = [(c.chunk_text or c.content) for c in candidates]
        lex = bm25_scores(query, texts)
        order = sorted(range(len(candidates)), key=lambda i: lex[i], reverse=True)
        lex_rank = {candidates[i].note_id: pos + 1 for pos, i in enumerate(order)}

        fused = sorted(
            candidates,
            key=lambda c: _rrf(dense_rank[c.note_id], self._k)
            + _rrf(lex_rank[c.note_id], self._k),
            reverse=True,
        )
        return list(fused[:top_k])


class CrossEncoderReranker:
    """Score query and document jointly with a cross-encoder."""

    name = "cross-encoder"
    cost_per_query_usd = 0.0  # local model, compute only

    def __init__(self, model_id: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model_id = model_id
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            logger.info("Loading cross-encoder %s", self._model_id)
            self._model = CrossEncoder(self._model_id, device="cpu")
        return self._model

    def rerank(
        self, query: str, candidates: Sequence[RetrievedNote], top_k: int = 5
    ) -> list[RetrievedNote]:
        if not candidates:
            return []
        model = self._get_model()
        pairs = [(query, c.chunk_text or c.content) for c in candidates]
        scores = model.predict(pairs, show_progress_bar=False)
        ranked = sorted(
            zip(candidates, scores), key=lambda pair: float(pair[1]), reverse=True
        )
        return [c for c, _ in ranked[:top_k]]


class GeminiReranker:
    """Use Gemini as a cross-encoder.

    Sends the query and all candidates in one call and asks for relevance
    scores, which is far cheaper than one call per candidate and keeps latency
    to a single round trip. Falls back to the original order if the response
    cannot be parsed, so a malformed reply degrades to dense ranking rather
    than to an exception.

    Requires ``GOOGLE_CLOUD_PROJECT`` and application default credentials.
    Unlike the other two rerankers this one costs money per query.
    """

    name = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        project: str | None = None,
        location: str | None = None,
    ) -> None:
        self._model = model
        self._project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self._location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai

            if not self._project:
                raise RuntimeError(
                    "GeminiReranker needs GOOGLE_CLOUD_PROJECT and application "
                    "default credentials."
                )
            self._client = genai.Client(
                vertexai=True, project=self._project, location=self._location
            )
        return self._client

    def rerank(
        self, query: str, candidates: Sequence[RetrievedNote], top_k: int = 5
    ) -> list[RetrievedNote]:
        if not candidates:
            return []
        from google.genai import types

        listing = "\n\n".join(
            f"[{i}] {c.title}\n{(c.chunk_text or c.content)[:900]}"
            for i, c in enumerate(candidates)
        )
        prompt = (
            "Score how well each passage answers the question, from 0 to 10.\n"
            "10 means the passage directly answers it. 0 means unrelated.\n"
            "Judge only the passage content, not its length or style.\n\n"
            f"Question: {query}\n\nPassages:\n{listing}\n\n"
            "Reply with one line per passage as `index:score`, nothing else."
        )

        try:
            response = self._get_client().models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1024,
                ),
            )
            scores = self._parse(response.text or "", len(candidates))
        except Exception as exc:
            logger.warning("Gemini rerank failed (%s); keeping dense order.", exc)
            return list(candidates[:top_k])

        ranked = sorted(
            zip(candidates, scores), key=lambda pair: pair[1], reverse=True
        )
        return [c for c, _ in ranked[:top_k]]

    @staticmethod
    def _parse(text: str, n: int) -> list[float]:
        """Parse `index:score` lines, defaulting anything missing to zero."""
        scores = [0.0] * n
        for match in re.finditer(r"(\d+)\s*[:=]\s*(\d+(?:\.\d+)?)", text):
            idx, val = int(match.group(1)), float(match.group(2))
            if 0 <= idx < n:
                scores[idx] = val
        return scores


def available() -> dict[str, Callable[[], object]]:
    """Rerankers the current environment can actually run.

    Gemini is offered only when credentials are configured, so the harness does
    not fail partway through a run on a machine without cloud access.
    """
    registry: dict[str, Callable[[], object]] = {
        "rrf": RRFReranker,
        "cross-encoder": CrossEncoderReranker,
    }
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        registry["gemini"] = GeminiReranker
    return registry
