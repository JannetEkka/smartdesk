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

## Architecture

```
User (HTTP request)
    │
    ▼
root_agent (SmartDesk orchestrator)
    ├── inbox_agent ──► Gmail MCP Server
    ├── planner_agent ──► Google Calendar MCP Server
    ├── data_agent ──► AlloyDB (vector search)
    └── response_formatter (SequentialAgent)
            │
            ▼
      Final response
```

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
git clone https://github.com/<username>/smartdesk.git
cd smartdesk

# 4. Create virtual environment (docs/adk.md — "Create a Python virtual environment")
# The docs use `uv venv` — follow that pattern:
uv venv --python 3.12
source .venv/bin/activate

# 5. Install dependencies (docs/adk.md — "Install requirements")
uv pip install -r requirements.txt
```

### PHASE 2: Configure Environment Variables (from docs/adk.md — Codelab 2, "Set up environment variables")

Follow the exact pattern from the zoo_guide_agent codelab:

```bash
# Get project details automatically (docs/adk.md — Codelab 2)
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=smartdesk-cr-service

# Create .env file (docs/adk.md — "Create the .env file using those variables")
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

Follow the AlloyDB Quick Setup codelab exactly:
- Create cluster in Google Cloud Console → AlloyDB for PostgreSQL
- Cluster name: `smartdesk-cluster`
- Instance name: `smartdesk-instance`
- Password: set and save it
- Region: `us-central1`
- Enable **Public IP** connectivity and add `0.0.0.0/0` to Authorized External Networks (for Cloud Shell testing only)
- Wait for READY status on both cluster and instance

> **IMPORTANT:** Remove `0.0.0.0/0` from Authorized External Networks and disable Public IP after testing is complete. For Cloud Run deployment, use the private IP with VPC egress instead.

**Step 3b: Enable Extensions (docs/alloydb.md — Codelab 3, "Task 1")**

In AlloyDB Studio (authenticate with postgres/your-password), run:

```sql
-- From docs/alloydb.md — "Enable extensions and permissions"
CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;
GRANT EXECUTE ON FUNCTION embedding TO postgres;
```

**Step 3c: Grant Vertex AI Role (docs/alloydb.md — Codelab 3, "Grant Vertex AI User role")**

In Cloud Console → IAM & Admin → IAM → Grant access:
- Principal: `service-PROJECT_NUMBER@gcp-sa-alloydb.iam.gserviceaccount.com`  
- Role: `Vertex AI User`

**Step 3d: Create Schema + Load Data**

Run `setup/setup_alloydb.sql` in AlloyDB Studio. This creates:
- `contacts` table — Personal CRM contacts
- `notes` table — Meeting notes with vector embeddings (768 dimensions, text-embedding-005)
- `tasks` table — Task management with status/priority

This is a **custom dataset** (not from any lab default) — satisfies Track 3 requirement.

**Step 3e: Test Vector Search (docs/alloydb.md — Codelab 3, "Task 4")**

Verify vector search works with a test query:

```sql
-- From docs/alloydb.md — "Perform Vector Search using text embeddings"
SELECT id, title, content FROM notes
ORDER BY content_embedding <=> embedding('text-embedding-005', 'product launch timeline')::vector
LIMIT 5;
```

### PHASE 4: Agent Code (from docs/adk.md — Codelab 2, Sections 7-8)

The agent code follows the exact zoo_guide_agent pattern from the codelab.

**File structure must be exactly:**
```
smartdesk_agent/
└── smartdesk_app/
    ├── __init__.py     # Contains: from . import agent
    ├── agent.py        # All agent definitions, root_agent is entry point
    ├── tools.py        # MCP toolsets + AlloyDB query functions
    └── .env            # Environment config (not committed to git)
```

**Key ADK patterns (from docs/adk.md — Codelab 2):**

1. **Imports** — follow exact import structure from zoo_guide_agent:
```python
import os
import logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
```

2. **State management via ToolContext** — save user input to state (docs/adk.md — "add_prompt_to_state"):
```python
def save_user_request(tool_context: ToolContext, request: str) -> dict[str, str]:
    """Saves the user's request to shared state."""
    tool_context.state["USER_REQUEST"] = request
    return {"status": "success"}
```

3. **Sub-agents with output_key** — pass data between agents (docs/adk.md — "Researcher Agent"):
```python
researcher = Agent(
    name="researcher",
    model=model_name,
    instruction="...\nPROMPT:\n{ PROMPT }\n",
    tools=[...],
    output_key="research_data"  # <-- This key is how data flows to next agent
)
```

4. **SequentialAgent workflow** — fixed pipeline (docs/adk.md — "tour_guide_workflow"):
```python
workflow = SequentialAgent(
    name="workflow",
    sub_agents=[researcher, formatter],  # Runs in order, shares state
)
```

5. **root_agent is the entry point** — ADK requires this variable name (docs/adk.md — "Assemble the main workflow"):
```python
root_agent = Agent(
    name="smartdesk",
    model=model_name,
    instruction="...",
    tools=[save_user_request],
    sub_agents=[inbox_agent, planner_agent, data_agent, response_formatter],
)
```

### PHASE 5: MCP Integration (from docs/mcp.md — Codelab 1 + Codelab 3)

**MCP Toolset pattern (docs/mcp.md — "MCP Toolset Initialization"):**

The Location Intelligence codelab shows the exact pattern for connecting to remote MCP servers:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

def get_gmail_mcp_toolset():
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://gmail-mcp-server-url",
            headers={"Authorization": f"Bearer {oauth_token}"},
            timeout=15,
        )
    )
    return tools
