# CLAUDE.md — SmartDesk Implementation Guide

## CRITICAL: Read This First
- **Always read `docs/adk.md`, `docs/mcp.md`, and `docs/alloydb.md` before writing or modifying code.** These contain the exact codelab steps the developer followed to learn these technologies. All implementation must follow the same patterns, imports, and structures shown in those docs.
- **GCP Project ID:** `smartdesk-492115`
- **Environment:** Google Cloud Console (Cloud Shell + Cloud Shell Editor)
- **Never guess patterns** — always verify against the docs first.

---

## Project Overview

SmartDesk is a multi-agent productivity assistant for the Google Cloud Hackathon (Multi-Agent Productivity Assistant track). It uses:
- **ADK** (Agent Development Kit) for agent orchestration
- **Gemini 2.5 Flash** as the LLM
- **MCP** (Model Context Protocol) for Gmail and Google Calendar integration  
- **AlloyDB** for PostgreSQL with vector search for a Personal CRM knowledge base
- **Cloud Run** for serverless deployment

---

## Current Status (as of 2026-04-08)

### What's Done
- All agents implemented and working: root_agent, inbox_agent, planner_agent, data_agent
- Gmail MCP server (stdio) — list, search, read, draft emails
- Calendar MCP server (stdio) — list, search, create events, find free time
- AlloyDB with vector search — contacts, notes (semantic search), tasks (CRUD)
- Per-user Google OAuth login/logout/switch-account via chat
- Anti-duplication callbacks (`_before_model` / `_after_model`) to prevent re-processing after sub-agent transfers
- Cloud Run deployment in progress (service account created, deploying)

### Known Issues & Gotchas
1. **429 RESOURCE_EXHAUSTED** — Gemini 2.5 Flash rate limits. Space requests ~30 seconds apart during demos. This is a Vertex AI quota issue, not a code bug.
2. **`LlmResponse(content=None)` does NOT stop ADK's LLM loop** — ADK retries when content is None. Must return `LlmResponse` with empty text part (`parts=[types.Part(text="")]`) to properly end the turn. This was the root cause of response duplication.
3. **Follow-up messages stay in sub-agent context** — After transferring to inbox_agent, subsequent messages in the same session continue with inbox_agent (ADK behavior). User must start a new session for different agent types.
4. **MCP tool discovery warnings** — `auth_config or auth_config.auth_scheme is missing` warnings are harmless. The MCP tools work without auth config because our custom servers handle OAuth internally.
5. **Gemini 2.5 Flash "thinking" can be slow** — Some LLM calls take 30-160 seconds. This is model thinking time, not a bug.

### Anti-Duplication Architecture (IMPORTANT — read before modifying agent.py)

The root_agent uses `before_model_callback` and `after_model_callback` to prevent duplicate sub-agent calls:

```
Flow: User message → root_agent LLM calls → transfer_to_agent → sub-agent runs → STOP

_after_model: detects transfer_to_agent function call → sets state["_transferred"] = True
Sub-agent runs to completion, control returns to root_agent
_before_model: sees _transferred=True → returns LlmResponse with empty text (ends turn), resets flag to False
Next user message: flag is False, so normal processing resumes
```

**CRITICAL:** Do NOT use `LlmResponse(content=None)` to stop the loop. It doesn't work — ADK retries. Always use `LlmResponse(content=types.Content(role="model", parts=[types.Part(text="")]))`.

### Auth Flow (login_google / switch_account)

```
1. User asks about email/calendar → root_agent calls check_login_status
2. If not logged in → root_agent calls login_google
3. login_google stores auth URL in state["_pending_auth_url"]
4. _before_model callback sees the URL → returns it as a model response (user sees sign-in link)
5. User signs in via browser, pastes redirect URL back in chat
6. root_agent calls complete_google_login → exchanges code for tokens
7. User is now authenticated for Gmail + Calendar MCP
```

switch_account: calls logout() first, then generates a new auth URL. Same flow as login.

---

## Architecture

