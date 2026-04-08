# SmartDesk — Multi-Agent Productivity Assistant
# Follows docs/adk.md — Codelab 2 (zoo_guide_agent) patterns exactly
# Structure: root_agent → sub-agents with output_key

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

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")


# --- State Management Tool ---

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state. Only call ONCE per user message."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}


# --- Sub-Agent 1: InboxAgent (Gmail via MCP) ---

gmail_toolset = tools.get_gmail_mcp_toolset()

inbox_agent = Agent(
    name="inbox_agent",
    model=model_name,
    description="Handles email tasks via Gmail. ONLY transfer here AFTER check_login_status confirms logged_in=true.",
    instruction="""You are the email assistant for SmartDesk. Use the Gmail MCP tools to help users manage their inbox.

IMPORTANT: Call each tool ONLY ONCE per request. Once you have the data, format and return it immediately.

CAPABILITIES:
- **list_emails**: List recent inbox emails with subject, sender, and snippet.
- **search_emails**: Search emails using Gmail query syntax (e.g., "from:alice subject:meeting").
- **read_email**: Read the full content of a specific email by message ID.
- **draft_email**: Create a draft email with recipient, subject, and body.

GUIDELINES:
- For inbox summaries, group by priority: urgent/action-needed first, FYI second.
- Include sender name, subject, and a one-line summary for each email.
- Use **bold** for names, dates, and action items. Use bullet points for lists.
""",
    tools=[gmail_toolset],
    output_key="inbox_data",
)


# --- Sub-Agent 2: PlannerAgent (Google Calendar via MCP) ---

calendar_toolset = tools.get_calendar_mcp_toolset()

planner_agent = Agent(
    name="planner_agent",
    model=model_name,
    description="Handles calendar and scheduling tasks. ONLY transfer here AFTER check_login_status confirms logged_in=true.",
    instruction="""You are the scheduling assistant for SmartDesk. Use the Calendar MCP tools to help users manage their Google Calendar.

IMPORTANT: Call each tool ONLY ONCE per request. Once you have the data, format and return it immediately.

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

data_agent = Agent(
    name="data_agent",
    model=model_name,
    description="Handles personal knowledge base queries: contacts, notes, tasks stored in AlloyDB with vector search.",
    instruction="""You are the knowledge base assistant for SmartDesk. You manage the user's personal CRM data stored in AlloyDB, including contacts, meeting notes, and tasks.

IMPORTANT: Call each tool ONLY ONCE per request. Once you have the data, format and return it immediately.

CAPABILITIES:
- **search_notes**: Semantic search over meeting notes using vector similarity.
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
#
# How the anti-reprocessing works:
#   _after_model detects transfer_to_agent → sets _transferred = True
#   Sub-agent runs to completion
#   Control returns to root_agent → _before_model fires
#   _before_model sees _transferred = True → blocks the LLM loop, resets flag
#   Next user message: flag is False, so the LLM runs normally

def _before_model(callback_context: CallbackContext, llm_request):
    """Inject auth URL if pending; block re-processing after sub-agent transfer."""

    # 1. Auth URL injection — show sign-in link without the LLM seeing the raw URL
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

    # 2. Anti-reprocessing — if a sub-agent already handled this request,
    #    stop the LLM loop so we don't duplicate the response.
    if callback_context.state.get("_transferred"):
        callback_context.state["_transferred"] = False  # Reset for next user message
        logging.info("[Callback] Sub-agent already handled this request — stopping LLM loop")
        return LlmResponse(content=None)

    return None


def _after_model(callback_context: CallbackContext, llm_response: LlmResponse):
    """Track transfer_to_agent calls so _before_model can block re-processing."""
    if not llm_response.content or not llm_response.content.parts:
        return None

    for part in llm_response.content.parts:
        if part.function_call and part.function_call.name == "transfer_to_agent":
            callback_context.state["_transferred"] = True
            logging.info("[Callback] transfer_to_agent detected — will block re-processing after sub-agent completes")
            break

    return None


# --- Root Agent (Orchestrator) ---
# root_agent is the ADK entry point — this variable name is mandatory

root_agent = Agent(
    name="smartdesk",
    model=model_name,
    description="SmartDesk — your personal productivity assistant for emails, calendar, and knowledge management.",
    instruction="""You are SmartDesk, a personal productivity assistant.

STEP 1 — CLASSIFY the user's request:
A) "switch account", "relogin", "re log in", "log out", "change account" → Call switch_account. Say NOTHING else.
B) "log in", "sign in" → Go to STEP 2.
C) Emails, inbox, Gmail → Go to STEP 2.
D) Calendar, schedule, meetings, events → Go to STEP 2.
E) Notes, contacts, tasks, knowledge base → Skip auth. Go to STEP 3 with data_agent.
F) General greeting or question → Respond directly. Do NOT transfer anywhere.
G) User pasted a URL containing "localhost" → Call complete_google_login with that URL, then proceed.

STEP 2 — AUTHENTICATE (do NOT transfer yet):
1. Call check_login_status.
2. If logged_in is true → Go to STEP 3.
3. If logged_in is false → Call login_google. Then STOP. Wait for the user.

STEP 3 — ROUTE:
1. Call add_prompt_to_state with the user's request.
2. Transfer to the correct sub-agent:
   - inbox_agent → emails
   - planner_agent → calendar/scheduling
   - data_agent → notes, contacts, tasks
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
