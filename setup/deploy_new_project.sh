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
    # "..." is the placeholder from the docs; pasting it verbatim is easy to do
    # and otherwise surfaces much later as an opaque auth failure.
    if [[ -z "${GOOGLE_API_KEY:-}" || "${GOOGLE_API_KEY}" == "..." ]]; then
      warn "EMBEDDER=gemini but GOOGLE_API_KEY is unset or still the placeholder."
      warn "Get a free key at https://aistudio.google.com/apikey, then re-run: $0 env"
    else
      echo "GOOGLE_API_KEY=${GOOGLE_API_KEY}" >> "$ENV_FILE"
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
    return 1
  fi

  # Catch the documentation placeholder being pasted verbatim, which otherwise
  # fails several commands later with an opaque DNS error on the host "HOST".
  if [[ "$DATABASE_URL" == *"USER:PASSWORD@HOST"* || "$DATABASE_URL" == *"DBNAME"* ]]; then
    echo "ERROR: DATABASE_URL still contains the placeholder from the docs:" >&2
    echo "  $DATABASE_URL" >&2
    echo "Replace USER, PASSWORD, HOST and DBNAME with a real Postgres that has" >&2
    echo "pgvector, then re-run: $0 db" >&2
    return 1
  fi

  # Fail early on missing packages rather than after the schema is half applied.
  if ! python3 -c "import sqlalchemy, pg8000" 2>/dev/null; then
    echo "ERROR: Python dependencies are missing. Install them with:" >&2
    echo "  pip install -r requirements.txt" >&2
    echo "(requirements-eval.txt is only needed for EMBEDDER=local or the" >&2
    echo " cross-encoder reranker — it pulls PyTorch, several hundred MB.)" >&2
    return 1
  fi

  # psql needs a plain postgresql:// URL; the app uses the +pg8000 driver form.
  local psql_url="${DATABASE_URL/+pg8000/}"

  echo "Creating extension and tables..."
  if ! psql "$psql_url" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS vector;"; then
    echo "ERROR: could not connect, or pgvector is unavailable on this server." >&2
    echo "Check the host is reachable and the database supports the vector" >&2
    echo "extension. Managed Postgres usually needs it enabled explicitly." >&2
    return 1
  fi

  # setup_alloydb.sql uses AlloyDB's in-database embedding() function, which
  # stock Postgres lacks. Its tables are created by ingest.py anyway, so a
  # failure here is expected off AlloyDB and is not fatal.
  psql "$psql_url" -f "$REPO_ROOT/setup/setup_alloydb.sql" >/dev/null 2>&1 || \
    warn "setup_alloydb.sql skipped (expected off AlloyDB: it uses embedding())."

  # Ingest BEFORE the chunks migration, not after. ingest.py creates both the
  # notes table and note_chunks, sized to the active embedder's dimension. The
  # migration declares a foreign key to notes, so running it first against a
  # fresh database fails with 'relation "notes" does not exist' — which is
  # exactly what happens when setup_alloydb.sql could not create notes either.
  #
  # Deliberately no --reset: that drops the notes table. Ingest is idempotent
  # via ON CONFLICT, so re-running is safe on a database with real notes in it.
  echo "Ingesting the eval corpus..."
  if ! ( cd "$REPO_ROOT" && SMARTDESK_EMBEDDER="$EMBEDDER" DATABASE_URL="$DATABASE_URL" \
      python3 evals/ingest.py --title-prefix ); then
    echo "ERROR: ingest failed. Nothing further will work until this does." >&2
    return 1
  fi

  # Now that notes exists, the migration is a no-op on a fresh database
  # (CREATE TABLE IF NOT EXISTS) and does real work only on an existing
  # AlloyDB deployment that predates chunking.
  psql "$psql_url" -v ON_ERROR_STOP=1 -f "$REPO_ROOT/setup/migrations/001_note_chunks.sql" \
    >/dev/null 2>&1 || warn "chunks migration reported an error (harmless if ingest already created note_chunks)."
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
    # if/else, not `A && B || C`: with the latter, a *failing* stage_db falls
    # through to the C branch and reports "DATABASE_URL not set", which is a
    # lie when the real problem was an unreachable host or a missing package.
    if [[ -n "${DATABASE_URL:-}" ]]; then
      stage_db || warn "db stage failed — fix the cause and re-run: $0 db"
    else
      warn "Skipping db: DATABASE_URL not set."
    fi
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
