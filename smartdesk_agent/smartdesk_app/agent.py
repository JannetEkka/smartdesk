# SmartDesk — Multi-Agent Productivity Assistant
# Follows docs/adk.md — Codelab 2 (zoo_guide_agent) patterns exactly
# Structure: root_agent → sub-agents with output_key → SequentialAgent formatter

import os
import logging
import warnings
from dotenv import load_dotenv

# Suppress noisy warnings before importing SDKs
warnings.filterwarnings("ignore", message=".*non-text parts in the response.*")
warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*")
warnings.filterwarnings("ignore", message=".*google-cloud-storage < 3\\.0\\.0.*")
logging.getLogger("opentelemetry.attributes").setLevel(logging.ERROR)

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from . import tools

# --- Setup Logging and Environment ---
# Pattern from docs/adk.md — Codelab 2, "Imports and Initial Setup"

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")


# --- State Management Tool ---
# Pattern from docs/adk.md — Codelab 2, "add_prompt_to_state"

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}


# --- Sub-Agent 1: InboxAgent (Gmail via MCP) ---
# Tools from docs/mcp.md — Codelab 3, StdioConnectionParams with custom MCP server

gmail_toolset = tools.get_gmail_mcp_toolset()

inbox_agent = Agent(
    name="inbox_agent",
    model=model_name,
    description="Handles email tasks via Gmail. ONLY transfer here AFTER check_login_status confirms logged_in=true.",
    instruction="""
    You are the email assistant for SmartDesk. Use the Gmail MCP tools to help users
    manage their inbox.

    CAPABILITIES:
    - **list_emails**: List recent inbox emails with subject, sender, and snippet.
    - **search_emails**: Search emails using Gmail query syntax (e.g., "from:alice subject:meeting").
    - **read_email**: Read the full content of a specific email by message ID.
    - **draft_email**: Create a draft email with recipient, subject, and body.

    GUIDELINES:
    - For inbox summaries, group by priority: urgent/action-needed first, FYI second.
    - Include sender name, subject, and a one-line summary for each email.
    - When drafting replies, first read the original email, then confirm the draft content.
    - Use search_emails for targeted lookups (e.g., "from:priya", "subject:launch").
    - Use **bold** for names, dates, and action items. Use bullet points for lists.
    """,
    tools=[gmail_toolset],
    output_key="inbox_data",
)


# --- Sub-Agent 2: PlannerAgent (Google Calendar via MCP) ---
# Tools from docs/mcp.md — Codelab 3, StdioConnectionParams with custom MCP server

calendar_toolset = tools.get_calendar_mcp_toolset()

planner_agent = Agent(
    name="planner_agent",
    model=model_name,
    description="Handles calendar and scheduling tasks. ONLY transfer here AFTER check_login_status confirms logged_in=true.",
    instruction="""
    You are the scheduling assistant for SmartDesk. Use the Calendar MCP tools to help
    users manage their Google Calendar.

    CAPABILITIES:
    - **list_events**: List today's or upcoming events (set days_ahead for range).
    - **search_events**: Search events by keyword in title/description.
    - **get_event**: Get full details of a specific event by ID.
    - **create_event**: Create a new event with time, attendees, and location.
    - **find_free_time**: Find available time slots on a specific date.

    GUIDELINES:
    - Always include the day of week, date, and time in responses (e.g., "Monday, April 7 at 2:00 PM").
    - Flag conflicts or back-to-back meetings proactively.
    - When booking, use find_free_time first, then confirm the slot before creating.
    - Use ISO 8601 format for times (e.g., "2026-04-07T14:00:00").
    - Use **bold** for names, dates, and action items. Use bullet points for lists.
    """,
    tools=[calendar_toolset],
    output_key="planner_data",
)


# --- Sub-Agent 3: DataAgent (AlloyDB with vector search) ---
# Tools from docs/alloydb.md — Codelab 3, vector search with embedding()

