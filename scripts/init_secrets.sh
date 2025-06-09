#!/bin/bash
# Initialize Docker secrets for MCP production

set -euo pipefail

create_secret() {
  local name="$1" value="$2"
  if docker secret inspect "$name" >/dev/null 2>&1; then
    echo "Secret $name already exists" >&2
  else
    echo "$value" | docker secret create "$name" - >/dev/null
    echo "Created secret $name" >&2
  fi
}

# Required environment variables
: "${GITHUB_TOKEN:?Need GITHUB_TOKEN}"
: "${POSTGRES_URL:?Need POSTGRES_URL}"
: "${GRAFANA_PASSWORD:?Need GRAFANA_PASSWORD}"

create_secret github_token "$GITHUB_TOKEN"
create_secret postgres_url "$POSTGRES_URL"
create_secret grafana_password "$GRAFANA_PASSWORD"

# Create additional encryption key if not exists
if ! docker secret inspect encryption_key >/dev/null 2>&1; then
  openssl rand -base64 32 | docker secret create encryption_key - >/dev/null
  echo "Generated encryption_key" >&2
fi

