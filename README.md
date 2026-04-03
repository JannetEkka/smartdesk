# SmartDesk — Multi-Agent Productivity Assistant

A multi-agent AI system built with **Google ADK**, **Gemini**, **MCP**, and **AlloyDB** that helps users manage emails, schedules, and personal knowledge through a single conversational API.

Built for the **Google Cloud Hackathon** — Multi-Agent Productivity Assistant track.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              User (API on Cloud Run)             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│          SmartDesk Orchestrator (root_agent)      │
│            Routes to sub-agents via ADK           │
└──────┬──────────────┬──────────────────┬────────┘
       │              │                  │
┌──────▼─────┐ ┌──────▼──────┐ ┌────────▼───────┐
│ InboxAgent │ │ PlannerAgent│ │   DataAgent    │
│ Gmail MCP  │ │Calendar MCP │ │ AlloyDB queries│
└──────┬─────┘ └──────┬──────┘ └────────┬───────┘
       │              │                  │
┌──────▼─────┐ ┌──────▼──────┐ ┌────────▼───────┐
│Gmail MCP   │ │Calendar MCP │ │   AlloyDB      │
│  Server    │ │   Server    │ │ (Vector Search)│
└────────────┘ └─────────────┘ └────────────────┘
```

## Tech Stack

| Component | Technology | Track |
|-----------|-----------|-------|
| Agent Framework | Google ADK (Agent Development Kit) | Track 1 |
| LLM | Gemini 2.5 Flash | Track 1 |
| Deployment | Cloud Run (serverless) | Track 1 |
| Email Integration | Gmail MCP Server | Track 2 |
| Calendar Integration | Google Calendar MCP Server | Track 2 |
| Database | AlloyDB for PostgreSQL | Track 3 |
| Vector Search | AlloyDB AI + text-embedding-005 | Track 3 |
| Natural Language Queries | AlloyDB AI natural language | Track 3 |

## Features

- **Multi-agent orchestration** — Root agent routes to specialized sub-agents
- **Email management** — Summarize, search, and draft emails via Gmail MCP
- **Calendar management** — Check schedule, find conflicts, book meetings via Calendar MCP
- **Personal knowledge base** — Store contacts, notes, and tasks in AlloyDB with semantic vector search
- **Multi-step workflows** — "Prepare me for my 3pm meeting" triggers calendar → notes → email pipeline
- **API-based** — Deployed on Cloud Run, callable via HTTP endpoint

## Project Structure

```
smartdesk/
├── README.md
├── CLAUDE.md                          # Claude Code instructions
├── .gitignore
├── docs/
│   ├── adk.md                         # ADK reference (Track 1)
│   ├── mcp.md                         # MCP reference (Track 2)
│   └── alloydb.md                     # AlloyDB reference (Track 3)
├── smartdesk_agent/
│   └── smartdesk_app/
│       ├── __init__.py
│       ├── agent.py                   # Main agent definitions
│       ├── tools.py                   # MCP toolset configs & custom tools
│       └── .env                       # Environment variables (not committed)
├── setup/
│   ├── setup_alloydb.sql              # AlloyDB schema + sample data
│   └── setup_env.sh                   # Environment setup script
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Quick Start

### Prerequisites
- Google Cloud project with billing enabled
- AlloyDB cluster and instance
- APIs enabled: Vertex AI, Cloud Run, AlloyDB, Compute Engine

### Setup

```bash
# Clone the repo
git clone https://github.com/<your-username>/smartdesk.git
cd smartdesk

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example smartdesk_agent/smartdesk_app/.env
# Edit .env with your project details

# Run locally
cd smartdesk_agent
adk web
```

### Deploy to Cloud Run

```bash
adk deploy cloud_run \
    --project $PROJECT_ID \
    --region us-central1 \
    --service_name smartdesk-agent \
    smartdesk_agent
```

## Documentation

- [ADK Reference (Track 1)](docs/adk.md) — Agent Development Kit patterns, deployment, A2A
- [MCP Reference (Track 2)](docs/mcp.md) — Model Context Protocol integration, MCP servers
- [AlloyDB Reference (Track 3)](docs/alloydb.md) — Database setup, vector search, natural language queries

## License

MIT
