"""Tests for BM25 scoring and rank fusion.

The cross-encoder and Gemini rerankers are not tested here: one needs a model
download and the other needs cloud credentials. Their contribution is measured
by the eval harness instead.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "smartdesk_agent" / "smartdesk_app"))

from rag.rerankers import (  # noqa: E402
    HybridFusionReranker,
    RRFReranker,
    bm25_scores,
    fuse_rankings,
)
from rag.retrieval import RetrievedNote  # noqa: E402


def _note(note_id: int, content: str, score: float = 0.5) -> RetrievedNote:
    return RetrievedNote(
        note_id=note_id, title=f"Note {note_id}", content=content, score=score
    )


def test_bm25_ranks_term_matches_above_non_matches():
    docs = [
        "the ssl certificate on staging expired overnight",
        "the dashboard redesign wireframes were approved",
        "pricing tiers were revised after finance review",
    ]
    scores = bm25_scores("ssl certificate expired", docs)
    assert scores[0] > scores[1]
    assert scores[0] > scores[2]


def test_bm25_ignores_stopwords():
    docs = ["alpha beta gamma", "the and of it is"]
    # A query of pure stopwords discriminates nothing.
    assert bm25_scores("the and of", docs) == [0.0, 0.0]


def test_bm25_handles_empty_inputs():
    assert bm25_scores("anything", []) == []
    assert bm25_scores("", ["some document"]) == [0.0]


def test_bm25_saturates_on_repeated_terms():
    """Term frequency saturation: 10 repeats must not score 10x a single one."""
    once = bm25_scores("alpha", ["alpha beta gamma delta", "zeta eta theta iota"])[0]
    many = bm25_scores("alpha", ["alpha alpha alpha alpha alpha alpha alpha alpha alpha alpha", "zeta eta theta iota"])[0]
    assert many > once
    assert many < once * 10


def test_fuse_rankings_rewards_agreement():
    """An item both signals rank first beats items they disagree about."""
    scores = fuse_rankings([[1, 2, 3], [1, 3, 2]])
    assert scores[1] > scores[2]
    assert scores[1] > scores[3]
    # 2 and 3 swap places between the two rankings, so RRF scores them equally.
    assert scores[2] == scores[3]


def test_fuse_rankings_handles_disjoint_rankings():
    scores = fuse_rankings([[1, 2], [3, 4]])
    assert set(scores) == {1, 2, 3, 4}
    assert scores[1] > scores[2]


def test_rrf_reranker_promotes_lexical_match():
    """A rare exact term should pull a note up past the dense ordering.

    This is the case dense retrieval handles worst and BM25 handles best. The
    note with the exact match sits last in the dense ordering and should be
    promoted above the notes that share no query term.
    """
    candidates = [_note(i, f"general note {i} about the quarter ahead") for i in range(1, 8)]
    candidates.append(_note(8, "the kubernetes ingress controller misrouted traffic"))

    ranked = RRFReranker().rerank("kubernetes ingress controller", candidates, top_k=8)
    assert ranked[0].note_id == 8


def test_rrf_ignores_documents_with_no_lexical_match():
    """Zero-BM25 documents must not earn an RRF contribution from sort order.

    Without this, a note sharing no query term is handed a lexical rank purely
    by its position in the list and can outscore a genuine match.
    """
    candidates = [
        _note(1, "completely unrelated content about wireframes"),
        _note(2, "also unrelated, discussing the pricing spreadsheet"),
        _note(3, "the certificate expired on the staging environment"),
    ]
    ranked = RRFReranker().rerank("certificate expired staging", candidates, top_k=3)
    assert ranked[0].note_id == 3


def test_rrf_reranker_respects_top_k():
    candidates = [_note(i, f"content {i}") for i in range(10)]
    assert len(RRFReranker().rerank("content", candidates, top_k=3)) == 3


def test_rerankers_handle_empty_candidates():
    assert RRFReranker().rerank("anything", [], top_k=5) == []
    assert HybridFusionReranker().fuse("anything", [], [], top_k=5) == []


def test_hybrid_fusion_deduplicates_by_note():
    """The same note from both retrievers must appear once."""
    notes = [_note(1, "alpha content"), _note(2, "beta content")]
    chunks = [_note(1, "alpha passage"), _note(3, "gamma passage")]

    fused = HybridFusionReranker().fuse("alpha", notes, chunks, top_k=10)
    ids = [n.note_id for n in fused]
    assert sorted(ids) == [1, 2, 3]
    assert len(ids) == len(set(ids))


def test_hybrid_fusion_prefers_note_agreed_by_both_retrievers():
    notes = [_note(7, "shared topic"), _note(8, "only in notes")]
    chunks = [_note(7, "shared topic passage"), _note(9, "only in chunks")]

    fused = HybridFusionReranker().fuse("shared topic", notes, chunks, top_k=3)
    assert fused[0].note_id == 7
