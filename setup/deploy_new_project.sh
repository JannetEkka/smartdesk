#!/usr/bin/env bash
#
# SmartDesk — set up and deploy into a fresh GCP project from Cloud Shell.
#
# Runs in stages so you can re-run one without redoing everything. Every stage
# is safe to run twice.
#
#   ./setup/deploy_new_project.sh all        # everything (except OAuth, see below)
#   ./setup/deploy_new_project.sh apis       # enable required APIs
#   ./setup/deploy_new_project.sh iam        # service account + roles
#   ./setup/deploy_new_project.sh env        # write smartdesk_app/.env
#   ./setup/deploy_new_project.sh db         # apply schema + ingest the corpus
#   ./setup/deploy_new_project.sh deploy     # deploy to Cloud Run
#   ./setup/deploy_new_project.sh url        # print the service URL
#
# ONE STEP CANNOT BE SCRIPTED: the OAuth client. OAuth clients are per-project,
# so the old project's client_secret.json will not work. Stage `oauth` prints
# what to click.
#
# Configure by exporting these before running (all have defaults):
#
#   PROJECT_ID     defaults to your current gcloud project
#   REGION         default us-central1
#   SERVICE_NAME   default smartdesk
#   DATABASE_URL   required for `db` and `deploy` — see setup/README for options
#   EMBEDDER       vertex (default) | gemini | local
#   GOOGLE_API_KEY required when EMBEDDER=gemini
#
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || true)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-smartdesk}"
SA_NAME="${SA_NAME:-smartdesk-cr-service}"
EMBEDDER="${EMBEDDER:-vertex}"
MODEL="${MODEL:-gemini-2.5-flash}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/smartdesk_agent/smartdesk_app/.env"

SERVICE_ACCOUNT="${SA_NAME}@${PROJECT_ID:-unset}.iam.gserviceaccount.com"

info() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[33m!!  %s\033[0m\n' "$*"; }

usage() { sed -n '2,30p' "$0" | sed 's/^#\{1,2\} \?//'; }

# Checked per-stage rather than at load, so `help` works without a project set.
require_project() {
  if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: no project set. Either:" >&2
    echo "  gcloud config set project YOUR_PROJECT_ID" >&2
    echo "  export PROJECT_ID=YOUR_PROJECT_ID" >&2
    exit 1
  fi
}

# ---------------------------------------------------------------------------

stage_apis() {
  require_project
  info "Enabling APIs on $PROJECT_ID (takes a minute)"
  gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    iamcredentials.googleapis.com \
    --project "$PROJECT_ID"
  echo "APIs enabled."
  warn "AlloyDB not enabled by default — it has no free tier and bills"
  warn "continuously. Enable it only if you chose AlloyDB:"
  warn "  gcloud services enable alloydb.googleapis.com servicenetworking.googleapis.com"
}

stage_iam() {
  require_project
  info "Creating service account $SERVICE_ACCOUNT"
  if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project "$PROJECT_ID" &>/dev/null; then
    echo "Already exists, skipping creation."
  else
    gcloud iam service-accounts create "$SA_NAME" \
      --display-name="SmartDesk Cloud Run service" \
      --project "$PROJECT_ID"
  fi

  info "Granting roles"
  # Vertex AI: calling Gemini and the embedding model.
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user" --condition=None --quiet
  # AlloyDB client: only needed if you are using AlloyDB. Harmless otherwise.
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/alloydb.client" --condition=None --quiet
  # Logging, so the service can write logs.
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter" --condition=None --quiet
  echo "Roles granted."
}

stage_oauth() {
  require_project
  info "OAuth client — this part is manual, the API cannot create it"
  cat <<EOF

OAuth clients are per-project. The old project's client_secret.json will NOT
work here. In the Cloud Console for project $PROJECT_ID:

  1. APIs & Services -> OAuth consent screen
       User type: External
       Add your Gmail addresses under "Test users" (required while the app is
       unverified — anyone not listed gets a 403 on sign-in)
       Scopes: Gmail and Calendar scopes as used by mcp_servers/auth.py

  2. APIs & Services -> Credentials -> Create credentials
       -> OAuth client ID -> Web application
       Add an authorised redirect URI. For local testing:
           http://localhost:8000/
       After deploying, add your Cloud Run URL too.

  3. Download the JSON and save it as:
       smartdesk_agent/smartdesk_app/client_secret.json

  4. Delete any stale token from the old project:
       rm -f smartdesk_agent/smartdesk_app/token.json

EOF
}

stage_env() {
  require_project
  info "Writing $ENV_FILE"
  mkdir -p "$(dirname "$ENV_FILE")"

  local use_vertex="TRUE"
  [[ "$EMBEDDER" == "gemini" ]] && use_vertex="FALSE"

  cat > "$ENV_FILE" <<EOF
# Generated by setup/deploy_new_project.sh
GOOGLE_GENAI_USE_VERTEXAI=${use_vertex}
GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
GOOGLE_CLOUD_LOCATION=${REGION}
PROJECT_ID=${PROJECT_ID}
SA_NAME=${SA_NAME}
SERVICE_ACCOUNT=${SERVICE_ACCOUNT}
MODEL=${MODEL}

# Retrieval
SMARTDESK_EMBEDDER=${EMBEDDER}
SMARTDESK_RETRIEVAL=baseline
EOF

  if [[ -n "${DATABASE_URL:-}" ]]; then
    echo "DATABASE_URL=${DATABASE_URL}" >> "$ENV_FILE"
  else
    warn "DATABASE_URL not set — add it to $ENV_FILE before deploying."
  fi

  if [[ "$EMBEDDER" == "gemini" ]]; then
    if [[ -n "${GOOGLE_API_KEY:-}" ]]; then
      echo "GOOGLE_API_KEY=${GOOGLE_API_KEY}" >> "$ENV_FILE"
    else
      warn "EMBEDDER=gemini but GOOGLE_API_KEY is not set."
      warn "Get one at https://aistudio.google.com/apikey"
    fi
  fi

  echo "Written. Contents (secrets masked):"
  sed -E 's/(PASSWORD|API_KEY)=.*/\1=***/; s#(://[^:]+:)[^@]+@#\1***@#' "$ENV_FILE"
}

stage_db() {
  info "Applying schema and ingesting the corpus"
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "ERROR: DATABASE_URL is required for this stage." >&2
    echo "Any Postgres with pgvector works. Examples:" >&2
    echo "  postgresql+pg8000://user:pw@host:5432/dbname" >&2
    exit 1
  fi

  # psql needs a plain postgresql:// URL; the app uses the +pg8000 driver form.
  local psql_url="${DATABASE_URL/+pg8000/}"

  echo "Creating extension and tables..."
  psql "$psql_url" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS vector;"
  psql "$psql_url" -v ON_ERROR_STOP=1 -f "$REPO_ROOT/setup/setup_alloydb.sql" || \
    warn "setup_alloydb.sql failed — it uses AlloyDB's embedding() function."
  psql "$psql_url" -v ON_ERROR_STOP=1 -f "$REPO_ROOT/setup/migrations/001_note_chunks.sql"

  echo "Ingesting the eval corpus..."
  ( cd "$REPO_ROOT" && SMARTDESK_EMBEDDER="$EMBEDDER" DATABASE_URL="$DATABASE_URL" \
      python3 evals/ingest.py --title-prefix )
}

stage_deploy() {
  require_project
  info "Deploying to Cloud Run as $SERVICE_NAME"

  # A YAML file rather than --set-env-vars: DATABASE_URL contains '@' and ':'
  # and a password may contain a comma, all of which collide with gcloud's
  # delimiter syntax. The file sidesteps quoting entirely.
  local vars_file
  vars_file="$(mktemp)"
  # Never leave a file containing the DB password and API key lying around.
  trap 'rm -f "$vars_file"' RETURN

  {
    echo "GOOGLE_CLOUD_PROJECT: \"${PROJECT_ID}\""
    echo "GOOGLE_CLOUD_LOCATION: \"${REGION}\""
    echo "MODEL: \"${MODEL}\""
    echo "SMARTDESK_EMBEDDER: \"${EMBEDDER}\""
    echo "SMARTDESK_RETRIEVAL: \"${SMARTDESK_RETRIEVAL:-baseline}\""
    if [[ "$EMBEDDER" == "gemini" ]]; then
      echo "GOOGLE_GENAI_USE_VERTEXAI: \"FALSE\""
      [[ -n "${GOOGLE_API_KEY:-}" ]] && echo "GOOGLE_API_KEY: \"${GOOGLE_API_KEY}\""
    else
      echo "GOOGLE_GENAI_USE_VERTEXAI: \"TRUE\""
    fi
    [[ -n "${DATABASE_URL:-}" ]] && echo "DATABASE_URL: \"${DATABASE_URL}\""
  } > "$vars_file"

  gcloud run deploy "$SERVICE_NAME" \
    --source "$REPO_ROOT" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --service-account "$SERVICE_ACCOUNT" \
    --allow-unauthenticated \
    --min-instances 0 \
    --memory 1Gi \
    --timeout 300 \
    --env-vars-file "$vars_file"

  stage_url
}

stage_url() {
  require_project
  local url
  url="$(gcloud run services describe "$SERVICE_NAME" \
    --project "$PROJECT_ID" --region "$REGION" \
    --format='value(status.url)' 2>/dev/null || true)"
  if [[ -z "$url" ]]; then
    warn "Service not deployed yet."
    return
  fi
  info "Service URL"
  echo "  $url"
  echo
  echo "The Dockerfile runs 'adk api_server', so this serves the API with no UI."
  echo "For the ADK web UI, redeploy with:"
  echo "  cd smartdesk_agent && adk deploy cloud_run \\"
  echo "    --project=$PROJECT_ID --region=$REGION \\"
  echo "    --service_name=$SERVICE_NAME --with_ui ./smartdesk_app"
  echo
  warn "Add $url to the OAuth client's authorised redirect URIs,"
  warn "and add every tester's email to the consent screen test user list."
}

# ---------------------------------------------------------------------------

case "${1:-all}" in
  -h|--help|help) usage ;;
  apis)   stage_apis ;;
  iam)    stage_iam ;;
  oauth)  stage_oauth ;;
  env)    stage_env ;;
  db)     stage_db ;;
  deploy) stage_deploy ;;
  url)    stage_url ;;
  all)
    stage_apis
    stage_iam
    stage_env
    [[ -n "${DATABASE_URL:-}" ]] && stage_db || warn "Skipping db: DATABASE_URL not set."
    stage_oauth
    echo
    warn "Set up the OAuth client above, then run: $0 deploy"
    ;;
  *)
    echo "Unknown stage: $1" >&2
    echo >&2
    usage >&2
    exit 1
    ;;
esac