```
User (HTTP request)
    │
    ▼
root_agent (SmartDesk orchestrator)
    │   tools: add_prompt_to_state, login_google, complete_google_login,
    │          check_login_status, switch_account
    │   callbacks: _before_model (auth URL injection + anti-reprocessing)
    │              _after_model (tracks transfer_to_agent calls)
    │
    ├── inbox_agent ──► Gmail MCP Server (stdio, gmail_server.py)
    ├── planner_agent ──► Calendar MCP Server (stdio, calendar_server.py)
    └── data_agent ──► AlloyDB (vector search, direct pg8000)
```

No response_formatter agent — each sub-agent formats its own output via `output_key`.

---

## File Reference

| File | What It Does |
|------|-------------|
| `smartdesk_agent/smartdesk_app/__init__.py` | Package init: `from . import agent` |
| `smartdesk_agent/smartdesk_app/agent.py` | All agent definitions, callbacks, root_agent entry point |
| `smartdesk_agent/smartdesk_app/tools.py` | MCP toolsets + AlloyDB tools + OAuth tools |
| `smartdesk_agent/smartdesk_app/mcp_servers/auth.py` | Shared OAuth 2.0 helper (generate_auth_url, exchange_auth_code, is_logged_in, logout) |
| `smartdesk_agent/smartdesk_app/mcp_servers/gmail_server.py` | Gmail MCP server (list, search, read, draft emails) |
| `smartdesk_agent/smartdesk_app/mcp_servers/calendar_server.py` | Calendar MCP server (list, search, create events, find free time) |
| `smartdesk_agent/smartdesk_app/.env` | Environment config (not committed) |
| `setup/setup_alloydb.sql` | Database schema + sample data |
| `requirements.txt` | Python dependencies |

---

## Step-by-Step Implementation (Follow Exactly)

### PHASE 1: Environment Setup (from docs/adk.md — Codelab 1, Section 3-4)

All work happens in **Google Cloud Shell**. Project ID is `smartdesk-492115`.

```bash
# 1. Set project (docs/adk.md — "Set Project ID")
gcloud config set project smartdesk-492115

# 2. Enable APIs (docs/adk.md — "Enable required APIs")
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com \
  alloydb.googleapis.com \
  servicenetworking.googleapis.com

# 3. Clone the repo
git clone https://github.com/JannetEkka/smartdesk.git
cd smartdesk

# 4. Create virtual environment (docs/adk.md — "Create a Python virtual environment")
uv venv --python 3.12
source .venv/bin/activate

# 5. Install dependencies (docs/adk.md — "Install requirements")
uv pip install -r requirements.txt
```

### PHASE 2: Configure Environment Variables (from docs/adk.md — Codelab 2, "Set up environment variables")

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=smartdesk-cr-service

cat <<EOF > smartdesk_agent/smartdesk_app/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL=gemini-2.5-flash
EOF
```

### PHASE 3: AlloyDB Setup (from docs/alloydb.md — Codelab 1 + Codelab 3)

**Step 3a: Create AlloyDB Cluster (docs/alloydb.md — "AlloyDB setup")**

- Cluster name: `smartdesk-cluster`
- Instance name: `smartdesk-instance`
- Region: `us-central1`
- Enable **Public IP** + add `0.0.0.0/0` to Authorized External Networks (testing only)

**Step 3b: Enable Extensions**

```sql
CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;
GRANT EXECUTE ON FUNCTION embedding TO postgres;
```

**Step 3c: Grant Vertex AI Role**

- Principal: `service-PROJECT_NUMBER@gcp-sa-alloydb.iam.gserviceaccount.com`  
- Role: `Vertex AI User`

**Step 3d: Create Schema + Load Data**

Run `setup/setup_alloydb.sql` in AlloyDB Studio.

**Step 3e: Test Vector Search**

```sql
SELECT id, title, content FROM notes
ORDER BY content_embedding <=> embedding('text-embedding-005', 'product launch timeline')::vector
LIMIT 5;
```

### PHASE 4-6: Agent Code, MCP, AlloyDB Tools

See `agent.py` and `tools.py` — these are fully implemented. Key patterns:

- **MCP**: Uses `StdioConnectionParams` + `StdioServerParameters` to connect to custom MCP servers (`gmail_server.py`, `calendar_server.py`)
- **AlloyDB**: Uses `pg8000` via SQLAlchemy. Vector search with `embedding('text-embedding-005', :query)::vector` and `<=>` operator.
- **Auth**: Per-user OAuth stored in `mcp_servers/auth.py`. Tokens saved to `~/.smartdesk_token.json`.

### PHASE 7: Local Testing

```bash
cd smartdesk_agent
adk web
# Open http://localhost:8000 or Cloud Shell Web Preview on port 8000
```

### PHASE 8: Deploy to Cloud Run

```bash
cd ~/smartdesk/smartdesk_agent
source smartdesk_app/.env

