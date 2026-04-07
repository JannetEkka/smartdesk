"""Shared OAuth 2.0 helper for Gmail and Calendar MCP servers.

Supports per-user login: any user can authenticate through the agent chat
by calling login_google (gets URL) → complete_google_login (pastes redirect URL).

Cloud Shell & Cloud Run compatible: uses manual copy-paste flow.
"""

import os
import json
import logging
from pathlib import Path

# Allow http://localhost for OAuth redirect (Desktop app flow)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

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


def generate_auth_url() -> dict:
    """Generate an OAuth URL for user login. Called by login_google agent tool."""
    if not _CLIENT_SECRET.exists():
        return {
            "error": "OAuth not configured. client_secret.json is missing. "
            "Ask the admin to set up OAuth credentials in Cloud Console."
        }

    flow = Flow.from_client_secrets_file(
        str(_CLIENT_SECRET),
        scopes=SCOPES,
        redirect_uri="http://localhost",
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    return {
        "auth_url": auth_url,
        "state": state,
    }


def exchange_auth_code(redirect_url: str) -> dict:
    """Exchange the OAuth redirect URL for credentials. Called by complete_google_login."""
    if not _CLIENT_SECRET.exists():
        return {"error": "client_secret.json is missing."}

    try:
        flow = Flow.from_client_secrets_file(
            str(_CLIENT_SECRET),
            scopes=SCOPES,
            redirect_uri="http://localhost",
        )
        flow.fetch_token(authorization_response=redirect_url)
        creds = flow.credentials

        # Save token (overwrites any previous user's token)
        with open(_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

        logger.info("New user authenticated successfully.")
        return {
            "status": "success",
            "message": "Logged in successfully! You can now use Gmail and Calendar features.",
        }
    except Exception as e:
        logger.error(f"Auth exchange failed: {e}")
        return {"error": f"Login failed: {str(e)}"}


def is_logged_in() -> dict:
    """Check if a user is currently logged in."""
    if not _TOKEN_FILE.exists():
        return {"logged_in": False, "message": "No one is logged in yet."}

    try:
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(_TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
            else:
                return {"logged_in": False, "message": "Session expired. Please log in again."}

        return {"logged_in": True}
    except Exception:
        return {"logged_in": False, "message": "Session invalid. Please log in again."}


def logout() -> dict:
    """Log out the current user by deleting the saved token."""
    if _TOKEN_FILE.exists():
        _TOKEN_FILE.unlink()
        logger.info("User logged out, token deleted.")
        return {"status": "success", "message": "Logged out. You can now log in with a different account."}
    return {"status": "success", "message": "No one was logged in."}


def get_credentials(allow_interactive: bool = False) -> Credentials:
    """Get valid OAuth 2.0 credentials from saved token.

    MCP servers call this to get the current user's credentials.
    If no token exists, raises with a clear message.
    """
    creds = None

    if _TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth token...")
            creds.refresh(Request())
            with open(_TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        elif allow_interactive:
            # Only used by authenticate.py (CLI)
            flow = Flow.from_client_secrets_file(
                str(_CLIENT_SECRET),
                scopes=SCOPES,
                redirect_uri="http://localhost",
            )
            auth_url, _ = flow.authorization_url(
                access_type="offline",
                prompt="consent",
            )
            print()
            print("=" * 60)
            print("Open this URL in your browser:")
            print()
            print(auth_url)
            print()
            print("After approving, copy the FULL URL from the browser address bar.")
            print("=" * 60)
            print()
            redirect_url = input("Paste the full redirect URL here: ").strip()
            flow.fetch_token(authorization_response=redirect_url)
            creds = flow.credentials
            with open(_TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            raise FileNotFoundError(
                "Not logged in. Please type 'log in' to authenticate with your Google account."
            )

    return creds
