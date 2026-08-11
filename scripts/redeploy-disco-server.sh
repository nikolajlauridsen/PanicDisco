#!/usr/bin/env bash
# Redeploys disco_server on the Raspberry Pi: pulls the latest code, re-syncs
# disco_shared and disco_server, restarts the systemd service, and checks it
# actually came back up. The Tailwind stylesheet is a committed build
# artifact (see README.md's "Frontend (Tailwind CSS)" section), so `git pull`
# alone brings the current styling — no Node/npm needed on the Pi at all. See
# README.md's "Deploying disco_server to a Raspberry Pi" section for the
# one-time setup this assumes is already done (uv installed, venvs created,
# the disco-server.service unit in place — see scripts/install-disco-server.sh).
set -euo pipefail

SERVICE_NAME="disco-server"
API_URL="http://localhost:5000/api/tracks"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Checking for local changes in $REPO_ROOT"
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "error: uncommitted changes present — commit, stash, or discard them before redeploying" >&2
    exit 1
fi

echo "==> Pulling latest changes"
git pull --ff-only

echo "==> Syncing disco_shared"
(cd src/disco_shared && uv sync)

echo "==> Syncing disco_server"
(cd src/disco_server && uv sync --extra deploy)

echo "==> Restarting $SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "==> Waiting for it to come back up"
for _ in $(seq 1 10); do
    if curl -sf "$API_URL" > /dev/null; then
        echo "==> $SERVICE_NAME is up and responding at $API_URL"
        exit 0
    fi
    sleep 1
done

echo "error: $SERVICE_NAME did not respond at $API_URL within 10s — check 'systemctl status $SERVICE_NAME' and 'journalctl -u $SERVICE_NAME'" >&2
exit 1
