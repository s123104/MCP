#!/bin/bash
# Rotate GitHub token secret
set -euo pipefail

ROTATION_INTERVAL="${ROTATION_INTERVAL:-86400}" # seconds, default 24h
SERVICE_NAME="${SERVICE_NAME:-github-mcp}"

rotate_github_token() {
  : "${NEW_GITHUB_TOKEN:?Need NEW_GITHUB_TOKEN}"
  echo "$NEW_GITHUB_TOKEN" | docker secret create github_token_new - >/dev/null
  docker service update --secret-rm github_token --secret-add source=github_token_new,target=github_token "$SERVICE_NAME" >/dev/null
  sleep 60
  docker secret rm github_token >/dev/null
  docker secret create github_token - <<<"$NEW_GITHUB_TOKEN" >/dev/null
  docker secret rm github_token_new >/dev/null
}

while true; do
  rotate_github_token
  sleep "$ROTATION_INTERVAL"
done

