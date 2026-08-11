#!/usr/bin/env bash
# Thin wrapper for tests/manual/track_manager.py so you don't have to spell
# out disco_client's venv path every time. Needs disco_client synced first
# (uv sync --extra dev in src/disco_client) and a disco_server instance
# already running (see README.md's Getting started).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

exec "$REPO_ROOT/src/disco_client/.venv/bin/python" "$REPO_ROOT/tests/manual/track_manager.py" "$@"
