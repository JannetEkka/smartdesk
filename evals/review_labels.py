#!/usr/bin/env python3
"""Interactive review of the labelled question set.

Every number in RESULTS.md rests on these labels being correct, and they were
generated rather than curated. A retrieval eval cannot tell a wrong label from
a bad retriever — both look like a low score — so the labels have to be read
by a human once.

This walks through each question, shows the notes currently labelled as
answering it, and lets you accept, re-label, reword, or drop it. Progress is
saved as you go, so you can stop and resume.

    python evals/review_labels.py                 # review everything unreviewed
    python evals/review_labels.py --all           # re-review everything
    python evals/review_labels.py --show-retrieved  # also show what search returns

``--show-retrieved`` needs DATABASE_URL and an embedder, and is the most
useful mode: seeing what retrieval actually returns often reveals that the
right answer is a note you had not labelled.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (sets sys.path)

REPO_ROOT = _bootstrap.REPO_ROOT
CORPUS = REPO_ROOT / "evals" / "corpus" / "notes.jsonl"
QUESTIONS = REPO_ROOT / "evals" / "questions.jsonl"

WIDTH = min(shutil.get_terminal_size((100, 24)).columns, 100)


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def save(path: Path, rows: list[dict]) -> None:
    """Write atomically: a crash mid-write must not destroy the label set."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    tmp.replace(path)


def rule(char: str = "-") -> str:
    return char * WIDTH


def show_note(note: dict, marker: str = "  ") -> None:
    body = note["content"]
    if len(body) > 300:
        body = body[:300].rsplit(" ", 1)[0] + " ..."
    print(f"{marker}[{note['id']}] {note['title']}")
    for line in _wrap(body, WIDTH - 6):
        print(f"      {line}")


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def parse_ids(raw: str, notes: dict) -> list[int] | None:
    """Parse a comma/space separated id list, rejecting unknown ids."""
    try:
        ids = [int(x) for x in raw.replace(",", " ").split()]
    except ValueError:
        print("  ! ids must be integers")
        return None
    unknown = [i for i in ids if i not in notes]
    if unknown:
        print(f"  ! no such note: {unknown}")
        return None
    if not ids:
        print("  ! need at least one id")
        return None
    return ids


def retrieved_for(question: str, k: int = 5) -> list[tuple[int, str, float]]:
    from rag.embeddings import get_embedder
    from rag.retrieval import retrieve_notes

    hits = retrieve_notes(question, k=k, embedder=get_embedder())
    return [(h.note_id, h.title, h.score) for h in hits]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="re-review already-reviewed ones")
    ap.add_argument(
        "--show-retrieved",
        action="store_true",
        help="also show what search actually returns (needs DATABASE_URL)",
    )
    args = ap.parse_args()

    notes = {n["id"]: n for n in load(CORPUS)}
    questions = load(QUESTIONS)
    todo = [q for q in questions if args.all or not q.get("reviewed")]

    if not todo:
        print("All labels already reviewed. Use --all to go through them again.")
        return 0

    print(rule("="))
    print(f"Reviewing {len(todo)} of {len(questions)} questions.")
    print("For each: does the labelled note actually answer the question?")
    print(rule("="))

    changed = 0
    for n, q in enumerate(todo, 1):
        print(f"\n{rule()}\n[{n}/{len(todo)}]  {q['id']}")
        print(f"\n  Q: {q['question']}\n")
        print("  Currently labelled as answering it:")
        for nid in q["relevant_note_ids"]:
            show_note(notes[nid], "  -> ")
        if q.get("note"):
            print(f"\n  (label note: {q['note']})")

        if args.show_retrieved:
            try:
                print("\n  What search returns today:")
                for rank, (nid, title, score) in enumerate(retrieved_for(q["question"]), 1):
                    hit = "*" if nid in q["relevant_note_ids"] else " "
                    print(f"    {hit}{rank}. [{nid}] {title}  ({score:.3f})")
            except Exception as exc:
                print(f"    (unavailable: {exc})")

        while True:
            choice = input(
                "\n  [a]ccept  [r]elabel  [w]ord (reword question)  [s]kip  [q]uit+save > "
            ).strip().lower()

            if choice in ("a", ""):
                q["reviewed"] = True
                changed += 1
                break
            if choice == "r":
                ids = parse_ids(input("  correct note id(s), space separated: "), notes)
                if ids is None:
                    continue
                print("  now labelled:")
                for i in ids:
                    show_note(notes[i], "  -> ")
                q["relevant_note_ids"] = ids
                q["reviewed"] = True
                changed += 1
                break
            if choice == "w":
                new = input("  reworded question: ").strip()
                if new:
                    q["question"] = new
                    q["reviewed"] = True
                    changed += 1
                    break
                print("  ! empty, ignored")
                continue
            if choice == "s":
                break
            if choice == "q":
                save(QUESTIONS, questions)
                print(f"\nSaved. {changed} updated. Re-run to continue.")
                return 0
            print("  ! pick a, r, w, s or q")

        # Save after every question: an interrupted session keeps its progress.
        save(QUESTIONS, questions)

    remaining = sum(1 for q in questions if not q.get("reviewed"))
    print(f"\n{rule('=')}")
    print(f"Done. {changed} updated, {remaining} still unreviewed.")
    if remaining == 0:
        print("\nThe harness will stop warning about unreviewed labels.")
        print("Re-run it — corrected labels change the numbers, and those are")
        print("the ones worth committing:")
        print("  python evals/harness.py --strategies baseline --save baseline_reviewed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted. Progress up to the last answered question was saved.")
        sys.exit(1)
