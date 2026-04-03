# SmartDesk — Container for Cloud Run deployment
# Note: Preferred deployment is via `adk deploy cloud_run` CLI (docs/adk.md — Codelab 2)
# This Dockerfile is for manual builds if needed

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY smartdesk_agent/ ./smartdesk_agent/

ENV PORT=8080

CMD ["adk", "api_server", "--port", "8080", "smartdesk_agent"]
