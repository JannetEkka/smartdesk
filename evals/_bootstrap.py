"""Make the ``rag`` package importable without loading the ADK agent stack.

``smartdesk_app/__init__.py`` imports ``agent``, which constructs the MCP
toolsets at module scope and spawns subprocesses. The eval harness needs only
the retrieval code, so it puts ``smartdesk_app`` itself on the path and imports
``rag`` as a top-level package. Inside the agent, the same package is imported
as ``smartdesk_app.rag``; the relative imports within it work either way.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_APP_DIR = REPO_ROOT / "smartdesk_agent" / "smartdesk_app"

for _p in (str(_APP_DIR), str(REPO_ROOT / "evals")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
