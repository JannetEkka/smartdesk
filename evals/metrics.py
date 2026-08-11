"""Retrieval metrics.

Two metrics, both standard, reported at several cutoffs:

**recall@k** — of the notes that genuinely answer a question, what fraction
appear in the top k? This is the metric that matters most here, because the
agent reads several results and can synthesise across them.

**MRR@k** — the reciprocal of the rank of the *first* relevant result, zero if
none appears within k. This matters because a language model weights the first
result it reads disproportionately, so being right at rank 1 is worth more
than being right at rank 5.

Both are macro-averaged: every question counts equally regardless of how many
relevant notes it has.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


def recall_at_k(retrieved: Sequence[int], relevant: Iterable[int], k: int) -> float:
    """Fraction of relevant items appearing in the top k retrieved."""
    relevant = set(relevant)
    if not relevant:
        return 0.0
    hits = len(relevant.intersection(retrieved[:k]))
    return hits / len(relevant)


def reciprocal_rank_at_k(
    retrieved: Sequence[int], relevant: Iterable[int], k: int
) -> float:
    """1/rank of the first relevant item within the top k, else 0."""
    relevant = set(relevant)
    for position, item in enumerate(retrieved[:k], start=1):
        if item in relevant:
            return 1.0 / position
    return 0.0


@dataclass
class EvalResult:
    """Aggregated metrics for one retrieval strategy."""

    name: str
    cutoffs: list[int]
    recall: dict[int, float]
    mrr: dict[int, float]
    n_queries: int
    per_query: list[dict]
    latency_ms: dict[str, float] | None = None
    extra: dict | None = None

    def to_dict(self) -> dict:
        out = {
            "name": self.name,
            "n_queries": self.n_queries,
            "cutoffs": self.cutoffs,
            "recall_at_k": {str(k): round(v, 4) for k, v in self.recall.items()},
            "mrr_at_k": {str(k): round(v, 4) for k, v in self.mrr.items()},
        }
        if self.latency_ms:
            out["latency_ms"] = {k: round(v, 1) for k, v in self.latency_ms.items()}
        if self.extra:
            out["extra"] = self.extra
        out["per_query"] = self.per_query
        return out


def evaluate(
    name: str,
    runs: list[tuple[str, list[int], list[int]]],
    cutoffs: Sequence[int] = (1, 3, 5, 10),
    latency_ms: dict[str, float] | None = None,
    extra: dict | None = None,
) -> EvalResult:
    """Aggregate per-query retrievals into recall@k and MRR@k.

    Args:
        runs: one ``(question_id, retrieved_note_ids, relevant_note_ids)``
            tuple per query, with retrieved ids in rank order.
    """
    cutoffs = list(cutoffs)
    recall = {k: 0.0 for k in cutoffs}
    mrr = {k: 0.0 for k in cutoffs}
    per_query = []

    for qid, retrieved, relevant in runs:
        row = {"question_id": qid, "retrieved": list(retrieved[: max(cutoffs)])}
        for k in cutoffs:
            r = recall_at_k(retrieved, relevant, k)
            m = reciprocal_rank_at_k(retrieved, relevant, k)
            recall[k] += r
            mrr[k] += m
            row[f"recall@{k}"] = round(r, 4)
            row[f"rr@{k}"] = round(m, 4)
        row["relevant"] = list(relevant)
        per_query.append(row)

    n = len(runs) or 1
    return EvalResult(
        name=name,
        cutoffs=cutoffs,
        recall={k: v / n for k, v in recall.items()},
        mrr={k: v / n for k, v in mrr.items()},
        n_queries=len(runs),
        per_query=per_query,
        latency_ms=latency_ms,
        extra=extra,
    )


def paired_bootstrap(
    a: EvalResult,
    b: EvalResult,
    metric: str,
    iterations: int = 10000,
    seed: int = 12345,
) -> dict:
    """Paired bootstrap of ``a - b`` on a per-query metric.

    With 30 questions, one question is worth 0.033 of recall@1, so raw deltas
    of that size are indistinguishable from noise. Resampling the *paired*
    per-query differences gives a confidence interval that says so explicitly,
    and a two-sided p-value for whether the difference is real.

    Pairing matters: both strategies answer the same questions, so comparing
    per-question differences removes the variance from questions simply being
    easy or hard.
    """
    import random

    by_id_a = {r["question_id"]: r[metric] for r in a.per_query}
    by_id_b = {r["question_id"]: r[metric] for r in b.per_query}
    shared = sorted(set(by_id_a) & set(by_id_b))
    diffs = [by_id_a[q] - by_id_b[q] for q in shared]
    n = len(diffs)
    if n == 0:
        return {"delta": 0.0, "ci_low": 0.0, "ci_high": 0.0, "p_value": 1.0, "n": 0}

    observed = sum(diffs) / n
    rng = random.Random(seed)
    means = []
    for _ in range(iterations):
        sample = [diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()

    lo = means[int(0.025 * iterations)]
    hi = means[int(0.975 * iterations)]
    # Two-sided p-value by recentring the bootstrap distribution on zero.
    centred = [m - observed for m in means]
    extreme = sum(1 for c in centred if abs(c) >= abs(observed))
    return {
        "delta": observed,
        "ci_low": lo,
        "ci_high": hi,
        "p_value": extreme / iterations,
        "n": n,
        "n_better": sum(1 for d in diffs if d > 0),
        "n_worse": sum(1 for d in diffs if d < 0),
    }


def format_significance(
    results: Sequence[EvalResult], baseline: EvalResult, metrics: Sequence[str] = ("recall@5", "rr@10")
) -> str:
    """Table of paired bootstrap comparisons against the baseline."""
    lines = [
        f"Paired bootstrap vs '{baseline.name}' (10k resamples, 95% CI)",
        "",
    ]
    name_w = max(len(r.name) for r in results) + 2
    for metric in metrics:
        lines.append(f"  {metric}")
        header = "    " + "strategy".ljust(name_w) + "  delta     95% CI              p      w/l"
        lines.append(header)
        lines.append("    " + "-" * (len(header) - 4))
        for r in results:
            if r is baseline:
                continue
            s = paired_bootstrap(r, baseline, metric)
            verdict = "" if s["p_value"] >= 0.05 else "  *"
            lines.append(
                f"    {r.name.ljust(name_w)}  {s['delta']:+.3f}   "
                f"[{s['ci_low']:+.3f}, {s['ci_high']:+.3f}]   "
                f"{s['p_value']:.2f}   {s['n_better']}/{s['n_worse']}{verdict}"
            )
        lines.append("")
    lines.append("  * = p < 0.05.  w/l = questions improved / regressed.")
    return "\n".join(lines)


def format_table(results: Sequence[EvalResult], baseline: EvalResult | None = None) -> str:
    """Render results as a fixed-width table, with deltas against a baseline."""
    if not results:
        return "(no results)"
    cutoffs = results[0].cutoffs
    name_w = max(len(r.name) for r in results) + 2
    name_w = max(name_w, 24)

    header = "strategy".ljust(name_w)
    for k in cutoffs:
        header += f"  R@{k:<7}"
    for k in cutoffs:
        header += f"  MRR@{k:<5}"
    lines = [header, "-" * len(header)]

    for r in results:
        line = r.name.ljust(name_w)
        for k in cutoffs:
            cell = f"{r.recall[k]:.3f}"
            if baseline is not None and r is not baseline:
                delta = r.recall[k] - baseline.recall[k]
                cell += f"{delta:+.3f}" if abs(delta) >= 0.0005 else "  ----"
            line += f"  {cell:<9}"
        for k in cutoffs:
            cell = f"{r.mrr[k]:.3f}"
            if baseline is not None and r is not baseline:
                delta = r.mrr[k] - baseline.mrr[k]
                cell += f"{delta:+.3f}" if abs(delta) >= 0.0005 else "  ----"
            line += f"  {cell:<9}"
        lines.append(line)

    return "\n".join(lines)
