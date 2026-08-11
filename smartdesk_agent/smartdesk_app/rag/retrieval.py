"""Retrieval strategies over the notes corpus.

Two retrieval paths, both returning the same shape so the eval harness can
compare them directly:

* ``retrieve_notes``  — the baseline. One embedding per note, cosine distance,
                        top k. This is what ``search_notes`` did originally.
* ``retrieve_chunks`` — chunk-level search collapsed back to parent notes, so
                        a hit inside a long note still cites the note.

Both use ``<=>`` (cosine distance) from the vector extension, which AlloyDB
and pgvector both provide, and both take the query embedding as a bound
parameter rather than calling AlloyDB's in-database ``embedding()`` function.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from . import db
from .embeddings import Embedder, get_embedder, to_pgvector

logger = logging.getLogger(__name__)


@dataclass
class RetrievedNote:
    """A retrieval result, always identified by the note a user would cite.

    ``chunk_text`` holds the specific passage that matched when the result came
    from chunk retrieval. The agent shows the note title as the citation but
    can read the passage that actually answered the question.
    """

    note_id: int
    title: str
    content: str
    score: float
    chunk_text: str | None = None
    matched_chunks: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        out = {
            "id": self.note_id,
            "title": self.title,
            "content": self.content,
            "similarity": round(self.score, 6),
        }
        if self.chunk_text is not None:
            out["matched_passage"] = self.chunk_text
        return out


def retrieve_notes(
    query: str,
    k: int = 5,
    embedder: Embedder | None = None,
    engine=None,
    query_vector: list[float] | None = None,
) -> list[RetrievedNote]:
    """Baseline retrieval: nearest whole-note embeddings.

    ``query_vector`` lets a caller reuse an embedding it already computed,
    which keeps the eval harness from paying for the same query twice.
    """
    embedder = embedder or get_embedder()
    vec = query_vector if query_vector is not None else embedder.embed_query(query)

    rows = db.query(
        """
        SELECT id, title, content,
               1 - (content_embedding <=> CAST(:qvec AS vector)) AS similarity
        FROM notes
        WHERE content_embedding IS NOT NULL
        ORDER BY content_embedding <=> CAST(:qvec AS vector)
        LIMIT :k
        """,
        {"qvec": to_pgvector(vec), "k": k},
        engine=engine,
    )
    return [
        RetrievedNote(
            note_id=r["id"],
            title=r["title"],
            content=r["content"],
            score=float(r["similarity"]),
        )
        for r in rows
    ]


def retrieve_chunks(
    query: str,
    k: int = 5,
    embedder: Embedder | None = None,
    engine=None,
    query_vector: list[float] | None = None,
    fetch_multiplier: int = 4,
) -> list[RetrievedNote]:
    """Chunk-level retrieval, collapsed to distinct parent notes.

    Several chunks of the same note may all rank highly. Collapsing keeps the
    result list at k *distinct notes* rather than k passages, matching what the
    baseline returns and what a user expects to be cited. A note's score is its
    best chunk's score.

    ``fetch_multiplier`` over-fetches chunks so that after collapsing there are
    still k distinct notes to return.
    """
    embedder = embedder or get_embedder()
    vec = query_vector if query_vector is not None else embedder.embed_query(query)

    rows = db.query(
        """
        SELECT c.note_id, c.id AS chunk_id, c.content AS chunk_content,
               n.title, n.content,
               1 - (c.content_embedding <=> CAST(:qvec AS vector)) AS similarity
        FROM note_chunks c
        JOIN notes n ON n.id = c.note_id
        WHERE c.content_embedding IS NOT NULL
        ORDER BY c.content_embedding <=> CAST(:qvec AS vector)
        LIMIT :limit
        """,
        {"qvec": to_pgvector(vec), "limit": max(k * fetch_multiplier, k)},
        engine=engine,
    )

    best: dict[int, RetrievedNote] = {}
    for r in rows:
        note_id = r["note_id"]
        existing = best.get(note_id)
        if existing is None:
            best[note_id] = RetrievedNote(
                note_id=note_id,
                title=r["title"],
                content=r["content"],
                score=float(r["similarity"]),
                chunk_text=r["chunk_content"],
                matched_chunks=[r["chunk_id"]],
            )
        else:
            existing.matched_chunks.append(r["chunk_id"])

    ranked = sorted(best.values(), key=lambda n: n.score, reverse=True)
    return ranked[:k]
