# SmartDesk — Tools & MCP Toolset Configuration
# Follows patterns from docs/mcp.md (BigQuery MCP) and docs/alloydb.md (direct connection)

import os
import logging
from dotenv import load_dotenv

import google.auth
import google.auth.transport.requests

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext

import sqlalchemy
from datetime import date, datetime

load_dotenv()


# =============================================================================
# MCP Toolsets (Track 2 — Model Context Protocol)
# Follows docs/mcp.md — Codelab 1, "MCP Toolset Initialization"
# Uses OAuth Bearer token pattern from get_bigquery_mcp_toolset()
# =============================================================================

def _get_oauth_token():
    """Get OAuth token using application default credentials.
    Pattern from docs/mcp.md — Codelab 1, get_bigquery_mcp_toolset()."""
    credentials, project_id = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token, project_id


def get_gmail_mcp_toolset():
    """Configure MCP toolset for Gmail integration.
    Pattern from docs/mcp.md — StreamableHTTPConnectionParams with OAuth."""
    gmail_mcp_url = os.getenv("GMAIL_MCP_URL", "")
    if not gmail_mcp_url:
        logging.warning("GMAIL_MCP_URL not set — Gmail tools will not be available.")
        return []

    oauth_token, project_id = _get_oauth_token()

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=gmail_mcp_url,
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "x-goog-user-project": project_id,
            },
            timeout=15,
        )
    )
    logging.info("Gmail MCP Toolset configured.")
    return tools


def get_calendar_mcp_toolset():
    """Configure MCP toolset for Google Calendar integration.
    Pattern from docs/mcp.md — StreamableHTTPConnectionParams with OAuth."""
    calendar_mcp_url = os.getenv("CALENDAR_MCP_URL", "")
    if not calendar_mcp_url:
        logging.warning("CALENDAR_MCP_URL not set — Calendar tools will not be available.")
        return []

    oauth_token, project_id = _get_oauth_token()

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=calendar_mcp_url,
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "x-goog-user-project": project_id,
            },
            timeout=15,
        )
    )
    logging.info("Calendar MCP Toolset configured.")
    return tools


# =============================================================================
# AlloyDB Connection (Track 3 — AI-ready databases)
# Follows docs/alloydb.md — Codelab 2, direct pg8000 connection
# Pattern: postgresql+pg8000://postgres:password@host:port/postgres
# =============================================================================

_engine = None


def _get_db_engine():
    """Create or return cached SQLAlchemy engine with direct pg8000 connection.
    Pattern from docs/alloydb.md — Codelab 2, DATABASE_URL approach."""
    global _engine
    if _engine is not None:
        return _engine

    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        _engine = sqlalchemy.create_engine(db_url)
    else:
        # Fallback: build URL from individual env vars
        user = os.getenv("ALLOYDB_USER", "postgres")
        password = os.getenv("ALLOYDB_PASSWORD", "")
        host = os.getenv("ALLOYDB_IP", "127.0.0.1")
        port = os.getenv("ALLOYDB_PORT", "5432")
        db = os.getenv("ALLOYDB_DB", "postgres")
        _engine = sqlalchemy.create_engine(
            f"postgresql+pg8000://{user}:{password}@{host}:{port}/{db}"
        )
    return _engine


def _serialize_value(val):
    """Convert non-JSON-serializable types to strings."""
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val


def _query_db(sql: str, params: dict = None) -> list[dict]:
    """Execute a SQL query and return results as list of dicts."""
    engine = _get_db_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql), params or {})
            columns = result.keys()
            return [
                {col: _serialize_value(val) for col, val in zip(columns, row)}
                for row in result.fetchall()
            ]
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return [{"error": str(e)}]


# =============================================================================
# AlloyDB Tools (exposed to DataAgent)
# Follows docs/alloydb.md — Codelab 3, vector search with embedding()
# =============================================================================

def search_notes(tool_context: ToolContext, query: str) -> list[dict]:
    """Search meeting notes using vector similarity.
    Uses embedding() and <=> operator from docs/alloydb.md — Codelab 3, Task 4."""
    sql = """
    SELECT id, title, content, created_at,
           1 - (content_embedding <=> embedding('text-embedding-005', :query)::vector) AS similarity
    FROM notes
    ORDER BY content_embedding <=> embedding('text-embedding-005', :query)::vector
    LIMIT 5;
    """
    results = _query_db(sql, {"query": query})
    logging.info(f"[search_notes] Found {len(results)} results for: {query}")
    return results


def get_contacts(tool_context: ToolContext, search_term: str) -> list[dict]:
    """Look up contacts by name, email, or company."""
    sql = """
    SELECT id, name, email, phone, company, role, notes
    FROM contacts
    WHERE name ILIKE :term OR email ILIKE :term OR company ILIKE :term
    LIMIT 10;
    """
    results = _query_db(sql, {"term": f"%{search_term}%"})
    logging.info(f"[get_contacts] Found {len(results)} contacts for: {search_term}")
    return results


def get_tasks(tool_context: ToolContext, status: str = "pending") -> list[dict]:
    """Get tasks filtered by status (pending, in_progress, done)."""
    sql = """
    SELECT id, title, description, status, priority, due_date, created_at
    FROM tasks
    WHERE status = :status
    ORDER BY
        CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        due_date ASC
    LIMIT 20;
    """
    results = _query_db(sql, {"status": status})
    logging.info(f"[get_tasks] Found {len(results)} tasks with status: {status}")
    return results


def add_note(tool_context: ToolContext, title: str, content: str) -> dict:
    """Add a new note with auto-generated vector embedding.
    Uses in-database embeddings from docs/alloydb.md — Codelab 2."""
    sql = """
    INSERT INTO notes (title, content, content_embedding)
    VALUES (:title, :content, embedding('text-embedding-005', :content)::vector)
    RETURNING id, title, created_at;
    """
    results = _query_db(sql, {"title": title, "content": content})
    logging.info(f"[add_note] Created note: {title}")
    return results[0] if results else {"error": "Failed to create note"}


def add_task(
    tool_context: ToolContext,
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = "",
) -> dict:
    """Add a new task to the task list."""
    sql = """
    INSERT INTO tasks (title, description, priority, due_date)
    VALUES (:title, :description, :priority, :due_date)
    RETURNING id, title, status, priority, due_date;
    """
    results = _query_db(sql, {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_date if due_date else None,
    })
    logging.info(f"[add_task] Created task: {title}")
    return results[0] if results else {"error": "Failed to create task"}


def update_task(
    tool_context: ToolContext,
    task_id: int,
    status: str = "",
    priority: str = "",
) -> dict:
    """Update a task's status or priority.
    Status options: pending, in_progress, done.
    Priority options: high, medium, low."""
    updates = []
    params = {"task_id": task_id}
    if status:
        updates.append("status = :status")
        params["status"] = status
    if priority:
        updates.append("priority = :priority")
        params["priority"] = priority
    if not updates:
        return {"error": "Provide at least one of status or priority to update."}

    sql = f"""
    UPDATE tasks SET {', '.join(updates)}
    WHERE id = :task_id
    RETURNING id, title, status, priority, due_date;
    """
    results = _query_db(sql, params)
    logging.info(f"[update_task] Updated task {task_id}: {params}")
    return results[0] if results else {"error": f"Task {task_id} not found"}
