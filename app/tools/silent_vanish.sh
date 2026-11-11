#!/usr/bin/env bash
# The silent-vanish tests (tests/db/test_silent_vanish.py): a Postgres in a network namespace of its own, and the test
# run inside that namespace, which asks this script to drop every packet there (iptables, as the namespace's root via
# podman unshare). Local only; CI has no such privilege, so the tests skip there. `podman pause` would not do: the host
# kernel still acknowledges a paused member's packets.
#
#   PATH=<venv>/bin:$PATH app/tools/silent_vanish.sh [test...]   # each test on a fresh Postgres (xstcp-pg, port 55460, tmpfs)
set -euo pipefail

IMAGE_PG=${IMAGE_PG:-docker.io/library/postgres:17}
APP=$(cd "$(dirname "$0")/.." && pwd)
SIG=$(mktemp -d)

down() {
  podman rm -f -v xstcp-pg >/dev/null 2>&1 || true
  rm -rf "$SIG"
}
trap down EXIT

netns() {
  local ns
  ns=$(podman inspect -f '{{.NetworkSettings.SandboxKey}}' xstcp-pg)
  [ -n "$ns" ] || { echo "silent_vanish: no network namespace for xstcp-pg" >&2; return 1; }
  echo "$ns"
}

up() {
  podman rm -f -v xstcp-pg >/dev/null 2>&1 || true
  podman run -d --name xstcp-pg --network none --tmpfs /var/lib/postgresql/data:rw,size=128m \
    -e POSTGRES_HOST_AUTH_METHOD=trust "$IMAGE_PG" postgres -p 55460 -c listen_addresses=127.0.0.1 \
    -c shared_buffers=32MB -c fsync=off >/dev/null
  for _ in $(seq 60); do
    if podman exec xstcp-pg pg_isready -q -h 127.0.0.1 -p 55460 -U postgres 2>/dev/null; then return 0; fi
    sleep 0.5
  done
  echo "silent_vanish: xstcp-pg never became ready" >&2
  return 1
}

drop_packets() {
  podman unshare nsenter --net="$1" sh -c 'iptables -I INPUT -j DROP && iptables -I OUTPUT -j DROP'
}

run() {
  local tests status=0 test_pid ns
  if [ $# -gt 0 ]; then tests=("$@"); else mapfile -t tests < <(grep -oP "^def \Ktest_\w+" "$APP/tests/db/test_silent_vanish.py"); fi
  [ "${#tests[@]}" -gt 0 ] || { echo "silent_vanish: found no tests" >&2; return 1; }
  for t in "${tests[@]}"; do
    up
    ns=$(netns)
    rm -f "$SIG/drop" "$SIG/dropped"
    (cd "$APP" && ASHFALL_VANISH="$SIG" podman unshare nsenter --net="$ns" \
      python -m pytest -q -rA -n 0 -p no:cacheprovider "tests/db/test_silent_vanish.py::$t") &
    test_pid=$!
    while kill -0 "$test_pid" 2>/dev/null; do
      if [ -e "$SIG/drop" ] && [ ! -e "$SIG/dropped" ]; then drop_packets "$ns" && touch "$SIG/dropped"; fi
      sleep 0.1
    done
    wait "$test_pid" || status=1
  done
  return $status
}

run "$@"
