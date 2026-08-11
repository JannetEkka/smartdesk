# SmartDesk — Tools & MCP Toolset Configuration
# MCP: follows docs/mcp.md — Codelab 3, StdioConnectionParams with custom MCP servers
# AlloyDB: follows docs/alloydb.md — Codelab 2+3, direct pg8000 connection

import os
import sys
import logging
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress noisy SDK warnings early
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")
logging.getLogger("opentelemetry.attributes").setLevel(logging.ERROR)

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.tool_context import ToolContext

import sqlalchemy
from datetime import date, datetime

load_dotenv()

# Resolve paths to our custom MCP server scripts
_MCP_SERVERS_DIR = Path(__file__).parent / "mcp_servers"
_GMAIL_SERVER = str(_MCP_SERVERS_DIR / "gmail_server.py")
_CALENDAR_SERVER = str(_MCP_SERVERS_DIR / "calendar_server.py")


# =============================================================================
# MCP Toolsets (Track 2 — Model Context Protocol)
# Follows docs/mcp.md — Codelab 3, "Build an MCP server with ADK tools"
# Uses StdioConnectionParams to connect to self-hosted MCP server scripts
# =============================================================================

def get_gmail_mcp_toolset():
    """Configure MCP toolset for Gmail via self-hosted MCP server.
    Pattern from docs/mcp.md — Codelab 3, StdioConnectionParams + StdioServerParameters."""
    tools = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[_GMAIL_SERVER],
            ),
            timeout=60,
        ),
    )
    logging.info("Gmail MCP Toolset configured (stdio).")
    return tools


def get_calendar_mcp_toolset():
    """Configure MCP toolset for Google Calendar via self-hosted MCP server.
    Pattern from docs/mcp.md — Codelab 3, StdioConnectionParams + StdioServerParameters."""
    tools = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[_CALENDAR_SERVER],
            ),
            timeout=60,
        ),
    )
    logging.info("Calendar MCP Toolset configured (stdio).")
    return tools


# =============================================================================
# Google Account Login Tools (per-user OAuth)
# Lets each user authenticate with their own Google account via the chat.
# =============================================================================

# Import auth helpers from the MCP servers package
sys.path.insert(0, str(_MCP_SERVERS_DIR))
from auth import generate_auth_url, exchange_auth_code, is_logged_in, logout


def login_google(tool_context: ToolContext) -> dict:
    """Start Google login. Generates auth URL and stores it for display."""
    if tool_context.state.get("_auth_url_shown"):
        return {"status": "already_shown"}
    result = generate_auth_url()
    if "error" in result:
        return result
    tool_context.state["_pending_auth_url"] = result.get("auth_url", "")
    tool_context.state["_auth_url_shown"] = True
    return {"status": "url_ready"}


def complete_google_login(tool_context: ToolContext, redirect_url: str) -> dict:
    """Complete Google login. The user pastes the full redirect URL from their
    browser after approving access. This finishes the sign-in process."""
    if tool_context.state.get("_auth_completed"):
        return {"status": "already_completed", "message": "Login was already completed. You can now use Gmail and Calendar features."}
    result = exchange_auth_code(redirect_url)
    if result.get("status") == "success":
        tool_context.state["_auth_completed"] = True
        tool_context.state["_auth_url_shown"] = False
        tool_context.state["_pending_auth_url"] = None
    return result


def check_login_status(tool_context: ToolContext) -> dict:
    """Check if a user is currently logged in to Google."""
    return is_logged_in()


def switch_account(tool_context: ToolContext) -> dict:
    """Switch Google account: logs out and generates a new sign-in URL."""
    if tool_context.state.get("_auth_url_shown"):
        return {"status": "already_shown"}
    logout()
    result = generate_auth_url()
    if "error" in result:
        return result
    tool_context.state["_pending_auth_url"] = result.get("auth_url", "")
    tool_context.state["_auth_url_shown"] = True
    tool_context.state["_auth_completed"] = False
    return {"status": "url_ready"}


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

