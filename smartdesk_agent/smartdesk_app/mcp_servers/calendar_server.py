"""Google Calendar MCP Server for SmartDesk.

Custom MCP server that wraps Google Calendar API calls as MCP tools.
Pattern from docs/mcp.md — Codelab 3, "Build an MCP server with ADK tools".

Run standalone:  python calendar_server.py
Connect via ADK: StdioConnectionParams pointing to this script.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("calendar_mcp_server")

app = Server("calendar-mcp-server")


def _get_calendar_service():
    """Build Calendar API service using application default credentials."""
    credentials, _ = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return build("calendar", "v3", credentials=credentials)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_events",
            description="List upcoming calendar events. Defaults to today's events.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to look (default 1 = today only, max 14).",
                        "default": 1,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default 10).",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="search_events",
            description="Search calendar events by keyword in the title or description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword to find in event titles/descriptions.",
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to search (default 7).",
                        "default": 7,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_event",
            description="Get full details of a specific calendar event by its event ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The Google Calendar event ID.",
                    },
                },
                "required": ["event_id"],
            },
        ),
        Tool(
            name="create_event",
            description="Create a new calendar event.",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Event title.",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format (e.g., '2026-04-07T14:00:00').",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO 8601 format (e.g., '2026-04-07T15:00:00').",
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional).",
                        "default": "",
                    },
                    "attendees": {
                        "type": "string",
                        "description": "Comma-separated email addresses of attendees (optional).",
                        "default": "",
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional).",
                        "default": "",
                    },
                },
                "required": ["summary", "start_time", "end_time"],
            },
        ),
        Tool(
            name="find_free_time",
            description="Find free time slots on a given day by checking existing events.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check in YYYY-MM-DD format (e.g., '2026-04-07').",
                    },
                    "work_start_hour": {
                        "type": "integer",
                        "description": "Start of work day (hour, default 9).",
                        "default": 9,
                    },
                    "work_end_hour": {
                        "type": "integer",
                        "description": "End of work day (hour, default 17).",
                        "default": 17,
                    },
                },
                "required": ["date"],
            },
        ),
    ]


def _format_event(event):
    """Format a calendar event into a clean dict."""
    start = event.get("start", {})
    end = event.get("end", {})
    return {
        "id": event.get("id", ""),
        "summary": event.get("summary", "(No title)"),
        "start": start.get("dateTime", start.get("date", "")),
        "end": end.get("dateTime", end.get("date", "")),
        "location": event.get("location", ""),
        "description": event.get("description", "")[:500],
        "attendees": [
            a.get("email", "") for a in event.get("attendees", [])
        ],
        "hangout_link": event.get("hangoutLink", ""),
        "status": event.get("status", ""),
    }


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        service = _get_calendar_service()

        if name == "list_events":
            days_ahead = min(arguments.get("days_ahead", 1), 14)
            max_results = min(arguments.get("max_results", 10), 25)

            now = datetime.now(timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()

            results = service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = [_format_event(e) for e in results.get("items", [])]
            if not events:
                return [TextContent(type="text", text="No upcoming events found.")]
            return [TextContent(type="text", text=json.dumps(events, indent=2))]

        elif name == "search_events":
            query = arguments["query"]
            days_ahead = min(arguments.get("days_ahead", 7), 30)

            now = datetime.now(timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()

            results = service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                q=query,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            events = [_format_event(e) for e in results.get("items", [])]
            if not events:
                return [TextContent(type="text", text=f"No events found matching: {query}")]
            return [TextContent(type="text", text=json.dumps(events, indent=2))]

        elif name == "get_event":
            event_id = arguments["event_id"]
            event = service.events().get(
                calendarId="primary", eventId=event_id
            ).execute()
            return [TextContent(type="text", text=json.dumps(_format_event(event), indent=2))]

        elif name == "create_event":
            event_body = {
                "summary": arguments["summary"],
                "start": {"dateTime": arguments["start_time"], "timeZone": "Asia/Kolkata"},
                "end": {"dateTime": arguments["end_time"], "timeZone": "Asia/Kolkata"},
            }
            if arguments.get("description"):
                event_body["description"] = arguments["description"]
            if arguments.get("location"):
                event_body["location"] = arguments["location"]
            if arguments.get("attendees"):
                emails = [e.strip() for e in arguments["attendees"].split(",") if e.strip()]
                event_body["attendees"] = [{"email": e} for e in emails]

            created = service.events().insert(
                calendarId="primary", body=event_body
            ).execute()

            return [TextContent(type="text", text=json.dumps({
                "status": "Event created successfully",
                "event_id": created["id"],
                "summary": created.get("summary", ""),
                "start": created["start"].get("dateTime", ""),
                "end": created["end"].get("dateTime", ""),
                "link": created.get("htmlLink", ""),
            }, indent=2))]

        elif name == "find_free_time":
            date_str = arguments["date"]
            work_start = arguments.get("work_start_hour", 9)
            work_end = arguments.get("work_end_hour", 17)

            # Parse the date and build time range
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            time_min = target_date.replace(hour=work_start, minute=0).isoformat() + "+05:30"
            time_max = target_date.replace(hour=work_end, minute=0).isoformat() + "+05:30"

            results = service.events().list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            busy_slots = []
            for event in results.get("items", []):
                start = event["start"].get("dateTime", "")
                end = event["end"].get("dateTime", "")
                if start and end:
                    busy_slots.append({
                        "summary": event.get("summary", "(busy)"),
                        "start": start,
                        "end": end,
                    })

            # Calculate free slots
            free_slots = []
            current = target_date.replace(hour=work_start, minute=0)
            work_end_time = target_date.replace(hour=work_end, minute=0)

            for slot in busy_slots:
                slot_start = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
                slot_start_naive = slot_start.replace(tzinfo=None)
                if slot_start_naive > current:
                    free_slots.append({
                        "start": current.strftime("%H:%M"),
                        "end": slot_start_naive.strftime("%H:%M"),
                        "duration_minutes": int((slot_start_naive - current).total_seconds() / 60),
                    })
                slot_end = datetime.fromisoformat(slot["end"].replace("Z", "+00:00"))
                current = max(current, slot_end.replace(tzinfo=None))

            if current < work_end_time:
                free_slots.append({
                    "start": current.strftime("%H:%M"),
                    "end": work_end_time.strftime("%H:%M"),
                    "duration_minutes": int((work_end_time - current).total_seconds() / 60),
                })

            return [TextContent(type="text", text=json.dumps({
                "date": date_str,
                "busy_slots": busy_slots,
                "free_slots": free_slots,
            }, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
