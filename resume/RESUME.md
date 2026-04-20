# Jannet Ekka

**AI Engineer | Ex-QA | Google Cloud + Agentic AI**

Bangalore / Remote · jannetaekka@gmail.com · [github.com/JannetEkka](https://github.com/JannetEkka) · [Portfolio](https://jannetekka.github.io/DSProjects/)

---

## Summary

AI engineer with 4 years of QA engineering at Deloitte and a PGP in AI/ML, now shipping production-grade agentic systems on Google Cloud. I build with Gemini, Vertex AI, ADK, and MCP — and I use Claude Code end-to-end for architecture, implementation, and debugging. Comfortable across Python, Go, JavaScript, React, Cloud Run, AlloyDB, and GitHub workflows. Recent work: a live 24/7 crypto trading agent (1st place, two hackathons), a multi-agent Google Workspace assistant, an AI healthcare test-case generator, and a poetry-to-image app. Looking for AI engineering roles at startups and teams where AI-assisted development is the norm.

---

## Skills

**AI / Agents** · Gemini 2.0/2.5, Vertex AI, Google ADK, Model Context Protocol (MCP), Imagen 3.0, text-embedding-005, RAG, vector search, prompt engineering, multi-agent orchestration, RL (GradientBoosting on trading data)

**Cloud / Infra** · Google Cloud Platform, Cloud Run, Firebase Hosting, AlloyDB (pgvector), GCS, Docker, docker-compose, GitHub Actions

**Languages** · Python, Go, JavaScript / TypeScript, Node.js, SQL, Bash

**Web / Apps** · React 18, Express, Streamlit, REST APIs, OAuth 2.0

**QA / Testing** · Selenium, PyTest, test automation frameworks, API testing, regression suites, HIPAA / FDA / GDPR / SOC2 test design

**AI-Assisted Dev** · Claude Code (daily driver), Claude API, GitHub Copilot, `gh` CLI, Git workflow at scale

---

## Experience

### Deloitte USI Consulting — QA Engineer, Analyst
*2019 – 2023 · Hyderabad, India*

- Owned functional and regression testing for enterprise client applications across web and API layers.
- Built and maintained Selenium automation suites in **Python, Go, and JavaScript**, cutting manual regression time and catching defects pre-release.
- Wrote test strategies, acceptance criteria, and compliance-aware test cases for audited domains.
- Collaborated daily with devs, BAs, and PMs across US/India time zones — shaped my bias for clear async communication and tight feedback loops.

---

## Selected Projects (Hackathons & Builds)

### SMT — Autonomous Crypto Trading Agent *(1st place · OpenServ Hackathon 2025 · 1st semifinals · WEEX AI Wars 2026)*
Three independent trading systems running 24/7 on GCP: a 6-persona Gemini-ensemble daemon, a GradientBoosting RL agent that learns from daemon trades, and a pure-Gemini agentic trader. Python, Vertex AI (Gemini 2.5 Flash), WEEX API, GCS, Cloud VM. Ships features like hot-reload settings, 15-gate trade filters, three-lane execution (slow/fast/recovery), and separate position books per system.
→ `github.com/JannetEkka/smt-weex-trading-bot`

### SmartDesk — Multi-Agent Productivity Assistant *(Google APAC Hackathon 2026 — submitted)*
Single chat interface backed by a team of ADK agents. Root orchestrator routes to inbox (Gmail MCP), planner (Calendar MCP), and data agent (AlloyDB vector search over tasks / notes / contacts). Per-user OAuth, Gemini 2.5 Flash, text-embedding-005, deployed on Cloud Run.
→ `github.com/JannetEkka/smartdesk`

### MedTestAI — Healthcare Test-Case Generator *(Semi-finalist · Google Gen AI Exchange Hackathon 2025)*
Generates HIPAA-aware test cases from healthcare requirement docs (PDF/TXT/MD) using Gemini 2.0 Flash. 8 compliance frameworks (HIPAA, FDA 21 CFR-11, GDPR, HITRUST, SOC2, ISO-13485/27001, ABDM). Node/Express on Cloud Run + React on Firebase. CSV / JSON / Excel export for JIRA / TestRail. Live: `pro-variety-472211-b9.web.app`.
→ `github.com/JannetEkka/MedTestAI`

### VerseCanvas — Poetry → AI Art
Gemini 2.0 analyzes theme/mood/imagery, Imagen 3.0 renders it across 6 art styles, PIL overlays the poem text. 6 languages, mood-intensity control, downloadable PNG. Streamlit on Vertex AI.
→ `github.com/JannetEkka/versecanvas`

---

## Education

**PGP in Artificial Intelligence & Machine Learning** — Great Learning
*Certificates from McCombs School of Business (UT Austin) & Great Lakes Institute of Management, Chennai* · 2024 – 2025

**B.Tech, Information Technology (CSE)** — KIIT University, Odisha · 2015 – 2019

---

## Community

**Google Developer Group** — active member, 2025 – present

---

## Notes for Hiring Managers

I build with AI assistants in the loop (Claude Code, Claude API) and I'm looking for teams that treat that as a feature, not a footnote. My QA background means I ship things that actually work — not just demos — and my recent projects have been designed, built, and shipped end-to-end with agentic tooling. Happy to walk through any repo live.
