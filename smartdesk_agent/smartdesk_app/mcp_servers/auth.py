"""Shared OAuth 2.0 helper for Gmail and Calendar MCP servers.

Uses the Desktop OAuth flow with client_secret.json, which avoids the
"This app is blocked" error that happens with gcloud's default OAuth client.

Setup:
1. Create OAuth consent screen (External, Testing mode) in Cloud Console
2. Create OAuth client ID (Desktop app) → download JSON
3. Save as smartdesk_agent/smartdesk_app/client_secret.json
"""

import os
import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

# Token + client secret paths (relative to smartdesk_app/)
_APP_DIR = Path(__file__).parent.parent
_CLIENT_SECRET = _APP_DIR / "client_secret.json"
_TOKEN_FILE = _APP_DIR / "token.json"

# All scopes needed by Gmail and Calendar MCP servers
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_credentials() -> Credentials:
    """Get valid OAuth 2.0 credentials, running the auth flow if needed.

    First run: opens a browser for consent, saves token.json.
    Subsequent runs: loads and refreshes the saved token.
    """
    creds = None

    # Load saved token if it exists
    if _TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)

    # If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth token...")
            creds.refresh(Request())
        else:
            if not _CLIENT_SECRET.exists():
                raise FileNotFoundError(
                    f"OAuth client secret not found at {_CLIENT_SECRET}. "
                    "Download it from Cloud Console → APIs & Services → Credentials → "
                    "OAuth 2.0 Client IDs → Download JSON, and save as client_secret.json "
                    "in the smartdesk_app/ directory."
                )
            logger.info("Running OAuth consent flow (will open browser)...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(_CLIENT_SECRET), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save for next run
        with open(_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        logger.info(f"OAuth token saved to {_TOKEN_FILE}")

    return creds
