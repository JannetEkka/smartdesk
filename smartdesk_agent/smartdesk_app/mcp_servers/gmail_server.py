"""Gmail MCP Server for SmartDesk.

Custom MCP server that wraps Gmail API calls as MCP tools.
Pattern from docs/mcp.md — Codelab 3, "Build an MCP server with ADK tools".

Run standalone:  python gmail_server.py
Connect via ADK: StdioConnectionParams pointing to this script.
"""

import asyncio
import base64
import json
import logging
import os
import sys
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add parent to path so we can import the shared auth module
sys.path.insert(0, os.path.dirname(__file__))
from auth import get_credentials

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("gmail_mcp_server")

app = Server("gmail-mcp-server")


def _get_gmail_service():
    """Build Gmail API service using Desktop OAuth credentials."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_emails",
            description="List recent emails from the user's Gmail inbox. Returns subject, sender, snippet, and message ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to return (default 10, max 20).",
                        "default": 10,
                    },
                },
            },
        ),
        Tool(
            name="search_emails",
            description="Search emails using Gmail search syntax (e.g., 'from:alice subject:meeting').",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query string.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default 10).",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="read_email",
            description="Read the full content of a specific email by its message ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The Gmail message ID to read.",
                    },
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="draft_email",
            description="Create a draft email in Gmail.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line.",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body text.",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
    ]


def _extract_headers(headers, names):
    """Extract specific headers from a Gmail message."""
    result = {}
    for header in headers:
        if header["name"] in names:
            result[header["name"]] = header["value"]
    return result


def _get_message_body(payload):
    """Extract plain text body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    # Check parts for multipart messages
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

    return "(No plain text body found)"


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        service = _get_gmail_service()

        if name == "list_emails":
            max_results = min(arguments.get("max_results", 10), 20)
            results = service.users().messages().list(
                userId="me", maxResults=max_results, labelIds=["INBOX"]
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                return [TextContent(type="text", text="No emails found in inbox.")]

            emails = []
            for msg in messages:
                detail = service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]
                ).execute()
                headers = _extract_headers(detail.get("payload", {}).get("headers", []),
                                           ["From", "Subject", "Date"])
                emails.append({
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": detail.get("snippet", ""),
                })

            return [TextContent(type="text", text=json.dumps(emails, indent=2))]

        elif name == "search_emails":
            query = arguments["query"]
            max_results = min(arguments.get("max_results", 10), 20)
            results = service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                return [TextContent(type="text", text=f"No emails found for query: {query}")]

            emails = []
            for msg in messages:
                detail = service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]
                ).execute()
                headers = _extract_headers(detail.get("payload", {}).get("headers", []),
                                           ["From", "Subject", "Date"])
                emails.append({
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": detail.get("snippet", ""),
                })

            return [TextContent(type="text", text=json.dumps(emails, indent=2))]

        elif name == "read_email":
            message_id = arguments["message_id"]
            detail = service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()
            headers = _extract_headers(detail.get("payload", {}).get("headers", []),
                                       ["From", "To", "Subject", "Date"])
            body = _get_message_body(detail.get("payload", {}))

            email_data = {
                "id": message_id,
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "body": body[:3000],  # Truncate very long emails
            }
            return [TextContent(type="text", text=json.dumps(email_data, indent=2))]

        elif name == "draft_email":
            message = MIMEText(arguments["body"])
            message["to"] = arguments["to"]
            message["subject"] = arguments["subject"]
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            draft = service.users().drafts().create(
                userId="me", body={"message": {"raw": raw}}
            ).execute()

            return [TextContent(type="text", text=json.dumps({
                "status": "Draft created successfully",
                "draft_id": draft["id"],
                "to": arguments["to"],
                "subject": arguments["subject"],
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
