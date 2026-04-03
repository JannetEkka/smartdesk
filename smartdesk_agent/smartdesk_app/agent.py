# SmartDesk — Multi-Agent Productivity Assistant
# Follows docs/adk.md — Codelab 2 (zoo_guide_agent) patterns exactly
# Structure: root_agent → sub-agents with output_key → SequentialAgent formatter

import os
import logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

import google.auth
import google.auth.transport.requests

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
# Tools from docs/mcp.md — StreamableHTTPConnectionParams with OAuth

gmail_toolset = tools.get_gmail_mcp_toolset()

inbox_agent = Agent(
    name="inbox_agent",
    model=model_name,
    description="Handles email tasks: reading, searching, summarizing, and drafting emails via Gmail.",
    instruction="""
    You are the email assistant for SmartDesk. You help users manage their Gmail inbox.
    You can:
    - Search and read emails
    - Summarize unread emails
    - Draft reply emails
    - Find emails from specific contacts

    Use the Gmail MCP tools available to you to complete these tasks.
    Always provide concise, actionable summaries.

    PROMPT:
    { PROMPT }
    """,
    tools=[gmail_toolset] if gmail_toolset else [],
    output_key="inbox_data",
)


# --- Sub-Agent 2: PlannerAgent (Google Calendar via MCP) ---

calendar_toolset = tools.get_calendar_mcp_toolset()

planner_agent = Agent(
    name="planner_agent",
    model=model_name,
    description="Handles calendar and scheduling tasks: checking schedule, finding conflicts, booking meetings.",
    instruction="""
    You are the scheduling assistant for SmartDesk. You help users manage their Google Calendar.
    You can:
    - Check today's or upcoming schedule
    - Find meeting conflicts
    - Get meeting details (attendees, location, agenda)
    - Suggest available time slots

    Use the Google Calendar MCP tools available to you.
    Always mention specific times and dates clearly.

    PROMPT:
    { PROMPT }
    """,
    tools=[calendar_toolset] if calendar_toolset else [],
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
    You can:
    - Search notes semantically (e.g., "what did we discuss about the product launch?")
    - Look up contact information
    - Query and update tasks
    - Add new notes and tasks

    Use the database tools available to you.

    PROMPT:
    { PROMPT }
    """,
    tools=[
        tools.search_notes,
        tools.get_contacts,
        tools.get_tasks,
        tools.add_note,
        tools.add_task,
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
    You are the friendly voice of SmartDesk. Your task is to take the gathered data
    and present it to the user in a complete and helpful answer.

    Available data (use whichever is present):
    - INBOX_DATA: { inbox_data }
    - PLANNER_DATA: { planner_data }
    - KNOWLEDGE_DATA: { knowledge_data }

    Guidelines:
    - Be concise but thorough
    - Use clear formatting with sections if multiple data sources are involved
    - Highlight action items or things that need the user's attention
    - If some data is missing, just present what you have
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
    You are SmartDesk, a personal productivity assistant. You coordinate specialized
    sub-agents to help users manage their work life.

    When a user makes a request:
    1. Use the 'add_prompt_to_state' tool to save their request.
    2. Analyze what the user needs and transfer to the appropriate sub-agent:
       - Email-related (read, search, draft, summarize emails) -> inbox_agent
       - Calendar-related (schedule, meetings, conflicts, availability) -> planner_agent
       - Knowledge-related (notes, contacts, tasks, past discussions) -> data_agent
    3. For complex requests that span multiple domains (e.g., "prepare me for my 3pm meeting"),
       you may need to call multiple sub-agents in sequence.

    Always be friendly and proactive. If the user's request is ambiguous,
    ask a clarifying question before routing.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[inbox_agent, planner_agent, data_agent, response_formatter],
)