```

**How MCPToolset works (docs/mcp.md — "MCPToolset"):**
- Connection Management: establishes and manages connection to MCP server
- Tool Discovery: queries server for available tools via `list_tools`
- Exposure to Agent: converts MCP tools to ADK-compatible BaseTool instances
- Proxying: transparently proxies calls via `call_tool`
- Optional Filtering: use `tool_filter` to select specific tools

**For Google Maps MCP (if needed) — docs/mcp.md — Codelab 3:**
```python
MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": api_key}
        ),
        timeout=15,
    ),
)
```

**For BigQuery MCP (docs/mcp.md — Codelab 1):**
```python
def get_bigquery_mcp_toolset():
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    oauth_token = credentials.token

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "x-goog-user-project": project_id
            }
        )
    )
    return tools
```

### PHASE 6: AlloyDB Tools (from docs/alloydb.md — Codelab 2 + Codelab 3)

**Vector search in SQL (docs/alloydb.md — Codelab 3, "Task 4"):**
```sql
SELECT id, title, content FROM notes
ORDER BY content_embedding <=> embedding('text-embedding-005', :query)::vector
LIMIT 5;
```

**In-database embeddings on INSERT (docs/alloydb.md — Codelab 2, "Real-time In-Database Embeddings"):**
```sql
INSERT INTO notes (title, content, content_embedding)
VALUES (:title, :content, embedding('text-embedding-005', :content)::vector)
```

**The `<=>` operator** is cosine distance — lower = more similar.

### PHASE 7: Local Testing (from docs/adk.md — Codelab 1, Section 7-8)

```bash
# Terminal mode (docs/adk.md — "Run the agent on the Terminal")
cd smartdesk_agent
adk run smartdesk_app

# Web UI mode (docs/adk.md — "Run the agent on the Development Web UI")
cd smartdesk_agent
adk web
# Then open http://localhost:8000 or use Cloud Shell Web Preview on port 8000
```

### PHASE 8: Deploy to Cloud Run (from docs/adk.md — Codelab 2, Sections 9-10)

**Step 8a: Create Service Account (docs/adk.md — "Prepare the application for deployment"):**
```bash
source smartdesk_agent/smartdesk_app/.env

# Create service account
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="SmartDesk Service Account"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

**Step 8b: Deploy (docs/adk.md — "Deploy the agent using the ADK CLI"):**
```bash
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

**Step 8c: Test the deployment:**
```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe smartdesk-agent \
  --region=us-central1 --format='value(status.url)')
echo $SERVICE_URL

# Test with curl
curl -X POST $SERVICE_URL/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my pending tasks?"}'
```

### PHASE 9: Cleanup (from docs/adk.md — Codelab 2, "Clean up environment")

```bash
# Delete Cloud Run service
gcloud run services delete smartdesk-agent --region=us-central1 --quiet
gcloud artifacts repositories delete cloud-run-source-deploy --location=us-central1 --quiet

# Delete AlloyDB (if needed)
# Do this from Cloud Console → AlloyDB → Delete cluster
```

---

## File Reference

| File | What It Does | Based On |
|------|-------------|----------|
| `smartdesk_agent/smartdesk_app/__init__.py` | Package init: `from . import agent` | docs/adk.md — Codelab 1 |
| `smartdesk_agent/smartdesk_app/agent.py` | Agent definitions (root + sub-agents) | docs/adk.md — Codelab 2 (zoo_guide_agent) |
| `smartdesk_agent/smartdesk_app/tools.py` | MCP toolsets + AlloyDB query functions | docs/mcp.md + docs/alloydb.md |
| `smartdesk_agent/smartdesk_app/.env` | Environment config | docs/adk.md — Codelab 2 |
| `setup/setup_alloydb.sql` | Database schema + sample data | docs/alloydb.md — Codelab 2+3 |
| `requirements.txt` | Python dependencies | docs/adk.md — Codelab 2 |

## Key Rules

1. **`root_agent` variable name is mandatory** — ADK uses it as the entry point
2. **`__init__.py` must contain `from . import agent`** — this is how ADK discovers the agent
3. **Use `output_key` on sub-agents** to pass data through SequentialAgent pipelines
4. **Use `tool_context.state["KEY"]` for state** — not global variables
5. **MCPToolset handles everything** — connection, discovery, proxying, shutdown
6. **Vector search uses `<=>` operator** with `embedding()` function in SQL
7. **AlloyDB extensions must be enabled first** — `google_ml_integration` and `vector`
8. **Vertex AI User role** must be granted to both the AlloyDB service account AND the Cloud Run service account
9. **Never hardcode project IDs in code** — always use `os.getenv()` or `.env`
10. **The GCP Project ID is `smartdesk-492115`** — use this everywhere

## Docs Reference (ALWAYS check before coding)

- **`docs/adk.md`** — How to build agents, SequentialAgent, tools, state, deployment. Based on: Building AI Agents with ADK Foundation, Build & Deploy ADK Agent on Cloud Run, A2A SDK.
- **`docs/mcp.md`** — How to connect to MCP servers, MCPToolset, BigQuery/Maps examples, building custom MCP servers. Based on: Location Intelligence with BigQuery & Maps, MCP Toolbox for Databases, MCP Tools with ADK.
- **`docs/alloydb.md`** — How to set up AlloyDB, enable extensions, vector search, embeddings, natural language SQL, Gemini Flash integration. Based on: AlloyDB Quick Setup, Surplus Engine with Gemini 3 Flash, Configure Vector Search.
