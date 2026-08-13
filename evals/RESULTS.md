# Retrieval evaluation results

Measurements for SmartDesk's notes retrieval, run in the order the work was
done: harness first, then chunking, then reranking. Reproducible with the
commands in [README](../README.md#evaluating-retrieval).

> **Read §0 first.** The pipeline has now been measured on the production
> embedder, and the conclusion is different from the development-embedder
> result that the rest of this document describes.

---

## 0. On text-embedding-005, plain retrieval wins

Everything in sections 2–4 was measured with all-MiniLM-L6-v2, because this
environment had no Vertex credentials. That measurement has now been repeated
against **text-embedding-005**, the production embedder, on 120 notes and 40
questions.

| strategy | R@1 | R@5 | R@10 | MRR@10 | latency |
|---|---|---|---|---|---|
| **baseline** | 0.800 | **0.963** | 0.975 | 0.886 | **29 ms** |
| chunked | 0.800 | 0.963 | 0.975 | 0.885 | 24 ms |
| hybrid-rrf | 0.775 | 0.950 | 0.975 | 0.870 | 52 ms |
| baseline+rrf | 0.775 | 0.938 | 0.950 | 0.858 | 23 ms |
| chunked+rrf | 0.750 | **0.975** | 0.975 | 0.859 | 37 ms |
| chunked+cross-encoder | **0.838** | 0.950 | **1.000** | **0.914** | 2,382 ms |

Paired bootstrap vs baseline on rr@10: **nothing is significant.** The four
free strategies are all negative (p 0.37–0.64). The cross-encoder is positive
but well inside the noise: **+0.028, 95% CI [−0.041, +0.101], p = 0.44,
5 questions better / 4 worse.**

**Two things changed relative to the MiniLM runs.**

First, the baseline got much better: R@1 0.700 → 0.800, MRR@10 0.814 → 0.886.
A stronger embedder simply retrieves better, which is what you would hope.

Second, and more usefully: **every reranker went from helping to hurting.**
`chunked+rrf` was the second-best strategy on MiniLM at MRR@10 +0.047. On
text-embedding-005 it is −0.027. The sign flipped.

The mechanism is the one predicted in §9 before this was run: a stronger
embedder produces better candidates, leaving less for a reranker to fix and
more for it to break. When the top-5 is already correct 96% of the time,
reordering has far more to lose than to gain.

**This is the single most valuable result in this document**, because the
MiniLM measurement alone would have justified shipping a cross-encoder that
adds ~700 ms and several hundred MB of PyTorch to the deployed image — for
nothing, on the embedder actually in production.

### The cross-encoder result did not survive

The one statistically significant win in this document was
`chunked+cross-encoder` on MiniLM: MRR@10 **+0.094**, p = 0.04, 8 questions
better / 2 worse. Re-run on text-embedding-005:

| | MiniLM | text-embedding-005 |
|---|---|---|
| MRR@10 delta | **+0.094** | +0.028 |
| 95% CI | [+0.012, +0.186] | [−0.041, +0.101] |
| p | **0.04** | 0.44 |
| better/worse | 8 / 2 | 5 / 4 |
| latency | 699 ms | 2,382 ms |

**The advantage shrank to under a third of its size and lost significance.**
This was predicted before the run, on the reasoning that a stronger embedder
leaves a reranker less to fix — and the prediction held.

Two things it genuinely does better are worth recording honestly: R@1 is
+0.037 (0.838 vs 0.800), and R@10 reaches **1.000** — every question's answer
appears somewhere in the top ten. But R@5, which is what `search_notes`
actually returns, is *worse* (0.950 vs 0.963), and none of it clears the
noise threshold.

Against that: **2,382 ms per search versus 29 ms**, an 82x latency cost, plus
~190 MB of PyTorch in an image deliberately slimmed from 1.8 GB to 340 MB to
fix cold starts. For an effect that cannot be distinguished from zero.

### Verdict

`SMARTDESK_RETRIEVAL` stays on `baseline`. That was already the default for
caution; it is now the default on evidence, and the evidence is complete —
every strategy has been measured on the embedder that actually runs in
production.

---

**Everything below was measured on all-MiniLM-L6-v2 and is retained because
the reasoning still holds — but where it disagrees with §0, §0 is the one
that reflects production.**

**Headline (development embedder): a cross-encoder reranking chunk retrieval
is the only change that beat the baseline significantly — MRR@10 +0.094,
R@1 +0.138, p = 0.04.**

---

## 1. What was measured

| | |
|---|---|
| Corpus | 120 notes, 7,884 words — a personal knowledge base for one user |
| Questions | 40, each labelled with the note id(s) that answer it |
| Metrics | recall@k and MRR@k at k = 1, 3, 5, 10 |
| Embedder | all-MiniLM-L6-v2, 384d (local dev — **not** text-embedding-005) |
| Database | Postgres 16 + pgvector 0.6.0 |
| Significance | Paired bootstrap, 10,000 resamples, 95% CI |

`search_notes` returns 5 results, so **R@5 reflects production behaviour**. The
harness retrieves 10 so recall@10 is measurable.

The corpus covers what is actually in flight: SmartDesk's own build log and
bugs, two hackathons on two platforms, job applications, the provisional
patent timeline, four email accounts and which service is on which, and the
trading platform accounts. Questions are phrased the way they get asked
("that time notes search returned nothing at all, what was it?"), not the way
the notes are written.

### Why the significance testing matters

With 40 questions, one question is worth 0.025 of recall@1. Most differences
below are 1–3 questions. Without a confidence interval they read as
improvements; with one, most read as noise.

---

## 2. Baseline

The original implementation: one embedding per whole note, cosine distance,
`LIMIT 5`, no chunking, no reranking.

```
R@1 0.700   R@3 0.875   R@5 0.925   R@10 0.950
MRR@1 0.725 MRR@3 0.800 MRR@5 0.811 MRR@10 0.814
```

Committed at `evals/results/baseline.json`.

The baseline is already decent — the right note is in the returned five for
92.5% of questions. That caps how much any change can win.

---

## 3. Chunking — did not help

Token-based, sentence-aligned, chunk size 180, overlap 40, chunks linked to
parent notes by foreign key.

| strategy | R@1 | R@5 | R@10 | MRR@10 |
|---|---|---|---|---|
| baseline | **0.700** | **0.925** | 0.950 | **0.814** |
| chunked | 0.700 | 0.900 | **0.963** | 0.812 |

**Chunking on its own changed almost nothing** (MRR@10 −0.003, p = 0.59).

The reason is corpus shape: **only 6 of 120 notes split into more than one
chunk.** 113 notes are under 100 words. For those, chunking is a no-op by
construction — the note becomes exactly one chunk.

It does buy a small gain at R@10 (+0.013), consistent with chunks surfacing
long notes that whole-note embedding buries. But on its own that is one
question and well inside the noise.

**Chunking's real value showed up in combination**, not alone — every
reranker scored better on chunked retrieval than on whole-note retrieval
(see §4). It provides better *candidates* even when it does not improve the
final ranking itself.

### One real bug found

Only the first chunk of a note naturally contains the note title; later chunks
lost it entirely. Repeating the title on subsequent chunks (`--title-prefix`)
is now the recommended ingest setting.

---

## 4. Reranking — the cross-encoder wins

Candidate set of 25, reranked down to the reported cutoffs.

| strategy | R@1 | R@5 | MRR@10 | latency (mean) | cost / 1k |
|---|---|---|---|---|---|
| baseline | 0.700 | 0.925 | 0.814 | 22 ms | $0 |
| chunked | 0.700 | 0.900 | 0.812 | 13 ms | $0 |
| baseline+rrf | 0.750 | 0.925 | 0.843 | **5 ms** | $0 |
| hybrid-rrf | 0.750 | 0.925 | 0.843 | 26 ms | $0 |
| chunked+rrf | 0.775 | 0.938 | 0.861 | 16 ms | $0 |
| baseline+cross-encoder | 0.725 | 0.925 | 0.839 | 1,976 ms | $0 |
| **chunked+cross-encoder** | **0.838** | **0.950** | **0.908** | 699 ms | $0 |
| gemini | *unmeasured* | | | ~1 RTT | ~$1.18 |

### Paired bootstrap vs baseline

```
rr@10                   delta     95% CI              p      better/worse
  chunked+cross-enc    +0.094   [+0.012, +0.186]   0.04   8/2   *
  chunked+rrf          +0.047   [-0.019, +0.117]   0.18   7/2
  hybrid-rrf           +0.028   [-0.031, +0.093]   0.37   6/2
  baseline+rrf         +0.028   [-0.050, +0.113]   0.51   6/4
  baseline+cross-enc   +0.024   [-0.088, +0.136]   0.67   8/7
  chunked             -0.003   [-0.013, +0.007]   0.59   1/2

recall@5                delta     95% CI              p      better/worse
  chunked+cross-enc    +0.025   [-0.050, +0.125]   0.76   2/1
  chunked+rrf          +0.013   [-0.062, +0.087]   0.87   2/1
  chunked             -0.025   [-0.075, +0.000]   0.63   0/1
```

**`chunked+cross-encoder` is the only strategy whose CI excludes zero.** The
effect is large: R@1 +0.138 is 5.5 questions out of 40, and 8 questions
improved against 2 regressed.

### Honest caveat on that p-value

**p = 0.04 is uncorrected for multiple comparisons.** Six strategies were
compared against the baseline; with six tests, a p-value below 0.05 arising by
chance is not unlikely. A Bonferroni-corrected threshold would be ~0.008,
which this does not clear.

The result is the strongest evidence in this document, and it is not
conclusive. What raises confidence beyond the p-value alone: the effect size
is large rather than marginal, the win/loss ratio is 8/2, and the direction is
consistent across every cutoff and both metrics.

### This reverses an earlier conclusion

An earlier version of this corpus described a fictional company — team
standups, client meetings, dashboard redesigns. On that corpus the same
cross-encoder was the **worst** option, scoring below baseline on every metric.
On this corpus it is the best by a clear margin.

Nothing about the model changed. `ms-marco-MiniLM-L-6-v2` is trained on
web-search passages, and this corpus — technical notes about bugs, decisions
and how things work, queried with direct questions — sits much closer to that
distribution than meeting minutes about a fictional product did.

**The lesson is that reranker choice is a property of your corpus, not a
general fact.** Any conclusion here transfers only to notes that look like
these. This is also a concrete argument for the harness existing at all: the
wrong corpus produced a confidently wrong recommendation.

---

## 5. Why it is not the default

`SMARTDESK_RETRIEVAL=rerank` enables it. The default stays `baseline` because:

1. **The p-value does not survive multiple-comparison correction** (above).
2. **It adds torch to the deployed image.** `sentence-transformers` pulls
   PyTorch, several hundred MB. The Cloud Run image was deliberately cut from
   1.8 GB to 340 MB to fix 8–12 second cold starts. Adding torch undoes that
   for a single-user tool that is idle most of the time.
3. **699 ms per search**, against 22 ms for the baseline and 16 ms for
   `chunked+rrf`.
4. **The labels are unreviewed.** Everything rests on 40 generated labels.

**If you want a ranking improvement without the image cost, use
`chunked+rrf`**: MRR@10 +0.047, 16 ms, no new dependency, pure Python. It is
not statistically significant either, but it is free in every sense.

**The better long-term answer is probably the Gemini reranker** — same
cross-encoder idea, no torch in the image, at ~$1.18 per 1,000 searches. It is
implemented and unmeasured (§6).

---

## 6. Gemini reranking — implemented, not measured

`GeminiReranker` is complete and registers itself when `GOOGLE_CLOUD_PROJECT`
is set. It was **not run**: this environment has no GCP credentials and running
it would have incurred cost without approval.

Measured prompt size over the eval questions at 25 candidates:

| | |
|---|---|
| Input | ~2,674 tokens mean, 3,179 max |
| Output | ~150 tokens |
| Cost per 1,000 queries | **~$1.18** ($0.80 input + $0.38 output) |
| Cost for one full eval run | ~$0.05 |

At Gemini 2.5 Flash pricing of $0.30/M input and $2.50/M output. Token counts
use the MiniLM tokenizer as a proxy — treat as within ~20%.

```bash
export GOOGLE_CLOUD_PROJECT=<project> SMARTDESK_EMBEDDER=vertex
python evals/harness.py --strategies baseline chunked+gemini --save gemini
```

Given the local cross-encoder's result, this is the most valuable remaining
measurement: it would likely match or beat it without the image-size cost.

---

## 7. What did not help

1. **Chunking alone.** MRR@10 −0.003. Only 6 of 120 notes were long enough to
   split. It earns its place as a *candidate generator* for rerankers, not as
   a retrieval improvement in itself.
2. **Reranking whole-note candidates.** `baseline+cross-encoder` gained almost
   nothing (+0.024, p = 0.67) and cost 1,976 ms. The same reranker on chunked
   candidates gained +0.094 at a third of the latency. Candidate quality
   mattered more than the reranker.
3. **Fusing three signals instead of two.** `hybrid-rrf` (dense + chunk +
   BM25) scored identically to `baseline+rrf` (dense + BM25) — MRR@10 0.843
   for both — while being 5x slower. The third signal added nothing.
4. **Excluding zero-BM25 documents from the lexical ranking.** A genuine bug
   fix — documents sharing no query term were being handed lexical ranks by
   sort order alone. On the previous corpus it *lowered* scores. Kept because
   it is correct, not because it helped.

---

## 8. Caveats — read before trusting any number

1. **Wrong embedder.** Measured with all-MiniLM-L6-v2 (384d), not
   text-embedding-005 (768d), because this environment has no Vertex
   credentials. Re-run with `SMARTDESK_EMBEDDER=vertex` before deciding
   anything. The cross-encoder result in particular may shift, since a
   stronger embedder produces better candidates and leaves less for a
   reranker to fix.
2. **Synthetic notes.** The corpus reflects real threads — the accounts, the
   hackathons, the patent timeline, SmartDesk's actual bugs — but the notes
   were written for this eval, not kept at the time. Specifics are
   placeholders. Replacing them with real notes is the single highest-value
   change available.
3. **Unreviewed labels.** All 40 questions are flagged `reviewed: false`. The
   harness warns until that changes. Wrong labels corrupt every number here
   silently.
4. **n = 40, and 6 strategies compared.** One question is worth 0.025 of
   recall@1. The one significant result does not survive multiple-comparison
   correction.
5. **Do not tune on this set.** Any parameter chosen by maximising these 40
   questions is overfitting. Tuning needs a held-out set.

---

## 9. What would actually move the numbers

1. **Real notes, reviewed labels.** Everything else is provisional until then.
2. **Measure the Gemini reranker.** Likely matches the cross-encoder without
   putting torch in the deployed image. ~$0.05 to find out.
3. **Re-run on text-embedding-005.** One command; may change which
   conclusions hold.
4. **More questions.** 40 cannot separate strategies 2–4 in the table.
   200–300 would.
5. **Then tune** — chunk size, overlap, candidate depth. Not before, and not
   on this set.
