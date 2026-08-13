# SmartDesk — Multi-Agent Assistant with a Measured RAG Pipeline

A single-user personal assistant built on **Google ADK**, **Gemini 2.5 Flash**,
**MCP**, and **Postgres/pgvector**, with a retrieval pipeline whose quality is
**measured rather than assumed**.

SmartDesk is one chat interface over three specialised agents — email, calendar,
and a personal knowledge base — so *"what's on my plate today?"* returns an
answer spanning all three.

**The retrieval evaluation is the point.** Most RAG projects ship chunking and
reranking because the techniques are standard. This one has a labelled question
set, recall@k and MRR@k with confidence intervals, and committed numbers for
every variant. On this corpus the standard techniques **did not help**, and the
measurement is what proved it — including a case where the same reranker looked
like a clear winner on one embedder and a clear loser on the production one.
Start at [`evals/RESULTS.md`](evals/RESULTS.md).

**Scope and history.** Originally built for the Google Cloud Multi-Agent
Productivity Assistant hackathon; now a personal project kept for its own sake
and as a worked example of retrieval evaluation. The eval corpus is a knowledge
base of that history, hackathon logistics included, because that is what was
actually going on while it was built.

There is no custom web frontend. The interface is ADK's own dev UI (`adk web`)
locally, or the **Cloud Run service URL** once deployed — see
[Running it](#running-it) for how to get that URL and how to deploy *with* the
ADK UI attached. The OAuth and session-state design both assume a single user.

## Architecture

```
User (HTTP request)
    |
    v
root_agent (SmartDesk orchestrator)
    |-- inbox_agent ----> Gmail MCP Server (stdio subprocess)
    |-- planner_agent --> Google Calendar MCP Server (stdio subprocess)
    '-- data_agent -----> retrieval pipeline
                              |
                              |  embed query (Vertex text-embedding-005
                              |               or local MiniLM)
                              v
                          AlloyDB / Postgres + pgvector
                              notes.content_embedding   (whole-note)
                              note_chunks.content_embedding (chunked)
                              |
                              v
                          optional rerank -> top 5 notes
```

The root agent handles authentication and routes each request to the right sub-agent via ADK's `transfer_to_agent`. Each sub-agent formats its own output — there is no separate response formatter.

Embeddings are computed **client-side** and bound as a query parameter rather than through AlloyDB's in-database `embedding()` function. That is what lets the identical code run against AlloyDB in production and plain Postgres + pgvector in development — the `<=>` cosine distance operator is the same on both.

## Tech Stack

| Component | Technology | Track |
|-----------|-----------|-------|
| Agent Framework | Google ADK 1.14.0 | Track 1 |
| LLM | Gemini 2.5 Flash (Vertex AI) | Track 1 |
| Deployment | Cloud Run (serverless) | Track 1 |
| Email Integration | Gmail MCP Server | Track 2 |
| Calendar Integration | Google Calendar MCP Server | Track 2 |
| Database | AlloyDB for PostgreSQL | Track 3 |
| Vector Search | text-embedding-005 (768 dims) | Track 3 |
| Dev Database | Postgres 16 + pgvector (same schema, no cloud cost) | Track 3 |
| Retrieval Eval | recall@k, MRR@k, paired bootstrap — see [RESULTS.md](evals/RESULTS.md) | Track 3 |

## Project Structure

```
smartdesk/
├── smartdesk_agent/
│   └── smartdesk_app/
│       ├── __init__.py        # from . import agent
│       ├── agent.py           # Agent definitions (root_agent entry point)
│       ├── tools.py           # MCP toolsets + AlloyDB query functions
│       ├── authenticate.py    # CLI script for pre-auth setup
│       ├── mcp_servers/
│       │   ├── auth.py              # Shared OAuth 2.0 helper
│       │   ├── gmail_server.py      # Gmail MCP server (stdio)
│       │   └── calendar_server.py   # Calendar MCP server (stdio)
│       └── rag/                     # Retrieval pipeline (see Evaluating retrieval)
│           ├── embeddings.py        # Pluggable embedders (Vertex / local)
│           ├── chunking.py          # Token-based chunking with overlap
│           ├── db.py                # Portable AlloyDB / pgvector access
│           ├── retrieval.py         # Whole-note and chunk-level search
│           └── rerankers.py         # BM25, RRF fusion, cross-encoder, Gemini
├── evals/
│   ├── RESULTS.md             # Measured results and what did NOT help
│   ├── corpus/notes.jsonl     # 120-note personal eval corpus
│   ├── questions.jsonl        # 40 labelled questions
│   ├── ingest.py              # Load corpus, build both indexes
│   ├── harness.py             # Run strategies, print comparison table
│   ├── metrics.py             # recall@k, MRR@k, paired bootstrap
│   └── results/               # Committed measurements (baseline.json, final.json)
├── setup/
│   ├── setup_env.sh           # Environment setup script
│   ├── setup_alloydb.sql      # AlloyDB schema + sample data
│   └── migrations/
│       └── 001_note_chunks.sql      # Additive, reversible chunks table
├── tests/
│   ├── test_chunking.py             # Overlap, coverage, termination
│   ├── test_metrics.py              # recall@k / MRR@k / bootstrap
│   ├── test_rerankers.py            # BM25 and rank fusion
│   └── test_retrieval_integration.py  # Real database, skipped without one
├── requirements.txt           # Runtime dependencies (deployed image)
├── requirements-eval.txt      # Eval + rerank extras (pulls PyTorch)
├── Dockerfile
└── .env.example
```

## Evaluating retrieval

Retrieval quality is measured, not assumed. **[evals/RESULTS.md](evals/RESULTS.md)
has the numbers**, including what did not help.

Measured on **text-embedding-005**, the production embedder — 120-note personal
corpus, 40 labelled questions:

| strategy | R@1 | R@5 | MRR@10 | latency |
|---|---|---|---|---|
| **`baseline`** *(default)* | 0.800 | **0.963** | 0.886 | **29 ms** |
| `chunked` | 0.800 | 0.963 | 0.885 | 24 ms |
| `hybrid` | 0.775 | 0.950 | 0.870 | 52 ms |
| chunked + RRF | 0.750 | **0.975** | 0.859 | 37 ms |
| `rerank` (cross-encoder) | **0.838** | 0.950 | **0.914** | 2,382 ms |

**Plain baseline retrieval wins.** Nothing is statistically significant. The
cross-encoder is nominally ahead on MRR@10 (+0.028) but the interval spans
zero (p = 0.44) and it costs **82x the latency** plus ~190 MB of PyTorch in an
image deliberately slimmed to fix cold starts. `search_notes` stays on
`baseline` — on evidence, not caution.

The same comparison on a weaker development embedder (all-MiniLM-L6-v2)
reached the *opposite* conclusion: there the cross-encoder won by a
significant margin (+0.094, p = 0.04). On the production embedder that shrank
to +0.028 and lost significance. A stronger embedder produces better
candidates and leaves less for a reranker to fix.
[RESULTS.md](evals/RESULTS.md) §0 has the detail; it is the clearest argument
in the project for measuring rather than assuming.

<details>
<summary>Development-embedder numbers (all-MiniLM-L6-v2), for comparison</summary>

120-note personal corpus, 40 labelled questions, all-MiniLM-L6-v2, Postgres + pgvector:

| strategy | R@1 | R@5 | MRR@10 | latency | cost / 1k |
|---|---|---|---|---|---|
| `baseline` *(default)* | 0.700 | 0.925 | 0.814 | 22 ms | $0 |
| `chunked` | 0.700 | 0.900 | 0.812 | 13 ms | $0 |
| `hybrid` | 0.750 | 0.925 | 0.843 | 26 ms | $0 |
| chunked + RRF | 0.775 | 0.938 | 0.861 | 16 ms | $0 |
| `rerank` (cross-encoder) | **0.838** | **0.950** | **0.908** | 699 ms | $0 |
| Gemini reranker | *unmeasured* | | | ~1 RTT | ~$1.18 |

`rerank` is the only strategy whose 95% confidence interval excludes zero
(MRR@10 +0.094, CI [+0.012, +0.186], p = 0.04, 8 questions better / 2 worse).

**It is still not the default**, because that p-value is uncorrected across six
compared strategies, because enabling it puts PyTorch in an image that was
deliberately cut from 1.8 GB to 340 MB to fix cold starts, and because the 40
labels have not been human-reviewed yet. `chunked+rrf` is the free alternative
at +0.047 MRR@10 and 16 ms.

Chunking on its own did **not** help (−0.003) — only 6 of 120 notes were long
enough to split.

</details>

### Reproducing the eval locally

Development runs against **Postgres + pgvector**, not AlloyDB, so nothing costs
money. The schema and the `<=>` operator are identical on both.

**1. Start Postgres with pgvector.** Either Docker:

```bash
docker run -d --name smartdesk-pg -p 5432:5432 \
  -e POSTGRES_USER=smartdesk -e POSTGRES_PASSWORD=smartdesk -e POSTGRES_DB=smartdesk \
  pgvector/pgvector:pg16
```

or a native install (`apt install postgresql-16 postgresql-16-pgvector`), then
create the `smartdesk` role and database.

**2. Install eval dependencies.** CPU-only wheels — no GPU needed, ~16 GB RAM is plenty:

```bash
pip install --index-url https://download.pytorch.org/whl/cpu \
            --extra-index-url https://pypi.org/simple \
            -r requirements-eval.txt
```

`requirements-eval.txt` includes `requirements.txt` and adds
`sentence-transformers` and `pytest`. It is kept separate because PyTorch is
several hundred MB and the deployed image installs `requirements.txt` only.

**3. Ingest the corpus and run the harness:**

```bash
export SMARTDESK_EMBEDDER=local
export DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk

python evals/ingest.py --reset --title-prefix   # ~9s on CPU
python evals/harness.py                          # all strategies
python evals/harness.py --strategies baseline --save baseline
```

`--reset` drops and recreates the tables, so only ever point it at a
development database. `--title-prefix` repeats the note title on chunks after
the first, which measurably beat plain chunking and is the recommended setting.
Chunk size and overlap are `--chunk-size` / `--overlap` (defaults 180 / 40).

The harness prints recall@k and MRR@k at k=1,3,5,10 for every strategy, deltas
against the baseline, a paired bootstrap significance test, and per-query
latency. `--save LABEL` writes `evals/results/LABEL.json` with per-question
detail so a run can be diffed against a previous one.

**Reading the output.** A delta without a `*` in the significance table is not
a demonstrated improvement. At 40 questions one question is worth 0.025 of
recall@1, so most differences in the table above are 1–3 questions.

### Running against Vertex and AlloyDB

To reproduce with the production embedder (`text-embedding-005`, 768d) and
enable the Gemini reranker:

```bash
export SMARTDESK_EMBEDDER=vertex GOOGLE_CLOUD_PROJECT=<project>
export DATABASE_URL=postgresql+pg8000://postgres:<pw>@<alloydb-ip>:5432/postgres
gcloud auth application-default login

psql "$PSQL_URL" -f setup/migrations/001_note_chunks.sql   # additive, reversible
python evals/ingest.py            # no --reset: leaves existing notes intact
python evals/harness.py --save vertex
```

> This calls Vertex AI and bills your project. Embedding the corpus is a
> fraction of a cent; a full harness run including Gemini reranking is ~$0.05.

### Retrieval modes

`search_notes` reads `SMARTDESK_RETRIEVAL`:

| value | behaviour |
|---|---|
| `baseline` *(default)* | Whole-note vector search — the original behaviour, 22 ms |
| `chunked` | Chunk-level search, collapsed back to parent notes, 13 ms |
| `hybrid` | Fuses whole-note, chunk, and BM25 rankings with RRF, 26 ms |
| `rerank` | Chunk retrieval reranked by a cross-encoder — best measured, 699 ms, requires `requirements-eval.txt` |

Switching to `chunked`, `hybrid`, or `rerank` needs the chunks table to exist
and be populated — apply `setup/migrations/001_note_chunks.sql` and run
`evals/ingest.py` (without `--reset`) to backfill. After that `add_note` keeps
both indexes current on every write, so modes can be switched freely.

### Labels need review

The corpus and its 40 question labels are **written for this eval, not kept
at the time**. The threads are real — the four accounts, the hackathons, the
patent timeline, SmartDesk's own bugs — but the specifics are placeholders.
Every question is flagged `reviewed: false` in `evals/questions.jsonl` and the
harness warns until that changes. Correct any wrong labels and flip the flag
before treating these numbers as ground truth.

### Tests

```bash
python -m pytest tests/
# Integration tests need a database and are skipped without one:
export SMARTDESK_TEST_DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk_test
python -m pytest tests/
```

## Running it

There is no custom frontend. What you get is one of three surfaces, and which
one depends on how you start it:

| Surface | Command | UI? |
|---|---|---|
| Local dev | `cd smartdesk_agent && adk web` | Yes — ADK dev UI on `http://localhost:8000` |
| Local API | `cd smartdesk_agent && adk api_server --port 8080 .` | No — HTTP endpoints only |
| Cloud Run | see below | Only if deployed with `--with_ui` |

**The Dockerfile in this repo runs `adk api_server`**, so a container built from
it serves the API with no browser UI. If you want the ADK UI on the deployed
service, deploy with `adk deploy cloud_run --with_ui` rather than building the
Dockerfile.

### Local

```bash
pip install -r requirements.txt
bash setup/setup_env.sh          # enables APIs, writes smartdesk_app/.env
# then add DATABASE_URL to smartdesk_agent/smartdesk_app/.env

cd smartdesk_agent && adk web    # http://localhost:8000
```

### Deploy to Cloud Run

The ADK CLI is the supported path — it builds and deploys in one step:

```bash
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_LOCATION=us-central1
export SERVICE_NAME=smartdesk

cd smartdesk_agent
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SERVICE_NAME \
  --with_ui \
  ./smartdesk_app
```

Drop `--with_ui` for an API-only service. To deploy the Dockerfile instead:

```bash
gcloud run deploy smartdesk \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=us-central1,MODEL=gemini-2.5-flash \
  --set-env-vars DATABASE_URL="postgresql+pg8000://postgres:PASSWORD@ALLOYDB_IP:5432/postgres"
```

`--allow-unauthenticated` is what lets anyone with the link open it. Without it
the URL returns 403 for everyone but you.

### Getting the URL

The deploy prints it, but to retrieve it later:

```bash
gcloud run services describe smartdesk \
  --region us-central1 \
  --format='value(status.url)'
```

That returns something like `https://smartdesk-<hash>-uc.a.run.app`. Append
`/dev-ui` for the ADK UI when deployed `--with_ui`.

> **Before sharing the URL:** every Google account that will sign in must be on
> the OAuth consent screen's test user list while the app is unverified, or
> sign-in fails with a 403. See [Authentication](#authentication).

### Service account roles

The runtime service account needs:

```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/alloydb.client"
```

### Cost notes

The service scales to zero, so an idle deployment costs nothing. Two things do
cost money continuously and are worth knowing about:

- **AlloyDB bills whether or not you use it.** Stop the cluster when not
  actively testing; develop against local Postgres + pgvector instead (see
  [Evaluating retrieval](#evaluating-retrieval)).
- **`--min-instances`** keeps containers warm and bills for them. Cold start is
  ~1.4s after the image slimming, so this is only worth setting temporarily —
  for example during a judging window — and turning off afterwards:

```bash
gcloud run services update smartdesk --region us-central1 --min-instances=1
gcloud run services update smartdesk --region us-central1 --min-instances=0
```

## Moving to a new GCP project

Nothing in this repo belongs to a GCP project — it is all code and config. To
move, you create a new project and redeploy the same code. What is genuinely
tied to the old project is the OAuth client, the database, and the deployed
service.

### Quickstart — paste this into Cloud Shell

```bash
# 1. Get the code
git clone https://github.com/JannetEkka/smartdesk.git
cd smartdesk

# 2. Create and select the project (skip `create` if it already exists)
export PROJECT_ID=smartdesk-$RANDOM
gcloud projects create "$PROJECT_ID" --name="SmartDesk"
gcloud config set project "$PROJECT_ID"

# link billing — required even for free-tier usage
gcloud billing accounts list
gcloud billing projects link "$PROJECT_ID" --billing-account=XXXXXX-XXXXXX-XXXXXX

# 3. Choose your database and embedder
export DATABASE_URL="postgresql+pg8000://USER:PASSWORD@HOST:5432/DBNAME"
export EMBEDDER=gemini                       # or: vertex
export GOOGLE_API_KEY=...                    # only when EMBEDDER=gemini

# 4. APIs, service account, IAM, .env, schema, corpus
./setup/deploy_new_project.sh all

# 5. Create the OAuth client (manual — the console steps are printed by step 4)
#    then save client_secret.json into smartdesk_agent/smartdesk_app/

# 6. Deploy and get the URL
./setup/deploy_new_project.sh deploy
```

`deploy_new_project.sh` runs in stages, and every stage is safe to re-run:

| Stage | Does |
|---|---|
| `apis` | Enables Run, Artifact Registry, Cloud Build, Vertex AI, IAM, Logging |
| `iam` | Creates the service account, grants `aiplatform.user`, `alloydb.client`, `logging.logWriter` |
| `oauth` | Prints the console steps (cannot be scripted) |
| `env` | Writes `smartdesk_app/.env`, masking secrets when it echoes back |
| `db` | `CREATE EXTENSION vector`, applies the schema and the chunks migration, ingests the corpus |
| `deploy` | `gcloud run deploy --source`, then prints the URL |
| `url` | Prints the service URL and the redirect-URI reminder |

`./setup/deploy_new_project.sh --help` lists them all.

> **Untested against a live project.** The script is syntax-checked and its
> env-var handling is tested (a password containing `@`, `,` and `:` round-trips
> correctly), but this environment has no GCP access, so it has not been run
> end to end. Expect to fix something.

> **AlloyDB is deliberately not enabled** by `apis`. It has no free tier and
> bills continuously. The script prints the command if you want it.

### What has to be recreated

| Thing | Tied to the old project? | Action |
|---|---|---|
| This repo | No | Nothing — it is on GitHub |
| `client_secret.json` | **Yes** | Recreate the OAuth client and consent screen |
| `token.json` | Yes (derived) | Delete it; sign in again after redeploying |
| Project ID in `.env` | Yes | Regenerate with `setup/setup_env.sh` |
| Database + notes | Yes | Recreate schema, re-ingest |
| Cloud Run service | Yes | Redeploy |
| Service account | Yes | Recreate, re-grant roles |

**The OAuth client is the step that catches people out.** OAuth clients are
per-project, so `client_secret.json` from the old project will not work. In the
new project: APIs & Services → OAuth consent screen (External), add your own
addresses as test users while it is unverified, then Credentials → Create
credentials → OAuth client ID → Web application. Download the JSON as
`smartdesk_agent/smartdesk_app/client_secret.json` and delete any stale
`token.json` next to it.

### Steps

```bash
gcloud projects create smartdesk-NEW --name="SmartDesk"
gcloud config set project smartdesk-NEW
# link billing in the console (the $300 / 90-day credit applies to new accounts)

bash setup/setup_env.sh          # enables APIs, rewrites .env with the new project
```

Then recreate the OAuth client as above, point `DATABASE_URL` at your chosen
database, apply the schema, re-ingest, and redeploy per
[Deploy to Cloud Run](#deploy-to-cloud-run).

### Keeping it cheap

Two facts worth knowing before you pick anything:

- **AlloyDB has no Always Free tier** — only a 30-day trial cluster. If your
  old bill was a surprise, this is very likely why. It bills continuously
  whether or not you use it.
- **Cloud Run does have an Always Free tier** — 2M requests and 180k vCPU-
  seconds per month. A personal assistant will not come close to that, so the
  service itself is effectively free as long as it scales to zero.

Database options, cheapest first:

| Option | Cost | Trade-off |
|---|---|---|
| Free managed Postgres (Neon, Supabase) | Free tier | Not a GCP product — check whether hackathon Track 3 scoring requires a Google database |
| Postgres on the Always Free `e2-micro` VM | Free | You install and maintain it; e2-micro is small |
| Cloud SQL Postgres | ~$8–10/mo smallest | Managed, in GCP, supports pgvector, no free tier |
| AlloyDB | Free 90 days on trial credit, then significant | Best Track 3 story; stop the cluster when idle |

**Any Postgres with pgvector works** — that is what the portability work in
`rag/db.py` bought. Only `DATABASE_URL` changes.

### Dropping Vertex billing entirely

The Gemini API (AI Studio) has a free tier covering both `gemini-2.5-flash`
and `gemini-embedding-001`, and needs only an API key rather than a billed
project:

```bash
# get a key at https://aistudio.google.com/apikey
export GOOGLE_API_KEY=...
export GOOGLE_GENAI_USE_VERTEXAI=FALSE     # agent uses the Gemini API
export SMARTDESK_EMBEDDER=gemini           # embeddings use the Gemini API
```

`SMARTDESK_EMBEDDER=gemini` pins `output_dimensionality=768`, so the existing
`VECTOR(768)` column needs no migration. Re-ingest after switching — vectors
from different models are not comparable, and mixing them silently degrades
retrieval rather than erroring.

> **Untested.** This path was written but not run — this environment has no
> API key. Free-tier rate limits also apply, so ingesting a large corpus may
> need throttling. The numbers in [RESULTS.md](evals/RESULTS.md) were measured
> on the local embedder; re-run the harness after switching to see whether
> retrieval quality holds.

## Authentication

SmartDesk uses **per-user Google OAuth**. Each user signs in with their own Google account through the chat — you will only see your own emails and calendar events.

**How it works:**
1. Ask the agent anything about email or calendar (e.g., "show my inbox")
2. The agent will provide a Google sign-in link
3. Open the link, sign in with your Google account, and approve access
4. You'll land on a page that won't load — that's expected
5. Copy the full URL from your browser's address bar and paste it back in the chat
6. You're in! The agent now has access to your Gmail and Calendar

**Privacy:** No one else's data is accessible. Your OAuth token is session-scoped and only used for the duration of your interaction.

> **Note for judges/testers:** Your Google account email must be added to the OAuth consent screen's test user list before you can sign in. Please share your email with the developer so it can be added.

## Sample Prompts

**Email (Track 2 — Gmail MCP):**
- "Show me my latest emails"
- "Search for emails from [colleague name]"
- "Draft an email to test@example.com about the project update"

**Calendar (Track 2 — Calendar MCP):**
- "What's on my schedule today?"
- "Find free time slots for tomorrow"
- "Create a meeting called 'Team Sync' tomorrow at 2pm to 3pm"

**Knowledge Base (Track 3 — AlloyDB with vector search):**
- "What are my pending tasks?"
- "Search my notes about product launch"
- "Add a task: Review Q2 budget with high priority, due 2026-04-10"
- "Look up contact info for Priya"
- "Mark task 3 as done"

**Multi-domain:**
- "Prepare me for my next meeting" (calendar + notes)
- "What's on my plate today?" (tasks + calendar)

**Account Management:**
- "Switch account" — logs out and provides a new Google sign-in link
- "Relogin" or "Change account" — same as above, lets you switch to a different Google account

## License

MIT
