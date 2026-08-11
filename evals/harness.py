#!/usr/bin/env python3
"""Run the retrieval eval and print a comparison table.

Each strategy is run over every labelled question, retrieving the top 10 notes
so recall@10 is measurable. Note that the shipped ``search_notes`` returns 5,
so the ``@5`` column is the one that reflects production behaviour today.

Usage::

    export SMARTDESK_EMBEDDER=local
    export DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk

    python evals/harness.py                       # every available strategy
    python evals/harness.py --strategies baseline # just one
    python evals/harness.py --save baseline       # write results/baseline.json
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
import time
from pathlib import Path

import _bootstrap  # noqa: F401  (sets sys.path)

REPO_ROOT = _bootstrap.REPO_ROOT

from rag import db, rerankers  # noqa: E402
from rag.embeddings import get_embedder  # noqa: E402
from rag.retrieval import retrieve_chunks, retrieve_notes  # noqa: E402

from metrics import EvalResult, evaluate, format_table  # noqa: E402

QUESTIONS = REPO_ROOT / "evals" / "questions.jsonl"
RESULTS_DIR = REPO_ROOT / "evals" / "results"

#: Deepest cutoff we report, and therefore how many results each strategy must
#: return.
MAX_K = 10
CUTOFFS = (1, 3, 5, 10)

#: Candidates pulled before reranking. The reranker reorders these and the
#: metrics are computed over the reordered list.
RERANK_CANDIDATES = 25


def load_questions() -> list[dict]:
    rows = [
        json.loads(line) for line in QUESTIONS.read_text().splitlines() if line.strip()
    ]
    if not rows:
        raise ValueError("No questions found.")
    return rows


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------
#
# Every strategy takes (question_text, precomputed_query_vector) and returns
# note ids in rank order. The query vector is computed once per question and
# shared, so strategies are compared on retrieval, not on embedding cost.


def _baseline(question: str, qvec: list[float]) -> list[int]:
    return [r.note_id for r in retrieve_notes(question, k=MAX_K, query_vector=qvec)]


def _chunked(question: str, qvec: list[float]) -> list[int]:
    return [r.note_id for r in retrieve_chunks(question, k=MAX_K, query_vector=qvec)]


def _make_reranked(reranker, source: str):
    """Wrap a reranker around a wide candidate fetch."""

    def run(question: str, qvec: list[float]) -> list[int]:
        fetch = retrieve_chunks if source == "chunked" else retrieve_notes
        candidates = fetch(question, k=RERANK_CANDIDATES, query_vector=qvec)
        ranked = reranker.rerank(question, candidates, top_k=MAX_K)
        return [r.note_id for r in ranked]

    return run


def build_strategies(selected: list[str] | None) -> dict:
    available = {
        "baseline": _baseline,
        "chunked": _chunked,
    }
    for name, factory in rerankers.available().items():
        for source in ("baseline", "chunked"):
            available[f"{source}+{name}"] = _make_reranked(factory(), source)

    if not selected:
        return available
    missing = [s for s in selected if s not in available]
    if missing:
        raise SystemExit(
            f"Unknown strategies: {', '.join(missing)}\n"
            f"Available: {', '.join(sorted(available))}"
        )
    return {s: available[s] for s in selected}


def run_strategy(name: str, fn, questions: list[dict], qvecs: dict) -> EvalResult:
    runs = []
    latencies = []
    for q in questions:
        start = time.perf_counter()
        retrieved = fn(q["question"], qvecs[q["id"]])
        latencies.append((time.perf_counter() - start) * 1000)
        runs.append((q["id"], retrieved, q["relevant_note_ids"]))

    latency = {
        "mean": statistics.mean(latencies),
        "p50": statistics.median(latencies),
        "p95": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0],
    }
    return evaluate(name, runs, CUTOFFS, latency_ms=latency)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategies", nargs="*", help="subset to run")
    parser.add_argument("--save", metavar="LABEL", help="write results/LABEL.json")
    parser.add_argument(
        "--baseline-name",
        default="baseline",
        help="strategy to show deltas against",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)

    questions = load_questions()
    unreviewed = sum(1 for q in questions if not q.get("reviewed"))

    embedder = get_embedder()
    embedder.embed_query("warmup")

    corpus_size = db.query("SELECT COUNT(*) AS n FROM notes")[0]["n"]
    chunk_rows = db.query("SELECT COUNT(*) AS n FROM note_chunks")
    chunk_count = chunk_rows[0]["n"] if chunk_rows else 0

    print(f"Embedder:  {embedder.name} ({embedder.dimension}d)")
    print(f"Corpus:    {corpus_size} notes, {chunk_count} chunks")
    print(f"Questions: {len(questions)}", end="")
    if unreviewed:
        print(f"  [WARNING: {unreviewed} labels not yet human-reviewed]")
    else:
        print()
    print()

    # Embed every question once and share across strategies.
    qvecs = {q["id"]: embedder.embed_query(q["question"]) for q in questions}

    strategies = build_strategies(args.strategies)
    results = []
    for name, fn in strategies.items():
        results.append(run_strategy(name, fn, questions, qvecs))

    baseline = next((r for r in results if r.name == args.baseline_name), None)
    print(format_table(results, baseline))
    print()
    print("latency per query (ms):")
    for r in results:
        if r.latency_ms:
            print(
                f"  {r.name:<28} mean {r.latency_ms['mean']:7.1f}   "
                f"p50 {r.latency_ms['p50']:7.1f}   p95 {r.latency_ms['p95']:7.1f}"
            )

    if args.save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RESULTS_DIR / f"{args.save}.json"
        payload = {
            "embedder": {"name": embedder.name, "dimension": embedder.dimension},
            "corpus": {"notes": corpus_size, "chunks": chunk_count},
            "questions": len(questions),
            "labels_reviewed": unreviewed == 0,
            "results": [r.to_dict() for r in results],
        }
        path.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"\nSaved {path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
