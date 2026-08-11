"""Tests for token-based chunking with overlap."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "smartdesk_agent" / "smartdesk_app"))

from rag.chunking import (  # noqa: E402
    WordTokenizer,
    chunk_text,
    split_sentences,
)

TOK = WordTokenizer()


def test_short_text_is_one_chunk():
    """A document under the budget passes through whole.

    This is what makes chunking safe to enable on a corpus of short notes:
    they are not split at all.
    """
    text = "The staging certificate expired. Rahul renewed it on Monday."
    chunks = chunk_text(text, chunk_size=100, overlap=20, tokenizer=TOK)
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].index == 0


def test_empty_text_yields_no_chunks():
    assert chunk_text("", 100, 20, TOK) == []
    assert chunk_text("   \n  ", 100, 20, TOK) == []


def test_long_text_splits_and_indexes_in_order():
    sentences = [f"Sentence number {i} about topic {i}." for i in range(40)]
    chunks = chunk_text(" ".join(sentences), chunk_size=30, overlap=8, tokenizer=TOK)

    assert len(chunks) > 1
    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert all(c.token_count <= 30 for c in chunks)


def test_chunks_overlap():
    """Consecutive chunks must share trailing/leading content.

    Overlap is the whole point: a fact on a boundary should survive intact in
    at least one chunk.
    """
    sentences = [f"Alpha {i} beta gamma delta epsilon." for i in range(30)]
    chunks = chunk_text(" ".join(sentences), chunk_size=25, overlap=10, tokenizer=TOK)

    assert len(chunks) >= 2
    for first, second in zip(chunks, chunks[1:]):
        tail = set(first.text.split())
        head = set(second.text.split())
        assert tail & head, "consecutive chunks share no tokens"


def test_no_overlap_when_overlap_is_zero():
    sentences = [f"Unique{i} word{i} token{i} filler{i}." for i in range(20)]
    chunks = chunk_text(" ".join(sentences), chunk_size=16, overlap=0, tokenizer=TOK)

    assert len(chunks) > 1
    seen = set()
    for chunk in chunks:
        words = set(chunk.text.split())
        assert not (words & seen), "chunks overlap despite overlap=0"
        seen |= words


def test_covers_all_content():
    """Every sentence must appear in at least one chunk."""
    sentences = [f"Fact {i} is that thing number {i} happened." for i in range(25)]
    text = " ".join(sentences)
    chunks = chunk_text(text, chunk_size=28, overlap=6, tokenizer=TOK)

    joined = " ".join(c.text for c in chunks)
    for sentence in sentences:
        assert sentence in joined, f"lost: {sentence}"


def test_oversized_sentence_is_hard_split():
    """A single sentence longer than the budget still respects chunk_size."""
    giant = " ".join(f"word{i}" for i in range(200)) + "."
    chunks = chunk_text(giant, chunk_size=40, overlap=5, tokenizer=TOK)

    assert len(chunks) > 1
    assert all(c.token_count <= 40 for c in chunks)


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("some text here", chunk_size=10, overlap=10, tokenizer=TOK)
    with pytest.raises(ValueError):
        chunk_text("some text here", chunk_size=10, overlap=25, tokenizer=TOK)


def test_terminates_on_pathological_overlap():
    """Near-maximal overlap must not loop forever.

    The packing loop falls forward when the overlap would consume a whole
    chunk; without that guard this input never terminates.
    """
    sentences = [f"Sentence {i} with several words in it here." for i in range(30)]
    chunks = chunk_text(" ".join(sentences), chunk_size=12, overlap=11, tokenizer=TOK)
    assert len(chunks) > 1
    assert all(c.token_count <= 12 for c in chunks)


def test_split_sentences_handles_punctuation_and_newlines():
    assert split_sentences("One. Two! Three?") == ["One.", "Two!", "Three?"]
    assert split_sentences("Title\nBody text here.") == ["Title", "Body text here."]
    assert split_sentences("") == []


def test_word_tokenizer_counts_and_splits():
    assert TOK.count("one two three") == 3
    assert TOK.count("") == 0
    pieces = TOK.hard_split("a b c d e f", 2)
    assert pieces == ["a b", "c d", "e f"]