data_agent = Agent(
    name="data_agent",
    model=model_name,
    description="Handles personal knowledge base queries: contacts, notes, tasks stored in AlloyDB with vector search.",
    instruction="""
    You are the knowledge base assistant for SmartDesk. You manage the user's personal CRM data
    stored in AlloyDB, including contacts, meeting notes, and tasks.

    CAPABILITIES:
    - **search_notes**: Semantic search over meeting notes. Use natural phrases like
      "product launch timeline" or "AI architecture discussion" — the vector search handles relevance.
    - **get_contacts**: Look up people by name, email, or company.
    - **get_tasks**: List tasks by status. Valid statuses: pending, in_progress, done.
    - **update_task**: Mark a task done, change priority, or move to in_progress. Requires the task ID.
    - **add_note**: Save a new meeting note or insight.
    - **add_task**: Create a new task with title, description, priority (high/medium/low), and optional due_date (YYYY-MM-DD).

    GUIDELINES:
    - When asked about past discussions, always use search_notes with a descriptive query.
    - When asked "what's on my plate" or similar, fetch pending tasks AND in_progress tasks.
    - When updating a task, first fetch tasks to find the correct ID, then call update_task.
    - Present results clearly: include names, dates, and key details.
    - Use **bold** for names, dates, and action items. Use bullet points for lists.
    """,
    tools=[
        tools.search_notes,
        tools.get_contacts,
        tools.get_tasks,
        tools.add_note,
        tools.add_task,
        tools.update_task,
    ],
    output_key="knowledge_data",
)


# --- Callbacks: auth URL injection + anti-reprocessing ---

def _before_model(callback_context: CallbackContext, llm_request):
    """Inject auth URL directly if pending — model never sees it."""
    url = callback_context.state.get("_pending_auth_url")
    if url:
        callback_context.state["_pending_auth_url"] = None
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=(
                    f"Please sign in: {url} "
                    "— after approving, copy the full URL from your browser and paste it here."
                ))],
            )
        )
    return None


def _after_model(callback_context: CallbackContext, llm_response: LlmResponse):
    """After a sub-agent has returned output, strip function_calls from the root
    agent's response to prevent re-processing (calling check_login_status,
    add_prompt_to_state, transfer again). The sub-agent's output_key data in
    state is the signal that a sub-agent has completed."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    # Check if any sub-agent has already produced output for this session
    sub_agent_done = any(
        callback_context.state.get(key)
        for key in ("inbox_data", "planner_data", "knowledge_data")
    )
    if not sub_agent_done:
        return None  # No sub-agent output yet — let everything through

    # Sub-agent completed. Strip function_calls to prevent re-processing.
    has_function_call = any(
        p.function_call for p in llm_response.content.parts
    )
    if has_function_call:
        text_parts = [p for p in llm_response.content.parts if p.text]
        llm_response.content.parts = text_parts if text_parts else [types.Part(text="")]
    return None


# --- Root Agent (Orchestrator) ---
# Pattern from docs/adk.md — Codelab 2, "Assemble the main workflow"
# root_agent is the ADK entry point — this variable name is mandatory

root_agent = Agent(
    name="smartdesk",
    model=model_name,
    description="SmartDesk — your personal productivity assistant for emails, calendar, and knowledge management.",
    instruction="""
    You are SmartDesk, a personal productivity assistant.

    IMPORTANT — NEVER RE-PROCESS:
    If a sub-agent (inbox_agent, planner_agent, data_agent) has already returned
    data for the current request, DO NOT call any more tools or transfer again.
    Just present the sub-agent's response to the user. Never call check_login_status,
    add_prompt_to_state, or transfer_to_agent a second time for the same request.

    STEP 1 — CLASSIFY the user's request:
    A) "switch account", "relogin", "re log in", "log out", "change account" → Call switch_account ONCE.
    B) "log in", "sign in" → Go to STEP 2.
    C) Emails, inbox, Gmail → Go to STEP 2.
    D) Calendar, schedule, meetings, events → Go to STEP 2.
    E) Notes, contacts, tasks, knowledge base → Skip auth. Go to STEP 3 with data_agent.
    F) General greeting or question → Respond directly. Do NOT transfer anywhere.
    G) User pasted a URL containing "localhost" → Call complete_google_login with that URL, then proceed with their original request.

    STEP 2 — AUTHENTICATE (you handle this, do NOT transfer yet):
    1. Call check_login_status.
    2. If logged_in is true → Go to STEP 3.
    3. If logged_in is false → Call login_google ONCE.
    4. After login_google or switch_account returns, STOP. Wait for the user.

    STEP 3 — ROUTE (only after auth is confirmed for email/calendar):
    1. Call add_prompt_to_state with the user's request.
    2. Transfer to the correct sub-agent:
       - inbox_agent → emails
       - planner_agent → calendar/scheduling
       - data_agent → notes, contacts, tasks
    3. Once a sub-agent returns, STOP. Present its response directly. Do NOT re-route or call more tools.
    """,
    tools=[
        add_prompt_to_state,
        tools.login_google,
        tools.complete_google_login,
        tools.check_login_status,
        tools.switch_account,
    ],
    sub_agents=[inbox_agent, planner_agent, data_agent],
    before_model_callback=_before_model,
    after_model_callback=_after_model,
)