# Create service account (if not already created)
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="SmartDesk Service Account"

# Grant yourself permission to use the service account
gcloud iam service-accounts add-iam-policy-binding \
  ${SERVICE_ACCOUNT} \
  --member="user:jannetaekka@gmail.com" \
  --role="roles/iam.serviceAccountUser"

# Grant Vertex AI User role to the service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

# Authenticate gcloud CLI (required for deploy)
gcloud auth login

# Deploy
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --service_name=smartdesk-agent \
  --with_ui \
  . \
  -- \
  --service-account=$SERVICE_ACCOUNT

# Get the service URL
SERVICE_URL=$(gcloud run services describe smartdesk-agent \
  --region=us-central1 --format='value(status.url)')
echo $SERVICE_URL
```

---

## Key Rules

1. **`root_agent` variable name is mandatory** — ADK uses it as the entry point
2. **`__init__.py` must contain `from . import agent`** — this is how ADK discovers the agent
3. **Use `output_key` on sub-agents** to pass data between agents
4. **Use `tool_context.state["KEY"]` for state** — not global variables
5. **MCPToolset handles everything** — connection, discovery, proxying, shutdown
6. **Vector search uses `<=>` operator** with `embedding()` function in SQL
7. **AlloyDB extensions must be enabled first** — `google_ml_integration` and `vector`
8. **Vertex AI User role** must be granted to AlloyDB SA, Cloud Run SA, AND your user account
9. **Never hardcode project IDs in code** — always use `os.getenv()` or `.env`
10. **The GCP Project ID is `smartdesk-492115`** — use this everywhere
11. **Never use `LlmResponse(content=None)`** — use empty text part to stop ADK LLM loop
12. **Tasks/notes/contacts skip auth** — only email and calendar need Google OAuth

## Demo Prompts (for testing / demo video)

**Email (Gmail MCP):**
- "Show me my latest emails"
- "Search for emails from support@hack2skill.com"
- "Draft an email to test@example.com about the project update"

**Calendar (Calendar MCP):**
- "What's on my schedule today?"
- "Find free time slots for tomorrow"
- "Create a meeting called 'Team Sync' tomorrow at 2pm to 3pm"

**Knowledge Base (AlloyDB vector search):**
- "What are my pending tasks?"
- "Search my notes about product launch"
- "Add a task: Review Q2 budget with high priority, due 2026-04-10"
- "Look up contact info for Priya"
- "Mark task 3 as done"

**Account Management:**
- "Switch account" — logs out and provides new Google sign-in link
- "Relogin" or "Change account" — same as above

**Demo tips:**
- Space requests ~30 seconds apart to avoid 429 rate limiting
- Start a new session when switching between agent types (email → calendar → tasks)
- For email/calendar: login first, then test prompts
- For tasks/notes/contacts: no login needed

## Docs Reference (ALWAYS check before coding)

- **`docs/adk.md`** — How to build agents, SequentialAgent, tools, state, deployment.
- **`docs/mcp.md`** — How to connect to MCP servers, MCPToolset, BigQuery/Maps examples, building custom MCP servers.
- **`docs/alloydb.md`** — How to set up AlloyDB, enable extensions, vector search, embeddings, natural language SQL, Gemini Flash integration.
