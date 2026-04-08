# SmartDesk Demo Video Script (~3 minutes)

**Format:** Screen recording of the SmartDesk web UI (ADK web interface) with voiceover.

---

## INTRO (0:00 – 0:20)

**[Show: SmartDesk web UI landing page]**

> "Hi, I'm [Your Name], and this is SmartDesk — a multi-agent productivity assistant built for the Google Cloud Gen AI Academy Hackathon.
>
> SmartDesk uses Google's Agent Development Kit — ADK — to orchestrate multiple AI agents powered by Gemini 2.5 Flash. It connects to Gmail and Google Calendar through custom MCP servers, and uses AlloyDB with vector search as a personal knowledge base. Everything runs serverless on Cloud Run."

---

## PART 1: Knowledge Base — AlloyDB + Vector Search (0:20 – 1:10)

**[Show: Type in chat]**

> "Let's start with the knowledge base. This uses AlloyDB with vector embeddings — no Google login needed."

**Prompt 1:** `What are my pending tasks?`

**[Wait for response — shows task list with priorities and due dates]**

> "SmartDesk routes this to the data_agent, which queries AlloyDB. You can see tasks sorted by priority — high priority ones first, with due dates."

**(~10 sec pause between prompts)**

**Prompt 2:** `Search my notes about product launch`

**[Wait for response — shows semantically matched notes]**

> "This is vector search in action. It uses the text-embedding-005 model inside AlloyDB to find semantically relevant notes — not just keyword matching. It found our Q3 launch planning discussion even though the query doesn't exactly match the note title."

**Prompt 3:** `Look up contact info for Priya`

**[Wait for response — shows contact details]**

> "Contacts are also in AlloyDB. Quick lookup by name, email, or company."

---

## PART 2: Google Login Flow (1:10 – 1:40)

**[Show: Type in chat]**

> "Now let's access email and calendar. These require Google OAuth."

**Prompt 4:** `Show me my latest emails`

**[Wait — SmartDesk detects not logged in, shows Google sign-in link]**

> "SmartDesk checks login status automatically. Since we're not signed in, it generates an OAuth URL. Let me sign in."

**[Click the sign-in link, approve in browser, copy redirect URL, paste back in chat]**

> "I approve access, then paste the redirect URL back. SmartDesk exchanges this for tokens — and we're authenticated."

---

## PART 3: Email — Gmail MCP (1:40 – 2:10)

**[After login completes, SmartDesk shows the emails]**

> "And there are my latest emails — fetched through our custom Gmail MCP server using the Model Context Protocol."

**(Start new session for calendar)**

**Prompt 5:** `Search for emails from support@hack2skill.com`

**[Wait for response — shows filtered email results]**

> "We can also search with Gmail query syntax. The inbox_agent handles all email operations — listing, searching, reading, and even drafting."

---

## PART 4: Calendar — Google Calendar MCP (2:10 – 2:40)

**[Start new session — already logged in from before]**

**Prompt 6:** `What's on my schedule today?`

**[Wait for response — shows today's events]**

> "For calendar, the planner_agent connects to a custom Calendar MCP server. It lists events, finds free time, and can create new meetings."

**Prompt 7:** `Find free time slots for tomorrow`

**[Wait for response — shows available slots]**

> "It analyzes existing events and identifies open windows — great for scheduling without back-and-forth."

---

## PART 5: Account Switch + Wrap-up (2:40 – 3:00)

**Prompt 8:** `Switch account`

**[Wait — SmartDesk logs out, generates new sign-in URL]**

> "Users can also switch Google accounts on the fly. SmartDesk logs out and provides a fresh sign-in link."

**[Show: Architecture diagram or slide briefly]**

> "To recap — SmartDesk is a multi-agent system: a root orchestrator with three specialized sub-agents for email, calendar, and knowledge base. Built with ADK, Gemini 2.5 Flash, MCP, and AlloyDB, all deployed on Cloud Run.
>
> Thanks for watching!"

---

## Demo Tips / Notes for Recording

1. **Space prompts ~30 seconds apart** to avoid Gemini 429 rate limits.
2. **Start a new session** when switching between agent types (email -> calendar).
3. **Pre-login** before recording Parts 3-4 if you want to save time, or show the full login flow once in Part 2 and skip re-login for subsequent parts.
4. **Trim silences** in editing — Gemini thinking time can be 30-60 seconds.
5. **If the video runs long**, cut Part 5 (account switch) and merge the recap into the calendar section.
6. **Total raw recording** will be ~8-10 minutes due to model thinking time. Edit down to 3 minutes.
