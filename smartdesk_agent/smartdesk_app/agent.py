# SmartDesk — Multi-Agent Productivity Assistant
# Main agent definitions following ADK patterns from codelabs

import os
import logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

from . import tools

# --- Setup ---
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")


# --- State Management Tools ---

def save_user_request(tool_context: ToolContext, request: str) -> dict[str, str]:
    """Saves the user's request to shared state for sub-agents to access."""
    tool_context.state["USER_REQUEST"] = request
    logging.info(f"[State updated] USER_REQUEST: {request}")
    return {"status": "success"}


# --- Sub-Agent 1: InboxAgent (Gmail via MCP) ---

inbox_agent = Agent(
    name="inbox_agent",
    model=model_name,
    description="Handles email-related tasks: reading, searching, summarizing, and drafting emails via Gmail.",
    instruction="""
    You are the email assistant for SmartDesk. You help users manage their Gmail inbox.
    You can:
    - Search and read emails
    - Summarize unread emails
    - Draft reply emails
    - Find emails from specific contacts

    Use the Gmail MCP tools available to you to complete these tasks.
    Always provide concise, actionable summaries.

    USER_REQUEST:
    { USER_REQUEST }
    """,
    tools=[tools.get_gmail_mcp_toolset()],
    output_key="inbox_data",
)


# --- Sub-Agent 2: PlannerAgent (Google Calendar via MCP) ---

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

    USER_REQUEST:
    { USER_REQUEST }
    """,
    tools=[tools.get_calendar_mcp_toolset()],
    output_key="planner_data",
)


# --- Sub-Agent 3: DataAgent (AlloyDB) ---

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
    - Find related information across notes using vector similarity

    Use the database tools available to you.

    USER_REQUEST:
    { USER_REQUEST }
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


# --- Response Formatter (SequentialAgent output) ---

response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all gathered information into a clear, friendly response.",
    instruction="""
    You are the final voice of SmartDesk. Your job is to take all the data gathered
    by the other agents and present it as a unified, helpful response to the user.

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

root_agent = Agent(
    name="smartdesk",
    model=model_name,
    description="SmartDesk — your personal productivity assistant for emails, calendar, and knowledge management.",
    instruction="""
    You are SmartDesk, a personal productivity assistant. You coordinate specialized
    sub-agents to help users manage their work life.

    When a user makes a request:
    1. Use the 'save_user_request' tool to store their request in state.
    2. Analyze what the user needs and transfer to the appropriate sub-agent(s):
       - Email-related (read, search, draft, summarize emails) → inbox_agent
       - Calendar-related (schedule, meetings, conflicts, availability) → planner_agent
       - Knowledge-related (notes, contacts, tasks, past discussions) → data_agent
    3. For complex multi-step requests (e.g., "prepare me for my 3pm meeting"),
       you may need to call multiple sub-agents in sequence.

    Always be friendly and proactive. If the user's request is ambiguous,
    ask a clarifying question before routing.
    """,
    tools=[save_user_request],
    sub_agents=[inbox_agent, planner_agent, data_agent, response_formatter],
)
