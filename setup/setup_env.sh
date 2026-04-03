#!/bin/bash
# SmartDesk — Environment Setup Script
# Run this in Google Cloud Shell to configure your project

set -e

echo "=== SmartDesk Environment Setup ==="

# Get project details
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"

# Enable required APIs
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

# Create .env file
echo ""
echo "Creating .env file..."
cat <<EOF > smartdesk_agent/smartdesk_app/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
EOF

echo ".env file created at smartdesk_agent/smartdesk_app/.env"
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Set up AlloyDB cluster (see docs/alloydb.md)"
echo "2. Add AlloyDB connection details to .env"
echo "3. Run setup/setup_alloydb.sql in AlloyDB Studio"
echo "4. Run: cd smartdesk_agent && adk web"
