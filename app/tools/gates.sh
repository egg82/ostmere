#!/usr/bin/env bash
# Every structural gate in docs/engineering.md's "Structural gates" table, plus CI's pyright, in one command; exits 1
# if any fails.
# tests/test_gates_command.py fails when a gate path in that table is missing from the lists below.
#
#   PATH=<venv>/bin:$PATH app/tools/gates.sh      # from anywhere; needs the dev requirements and `npm ci` in app/client
set -uo pipefail

APP=$(cd "$(dirname "$0")/.." && pwd)

PYTEST_GATES=(
  app/tests/test_file_size.py
  app/tests/test_text_size.py
  app/tests/test_function_size.py
  app/tests/test_suppressions.py
  app/tests/test_save_fields.py
  app/tests/opening/test_requires_shown.py
  app/tests/opening/test_player_only.py
  app/tests/opening/test_answer_gate.py
  app/tests/opening/test_pool_checks.py
  app/tests/test_boundaries.py
  app/tests/test_doc_citations.py
  app/tests/engine/test_design_index.py
  app/tests/test_decision_citations.py
  app/tests/test_canon_ids.py
  app/tests/test_scene_depth.py
  app/tests/test_scene_builds.py
  app/tests/test_scene_stores.py
  app/tests/test_scene_shown.py
  app/tests/test_scene_people.py
  app/tests/test_scene_sites.py
  app/tests/test_scene_lodging.py
  app/tests/test_ci_budget.py
)
CLIENT_GATES=(
  app/client/gates/function-size.mjs
)
PLANT_CHECK=app/tools/mutate_suite.py
JOURNAL_PLANTS=app/tests/journal_contract/plant_mutants.py

failed=()
step() {
  local name=$1
  shift
  echo "== $name"
  "$@" || failed+=("$name")
}

plants() {
  local suite bad=0
  python -m tools.mutate_suite --plants || bad=1
  python "${JOURNAL_PLANTS#app/}" --plants || bad=1
  for suite in $(python -c "from tools.mutate_suite import SUITES; print(*SUITES)"); do
    python -m tools.mutate_suite "$suite" --check || bad=1
  done
  return $bad
}

cd "$APP" || exit 1
step "python gates" python -m pytest -q -n 2 "${PYTEST_GATES[@]#app/}"
step "pyright" pyright
for gate in "${CLIENT_GATES[@]}"; do
  step "$gate" bash -c 'cd client && node --input-type=module -e "(await import(process.argv[1])).run()" "./${1#app/client/}"' _ "$gate"
done
step "$PLANT_CHECK" plants

if [ ${#failed[@]} -gt 0 ]; then
  echo "GATES FAILED: ${failed[*]}" >&2
  exit 1
fi
echo "all gates passed"
