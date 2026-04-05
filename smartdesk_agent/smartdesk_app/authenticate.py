#!/usr/bin/env python3
"""Pre-authenticate Gmail & Calendar OAuth for SmartDesk MCP servers.

Run this ONCE before starting adk web:
    python smartdesk_agent/smartdesk_app/authenticate.py

It opens a browser for Google consent, then saves token.json.
The MCP servers will use this saved token automatically.
"""

import sys
import os

# Add mcp_servers to path so we can import auth
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_servers"))
from auth import get_credentials

if __name__ == "__main__":
    print("Starting OAuth consent flow...")
    print("A browser tab will open — sign in and approve access.")
    print()
    creds = get_credentials(allow_interactive=True)
    print()
    print("Authentication successful! token.json saved.")
    print("You can now run: cd smartdesk_agent && adk web")
