#!/usr/bin/env bash
# One-time setup for disco_server on a Raspberry Pi (or any Debian-based
# host): installs system dependencies, syncs the Python environment,
# initializes the database, and installs+starts a systemd service so it
# survives reboots. Safe to re-run — every step is idempotent.
#
# Assumes you've already `git clone`d the repo and are running this from
# inside it (see README.md's "Deploying disco_server to a Raspberry Pi"
# section for the full picture, and scripts/redeploy-disco-server.sh for
# pulling and applying future updates once this has run).
set -euo pipefail

SERVICE_NAME="disco-server"
SERVICE_USER="$(whoami)"
API_URL="http://localhost:5000/api/tracks"

export PATH="$HOME/.local/bin:$PATH"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="$REPO_ROOT/src/disco_server"

echo "==> Installing system dependencies (vlc, git)"
sudo apt-get update
sudo apt-get install -y vlc git

if ! command -v uv > /dev/null 2>&1; then
    echo "==> Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "==> uv already installed, skipping"
fi

echo "==> Syncing disco_shared"
(cd "$REPO_ROOT/src/disco_shared" && uv sync)

echo "==> Syncing disco_server"
(cd "$SERVER_DIR" && uv sync --extra deploy)

echo "==> Initializing the database (safe to re-run)"
(cd "$SERVER_DIR" && uv run flask --app disco_server init-db)

echo "==> Installing systemd service"
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=PanicDisco server
After=network.target sound.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${SERVER_DIR}
ExecStart=${SERVER_DIR}/.venv/bin/waitress-serve --host=0.0.0.0 --port=5000 --call disco_server:create_app
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

echo "==> Enabling and starting $SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

echo "==> Waiting for it to come up"
for _ in $(seq 1 10); do
    if curl -sf "$API_URL" > /dev/null; then
        echo "==> $SERVICE_NAME is up and responding at $API_URL"
        exit 0
    fi
    sleep 1
done

echo "error: $SERVICE_NAME did not respond at $API_URL within 10s — check 'systemctl status $SERVICE_NAME' and 'journalctl -u $SERVICE_NAME'" >&2
exit 1
