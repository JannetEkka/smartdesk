-- SmartDesk migration 001 — note_chunks
--
-- Adds chunk-level retrieval alongside the existing whole-note embeddings.
--
-- This migration is ADDITIVE and REVERSIBLE. It creates one new table and
-- touches nothing that already exists: the `notes` table keeps its rows and
-- its content_embedding column, so the default retrieval path is unaffected
-- and this can be applied to a live database.
--
-- To roll back, see the bottom of this file.
--
-- Dimension note: VECTOR(768) matches text-embedding-005, the production
-- embedder. A local development database built with the 384-dimension MiniLM
-- embedder needs VECTOR(384) instead — evals/ingest.py creates the table with
-- the active embedder's dimension automatically, so this file is only for
-- AlloyDB and other 768-dimension deployments.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS note_chunks (
    id SERIAL PRIMARY KEY,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    content_embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (note_id, chunk_index)
);

-- Chunk hits resolve back to their parent note for citation, so note_id is
-- the hot lookup path.
CREATE INDEX IF NOT EXISTS note_chunks_note_id_idx ON note_chunks (note_id);

-- ON DELETE CASCADE means deleting a note removes its chunks automatically,
-- rather than relying on application code to remember.

-- Backfill chunks for existing notes with:
--     SMARTDESK_EMBEDDER=vertex python evals/ingest.py
-- (without --reset, which would drop the notes table).

-- ---------------------------------------------------------------------------
-- Rollback
-- ---------------------------------------------------------------------------
-- DROP TABLE IF EXISTS note_chunks;
--
-- Nothing else needs undoing: no existing table or column was modified.
