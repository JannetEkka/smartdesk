# SmartDesk — PPT Slide Content

> **NOTE:** Upload the hackathon template (.pptx) to the GitHub repo and tell me the filename.
> I'll then map this content to the exact slides in the template. Below is the content
> organized by the standard hackathon template sections (Participant Details, Problem Statement,
> Solution, Architecture, Tech Stack, Demo, etc.)

---

## Slide 1: Title / Participant Details

- **Participant Name:** [Your Name]
- **Problem Statement:** Multi-Agent Productivity Assistant
- **Project Name:** SmartDesk
- **Tagline:** Your AI-powered productivity command center — emails, calendar, and knowledge base, all in one chat.

---

## Slide 2: Problem Statement

**The Problem:**
- Professionals juggle multiple tools daily — Gmail, Google Calendar, notes, task trackers, contacts — leading to constant context switching.
- Finding information requires opening multiple apps: "Did Priya email me about the launch date, or was it in my meeting notes?"
- No unified interface to manage email, calendar, and personal knowledge base with natural language.

**Who it helps:** Knowledge workers, project managers, and anyone overwhelmed by tool fragmentation.

---

## Slide 3: Solution Overview

**SmartDesk** is a multi-agent AI assistant that unifies:

| Capability | What it Does |
|---|---|
| **Email (Gmail)** | List, search, read, and draft emails via natural language |
| **Calendar** | View schedule, find free time, create events |
| **Knowledge Base** | Semantic search over notes, contact lookup, task management |
| **Account Management** | Per-user Google OAuth login/switch directly in chat |

**One chat interface. Three specialized AI agents. Zero context switching.**

---

## Slide 4: Architecture

```
User (Browser)
    │
    ▼ (HTTP / Cloud Run)
Root Agent (SmartDesk Orchestrator)
    │   Gemini 2.5 Flash
    │   OAuth tools + routing logic
    │
    ├── Inbox Agent ──► Gmail MCP Server (stdio)
    │                      └── Gmail API (OAuth 2.0)
    │
    ├── Planner Agent ──► Calendar MCP Server (stdio)
    │                        └── Google Calendar API (OAuth 2.0)
    │
    └── Data Agent ──► AlloyDB (PostgreSQL)
                          └── Vector Search (text-embedding-005)
```

- **Root agent** classifies requests and routes to the right sub-agent
- **Anti-duplication callbacks** prevent response loops after agent transfers
- **MCP (Model Context Protocol)** connects agents to external APIs via standardized tool interface

---

## Slide 5: Tech Stack / Google Cloud Services Used

| Technology | Role |
|---|---|
| **ADK (Agent Development Kit)** | Multi-agent orchestration framework |
| **Gemini 2.5 Flash** | LLM powering all agents (via Vertex AI) |
| **MCP (Model Context Protocol)** | Standardized tool integration for Gmail & Calendar |
| **AlloyDB** | PostgreSQL-compatible DB with vector search |
| **text-embedding-005** | In-database vector embeddings for semantic search |
| **Cloud Run** | Serverless deployment |
| **Google OAuth 2.0** | Per-user authentication for Gmail & Calendar |
| **Python + pg8000** | Backend language + AlloyDB driver |

---

## Slide 6: Key Features / Innovation

1. **Multi-Agent Routing** — Root agent intelligently classifies and routes to specialized sub-agents (email, calendar, knowledge base).

2. **Custom MCP Servers** — Built from scratch for Gmail and Calendar, following the Model Context Protocol standard. Not using pre-built connectors.

3. **In-Database Vector Search** — Notes are embedded using `text-embedding-005` *inside* AlloyDB. Semantic search happens at the database level — no external vector DB needed.

4. **Per-User OAuth in Chat** — Users login/switch Google accounts directly in the chat interface. Tokens are managed per-session.

5. **Anti-Duplication Architecture** — Custom `before_model` / `after_model` callbacks prevent the LLM loop from re-processing after sub-agent transfers (solved a real ADK behavior quirk).

---

## Slide 7: Demo Screenshots / Live Demo

*[Insert screenshots of:]*
1. Knowledge base query — "Search my notes about product launch" showing vector search results
2. Gmail integration — "Show me my latest emails" with email listing
3. Calendar — "What's on my schedule today?" with event display
4. Login flow — Sign-in URL → paste redirect → authenticated

**Demo Video Link:** [Your 3-min demo video URL]
**Cloud Run URL:** [Your deployment URL]

---

## Slide 8: Challenges & Learnings

| Challenge | How We Solved It |
|---|---|
| **ADK response duplication** | Built custom `before_model`/`after_model` callbacks; discovered `LlmResponse(content=None)` doesn't stop ADK's loop — must use empty text part |
| **Gemini 429 rate limits** | Spaced API calls; implemented proper error handling |
| **MCP auth warnings** | Identified as harmless — custom servers handle OAuth internally |
| **Sub-agent context stickiness** | Documented behavior; use new sessions for different agent types |

**Key Learning:** Building with emerging frameworks (ADK, MCP) requires understanding internal behaviors deeply — reading source code, not just docs.

---

## Slide 9: Future Scope

- **Multi-user support** with session-isolated OAuth tokens
- **Google Drive agent** for document search and summarization
- **Slack MCP server** for team messaging integration
- **Smart scheduling** — auto-suggest meeting times based on email context + calendar availability
- **RAG over emails** — vector-embed email history for semantic search across inbox

---

## Slide 10: Thank You / Links

- **GitHub:** github.com/JannetEkka/smartdesk
- **Cloud Run:** [deployment URL]
- **Demo Video:** [video link]
- **Built with:** Google ADK, Gemini 2.5 Flash, MCP, AlloyDB, Cloud Run
