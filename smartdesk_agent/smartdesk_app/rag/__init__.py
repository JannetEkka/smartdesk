"""Retrieval pipeline for SmartDesk's notes knowledge base.

Kept deliberately small and dependency-free beyond what the project already
uses: plain SQL over SQLAlchemy, no retrieval framework. The pieces are
separable so each can be measured on its own:

    embeddings.py  pluggable embedding providers (Vertex / local)
    chunking.py    token-based chunking with overlap
    db.py          portable Postgres/AlloyDB access and schema helpers
    retrieval.py   whole-note and chunk-level retrieval
    rerankers.py   candidate reordering strategies
"""

from .embeddings import Embedder, LocalEmbedder, VertexEmbedder, get_embedder
from .chunking import Chunk, chunk_text
from .retrieval import RetrievedNote, retrieve_chunks, retrieve_notes

__all__ = [
    "Embedder",
    "LocalEmbedder",
    "VertexEmbedder",
    "get_embedder",
    "Chunk",
    "chunk_text",
    "RetrievedNote",
    "retrieve_notes",
    "retrieve_chunks",
]
