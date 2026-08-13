# Roadmap

Open work on SmartDesk, ordered by what blocks what. Written at the point the
RAG pipeline was finished and measured end to end.

**Status: the RAG pipeline is done.** Corpus, labelled set, metrics, chunking,
four rerankers, significance testing, and committed numbers on the production
embedder — see [`evals/RESULTS.md`](evals/RESULTS.md). Everything below is
deployment plumbing and content accuracy, not retrieval work.

---

## 1. Redeploy so the live service actually runs — **blocker**

The deployed revision fails at import:

```
Fail to load 'smartdesk_app' module. No module named 'google_auth_oauthlib'
```

`adk deploy cloud_run ./smartdesk_app` copies only the agent directory and
generates its own Dockerfile, so the repository-root `requirements.txt` was
never in the image. `smartdesk_app/requirements.txt` now exists to fix that,
but the fix has not been deployed.

```bash
cd smartdesk_agent
adk deploy cloud_run --project=smartdesk-505315 --region=us-central1 \
  --service_name=smartdesk --with_ui ./smartdesk_app
```

Then push the environment, which `adk deploy` does not carry over. The `^|^`
delimiter is required — the Neon URL contains `@` and `:` which break the
default parsing:

```bash
gcloud run services update smartdesk --region us-central1 \
  --update-env-vars "^|^DATABASE_URL=$DATABASE_URL|SMARTDESK_EMBEDDER=vertex|GOOGLE_GENAI_USE_VERTEXAI=TRUE|GOOGLE_CLOUD_PROJECT=smartdesk-505315|GOOGLE_CLOUD_LOCATION=us-central1|MODEL=gemini-2.5-flash"
```

Verify by opening `/dev-ui` and asking a notes question, not just by checking
the service responds.

## 2. Rotate the exposed credentials — **do this regardless**

Both were pasted into a chat transcript during setup:

- **OAuth client secret** (`GOCSPX-…Ls9c`) — Credentials → the client →
  *Add secret*, redeploy with the new `client_secret.json`, then delete the old
  secret. Google supports two live secrets so this is zero-downtime.
- **Neon database password** — Neon console → Roles → reset. Update
  `DATABASE_URL` in `.env` and in the Cloud Run env.

Neither is in git (`.gitignore` covers `*.json` and `.env`), so this is about
the transcript, not the repository.

## 3. Correct the invented note content

The corpus reflects real *threads* but some specifics were written as
placeholders and are factually wrong:

| Topic | Note IDs | What is invented |
|---|---|---|
| SMT | 39, 79, 113 | What SMT actually is — never stated |
| Patent | 36, 37, 38, 78, 112 | Subject matter and field |
| Job search | 31–35, 57, 66, 73, 100–102 | Target roles, companies, follow-up cadence |

Edit `content` in `evals/corpus/notes.jsonl`, then:

```bash
python -m pytest tests/test_eval_data.py -q   # catches broken labels
python evals/ingest.py --title-prefix          # re-embed
python evals/harness.py --strategies baseline --save baseline_real
```

Labels are correct *given the notes as written*, so rewriting content may
invalidate some. Re-check any question pointing at the ids above:
`python evals/review_labels.py --all --show-retrieved`.

## 4. Measure the Gemini reranker — the last unmeasured strategy

Implemented in `rag/rerankers.py`, never run. ~$0.05 for a full pass.

```bash
export GOOGLE_CLOUD_PROJECT=smartdesk-505315
python evals/harness.py --strategies baseline chunked+gemini --save vertex_gemini
```

Expectation, stated in advance: **it will not help.** Every other reranker went
negative once the production embedder was in play. Worth running precisely
because that is a falsifiable prediction — and if it wins, that is interesting.

## 5. Re-measure latency from the deployed service

The Neon run showed 2,166 ms per query against 29 ms on local Docker. That is
almost certainly cross-cloud round trip: Neon is in AWS `us-east-2`, the
measurement ran from Cloud Shell. From Cloud Run in `us-central1` it should
drop substantially, but nobody has checked.

If it stays high, the fix is a Neon region closer to `us-central1`, or moving
to Cloud SQL in the same region. Retrieval *quality* is region-independent;
only latency is affected, so none of the numbers in RESULTS.md change.

---

## Known limitations, deliberately unfixed

Not bugs — accepted trade-offs, recorded so they are not rediscovered as
oversights.

**Single-user by design.** OAuth tokens are written to a process-wide file on
the instance, so two users on the same container could share credentials. Fine
for one user, unacceptable for two. Fixing it means Secret Manager keyed per
user, plus session state scoped to a user identity rather than a session.

**No vector index.** Sequential scan is exact and fast enough at 120 notes.
Revisit past ~10,000 rows, then benchmark HNSW against exact search *on the
eval set* rather than assuming.

**Chunking is off by default.** It measured neutral-to-negative: only 6 of 120
notes are long enough to split. Kept because it is the right mechanism for a
corpus of long documents, and this corpus may become one.

**No agent-routing eval.** Which sub-agent should handle a given request is
itself a labelling problem, and mis-routing is currently invisible. The same
harness pattern would work: label requests with the correct agent, measure.
This is the most natural next evaluation to build.

**n = 40.** One question is worth 0.025 of recall@1. The eval detects large
effects and nothing else. Detecting a 2-point improvement reliably needs
roughly 300 questions. Do not tune parameters against this set — that is
fitting noise.
