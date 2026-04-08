#!/bin/bash
# SmartDesk — Environment Setup Script
# Pattern from docs/adk.md — Codelab 2, "Set up environment variables"
# Run this in Google Cloud Shell to configure your project

set -e

echo "=== SmartDesk Environment Setup ==="

# 1. Set the variables in your terminal first
# Pattern from docs/adk.md — Codelab 2
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=smartdesk-cr-service

echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"

# 2. Enable required APIs
# Pattern from docs/adk.md — Codelab 2, "Enable APIs"
echo ""
echo "Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com \
  alloydb.googleapis.com \
  servicenetworking.googleapis.com

echo "APIs enabled successfully."

# 3. Create the .env file using those variables
# Pattern from docs/adk.md — Codelab 2, "Create the .env file"
echo ""
echo "Creating .env file..."
cat <<EOF > smartdesk_agent/smartdesk_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL=gemini-2.5-flash
EOF

echo ".env file created at smartdesk_agent/smartdesk_agent/.env"

# 4. Check the .env file
echo ""
echo "Verify .env contents:"
cat smartdesk_agent/smartdesk_agent/.env

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Add AlloyDB connection details to .env:"
echo "   DATABASE_URL=postgresql+pg8000://postgres:YOUR_PASSWORD@YOUR_ALLOYDB_IP:5432/postgres"
echo "2. Set up AlloyDB cluster (see docs/alloydb.md)"
echo "3. Run setup/setup_alloydb.sql in AlloyDB Studio"
echo "4. Add MCP server URLs to .env (GMAIL_MCP_URL, CALENDAR_MCP_URL)"
echo "5. Run: cd smartdesk_agent && adk web"
