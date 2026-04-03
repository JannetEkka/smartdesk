# SmartDesk — Tools & MCP Toolset Configuration
# Connects sub-agents to Gmail MCP, Calendar MCP, and AlloyDB

import os
import logging
from dotenv import load_dotenv

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext

import sqlalchemy
from google.cloud.alloydb.connector import Connector

load_dotenv()


# =============================================================================
# MCP Toolsets (Track 2 — Model Context Protocol)
# =============================================================================

def get_gmail_mcp_toolset():
    """Configure MCP toolset for Gmail integration."""
    # TODO: Replace with actual Gmail MCP server URL once available
    # For hackathon, this uses the Google-hosted Gmail MCP server
    gmail_mcp_url = os.getenv("GMAIL_MCP_URL", "https://gmail.mcp.claude.com/mcp")

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=gmail_mcp_url,
            timeout=15,
        )
    )
    logging.info("Gmail MCP Toolset configured.")
    return tools


def get_calendar_mcp_toolset():
    """Configure MCP toolset for Google Calendar integration."""
    # TODO: Replace with actual Calendar MCP server URL once available
    calendar_mcp_url = os.getenv("CALENDAR_MCP_URL", "https://gcal.mcp.claude.com/mcp")

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=calendar_mcp_url,
            timeout=15,
        )
    )
    logging.info("Calendar MCP Toolset configured.")
    return tools


# =============================================================================
# AlloyDB Connection (Track 3 — AI-ready databases)
# =============================================================================

def _get_db_engine():
    """Create SQLAlchemy engine connected to AlloyDB."""
    connector = Connector()

    def getconn():
        return connector.connect(
            instance_uri=os.getenv("ALLOYDB_INSTANCE_URI", ""),
            driver="pg8000",
            user=os.getenv("ALLOYDB_USER", "postgres"),
            password=os.getenv("ALLOYDB_PASSWORD", ""),
            db=os.getenv("ALLOYDB_DB", "postgres"),
        )

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine


def _query_db(sql: str, params: dict = None) -> list[dict]:
    """Execute a SQL query and return results as list of dicts."""
    engine = _get_db_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(sql), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return [{"error": str(e)}]


# =============================================================================
# AlloyDB Tools (exposed to DataAgent)
# =============================================================================

def search_notes(tool_context: ToolContext, query: str) -> list[dict]:
    """Search meeting notes and documents using vector similarity in AlloyDB.
    Uses text-embedding-005 to find semantically similar notes."""
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
    """Add a new note to the knowledge base with auto-generated vector embedding."""
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
    due_date: str = None,
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
        "due_date": due_date,
    })
    logging.info(f"[add_task] Created task: {title}")
    return results[0] if results else {"error": "Failed to create task"}
