"""End-to-end retrieval tests against a real Postgres + pgvector database.

Skipped unless SMARTDESK_TEST_DATABASE_URL is set, so the suite still runs on
a machine with no database. These are the tests that would catch a broken SQL
statement or a dimension mismatch, which unit tests over pure functions cannot.

    export SMARTDESK_TEST_DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk_test
    python -m pytest tests/test_retrieval_integration.py
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "smartdesk_agent" / "smartdesk_app"))

from rag import db  # noqa: E402
from rag.rerankers import HybridFusionReranker  # noqa: E402
from rag.retrieval import retrieve_chunks, retrieve_notes  # noqa: E402

DB_URL = os.getenv("SMARTDESK_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DB_URL, reason="SMARTDESK_TEST_DATABASE_URL not set"
)

DIM = 8

# Deterministic hand-built vectors so retrieval order is known in advance,
# with no embedding model involved.
DOCS = [
    (1, "Staging SSL certificate expired", [1, 0, 0, 0, 0, 0, 0, 0]),
    (2, "Cloud Run cold start latency", [0, 1, 0, 0, 0, 0, 0, 0]),
    (3, "Pricing tiers revised", [0, 0, 1, 0, 0, 0, 0, 0]),
    (4, "Grafana alert storm", [0, 0, 0, 1, 0, 0, 0, 0]),
]


@pytest.fixture(scope="module")
def engine():
    eng = db.get_engine(DB_URL)
    db.execute("CREATE EXTENSION IF NOT EXISTS vector;", engine=eng)
    db.execute("DROP TABLE IF EXISTS note_chunks;", engine=eng)
    db.execute("DROP TABLE IF EXISTS notes;", engine=eng)
    db.execute(
        f"""
        CREATE TABLE notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            content TEXT NOT NULL,
            content_embedding VECTOR({DIM}),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        engine=eng,
    )
    db.ensure_chunks_table(DIM, engine=eng)

    for note_id, title, vec in DOCS:
        literal = "[" + ",".join(str(float(x)) for x in vec) + "]"
        db.execute(
            """
            INSERT INTO notes (id, title, content, content_embedding)
            VALUES (:id, :title, :content, CAST(:vec AS vector));
            """,
            {"id": note_id, "title": title, "content": f"Body of {title}.", "vec": literal},
            engine=eng,
        )
        db.execute(
            """
            INSERT INTO note_chunks
                (note_id, chunk_index, content, token_count, content_embedding)
            VALUES (:id, 0, :content, 5, CAST(:vec AS vector));
            """,
            {"id": note_id, "content": f"{title}. Body of {title}.", "vec": literal},
            engine=eng,
        )
    yield eng
    db.execute("DROP TABLE IF EXISTS note_chunks;", engine=eng)
    db.execute("DROP TABLE IF EXISTS notes;", engine=eng)


def test_retrieve_notes_orders_by_cosine_distance(engine):
    """The vector nearest the query must come first."""
    hits = retrieve_notes(
        "irrelevant", k=4, query_vector=[1, 0, 0, 0, 0, 0, 0, 0], engine=engine
    )
    assert [h.note_id for h in hits][0] == 1
    assert hits[0].score == pytest.approx(1.0, abs=1e-6)


def test_retrieve_notes_respects_k(engine):
    hits = retrieve_notes(
        "q", k=2, query_vector=[0, 1, 0, 0, 0, 0, 0, 0], engine=engine
    )
    assert len(hits) == 2
    assert hits[0].note_id == 2


def test_retrieve_chunks_resolves_to_parent_note(engine):
    """A chunk hit must carry the parent note's id and title for citation."""
    hits = retrieve_chunks(
        "q", k=2, query_vector=[0, 0, 0, 1, 0, 0, 0, 0], engine=engine
    )
    assert hits[0].note_id == 4
    assert hits[0].title == "Grafana alert storm"
    assert hits[0].chunk_text is not None
    assert hits[0].matched_chunks


def test_retrieve_chunks_returns_distinct_notes(engine):
    hits = retrieve_chunks(
        "q", k=4, query_vector=[1, 0, 0, 0, 0, 0, 0, 0], engine=engine
    )
    ids = [h.note_id for h in hits]
    assert len(ids) == len(set(ids))


def test_to_dict_shape_matches_tool_contract(engine):
    """search_notes returns these keys to the agent; they must not drift."""
    hits = retrieve_notes(
        "q", k=1, query_vector=[1, 0, 0, 0, 0, 0, 0, 0], engine=engine
    )
    payload = hits[0].to_dict()
    assert set(payload) >= {"id", "title", "content", "similarity"}


def test_hybrid_fusion_over_real_candidates(engine):
    qvec = [1, 0, 0, 0, 0, 0, 0, 0]
    notes = retrieve_notes("ssl certificate", k=4, query_vector=qvec, engine=engine)
    chunks = retrieve_chunks("ssl certificate", k=4, query_vector=qvec, engine=engine)

    fused = HybridFusionReranker().fuse("ssl certificate", notes, chunks, top_k=3)
    assert fused[0].note_id == 1
    assert len({h.note_id for h in fused}) == len(fused)


def test_chunks_cascade_on_note_delete(engine):
    """Deleting a note must remove its chunks via the foreign key."""
    db.execute(
        "INSERT INTO notes (id, title, content, content_embedding) "
        "VALUES (99, 't', 'c', CAST('[0,0,0,0,0,0,0,1]' AS vector));",
        engine=engine,
    )
    db.execute(
        "INSERT INTO note_chunks (note_id, chunk_index, content, token_count, content_embedding) "
        "VALUES (99, 0, 'c', 1, CAST('[0,0,0,0,0,0,0,1]' AS vector));",
        engine=engine,
    )
    db.execute("DELETE FROM notes WHERE id = 99;", engine=engine)

    remaining = db.query(
        "SELECT COUNT(*) AS n FROM note_chunks WHERE note_id = 99", engine=engine
    )
    assert remaining[0]["n"] == 0


def test_chunks_table_dimension_reports_declared_dim(engine):
    assert db.chunks_table_dimension(engine=engine) == DIM
