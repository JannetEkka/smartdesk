#!/usr/bin/env python3
"""Load the eval corpus into a database and build both retrieval indexes.

Creates the notes table if missing, loads ``evals/corpus/notes.jsonl``, embeds
each note whole (the baseline path), then chunks each note and embeds the
chunks (the chunked path). Both live side by side so the harness can measure
them against each other without re-ingesting.

Usage::

    # local development against Postgres + pgvector
    export SMARTDESK_EMBEDDER=local
    export DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk
    python evals/ingest.py --reset

    # against AlloyDB with the production embedder
    export SMARTDESK_EMBEDDER=vertex
    export DATABASE_URL=postgresql+pg8000://postgres:...@<alloydb-ip>:5432/postgres
    python evals/ingest.py --chunk-size 180 --overlap 40
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import _bootstrap  # noqa: F401  (sets sys.path)

REPO_ROOT = _bootstrap.REPO_ROOT

from rag import db  # noqa: E402
from rag.chunking import chunk_text, get_tokenizer  # noqa: E402
from rag.embeddings import get_embedder, to_pgvector  # noqa: E402

CORPUS = REPO_ROOT / "evals" / "corpus" / "notes.jsonl"

# Mirrors setup/setup_alloydb.sql but with the vector dimension supplied by the
# active embedder, so a 384-dimension local run and a 768-dimension Vertex run
# both work from the same code.
NOTES_DDL = """
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR({dim}),
    created_at TIMESTAMP DEFAULT NOW()
);
"""


def load_corpus() -> list[dict]:
    rows = [json.loads(line) for line in CORPUS.read_text().splitlines() if line.strip()]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Corpus contains duplicate note ids.")
    return rows


def reset_tables(dim: int) -> None:
    """Drop and recreate both tables.

    Only ever run against a development database: it destroys the notes table.
    The migration path for a database with real data is
    setup/migrations/001_note_chunks.sql, which is additive.
    """
    db.execute("DROP TABLE IF EXISTS note_chunks;")
    db.execute("DROP TABLE IF EXISTS notes;")
    db.execute(NOTES_DDL.format(dim=dim))
    db.ensure_chunks_table(dim)


def ingest_notes(rows: list[dict], embedder) -> None:
    """Insert notes with whole-document embeddings (the baseline index)."""
    texts = [f"{r['title']}\n{r['content']}" for r in rows]
    start = time.perf_counter()
    vectors = embedder.embed_documents(texts)
    elapsed = time.perf_counter() - start
    print(f"  embedded {len(vectors)} notes in {elapsed:.1f}s")

    for row, vec in zip(rows, vectors):
        db.execute(
            """
            INSERT INTO notes (id, title, content, content_embedding)
            VALUES (:id, :title, :content, CAST(:vec AS vector))
            ON CONFLICT (id) DO UPDATE
              SET title = EXCLUDED.title,
                  content = EXCLUDED.content,
                  content_embedding = EXCLUDED.content_embedding
            """,
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "vec": to_pgvector(vec),
            },
        )
    # SERIAL keeps its own counter, which explicit ids bypass; resync it so
    # later inserts through add_note() do not collide.
    db.execute("SELECT setval('notes_id_seq', (SELECT MAX(id) FROM notes));")


def ingest_chunks(rows: list[dict], embedder, chunk_size: int, overlap: int) -> dict:
    """Chunk every note and embed the chunks (the chunked index)."""
    tokenizer = get_tokenizer()
    db.execute("DELETE FROM note_chunks;")

    pending: list[tuple[int, int, str, int]] = []
    for row in rows:
        text = f"{row['title']}\n{row['content']}"
        for chunk in chunk_text(text, chunk_size, overlap, tokenizer):
            pending.append((row["id"], chunk.index, chunk.text, chunk.token_count))

    start = time.perf_counter()
    vectors = embedder.embed_documents([c[2] for c in pending])
    elapsed = time.perf_counter() - start
    print(f"  embedded {len(vectors)} chunks in {elapsed:.1f}s")

    for (note_id, idx, text, tokens), vec in zip(pending, vectors):
        db.execute(
            """
            INSERT INTO note_chunks (note_id, chunk_index, content, token_count, content_embedding)
            VALUES (:note_id, :idx, :content, :tokens, CAST(:vec AS vector))
            ON CONFLICT (note_id, chunk_index) DO UPDATE
              SET content = EXCLUDED.content,
                  token_count = EXCLUDED.token_count,
                  content_embedding = EXCLUDED.content_embedding
            """,
            {
                "note_id": note_id,
                "idx": idx,
                "content": text,
                "tokens": tokens,
                "vec": to_pgvector(vec),
            },
        )

    per_note: dict[int, int] = {}
    for note_id, _, _, _ in pending:
        per_note[note_id] = per_note.get(note_id, 0) + 1
    multi = sum(1 for v in per_note.values() if v > 1)
    return {
        "chunks": len(pending),
        "notes": len(per_note),
        "notes_with_multiple_chunks": multi,
        "tokenizer": getattr(tokenizer, "name", "unknown"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-size", type=int, default=180, help="tokens per chunk")
    parser.add_argument("--overlap", type=int, default=40, help="tokens of overlap")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="drop and recreate tables first (development databases only)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)

    embedder = get_embedder()
    # Touch the model so `dimension` is accurate before any DDL is emitted.
    embedder.embed_query("warmup")
    print(f"Embedder: {embedder.name} ({embedder.dimension}d)")

    rows = load_corpus()
    print(f"Corpus:   {len(rows)} notes from {CORPUS.relative_to(REPO_ROOT)}")

    db.ensure_vector_extension()
    if args.reset:
        reset_tables(embedder.dimension)
    else:
        db.execute(NOTES_DDL.format(dim=embedder.dimension))
        db.ensure_chunks_table(embedder.dimension)

    existing_dim = db.chunks_table_dimension()
    if existing_dim and existing_dim != embedder.dimension:
        print(
            f"ERROR: note_chunks.content_embedding is {existing_dim}d but the active "
            f"embedder produces {embedder.dimension}d. Re-run with --reset, or point "
            f"DATABASE_URL at a database built with this embedder.",
            file=sys.stderr,
        )
        return 1

    print("Ingesting whole-note embeddings (baseline index)...")
    ingest_notes(rows, embedder)

    print(f"Ingesting chunks (size={args.chunk_size}, overlap={args.overlap})...")
    stats = ingest_chunks(rows, embedder, args.chunk_size, args.overlap)
    print(
        f"  {stats['chunks']} chunks across {stats['notes']} notes "
        f"({stats['notes_with_multiple_chunks']} notes split into >1 chunk, "
        f"tokenizer={stats['tokenizer']})"
    )
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
