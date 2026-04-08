# SmartDesk — PPT Content (Mapped to Hackathon Template)

> Template: `docs/Prototype Submission Deck.pptx` (11 slides)
> Replace every "Type here…" placeholder with the content below.

---

## Slide 1: Participant Details

- **Participant Name:** Jannet Ekka
- **Problem Statement:** Build a multi-agent AI system that helps users manage tasks, schedules, and information by interacting with multiple tools and data sources.

---

## Slide 2: Brief about the idea

SmartDesk is a multi-agent AI productivity assistant that lets users manage their Gmail inbox, Google Calendar, and a personal knowledge base (contacts, notes, tasks) — all through a single natural language chat interface.

Instead of switching between multiple apps, users simply type what they need: "Show me my latest emails," "What's on my schedule today?," or "Search my notes about the product launch." SmartDesk's orchestrator agent intelligently routes each request to the right specialized sub-agent, which connects to the appropriate service via custom MCP servers (for Gmail & Calendar) or AlloyDB with vector search (for the knowledge base).

Built entirely on Google Cloud — ADK for agent orchestration, Gemini 2.5 Flash as the LLM, AlloyDB for AI-ready database with in-database vector embeddings, and Cloud Run for serverless deployment.

---

## Slide 3: Solution Explanation

**How did you approach the common problem statement and translate it into a working solution using ADK, MCP/AlloyDB AI while ensuring the hackathon's core requirements are met?**

I started by studying the ADK, MCP, and AlloyDB codelabs to understand the exact patterns and APIs. Then I designed a multi-agent architecture where a root orchestrator agent routes user requests to three specialized sub-agents. For Gmail and Calendar, I built custom MCP servers (using stdio transport) that handle OAuth and call the Google APIs. For the knowledge base, I connected directly to AlloyDB using pg8000 and leveraged its built-in `embedding()` function with `text-embedding-005` for vector search — no external vector DB needed. This ensures all three hackathon tracks (ADK, MCP, AlloyDB) are deeply integrated, not just surface-level.

**What real-world problem does your solution address, and what practical impact does it create for users?**

Professionals lose significant time context-switching between email, calendar, notes, and task managers. SmartDesk eliminates this by unifying all productivity tools into one conversational AI interface. A user can ask "What did Priya say about the launch timeline?" and get an answer from their notes via semantic search — without opening a single app. The practical impact: fewer tabs, faster decisions, and a personal AI assistant that actually knows your work context.

**What is the core approach or workflow behind your solution?**

User sends a message → Root agent classifies intent (email / calendar / knowledge base / auth) → Routes to the correct sub-agent → Sub-agent calls its tools (Gmail MCP, Calendar MCP, or AlloyDB) → Returns a formatted response. Authentication is handled in-chat via OAuth — users click a sign-in link, approve, and paste back the redirect URL. The knowledge base (contacts, notes, tasks) works without any login.

SmartDesk handles multi-step workflows end-to-end:
- **Auth → Execute:** "Show my emails" triggers login check → OAuth flow → token exchange → email fetch — all within the conversation.
- **Query → Update:** "Mark task 3 as done" fetches tasks to verify the ID, then updates the status in AlloyDB.
- **Search → Act:** "Draft an email about the project update" searches context, composes a full professional email, and creates a Gmail draft — no user hand-holding needed.

---

## Slide 4: Opportunities — USP & Differentiation

**How different is it from existing ideas?**

Most AI assistants either focus on a single domain (just email, just calendar) or require pre-configured API keys and complex setup. SmartDesk is different because:

- **Unified multi-agent system** — Not three separate tools stitched together. One orchestrator that intelligently routes to specialized agents based on intent.
- **Custom MCP servers, not pre-built connectors** — Gmail and Calendar integration built from scratch using the Model Context Protocol standard, giving full control over auth, error handling, and response formatting.
- **In-database vector search** — Notes use AlloyDB's native `embedding()` function with `text-embedding-005`. Semantic search runs inside the database itself — no Pinecone, no Chroma, no external vector DB.
- **In-chat OAuth** — Users authenticate by clicking a link in the chat and pasting back the redirect URL. No separate login page, no config files.

**USP:** A truly integrated, deploy-ready AI assistant that combines email + calendar + semantic knowledge base in one chat, built entirely on Google Cloud's latest AI stack (ADK + MCP + AlloyDB + Gemini).

---

## Slide 5: List of Features

1. **Email Management (Gmail MCP)**
   - List recent inbox emails with sender, subject, snippet
   - Search emails using Gmail query syntax (e.g., "from:alice subject:meeting")
   - Read full email content by message ID
   - Draft and compose professional emails from a topic description

2. **Calendar Management (Google Calendar MCP)**
   - View today's schedule and upcoming events
   - Search events by keyword
   - Find free time slots on any date
   - Create new events with title, time, and attendees

3. **Personal Knowledge Base (AlloyDB + Vector Search)**
   - Semantic search over meeting notes (vector similarity with text-embedding-005)
   - Contact lookup by name, email, or company
   - Task management — view by status, create tasks with priority and due date, mark done

4. **In-Chat Authentication**
   - Google OAuth sign-in/sign-out directly in the chat
   - Switch Google accounts on the fly
   - No login needed for knowledge base features

5. **Intelligent Agent Routing**
   - Root agent classifies and routes to the right sub-agent automatically
   - Anti-duplication callbacks prevent repeated responses after agent transfers

6. **Multi-Step Workflow Execution**
   - Auth-gated workflows: auto-detects login requirement → authenticates → then executes the original request
   - Chained operations: fetch → verify → update (e.g., task status changes)
   - Compose-and-act: generates full email drafts from a topic, creates calendar events from natural language

---

## Slide 6: Process Flow Diagram

