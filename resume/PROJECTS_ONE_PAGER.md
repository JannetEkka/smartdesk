# Jannet Ekka — Projects One-Pager

*AI engineer. Google Cloud + agentic AI. Built and shipped with Claude Code.*

---

## 1. SMT — Autonomous Crypto Trading Agent
**Status:** Live 24/7 on GCP (UAT) · **Stack:** Python, Gemini 2.5 Flash (Vertex AI), WEEX API, GCS, GradientBoosting · **Recognition:** 1st place — OpenServ Hackathon 2025 · 1st in semifinals — WEEX AI Wars 2026

**What it is.** Three trading systems sharing one exchange account, each with its own capital, position book, and risk profile. They don't interfere — one system's loss doesn't move another's decisions.

- **Daemon (main bot).** 6-persona Gemini ensemble (whale / sentiment / flow / tech + two voters) passing signals through 15 quality gates. Three execution lanes: 10-min full analysis, 2-min BTC breakout fast-path, 2-min wick-recovery mean reversion. 3 positions max, $1K margin each, 20x leverage.
- **RL agent.** GradientBoosting trained on 22 features from daemon history (persona signals, market state, portfolio, derived agreement metrics). Three models — gate override (WIN/WAIT/LOSS), position sizing, entry quality — decide whether to trade and how hard. 2 positions, $500 each, 15x.
- **Agentic AI.** Gemini 2.5 Flash reasoning directly on market data. Two jobs: (1) tune daemon parameters every 5 min via hot-reload `smt_settings.json`, (2) pick one best trade across 8 pairs every 3 min.

**Why it matters.** Shows I can design and operate a real-money-adjacent distributed system: GCP infra (e2-medium VM, static IP whitelisted with WEEX, GCS), hot-reload config, JSONL data pipeline (collector → backfill → training), watchdog + nightly test harness, and three coexisting decision loops.

**Repo:** `github.com/JannetEkka/smt-weex-trading-bot`

---

## 2. SmartDesk — Multi-Agent Productivity Assistant
**Status:** Submitted to Google APAC Hackathon 2026 · **Stack:** Google ADK 1.14, Gemini 2.5 Flash, MCP, AlloyDB (pgvector), Cloud Run

**What it is.** One chat window, a team of specialized agents behind it. Ask *"what's on my plate today?"* and SmartDesk answers across your inbox, calendar, and notes.

- `root_agent` handles auth and routes via ADK's `transfer_to_agent`.
- `inbox_agent` → Gmail via a custom MCP server (stdio).
- `planner_agent` → Google Calendar via MCP.
- `data_agent` → AlloyDB vector search over tasks, notes, contacts (text-embedding-005, 768 dims).

Per-user Google OAuth — the agent asks you to sign in mid-chat, you paste the redirect URL back, done. No separate response formatter; each sub-agent owns its own output.

**Why it matters.** Hits all three hackathon tracks in one repo: agent framework (ADK + Gemini on Vertex), MCP integration (two custom servers), and managed DB (AlloyDB with vector search). Clean separation of concerns, deployable as one Cloud Run service.

**Repo:** `github.com/JannetEkka/smartdesk`

---

## 3. MedTestAI — AI Healthcare Test-Case Generator
**Status:** Live demo · **Stack:** Node.js/Express, React 18, Gemini 2.0 Flash, Cloud Run, Firebase Hosting · **Recognition:** Semi-finalist — Google Gen AI Exchange Hackathon 2025

**What it is.** Upload a healthcare requirements doc (PDF / TXT / MD) or type requirements in, pick a methodology (Agile / Waterfall / Hybrid) and compliance frameworks (HIPAA, FDA 21 CFR-11, GDPR, HITRUST, SOC2, ISO-13485/27001, ABDM) — Gemini returns structured test cases with preconditions, steps, expected results, compliance tags, and risk level. Export to CSV / JSON / Excel for JIRA or TestRail.

**Why it matters.** Combines my two backgrounds: healthcare-grade QA rigor and generative AI. Stateless architecture (no PHI stored), HTTPS-only, environment-var secrets, <$15/month at moderate use. Estimated 60-80% of QA time saved on test-case drafting — that was the pitch, and it lands because I've lived the problem.

**Live:** `pro-variety-472211-b9.web.app` · **Repo:** `github.com/JannetEkka/MedTestAI`

---

## 4. VerseCanvas — Poetry to AI Art
**Status:** Working app · **Stack:** Streamlit, Google Gemini 2.0 Flash, Imagen 3.0, PIL, Vertex AI

**What it is.** Paste a poem, get 1–3 background artworks with the poem overlaid — shareable in two clicks. Gemini extracts themes, mood, and visual elements; Imagen renders across six styles (photorealistic, watercolor, oil, digital, abstract, minimalist); PIL applies customizable text overlay (font, size, position, color, alignment). Supports 6 languages.

**Why it matters.** End-to-end creative AI pipeline — analysis, generation, post-processing — with careful attention to UX details most demos skip (text overlay enabled by default, brightness/contrast/blur controls, carousel navigation, one-click PNG export).

**Repo:** `github.com/JannetEkka/versecanvas`

---

## Common Threads

- **Google Cloud first.** Every project runs on GCP — Vertex AI, Cloud Run, Firebase, AlloyDB, GCS.
- **Agentic architectures.** Multi-agent orchestration (ADK), MCP servers, tool-calling LLMs, and mixed learned/reasoned systems (RL + Gemini).
- **QA DNA.** Tests, gates, watchdogs, nightly harnesses, graceful degradation — shipped, not just demoed.
- **AI-assisted development.** Claude Code in the loop for architecture, implementation, and debugging across all four repos.

---

*Contact: jannetaekka@gmail.com · [github.com/JannetEkka](https://github.com/JannetEkka) · [Portfolio](https://jannetekka.github.io/DSProjects/)*
