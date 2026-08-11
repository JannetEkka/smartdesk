"""Portable database access for the RAG pipeline.

The same code runs against AlloyDB (production) and Postgres + pgvector
(development). Nothing here uses AlloyDB-only features: embeddings arrive as
bound parameters rather than through the in-database ``embedding()`` function,
and ``<=>`` is provided by the ``vector`` extension on both.
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime
from typing import Any

import sqlalchemy

logger = logging.getLogger(__name__)

_engine = None


def get_engine(url: str | None = None):
    """Create or return the cached SQLAlchemy engine.

    Resolution order matches the existing tools.py behaviour so both share one
    configuration surface: explicit argument, then ``DATABASE_URL``, then the
    individual ``ALLOYDB_*`` variables.
    """
    global _engine
    if url:
        return sqlalchemy.create_engine(url)
    if _engine is not None:
        return _engine

    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        _engine = sqlalchemy.create_engine(db_url)
    else:
        user = os.getenv("ALLOYDB_USER", "postgres")
        password = os.getenv("ALLOYDB_PASSWORD", "")
        host = os.getenv("ALLOYDB_IP", "127.0.0.1")
        port = os.getenv("ALLOYDB_PORT", "5432")
        db = os.getenv("ALLOYDB_DB", "postgres")
        _engine = sqlalchemy.create_engine(
            f"postgresql+pg8000://{user}:{password}@{host}:{port}/{db}"
        )
    return _engine


def reset_engine() -> None:
    """Drop the cached engine. Used by tests that switch databases."""
    global _engine
    _engine = None


def _serialize(val: Any) -> Any:
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val


def query(sql: str, params: dict | None = None, engine=None) -> list[dict]:
    """Run a query and return rows as dicts.

    Errors are raised rather than swallowed. The agent-facing wrappers in
    tools.py convert them into a friendly payload; internal callers such as the
    eval harness need the failure to be loud, because a silently empty result
    set would quietly corrupt a measurement.
    """
    engine = engine or get_engine()
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(sql), params or {})
        if not result.returns_rows:
            conn.commit()
            return []
        columns = result.keys()
        rows = [
            {col: _serialize(val) for col, val in zip(columns, row)}
            for row in result.fetchall()
        ]
        conn.commit()
        return rows


def execute(sql: str, params: dict | None = None, engine=None) -> None:
    """Run a statement for its side effects."""
    engine = engine or get_engine()
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(sql), params or {})
        conn.commit()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
#
# The chunks table is additive: `notes` keeps its own `content_embedding`
# column and every existing row, so the baseline retrieval path and anything
# else reading `notes` continues to work untouched. Chunks reference their
# parent note with ON DELETE CASCADE, which is what lets a chunk hit resolve
# back to a citable note.

CHUNKS_DDL = """
CREATE TABLE IF NOT EXISTS note_chunks (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    content_embedding VECTOR({dim}),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (note_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS note_chunks_note_id_idx ON note_chunks (note_id);
"""


def ensure_vector_extension(engine=None) -> None:
    execute("CREATE EXTENSION IF NOT EXISTS vector;", engine=engine)


def ensure_chunks_table(dim: int, engine=None) -> None:
    """Create the chunks table if absent.

    ``dim`` comes from the active embedder rather than being hard-coded, so a
    384-dimension development run and a 768-dimension production run share this
    code. Creating a table is reversible (``DROP TABLE note_chunks``) and
    leaves `notes` untouched.
    """
    execute(CHUNKS_DDL.format(dim=int(dim)), engine=engine)


def chunks_table_dimension(engine=None) -> int | None:
    """Return the declared dimension of note_chunks.content_embedding.

    Used to detect a stale chunks table left over from a run with a different
    embedder, which would otherwise fail confusingly at query time.
    """
    rows = query(
        """
        SELECT a.atttypmod AS dim
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        WHERE c.relname = 'note_chunks' AND a.attname = 'content_embedding'
        """,
        engine=engine,
    )
    if not rows or rows[0]["dim"] in (None, -1):
        return None
    return int(rows[0]["dim"])
