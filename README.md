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

## Documentation

- [ADK Reference (Track 1)](docs/adk.md)
- [MCP Reference (Track 2)](docs/mcp.md)
- [AlloyDB Reference (Track 3)](docs/alloydb.md)

## License

MIT
