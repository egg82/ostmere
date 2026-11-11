#!/usr/bin/env bash
# run.sh <worktree> <name> [WxH] [maxMin]: the "was it seen" playthrough (play.mjs, probe.js) against a checkout's own
# server and client, in one Playwright container with its own loopback. Builds the checkout's client first.
# Needs SITE_PACKAGES (app/requirements.txt installed for the Playwright image's python3) and NODE_MODULES (holding
# playwright 1.56); ASSETS (the assets volume's copy, for the scene art) is optional. Writes OUT/<name>/ (default
# ./seen-runs): seen.json, events.json, shots/. Compare two runs with report.mjs. The server holds the game, so it
# needs DATABASE_URL (a migrated Postgres the container reaches) and ASHFALL_RATE_KEY, passed through from the caller.
set -uo pipefail
WT=$(cd "${1:?worktree}" && pwd)
name=${2:?name}
view=${3:-1280x800}
max=${4:-40}
: "${SITE_PACKAGES:?set SITE_PACKAGES}" "${NODE_MODULES:?set NODE_MODULES}"
OUT=${OUT:-$PWD/seen-runs}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"

podman run --rm --cpus=2 -v "$WT/app/client:/src:ro,z" -v "$WT/app/client:/out:z" docker.io/library/node:22-slim sh -c \
  'mkdir /c && cd /src && tar --exclude=node_modules --exclude=build -cf - . | tar -xf - -C /c && cd /c && npm ci --no-audit --no-fund >/tmp/ci.log 2>&1 && node build.mjs /out/build' \
  || { echo "client build failed"; exit 1; }

assets=()
if [ -n "${ASSETS:-}" ]; then assets=(-v "$ASSETS:/assets:ro,z" -e ASSETS_DIR=/assets); fi
podman run --rm --name "seen-$name" --cpus=2 --ipc=host \
  -v "$SITE_PACKAGES:/sp:ro,z" -v "$WT/app:/w:ro,z" -v "$WT/app/client/build:/w/ashfall_app/build/client:ro,z" \
  "${assets[@]}" -v "$OUT:/vp:z" -v "$NODE_MODULES:/node_modules:ro,z" -v "$HERE:/tool:ro,z" \
  -e PYTHONPATH=/sp:/w -e DATABASE_URL -e ASHFALL_RATE_KEY -w /w mcr.microsoft.com/playwright:v1.56.0-noble bash -c '
    python3 -m uvicorn ashfall_app.main:create_app --factory --host 127.0.0.1 --port 18771 > /vp/server-'"$name"'.log 2>&1 &
    H="import urllib.request;print(urllib.request.urlopen(\"http://127.0.0.1:18771/healthz\").read().decode())"
    for i in $(seq 1 60); do python3 -c "$H" >/dev/null 2>&1 && break; sleep 0.5; done
    python3 -c "$H" >/dev/null || { echo NO_SERVER; tail -30 /vp/server-'"$name"'.log; exit 1; }
    node /tool/play.mjs '"$name $view $max"'
    echo "SCRIPT_RC=$?"'
