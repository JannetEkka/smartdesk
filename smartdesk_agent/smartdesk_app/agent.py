# SmartDesk — Multi-Agent Productivity Assistant
# Follows docs/adk.md — Codelab 2 (zoo_guide_agent) patterns exactly
# Structure: root_agent → sub-agents with output_key → SequentialAgent formatter

import os
import logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

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
    description="Handles email tasks: reading, searching, summarizing, and drafting emails via Gmail.",
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
    description="Handles calendar and scheduling tasks: checking schedule, finding conflicts, booking meetings.",
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


# --- Response Formatter Agent ---
# Pattern from docs/adk.md — Codelab 2, "Response Formatter Agent"

response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all gathered information into a clear, friendly response.",
    instruction="""
    You are the friendly voice of SmartDesk. Synthesize the gathered data into a
    clear, actionable response.

    DATA SOURCES (use whichever is present):
    - **inbox_data**: Email summaries, search results, draft confirmations
    - **planner_data**: Schedule details, conflicts, booking confirmations
    - **knowledge_data**: Contact info, meeting notes, task lists, task updates

    FORMATTING RULES:
    - Lead with the most important information.
    - Use **bold** for names, dates, and action items.
    - Use bullet points for lists of 3+ items.
    - Add section headers (##) only when combining data from multiple sources.
    - Flag overdue tasks or urgent items with a clear call-out.
    - Keep responses concise — no filler, no restating the question.
    """,
)


# --- Root Agent (Orchestrator) ---
# Pattern from docs/adk.md — Codelab 2, "Assemble the main workflow"
# root_agent is the ADK entry point — this variable name is mandatory

root_agent = Agent(
    name="smartdesk",
    model=model_name,
    description="SmartDesk — your personal productivity assistant for emails, calendar, and knowledge management.",
    instruction="""
    You are SmartDesk, a personal productivity assistant.

    AUTHENTICATION (email/calendar only — data_agent does NOT need login):
    1. Call check_login_status first.
    2. If not logged in, call login_google ONCE. It returns an auth_url.
    3. Respond with EXACTLY this (replacing [URL] with the auth_url) and NOTHING ELSE:
       "Please sign in: [URL] — after approving, copy the URL from your browser and paste it here."
    4. STOP. Do NOT call any more tools. Wait for the user's next message.
    5. When the user pastes a URL with "localhost", call complete_google_login with it.

    ROUTING (after auth):
    - Call add_prompt_to_state, then transfer to the right sub-agent:
      inbox_agent (emails), planner_agent (calendar), data_agent (notes/contacts/tasks).
    - For multi-domain requests, route to each sub-agent in turn.
    - Transfer to response_formatter for the final answer.
    """,
    tools=[
        add_prompt_to_state,
        tools.login_google,
        tools.complete_google_login,
        tools.check_login_status,
    ],
    sub_agents=[inbox_agent, planner_agent, data_agent, response_formatter],
)
