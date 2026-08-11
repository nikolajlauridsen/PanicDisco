#!/usr/bin/env bash
# Runs every test suite across all packages: disco_shared, disco_client
# (mocked), disco_server (integration), and the real end-to-end suite
# (disco_client against a live disco_server). Syncs each package first, so
# this works from a fresh clone with nothing set up yet. Runs everything
# even if an earlier suite fails, then reports a summary at the end.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export PATH="$HOME/.local/bin:$PATH"

echo "==> Syncing disco_shared"
(cd src/disco_shared && uv sync --extra dev) || exit 1

echo "==> Syncing disco_server (dev + e2e extras)"
(cd src/disco_server && uv sync --extra dev --extra e2e) || exit 1

echo "==> Syncing disco_client"
(cd src/disco_client && uv sync --extra dev) || exit 1

FAILED=()

run_suite() {
    local name="$1"
    shift
    echo
    echo "==> Running $name"
    if "$@"; then
        echo "==> $name: PASSED"
    else
        echo "==> $name: FAILED"
        FAILED+=("$name")
    fi
}

run_suite "disco_shared"               src/disco_shared/.venv/bin/python -m pytest tests/disco_shared -v
run_suite "disco_client (mocked)"      src/disco_client/.venv/bin/python -m pytest tests/disco_client -v
run_suite "disco_server (integration)" src/disco_server/.venv/bin/python -m pytest tests/integration -v
run_suite "e2e (real HTTP)"            src/disco_server/.venv/bin/python -m pytest tests/e2e -v

rm -rf src/disco_server/instance

echo
if [ ${#FAILED[@]} -eq 0 ]; then
    echo "==> All test suites passed"
    exit 0
fi

echo "==> Failed: ${FAILED[*]}"
exit 1
