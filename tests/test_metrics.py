"""Tests for the retrieval metrics.

The metrics are the thing every conclusion rests on, so they are tested
against hand-computed values rather than against themselves.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "evals"))

from metrics import (  # noqa: E402
    evaluate,
    paired_bootstrap,
    recall_at_k,
    reciprocal_rank_at_k,
)


def test_recall_counts_fraction_of_relevant_found():
    retrieved = [3, 1, 7, 2, 9]
    assert recall_at_k(retrieved, [3], 1) == 1.0
    assert recall_at_k(retrieved, [1], 1) == 0.0
    assert recall_at_k(retrieved, [1], 3) == 1.0
    # Two relevant, one found in the top 3.
    assert recall_at_k(retrieved, [3, 2], 3) == 0.5
    assert recall_at_k(retrieved, [3, 2], 5) == 1.0


def test_recall_with_no_relevant_is_zero():
    assert recall_at_k([1, 2, 3], [], 3) == 0.0


def test_recall_ignores_extra_retrieved_beyond_k():
    assert recall_at_k([9, 9, 9, 4], [4], 3) == 0.0
    assert recall_at_k([9, 9, 9, 4], [4], 4) == 1.0


def test_reciprocal_rank_uses_first_relevant_position():
    assert reciprocal_rank_at_k([5, 2, 8], [5], 3) == 1.0
    assert reciprocal_rank_at_k([5, 2, 8], [2], 3) == 0.5
    assert reciprocal_rank_at_k([5, 2, 8], [8], 3) == 1.0 / 3
    assert reciprocal_rank_at_k([5, 2, 8], [99], 3) == 0.0


def test_reciprocal_rank_respects_cutoff():
    # Relevant item sits at rank 3, so it does not count at k=2.
    assert reciprocal_rank_at_k([1, 2, 3], [3], 2) == 0.0
    assert reciprocal_rank_at_k([1, 2, 3], [3], 3) == 1.0 / 3


def test_reciprocal_rank_takes_earliest_of_several_relevant():
    assert reciprocal_rank_at_k([1, 2, 3], [2, 3], 3) == 0.5


def test_evaluate_macro_averages_over_queries():
    runs = [
        ("q1", [1, 2, 3], [1]),  # RR=1.0   recall@3=1.0
        ("q2", [4, 5, 6], [5]),  # RR=0.5   recall@3=1.0
        ("q3", [7, 8, 9], [99]),  # RR=0.0  recall@3=0.0
    ]
    result = evaluate("test", runs, cutoffs=(1, 3))

    assert result.n_queries == 3
    assert result.recall[1] == 1 / 3       # only q1 hits at rank 1
    assert result.recall[3] == 2 / 3       # q1 and q2
    assert result.mrr[3] == (1.0 + 0.5 + 0.0) / 3


def test_evaluate_weights_every_question_equally():
    """A question with many relevant notes must not dominate the average."""
    runs = [
        ("many", [1, 2, 3], [1, 2, 3]),  # recall@3 = 1.0
        ("one", [9, 9, 9], [4]),         # recall@3 = 0.0
    ]
    result = evaluate("test", runs, cutoffs=(3,))
    assert result.recall[3] == 0.5


def test_paired_bootstrap_detects_no_difference():
    runs = [(f"q{i}", [1], [1]) for i in range(20)]
    a = evaluate("a", runs, cutoffs=(1,))
    b = evaluate("b", runs, cutoffs=(1,))

    stats = paired_bootstrap(a, b, "rr@1")
    assert stats["delta"] == 0.0
    assert stats["ci_low"] == 0.0 and stats["ci_high"] == 0.0
    assert stats["n_better"] == 0 and stats["n_worse"] == 0


def test_paired_bootstrap_detects_consistent_difference():
    good = evaluate("good", [(f"q{i}", [1], [1]) for i in range(30)], cutoffs=(1,))
    bad = evaluate("bad", [(f"q{i}", [9], [1]) for i in range(30)], cutoffs=(1,))

    stats = paired_bootstrap(good, bad, "rr@1")
    assert stats["delta"] == 1.0
    assert stats["n_better"] == 30
    assert stats["p_value"] < 0.05


def test_paired_bootstrap_is_deterministic():
    a = evaluate("a", [(f"q{i}", [1 if i % 2 else 9], [1]) for i in range(20)], cutoffs=(1,))
    b = evaluate("b", [(f"q{i}", [9], [1]) for i in range(20)], cutoffs=(1,))
    assert paired_bootstrap(a, b, "rr@1") == paired_bootstrap(a, b, "rr@1")
