# SmartDesk Demo Video Script (~3 minutes)

**Format:** Screen recording of the SmartDesk web UI (ADK web interface) with voiceover.

---

## INTRO (0:00 – 0:20)

**[Show: SmartDesk web UI landing page]**

> "Hi, I'm [Your Name], and this is SmartDesk — a multi-agent AI system built for the Google Cloud Gen AI Academy Hackathon.
>
> The problem statement asks us to build a system that helps users manage tasks, schedules, and information using multiple agents, tools, and data sources. SmartDesk does exactly that — it uses ADK to orchestrate multiple agents powered by Gemini 2.5 Flash, connects to Gmail and Google Calendar through custom MCP servers, and uses AlloyDB with vector search as a structured database. It handles multi-step workflows end-to-end and is deployed as an API on Cloud Run."

---

## PART 1: Knowledge Base — AlloyDB + Vector Search (0:20 – 1:10)

**[Show: Type in chat]**

> "Let's start with the knowledge base. This uses AlloyDB with vector embeddings — no Google login needed."

**Prompt 1:** `What are my pending tasks?`

**[Wait for response — shows task list with priorities and due dates]**

> "SmartDesk routes this to the data_agent, which queries AlloyDB — that's the structured database requirement. Tasks are sorted by priority with due dates."

**(~10 sec pause between prompts)**

**Prompt 2:** `Mark task 3 as done`

**[Wait for response — confirms task updated]**

> "This is a multi-step workflow — the agent fetches the task, verifies the ID, then updates the status in AlloyDB. All in one request."

**(~10 sec pause)**

**Prompt 3:** `Search my notes about product launch`

**[Wait for response — shows semantically matched notes]**

> "This is vector search in action. It uses the text-embedding-005 model inside AlloyDB to find semantically relevant notes — not just keyword matching. It found our Q3 launch planning discussion even though the query doesn't exactly match the note title."

**Prompt 4:** `Look up contact info for Priya`

**[Wait for response — shows contact details]**

> "Contacts are also in AlloyDB. Quick lookup by name, email, or company. That covers storing and retrieving structured data from a database."

---

## PART 2: Google Login Flow (1:10 – 1:40)

**[Show: Type in chat]**

> "Now let's access email and calendar. These require Google OAuth."

**Prompt 5:** `Show me my latest emails`

**[Wait — SmartDesk detects not logged in, shows Google sign-in link]**

> "SmartDesk checks login status automatically. Since we're not signed in, it generates an OAuth URL. This is a multi-step workflow — it checks auth, generates the URL, and waits. Let me sign in."

**[Click the sign-in link, approve in browser, copy redirect URL, paste back in chat]**

> "I paste the redirect URL back. SmartDesk exchanges the authorization code for tokens — and we're authenticated. That whole flow — check login, generate URL, exchange code, fetch emails — is all handled automatically across multiple steps."

---

## PART 3: Email — Gmail MCP (1:40 – 2:10)

**[After login completes, SmartDesk shows the emails]**

> "And there are my latest emails — fetched through our custom Gmail MCP server using the Model Context Protocol."

**(Start new session for calendar)**

**Prompt 6:** `Search for emails from support@hack2skill.com`

**[Wait for response — shows filtered email results]**

> "We can also search with Gmail query syntax. The inbox_agent handles all email operations — listing, searching, reading, and even drafting."

---

## PART 4: Calendar — Google Calendar MCP (2:10 – 2:40)

**[Start new session — already logged in from before]**

**Prompt 7:** `What's on my schedule today?`

**[Wait for response — shows today's events]**

> "For calendar, the planner_agent connects to a custom Calendar MCP server. It lists events, finds free time, and can create new meetings."

**Prompt 8:** `Find free time slots for tomorrow`

**[Wait for response — shows available slots]**

> "It analyzes existing events and identifies open windows — great for scheduling without back-and-forth."

---

## PART 5: Account Switch + Wrap-up (2:40 – 3:00)

**Prompt 9:** `Switch account`

**[Wait — SmartDesk logs out, generates new sign-in URL]**

> "Users can also switch Google accounts on the fly. SmartDesk logs out and provides a fresh sign-in link."

**[Show: Architecture diagram or slide briefly]**

> "To recap — SmartDesk meets every core requirement: a primary agent coordinating three sub-agents, structured data in AlloyDB, multiple tools via MCP, multi-step workflows like auth-then-execute, and it's deployed as an API on Cloud Run.
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
