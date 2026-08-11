# Retrieval evaluation results

Measurements for SmartDesk's notes retrieval, run in the order the work was
done: harness first, then chunking, then reranking. Every number below is
reproducible with the commands in [README](../README.md#evaluating-retrieval).

**Headline: the baseline is already strong, and nothing tested beat it by a
statistically significant margin. `search_notes` therefore still defaults to
the original behaviour.** The alternatives are implemented and switchable, but
promoting one to default is not justified by this evidence.

---

## 1. What was measured

| | |
|---|---|
| Corpus | 120 notes, 8,899 words (synthetic — see caveats) |
| Questions | 30, each labelled with the note id(s) that answer it |
| Metrics | recall@k and MRR@k at k = 1, 3, 5, 10 |
| Embedder | all-MiniLM-L6-v2, 384d (local dev — **not** text-embedding-005) |
| Database | Postgres 16 + pgvector 0.6.0 |
| Significance | Paired bootstrap, 10,000 resamples, 95% CI |

`search_notes` returns 5 results, so **R@5 is the column that reflects
production behaviour**. The harness retrieves 10 so recall@10 is measurable.

### Why the significance testing matters

With 30 questions, one question is worth 0.033 of recall@1. Most differences
below are 1–2 questions. Without a confidence interval these read as
improvements; with one, they read as noise. Every comparison in this document
that lacks a `*` has a 95% CI spanning zero.

---

## 2. Baseline

The original implementation: one embedding per whole note, cosine distance,
`LIMIT 5`, no chunking, no reranking.

```
R@1 0.617   R@3 0.883   R@5 0.950   R@10 0.967
MRR@1 0.733 MRR@3 0.822 MRR@5 0.831 MRR@10 0.831
```

Committed at `evals/results/baseline.json`.

**The baseline is good.** R@5 = 0.950 means the correct note is in the returned
five for 95% of questions, leaving 0.05 of headroom. This is the single most
important fact in this document: it caps how much any later change can
possibly win, and it is why the deltas below are small.

MRR@1 (0.733) exceeds R@1 (0.617) because six questions have two relevant
notes, and recall@1 can be at most 0.5 for those.

---

## 3. Chunking — did not help

Token-based, sentence-aligned, chunk size 180, overlap 40, chunks linked to
parent notes by foreign key.

| strategy | R@1 | R@5 | MRR@10 |
|---|---|---|---|
| baseline | **0.617** | **0.950** | **0.831** |
| chunked, naive | 0.583 | 0.933 | 0.797 |
| chunked, title repeated on later chunks | 0.617 | 0.933 | 0.817 |

**Chunking did not improve retrieval on this corpus, and naive chunking made
it worse.**

The reason is corpus shape: **only 9 of 120 notes split into more than one
chunk.** 105 notes are under 100 words. For those, chunking is a no-op by
construction — the note becomes exactly one chunk.

Per-question, chunking changed 6 of 30 questions:

- **1 improved**: q19 ("what went wrong on launch day?"), whose answer is a
  336-word note. Chunking helped exactly where the theory says it should.
- **5 regressed**, four of them targeting notes of 57–62 words.

The regression mechanism is worth stating because it is not obvious: chunking
short notes changes nothing about *those* notes, but splitting the long notes
produces sharper, more topically focused chunks that then outrank the correct
short note. Chunking a corpus makes its long documents more competitive
everywhere, not just on questions about them.

### One real bug found

Only the first chunk of a note naturally contains the note title; later chunks
lost it entirely. Repeating the title on subsequent chunks recovered most of
the regression (MRR@10 0.797 → 0.817) but still did not reach the baseline's
0.831. This is `--title-prefix` in `evals/ingest.py`.

### Verdict

Chunking is kept in the codebase, off by default. It is the right mechanism for
a corpus of long documents and this corpus is not one. If the real note corpus
skews longer than this synthetic one, re-run before concluding anything — the
result is a property of the corpus, not of the technique.

---

## 4. Reranking

Candidate set of 25, reranked down to the reported cutoffs.

| strategy | R@1 | R@5 | MRR@10 | latency (mean) | cost / 1k queries |
|---|---|---|---|---|---|
| baseline | 0.617 | **0.950** | 0.831 | 16 ms | $0 |
| hybrid-rrf | **0.667** | 0.883 | **0.834** | 45 ms | $0 |
| chunked+rrf | 0.633 | 0.883 | 0.818 | 13 ms | $0 |
| chunked+cross-encoder | 0.633 | 0.917 | 0.820 | 490 ms | $0 (local CPU) |
| baseline+rrf | 0.583 | 0.867 | 0.786 | 6 ms | $0 |
| baseline+cross-encoder | 0.533 | 0.900 | 0.758 | 1,767 ms | $0 (local CPU) |
| **gemini** | *unmeasured* | | | ~1 network RTT | **~$1.18** |

### Paired bootstrap vs baseline

```
recall@5                delta     95% CI              p      better/worse
  hybrid-rrf            -0.067   [-0.150, +0.000]   0.12   0/3
  chunked+rrf           -0.067   [-0.150, +0.000]   0.12   0/3
  baseline+rrf          -0.083   [-0.167, -0.017]   0.06   0/4
  chunked+cross-enc     -0.033   [-0.083, +0.000]   0.27   0/2

rr@10                   delta     95% CI              p      better/worse
  hybrid-rrf            +0.004   [-0.109, +0.106]   0.95   5/2
  chunked+rrf           -0.013   [-0.143, +0.109]   0.85   5/4
  baseline+cross-enc    -0.072   [-0.202, +0.051]   0.26   5/7
```

**No strategy is significantly better than baseline on any metric.** The
closest thing to a signal is that `hybrid-rrf` improves 5 questions and
regresses 2 on MRR@10 — a favourable ratio, but a delta of +0.004 with a CI
almost 30x wider than the effect.

Every reranker *lowers* R@5. Reranking reorders 25 candidates and returns the
top few; a relevant note that dense retrieval had at rank 4 can be pushed past
the cutoff. When the baseline ordering is already 95% correct at k=5, a
reranker has far more to lose than to gain.

### Recommendation: `hybrid-rrf`, if any

Fuses three rankings — whole-note dense, chunk dense, and BM25 — with
reciprocal rank fusion. Chosen over the alternatives because:

- It is the only strategy that improves the top of the ranking (R@1 +0.050,
  MRR@1 +0.033), which is what an LLM reads most heavily.
- It is free and adds ~29 ms, versus 490–1,767 ms for the cross-encoder.
- Its three signals fail differently: embeddings handle paraphrase, BM25
  handles rare exact terms (names, error strings), chunks handle long notes.

**But it is shipped off by default** (`SMARTDESK_RETRIEVAL=hybrid` to enable),
because "best of several statistically indistinguishable options" is not
grounds for changing production behaviour.

### The cross-encoder was the worst option

`ms-marco-MiniLM-L-6-v2` was worse than baseline on every metric *and* 30–110x
slower. It is trained on MS MARCO web-search passages; meeting notes are a
different domain, and a 6-layer model has little capacity to bridge that.

**This does not predict how Gemini would do.** A domain-mismatched 22M-parameter
cross-encoder failing says nothing about a frontier model. Do not read the
cross-encoder row as evidence against LLM reranking.

---

## 5. Gemini reranking — implemented, not measured

`GeminiReranker` is complete and registers itself when `GOOGLE_CLOUD_PROJECT`
is set. It was **not run**, because this environment has no GCP credentials and
running it would have incurred cost without approval.

Measured prompt size over the 30 eval questions at 25 candidates:

| | |
|---|---|
| Input | ~2,674 tokens mean, 3,179 max |
| Output | ~150 tokens (25 lines of `index:score`) |
| Cost per 1,000 queries | **~$1.18** ($0.80 input + $0.38 output) |
| Cost for one full eval run | ~$0.04 |

At Gemini 2.5 Flash pricing of $0.30/M input and $2.50/M output. Token counts
use the MiniLM tokenizer as a proxy, so treat them as within ~20%.

To measure it:

```bash
export GOOGLE_CLOUD_PROJECT=<project> SMARTDESK_EMBEDDER=vertex
python evals/harness.py --strategies baseline chunked+gemini --save gemini
```

---

## 6. What did not help

Collected explicitly, because the null results are the useful part:

1. **Chunking**, on this corpus. Helped 1 question, hurt 5. Only 9 of 120 notes
   were long enough to split at all.
2. **Every reranker, on recall@5.** All lowered it. Reranking has more to lose
   than gain against an already-strong ordering.
3. **The local cross-encoder**, on everything. Worse accuracy and 30–110x the
   latency.
4. **Excluding zero-BM25 documents from the lexical ranking.** This started as
   a genuine bug fix — documents sharing no query term were being handed
   lexical ranks by sort order alone, letting a note with no match outscore a
   real one. Fixing it *lowered* `hybrid-rrf` from MRR@10 0.872 to 0.834. The
   fix is principled and was kept; the pre-fix numbers are preserved in
   `results/all_strategies.json` against post-fix `results/final.json`. Both
   deltas are inside the noise band, so neither version is demonstrably better
   — which is itself the point. A 30-question eval cannot adjudicate this.
5. **Retrieving a wider candidate set** (25 vs 10) did not help on its own; it
   only matters in combination with a reranker good enough to exploit it.

---

## 7. Caveats — read before trusting any number above

1. **Wrong embedder.** Everything is measured with all-MiniLM-L6-v2 (384d), not
   text-embedding-005 (768d), because this environment has no Vertex
   credentials. Relative orderings may not transfer. Re-run with
   `SMARTDESK_EMBEDDER=vertex` before making decisions.
2. **Synthetic corpus.** The 120 notes were generated, not real. The original
   corpus had 5 notes, which makes recall@5 100% by construction and every
   metric here degenerate — hence the synthetic set.
3. **Unreviewed labels.** All 30 questions are flagged `reviewed: false`. They
   were written against the notes and are believed correct, but they have not
   been human-verified. The harness prints a warning until they are. Wrong
   labels corrupt every number silently.
4. **n = 30.** One question is worth 0.033 of recall@1. This eval can detect
   large effects and nothing else. Detecting a 2-point improvement reliably
   needs roughly 300 questions.
5. **Do not tune on this set.** Any parameter chosen by maximising these 30
   questions is overfitting. A held-out set is needed before tuning RRF
   weights, chunk sizes, or candidate depth.

---

## 8. What would actually move the numbers

In order of expected value:

1. **Real notes and reviewed labels.** Every conclusion here is provisional
   until the corpus is real. This is the whole ballgame.
2. **More questions.** 30 cannot resolve the effects being chased. 200–300
   would.
3. **Re-run on text-embedding-005.** One command; changes which conclusions
   hold.
4. **Then, and only then**, tune. Chunk size, overlap, RRF weights and
   candidate depth are all unexplored, and exploring them now would just fit
   noise.
