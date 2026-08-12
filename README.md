# SmartDesk — Multi-Agent Productivity Assistant

A multi-agent AI system built with **Google ADK**, **Gemini 2.5 Flash**, **MCP**, and **AlloyDB** for the **Google Cloud Hackathon** (Multi-Agent Productivity Assistant track).

SmartDesk is a single chat interface backed by a team of specialized agents that handle email, calendar, and a personal knowledge base — so you can ask things like *"what's on my plate today?"* and get an answer that spans your inbox, schedule, and notes.

**Scope:** a single-user personal project. There is no web frontend — the interface is ADK's dev UI (`adk web`) locally, or an HTTP request against the Cloud Run service. The OAuth and session-state design both assume one user; see [`evals/RESULTS.md`](evals/RESULTS.md) and the corpus notes for where that assumption is baked in.

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
enough to split. It earns its place as a *candidate generator* for rerankers,
not as a retrieval win by itself. [RESULTS.md](evals/RESULTS.md) has the full
picture, including a case where the same reranker was the *worst* option on a
different corpus.

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
