# SmartDesk — Multi-Agent Productivity Assistant

A multi-agent AI system built with **Google ADK**, **Gemini 2.5 Flash**, **MCP**, and **AlloyDB** for the **Google Cloud Hackathon** (Multi-Agent Productivity Assistant track).

## Architecture

```
User (HTTP request)
    |
    v
root_agent (SmartDesk orchestrator)
    |-- inbox_agent ----> Gmail MCP Server
    |-- planner_agent --> Google Calendar MCP Server
    |-- data_agent -----> AlloyDB (vector search)
    '-- response_formatter
            |
            v
      Final response
```

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
│       ├── mcp_servers/
│       │   ├── auth.py        # Shared OAuth 2.0 helper
│       │   ├── gmail_server.py    # Gmail MCP server (stdio)
│       │   └── calendar_server.py # Calendar MCP server (stdio)
│       └── .env               # Environment config (not committed)
├── setup/
│   ├── setup_env.sh           # Environment setup script
│   └── setup_alloydb.sql      # AlloyDB schema + sample data
├── docs/
│   ├── adk.md                 # ADK reference (Track 1)
│   ├── mcp.md                 # MCP reference (Track 2)
│   └── alloydb.md             # AlloyDB reference (Track 3)
├── requirements.txt
├── Dockerfile
├── .env.example
└── CLAUDE.md
```

## Quick Start

```bash
# 1. Set project (docs/adk.md — Codelab 1)
gcloud config set project smartdesk-492115

# 2. Run environment setup
chmod +x setup/setup_env.sh
./setup/setup_env.sh

# 3. Create virtual environment (docs/adk.md — Codelab 1)
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# 4. Configure AlloyDB and MCP URLs in .env
# See .env.example for all required variables

# 5. Run locally (docs/adk.md — Codelab 1)
cd smartdesk_agent
adk web
# Open http://localhost:8000
```

## Deploy to Cloud Run

```bash
# Pattern from docs/adk.md — Codelab 2, Section 10
source smartdesk_agent/smartdesk_app/.env

# Create service account
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="SmartDesk Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

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

## Sample Test Prompts

These prompts demonstrate SmartDesk's capabilities across all three tracks:

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

## Documentation

- [ADK Reference (Track 1)](docs/adk.md)
- [MCP Reference (Track 2)](docs/mcp.md)
- [AlloyDB Reference (Track 3)](docs/alloydb.md)

## License

MIT
