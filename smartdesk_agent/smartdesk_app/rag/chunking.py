"""Token-based chunking with overlap.

Notes are currently embedded whole, which works while notes are short but
loses recall once a document covers several topics: one vector has to
represent all of them, and it ends up close to none of them.

The chunker packs whole sentences into token-budgeted windows and carries a
configurable overlap between consecutive windows, so a fact sitting on a chunk
boundary still appears intact in one of them. Chunks keep a ``note_id`` so a
chunk hit resolves back to a citable parent note.

Token counting goes through a small ``Tokenizer`` abstraction. When
``transformers`` is importable (it ships with sentence-transformers) the real
subword tokenizer is used; otherwise a dependency-free regex word tokenizer
stands in. Segmentation only needs to be consistent, not identical to the
embedding model's own tokenizer, so the approximation is acceptable for the
Vertex path — but chunk sizes are expressed in whichever unit is active, which
matters when comparing runs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)

# Split after ., !, ? or a newline. Deliberately simple: the corpus is meeting
# notes, not prose with heavy abbreviation use.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
_WORD_RE = re.compile(r"\S+")


class Tokenizer(Protocol):
    def count(self, text: str) -> int:
        """Number of tokens in text."""
        ...

    def hard_split(self, text: str, size: int) -> list[str]:
        """Split text into pieces of at most ``size`` tokens each."""
        ...


class WordTokenizer:
    """Whitespace-delimited tokens. No dependencies, fully deterministic."""

    name = "word"

    def count(self, text: str) -> int:
        return len(_WORD_RE.findall(text))

    def hard_split(self, text: str, size: int) -> list[str]:
        words = _WORD_RE.findall(text)
        return [
            " ".join(words[i : i + size]) for i in range(0, len(words), size)
        ] or [""]


class HFTokenizer:
    """Real subword tokenizer from a Hugging Face model."""

    def __init__(self, model_id: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        from transformers import AutoTokenizer

        self.name = model_id.split("/")[-1]
        self._tok = AutoTokenizer.from_pretrained(model_id)

    def count(self, text: str) -> int:
        return len(self._tok.encode(text, add_special_tokens=False))

    def hard_split(self, text: str, size: int) -> list[str]:
        ids = self._tok.encode(text, add_special_tokens=False)
        return [
            self._tok.decode(ids[i : i + size]) for i in range(0, len(ids), size)
        ] or [""]


def get_tokenizer(prefer_subword: bool = True) -> Tokenizer:
    """Return a subword tokenizer when available, else the word tokenizer."""
    if prefer_subword:
        try:
            return HFTokenizer()
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.info("Subword tokenizer unavailable (%s); using word tokenizer.", exc)
    return WordTokenizer()


@dataclass(frozen=True)
class Chunk:
    """One chunk of a note, with the position needed to order and cite it."""

    index: int
    text: str
    token_count: int


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.split(text) if s and s.strip()]


def chunk_text(
    text: str,
    chunk_size: int = 180,
    overlap: int = 40,
    tokenizer: Tokenizer | None = None,
) -> list[Chunk]:
    """Split ``text`` into overlapping, sentence-aligned chunks.

    Args:
        text: The document to split.
        chunk_size: Maximum tokens per chunk.
        overlap: Tokens of trailing context repeated at the start of the next
            chunk. Must be smaller than ``chunk_size``.

    Returns:
        Chunks in document order. A document shorter than ``chunk_size``
        produces exactly one chunk holding the whole text, which is what makes
        this safe to apply to a corpus of short notes: they simply pass
        through unchanged.
    """
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})"
        )
    tokenizer = tokenizer or get_tokenizer()
    text = (text or "").strip()
    if not text:
        return []

    # Split into sentences, then hard-split any sentence that alone exceeds the
    # budget. After this pass every unit fits in a chunk, which keeps the
    # packing loop below simple and guarantees it terminates.
    units: list[str] = []
    for sentence in split_sentences(text):
        if tokenizer.count(sentence) > chunk_size:
            units.extend(tokenizer.hard_split(sentence, chunk_size))
        else:
            units.append(sentence)
    if not units:
        return []

    counts = [tokenizer.count(u) for u in units]

    chunks: list[Chunk] = []
    i = 0
    while i < len(units):
        # Greedily pack sentences until the budget is spent. The `j == i` guard
        # ensures a chunk always contains at least one unit.
        j, total = i, 0
        while j < len(units) and (total + counts[j] <= chunk_size or j == i):
            total += counts[j]
            j += 1

        chunks.append(
            Chunk(index=len(chunks), text=" ".join(units[i:j]), token_count=total)
        )

        if j >= len(units):
            break

        # Back up far enough to repeat roughly `overlap` tokens of context.
        k, carried = j, 0
        while k > i and carried + counts[k - 1] <= overlap:
            carried += counts[k - 1]
            k -= 1

        # If the overlap would consume the whole chunk we would never advance,
        # so fall forward to j and accept no overlap for this boundary.
        i = k if k > i else j

    return chunks