*(Create a simple diagram or paste this text flow)*

```
┌─────────────────────────────────────────────────────┐
│                    USER MESSAGE                      │
└────────────────────────┬────────────────────────────┘
                         ▼
              ┌─────────────────────┐
              │    ROOT AGENT       │
              │  (SmartDesk)        │
              │  Classify Intent    │
              └──┬──────┬──────┬───┘
                 │      │      │
    ┌────────────┘      │      └────────────┐
    ▼                   ▼                   ▼
┌──────────┐    ┌──────────────┐    ┌──────────┐
│  INBOX   │    │   PLANNER    │    │   DATA   │
│  AGENT   │    │   AGENT      │    │   AGENT  │
└────┬─────┘    └──────┬───────┘    └────┬─────┘
     ▼                 ▼                 ▼
┌──────────┐    ┌──────────────┐    ┌──────────┐
│ Gmail    │    │  Calendar    │    │ AlloyDB  │
│ MCP      │    │  MCP Server  │    │ Vector   │
│ Server   │    │              │    │ Search   │
└──────────┘    └──────────────┘    └──────────┘
     ▼                 ▼                 ▼
┌──────────┐    ┌──────────────┐    ┌──────────┐
│ Gmail    │    │  Google      │    │ text-    │
│ API      │    │  Calendar    │    │embedding │
│ (OAuth)  │    │  API (OAuth) │    │ -005     │
└──────────┘    └──────────────┘    └──────────┘
```

---

## Slide 7: Wireframes / Mock Diagrams

*(Insert screenshots of the ADK web UI showing:)*

1. **Chat interface** — The main ADK web UI at `localhost:8000` or Cloud Run URL
2. **Login flow** — User sees sign-in link → pastes redirect URL → "Login successful"
3. **Email query** — "Show me my latest emails" → formatted email list
4. **Knowledge base query** — "Search my notes about product launch" → vector search results with similarity scores

*(Take these screenshots while recording the demo video — two birds, one stone)*

---

## Slide 8: Architecture Diagram

*(Create a clean diagram from this — use draw.io, Google Drawings, or similar)*

```
                    ┌──────────────────┐
                    │   User Browser   │
                    └────────┬─────────┘
                             │ HTTP
                             ▼
                    ┌──────────────────┐
                    │    Cloud Run     │
                    │  (Serverless)    │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      Root Agent (SmartDesk)   │
              │      Gemini 2.5 Flash (LLM)  │
              │      OAuth + Routing Logic    │
              │      before/after callbacks   │
              └──┬──────────┬──────────┬─────┘
                 │          │          │
      ┌──────────┘          │          └──────────┐
      ▼                     ▼                     ▼
┌────────────┐     ┌──────────────┐      ┌────────────┐
│ Inbox Agent│     │Planner Agent │      │ Data Agent │
│            │     │              │      │            │
└─────┬──────┘     └──────┬───────┘      └─────┬──────┘
      │ stdio             │ stdio              │ pg8000
      ▼                   ▼                    ▼
┌────────────┐     ┌──────────────┐      ┌────────────────┐
│Gmail MCP   │     │Calendar MCP  │      │   AlloyDB      │
│Server      │     │Server        │      │   (PostgreSQL) │
└─────┬──────┘     └──────┬───────┘      │                │
      │ OAuth 2.0         │ OAuth 2.0    │ vector ext     │
      ▼                   ▼              │ google_ml ext  │
┌────────────┐     ┌──────────────┐      │ embedding()    │
│ Gmail API  │     │Calendar API  │      │ text-emb-005   │
└────────────┘     └──────────────┘      └────────────────┘
```

---

## Slide 9: Technologies / Google Services Used

**Why this AI stack?**

| Technology | Why We Chose It | How It's Used |
|---|---|---|
| **ADK (Agent Development Kit)** | Google's official framework for building multi-agent systems. Handles agent orchestration, tool discovery, and state management out of the box. | Root agent + 3 sub-agents with automatic routing |
| **Gemini 2.5 Flash** | Fast, capable LLM with function calling support. Runs on Vertex AI with no separate API key needed. | Powers all 4 agents (root + 3 sub-agents) |
| **MCP (Model Context Protocol)** | Standardized protocol for connecting LLMs to external tools. Future-proof — any MCP-compatible client can use our servers. | Custom Gmail & Calendar MCP servers (stdio transport) |
| **AlloyDB** | PostgreSQL-compatible with built-in vector search and the `embedding()` function. Eliminates the need for a separate vector database. | Personal CRM: contacts, notes (with embeddings), tasks |
| **text-embedding-005** | Google's latest text embedding model. Runs inside AlloyDB via `google_ml_integration` — no external API calls for embedding. | Semantic search over meeting notes |
| **Cloud Run** | Serverless, auto-scaling, pay-per-use. ADK has built-in Cloud Run deployment support. | Production deployment of the full agent system |
| **Google OAuth 2.0** | Secure per-user authentication for Gmail and Calendar access. | In-chat login/logout/switch-account flow |

**Scalability:** Cloud Run auto-scales horizontally. AlloyDB handles vector search at database level (no external vector DB bottleneck). MCP servers are stateless (stdio per-session). The architecture is ready for multi-user production use.

---

## Slide 10: Snapshots of the Prototype

*(Insert 3-4 screenshots showing the working prototype:)*

1. **Task management** — "What are my pending tasks?" showing the formatted task list from AlloyDB
2. **Vector search** — "Search my notes about product launch" showing semantically matched results
3. **Email listing** — "Show me my latest emails" showing Gmail inbox via MCP
4. **Calendar** — "What's on my schedule today?" showing events via Calendar MCP

*(Capture these during your demo recording)*

---

## Slide 11: Closing Slide

*(Template has a branded closing image — no text needed)*
