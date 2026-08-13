"""Integrity checks on the eval corpus and labelled question set.

These exist because of a real failure: the corpus and the question set were
rewritten together, but only the corpus reached a commit. The repo then held a
120-note personal corpus alongside 30 questions written against a completely
different corpus, so every label pointed at a note id that meant something
else. "why was the app answering me twice?" resolved to a standup note.

Nothing caught it. The harness ran happily, the metrics computed, and the
numbers were meaningless. A retrieval eval fails silently by construction —
it cannot tell a wrong label from a bad retriever — so the data it rests on
needs checking directly.

Everything here is cheap and needs no database or model.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "evals" / "corpus" / "notes.jsonl"
QUESTIONS = REPO_ROOT / "evals" / "questions.jsonl"


def _load(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text().splitlines() if line.strip()
    ]


@pytest.fixture(scope="module")
def notes() -> dict[int, dict]:
    return {n["id"]: n for n in _load(CORPUS)}


@pytest.fixture(scope="module")
def questions() -> list[dict]:
    return _load(QUESTIONS)


# ---------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------


def test_corpus_is_valid_jsonl():
    rows = _load(CORPUS)
    assert rows, "corpus is empty"
    for row in rows:
        assert set(row) >= {"id", "title", "content"}, f"missing fields: {row}"


def test_note_ids_are_unique_integers():
    """Duplicate or non-integer ids silently break label resolution."""
    rows = _load(CORPUS)
    ids = [r["id"] for r in rows]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate note ids: {sorted(duplicates)}"
    non_int = [i for i in ids if not isinstance(i, int) or isinstance(i, bool)]
    assert not non_int, f"non-integer note ids: {non_int}"


def test_notes_have_content():
    for row in _load(CORPUS):
        assert row["title"].strip(), f"note {row['id']} has an empty title"
        assert len(row["content"].split()) >= 10, (
            f"note {row['id']} is too short to be a meaningful retrieval target"
        )


# ---------------------------------------------------------------------------
# Questions and labels
# ---------------------------------------------------------------------------


def test_questions_are_valid_jsonl():
    rows = _load(QUESTIONS)
    assert rows, "question set is empty"
    for row in rows:
        assert set(row) >= {"id", "question", "relevant_note_ids"}, (
            f"missing fields: {row}"
        )


def test_question_ids_are_unique():
    ids = [q["id"] for q in _load(QUESTIONS)]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"duplicate question ids: {sorted(duplicates)}"


def test_every_label_resolves_to_a_real_note(notes, questions):
    """The check that would have caught the corpus/questions mismatch.

    A label pointing at a missing id is obvious. The dangerous case is a label
    pointing at an id that exists but belongs to a different corpus — that is
    invisible here, which is why test_labels_share_vocabulary_with_notes also
    exists.
    """
    broken = [
        (q["id"], note_id)
        for q in questions
        for note_id in q["relevant_note_ids"]
        if note_id not in notes
    ]
    assert not broken, f"labels pointing at non-existent notes: {broken}"


def test_every_question_has_at_least_one_label(questions):
    unlabelled = [q["id"] for q in questions if not q["relevant_note_ids"]]
    assert not unlabelled, f"questions with no relevant notes: {unlabelled}"


def test_labels_have_no_duplicates_within_a_question(questions):
    for q in questions:
        ids = q["relevant_note_ids"]
        assert len(ids) == len(set(ids)), (
            f"{q['id']} lists the same note twice: {ids}"
        )


#: Fraction of questions allowed to share no content word with their labelled
#: notes. Some zero-overlap questions are *desirable* — they are pure semantic
#: matches, the case that justifies vector search over keyword search. On the
#: current set exactly one question qualifies ("when does the patent clock run
#: out?" against a note that never says "patent"). A wholesale corpus swap
#: pushes this far higher, which is what the threshold detects.
MAX_ZERO_OVERLAP_FRACTION = 0.30

_STOPWORDS = set(
    """a an and are as at be by can did do does for from had has have how i
    if in is it its me my of on or should that the their to was we were what
    when where which who why will with you your do not don't""".split()
)


def _content_words(text: str) -> set[str]:
    return {w.strip(".,:;?!()[]'\"").lower() for w in text.split()} - _STOPWORDS - {""}


def _zero_overlap_questions(notes: dict, questions: list[dict]) -> list[tuple]:
    out = []
    for q in questions:
        q_words = _content_words(q["question"])
        labelled: set[str] = set()
        for note_id in q["relevant_note_ids"]:
            note = notes[note_id]
            labelled |= _content_words(note["title"]) | _content_words(note["content"])
        if not (q_words & labelled):
            out.append((q["id"], q["question"]))
    return out


def test_labels_mostly_share_vocabulary_with_notes(notes, questions):
    """Catch labels that resolve but belong to a different corpus.

    A wholesale corpus swap leaves every label resolving to *some* note while
    meaning nothing — the exact failure this file exists for. Lexical overlap
    between a question and its labelled notes is a weak proxy for "these were
    written against each other".

    Checked in aggregate rather than per question, because individual
    zero-overlap questions are a sign of a *good* eval set, not a broken one.
    Only human review can confirm any single label is correct.
    """
    suspicious = _zero_overlap_questions(notes, questions)
    fraction = len(suspicious) / len(questions)

    assert fraction <= MAX_ZERO_OVERLAP_FRACTION, (
        f"{len(suspicious)}/{len(questions)} questions ({fraction:.0%}) share no "
        f"content word with any labelled note, above the {MAX_ZERO_OVERLAP_FRACTION:.0%} "
        f"threshold. This usually means the corpus and the question set were "
        f"written against different data. Examples: {suspicious[:5]}"
    )


def test_zero_overlap_detector_fires_on_a_corpus_swap(notes, questions):
    """The detector above must actually detect the thing it is for.

    Shifting every label by a fixed offset simulates a corpus swap: every id
    still resolves, but to the wrong note. If this does not trip the
    threshold, the check above is decoration.
    """
    ids = sorted(notes)
    shifted = [
        {
            **q,
            "relevant_note_ids": [
                ids[(ids.index(n) + len(ids) // 2) % len(ids)]
                for n in q["relevant_note_ids"]
            ],
        }
        for q in questions
    ]
    fraction = len(_zero_overlap_questions(notes, shifted)) / len(shifted)
    assert fraction > MAX_ZERO_OVERLAP_FRACTION, (
        f"a fully mislabelled set only reached {fraction:.0%} zero-overlap, "
        "so the threshold would not catch a corpus swap"
    )


def test_review_flag_is_present_and_boolean(questions):
    """The harness warns on unreviewed labels, so the flag must be readable."""
    for q in questions:
        assert "reviewed" in q, f"{q['id']} has no 'reviewed' flag"
        assert isinstance(q["reviewed"], bool), (
            f"{q['id']} has a non-boolean 'reviewed': {q['reviewed']!r}"
        )


def test_corpus_and_questions_are_large_enough_to_measure(notes, questions):
    """Guard the degenerate case that started this work.

    The original corpus had 5 notes, which makes recall@5 100% by construction
    and every metric meaningless. Retrieval over a corpus smaller than the
    deepest cutoff cannot be evaluated at all.
    """
    assert len(notes) > 10, (
        f"corpus of {len(notes)} notes is too small: recall@10 is degenerate "
        "when the corpus is no larger than the cutoff"
    )
    assert len(questions) >= 20, (
        f"{len(questions)} questions cannot resolve differences between "
        "retrieval strategies"
    )
