# SmartDesk — Multi-Agent Productivity Assistant

A multi-agent AI system built with **Google ADK**, **Gemini 2.5 Flash**, **MCP**, and **AlloyDB** for the **Google Cloud Hackathon** (Multi-Agent Productivity Assistant track).

SmartDesk is a single chat interface backed by a team of specialized agents that handle email, calendar, and a personal knowledge base — so you can ask things like *"what's on my plate today?"* and get an answer that spans your inbox, schedule, and notes.

## Architecture

```
User (HTTP request)
    |
    v
root_agent (SmartDesk orchestrator)
    |-- inbox_agent ----> Gmail MCP Server
    |-- planner_agent --> Google Calendar MCP Server
    '-- data_agent -----> AlloyDB (vector search)
```

The root agent handles authentication and routes each request to the right sub-agent via ADK's `transfer_to_agent`. Each sub-agent formats its own output — there is no separate response formatter.

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

## Project Structure

```
smartdesk/
├── smartdesk_agent/
│   └── smartdesk_app/
│       ├── __init__.py        # from . import agent
│       ├── agent.py           # Agent definitions (root_agent entry point)
│       ├── tools.py           # MCP toolsets + AlloyDB query functions
│       ├── authenticate.py    # CLI script for pre-auth setup
│       └── mcp_servers/
│           ├── auth.py              # Shared OAuth 2.0 helper
│           ├── gmail_server.py      # Gmail MCP server (stdio)
│           └── calendar_server.py   # Calendar MCP server (stdio)
│       └── rag/                     # Retrieval pipeline (see Evaluating retrieval)
│           ├── embeddings.py        # Pluggable embedders (Vertex / local)
│           ├── chunking.py          # Token-based chunking with overlap
│           ├── db.py                # Portable AlloyDB / pgvector access
│           ├── retrieval.py         # Whole-note and chunk-level search
│           └── rerankers.py         # BM25, RRF fusion, cross-encoder, Gemini
├── evals/
│   ├── RESULTS.md             # Measured results and what did NOT help
│   ├── corpus/notes.jsonl     # 120-note synthetic eval corpus
│   ├── questions.jsonl        # 30 labelled questions
│   ├── ingest.py              # Load corpus, build both indexes
│   ├── harness.py             # Run strategies, print comparison table
│   ├── metrics.py             # recall@k, MRR@k, paired bootstrap
│   └── results/               # Committed measurements
├── setup/
│   ├── setup_env.sh           # Environment setup script
│   ├── setup_alloydb.sql      # AlloyDB schema + sample data
│   └── migrations/            # Additive schema migrations
├── tests/
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Evaluating retrieval

Retrieval quality is measured, not assumed. **[evals/RESULTS.md](evals/RESULTS.md)
has the numbers**, including what did not help.

Short version: the baseline (whole-note embedding, cosine, top 5) scores
R@5 0.925 / MRR@10 0.814 on a 120-note personal corpus with 40 labelled
questions. A cross-encoder reranking chunk retrieval is the only change that
beat it significantly (MRR@10 +0.094, R@1 +0.138, p = 0.04) — but that
p-value is uncorrected across six compared strategies, and enabling it puts
PyTorch in the deployed image. `search_notes` therefore still defaults to
the baseline.

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

**2. Install eval dependencies.** The local embedder is CPU-only and needs no GPU:

```bash
pip install -r requirements.txt
pip install --index-url https://download.pytorch.org/whl/cpu \
            --extra-index-url https://pypi.org/simple sentence-transformers
```

**3. Ingest the corpus and run the harness:**

```bash
export SMARTDESK_EMBEDDER=local
export DATABASE_URL=postgresql+pg8000://smartdesk:smartdesk@127.0.0.1:5432/smartdesk

python evals/ingest.py --reset --title-prefix   # ~9s on CPU
python evals/harness.py                          # all strategies
python evals/harness.py --strategies baseline --save baseline
```

The harness prints recall@k and MRR@k at k=1,3,5,10 for every strategy, deltas
against the baseline, a paired bootstrap significance test, and per-query
latency.

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
> fraction of a cent; a full harness run including Gemini reranking is ~$0.04.

### Retrieval modes

`search_notes` reads `SMARTDESK_RETRIEVAL`:

| value | behaviour |
|---|---|
| `baseline` *(default)* | Whole-note vector search — the original behaviour |
| `chunked` | Chunk-level search, collapsed back to parent notes |
| `hybrid` | Fuses whole-note, chunk, and BM25 rankings with RRF (~26ms) |
| `rerank` | Chunk retrieval reranked by a cross-encoder — best measured, ~700ms, needs `sentence-transformers` |

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