# Retrieval mode, selected with SMARTDESK_RETRIEVAL:
#   baseline  whole-note vector search (default — matches the original tool)
#   chunked   chunk-level search collapsed back to parent notes
#   hybrid    fuses whole-note, chunk, and lexical rankings
#
# The default is deliberately the original behaviour. On the eval set no
# alternative beat it by a statistically significant margin, so promoting one
# to default is not justified by the evidence. See evals/RESULTS.md.
_RETRIEVAL_MODE = os.getenv("SMARTDESK_RETRIEVAL", "baseline").lower()

_SEARCH_LIMIT = int(os.getenv("SMARTDESK_SEARCH_LIMIT", "5"))

#: Candidates fetched before fusion in hybrid mode.
_HYBRID_CANDIDATES = int(os.getenv("SMARTDESK_HYBRID_CANDIDATES", "25"))


def search_notes(tool_context: ToolContext, query: str) -> list[dict]:
    """Search meeting notes using vector similarity.

    Embeddings are computed client-side and passed as a bound parameter rather
    than through AlloyDB's in-database embedding() function, so the same query
    runs on AlloyDB and on stock Postgres with pgvector. The <=> cosine
    distance operator is identical on both.

    Retrieval mode comes from SMARTDESK_RETRIEVAL; see evals/RESULTS.md for
    the measurements behind the default.
    """
    from .rag import rerankers
    from .rag.retrieval import retrieve_chunks, retrieve_notes

    try:
        if _RETRIEVAL_MODE == "hybrid":
            notes = retrieve_notes(query, k=_HYBRID_CANDIDATES)
            chunks = retrieve_chunks(query, k=_HYBRID_CANDIDATES)
            hits = rerankers.HybridFusionReranker().fuse(
                query, notes, chunks, top_k=_SEARCH_LIMIT
            )
        elif _RETRIEVAL_MODE == "chunked":
            hits = retrieve_chunks(query, k=_SEARCH_LIMIT)
        else:
            hits = retrieve_notes(query, k=_SEARCH_LIMIT)
    except Exception as e:
        logging.error(f"[search_notes] Retrieval failed: {e}")
        return [{"error": str(e)}]

    logging.info(
        f"[search_notes] mode={_RETRIEVAL_MODE} found {len(hits)} results for: {query}"
    )
    return [hit.to_dict() for hit in hits]


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

    Writes the whole-note embedding and, when the note_chunks table exists,
    the note's chunks too. Keeping both indexes current on write is what lets
    SMARTDESK_RETRIEVAL be switched without a re-ingest.
    """
    from .rag.chunking import chunk_text
    from .rag.embeddings import get_embedder, to_pgvector

    embedder = get_embedder()
    body = f"{title}\n{content}"

    try:
        note_vec = embedder.embed_documents([body])[0]
    except Exception as e:
        logging.error(f"[add_note] Embedding failed: {e}")
        return {"error": f"Could not embed note: {e}"}

    results = _query_db(
        """
        INSERT INTO notes (title, content, content_embedding)
        VALUES (:title, :content, CAST(:vec AS vector))
        RETURNING id, title, created_at;
        """,
        {"title": title, "content": content, "vec": to_pgvector(note_vec)},
    )
    if not results or "error" in results[0]:
        return results[0] if results else {"error": "Failed to create note"}

    note_id = results[0]["id"]
    try:
        chunks = chunk_text(body)
        if chunks:
            vectors = embedder.embed_documents([c.text for c in chunks])
            for chunk, vec in zip(chunks, vectors):
                _query_db(
                    """
                    INSERT INTO note_chunks
                        (note_id, chunk_index, content, token_count, content_embedding)
                    VALUES (:note_id, :idx, :content, :tokens, CAST(:vec AS vector))
                    ON CONFLICT (note_id, chunk_index) DO UPDATE
                      SET content = EXCLUDED.content,
                          token_count = EXCLUDED.token_count,
                          content_embedding = EXCLUDED.content_embedding;
                    """,
                    {
                        "note_id": note_id,
                        "idx": chunk.index,
                        "content": chunk.text,
                        "tokens": chunk.token_count,
                        "vec": to_pgvector(vec),
                    },
                )
    except Exception as e:
        # The note itself is saved; a missing chunks table only means the
        # chunked and hybrid retrieval modes are unavailable.
        logging.warning(f"[add_note] Chunk indexing skipped for note {note_id}: {e}")

    logging.info(f"[add_note] Created note: {title}")
    return results[0]


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
