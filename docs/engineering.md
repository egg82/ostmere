# Engineering

How the code is built and shipped. habits is an earlier agent-built app by the same owner; each rule below
is something it started the other way and later had to undo, so here it holds from the first line of code. Game
design is in `decisions/`, indexed by `decisions.md`.

## The pipeline

Every change reaches `main` through a pull request (`gh pr create`), and branch protection requires the `ci-ok` job,
which fails unless every job the run was meant to run passed. `.github/workflows/ci.yml` runs on every pull request
and every push to `main`. Its `changes` job sorts the run: a pull request that changes only `docs/`, top-level
Markdown or `LICENSE` runs `docs` (the citation tests and the household-names guard), and anything else runs the
per-PR set: `tests` (two shards, on a `postgres:18.6` container, production's version), `shards-cover`,
`playthrough-smoke` (the opening's representative routes), `engine-bench`, `saves-forward`, strict `pyright` and
`client`, while `app-image` builds `app/Containerfile` beside them. The whole-game playthroughs (`playthrough`,
`chapter-saves`, `playthrough-week-one`, `playthrough-week-one-saved`, `playthrough-week-two`) are the full run:
nightly on `main`, on a pull request labelled `playthroughs`, and on a manual dispatch. Label a pull request whose
change a balance or pacing invariant could catch when it should not wait for the night. A pull request builds the
image and pushes nothing. On `main` the image is pushed by
digest alone, and once `ci-ok` is green `release` tags that digest `dev` and `main-<sha8>-<commit ts>`, so the deploy
waits for green; commit timestamps may not go backwards, because the tags are ordered by string, and `release` refuses
a commit older than its parent. Publishing a GitHub release tags the same image `<version>` and `latest`
(`.github/workflows/container-release.yml`). The nightly run (`.github/workflows/nightly.yml`) is the full run plus
`tests-deep`, the deep Hypothesis profile and every route and seed; its reds are real breaks on `main` and are fixed
the next day.

Images go to two registries, `docker.io/<DOCKERHUB_USERNAME>/ostmere` and `ghcr.io/<owner>/ostmere`, named once in the
workflow's `DOCKERHUB_REPO` and `GHCR_REPO`. The repository needs one variable, `DOCKERHUB_USERNAME`, and two secrets:
`DOCKERHUB_TOKEN` (a Docker Hub access token with write access) and `OSTMERE_HOUSEHOLD_NAMES` (for
`app/tests/test_household_names.py`); GHCR uses the workflow's own `GITHUB_TOKEN`.

Flux image automation picks the newest `main-` tag of `ghcr.io/egg82/ostmere`, writes it to the cluster repo, and rolls
the Deployment, whose migrate init container runs `python -m ashfall_app.db migrate` from the same image.
`ostmere.yggdrasil.pub` reaches it through the gateway inside the network and a tunnel outside it. The old host
`ashfall.yggdrasil.pub` still reaches both tiers and gets a 301 to the new one (`app/ashfall_app/old_host.py`).
Secrets live in the deployment's secret store, read by External Secrets, never in either repo.

Scene art is seeded onto the assets volume by hand, so after `release` a push to `main` runs `scene-art-drift`: it
compares the `source` digest in the manifest served live with the one `tools/scene/drift.py` computes from the pushed
sha's generator modules, and shows a warning (never a red run, never a reseed) when they differ or the manifest cannot
be read. `app/tools/seed_assets.sh` seeds every site named in `SITES` (kubeconfig contexts, required) in one run: the
first from `$ASHFALL_ASSETS` (refusing when its volume already holds more files in any kind), each later one by
streaming `tar` from the first site's running `web` pod into the cluster repo's seed Job (`JOB_MANIFEST`, required).
Each site's volume (`art/`, `journal/`, `audio/`, whichever exist) must match the source's file count and bytes per
kind or the run stops there with a non-zero exit; a later site whose namespace does not exist yet is skipped with a
warning. `KUBE_CONTEXT=<site>` seeds one site from the local tree, and `FROM_CONTEXT=<a> KUBE_CONTEXT=<b>` one site from
another's live pod, whose volume is the source of truth.

After merging a pull request that changes a readout, the merging session runs `python -m tools.drift_judge --brief`
(from `app/`, `PYTHONPATH=.`) and gives its output to a fresh subagent as the brief, which judges the movement since
`app/tests/readouts/ANCHOR` against the owner's direction (`docs/design/drift-judge.md`). Nothing in CI runs it or
calls a model.

## Patterns

The aim behind every rule here, as in habits: **make bugs hard to create and easy to find.** That is what KISS,
small functions, narrow interfaces and named systems are for, and why the patterns books exist. This is a real game,
so they apply: Nystrom's *Game Programming Patterns*
(gameprogrammingpatterns.com: read the chapter, not a summary), the Gang of Four, and what has been built on them
since (ECS, data-oriented design). Use a pattern where it earns its place; judging the fit matters more than the
pattern.

- **Fit pass before a new kind of thing.** When an ask adds a system, something placed in the world, new data, or a new
  roll or schedule: what is it an instance of, which row of `docs/systems.md` already does that, and how do games usually
  solve it? Extend or combine; build new only when nothing fits, and say why. Its issue carries a
  "Fits into:" line. Tweaks to lines, art and numbers need no fit pass.
- **`docs/systems.md` is the inventory**: what counts as a system (behind the locator) and what is model, data or
  module, each row's question and pattern, and the engine's contract. Planned before the code; updated in the same
  change that adds, merges or retires a row.
- **The usual shapes here:** a discrete-event engine for the economy (`docs/systems.md`), not a fixed-step loop; Type Object and data files
  for content (a new monster is data, not a class); Command for player actions (replay, undo, a log); Event Queue and
  Observer to decouple systems; Double Buffer where readers must not see a half-written tick; Dirty Flag and caches for
  expensive derived state; Component when entities share behaviour across kinds; seeded randomness from one source.
- **Don't:** Singletons or module globals for shared systems (use the locator); god objects, or one object's fields
  shared across many mixins (habits' page `App` is 21 of them); inheritance trees for content kinds; behaviour
  decided by matching words in natural-language text (put a field where the text is authored).

## How code gets written

Agents write most of this code, and measured evidence says prompting doesn't stop agent code from eroding; only
structural checks hold (`docs/research/agentic-engineering.md`). So:

- **A rule that can be a gate is one.** Boundaries in `docs/systems.md` (the engine imports nothing but itself, no
  caller imports a system's implementation) are import tests in CI, not prose.
- **A gate checks structure, never the wording of prose**: paths, symbols, ids, headings and explicit fields, not a
  phrase found in a doc, which breaks on an unrelated reword.
- **Every defect becomes a permanent guard**: the fix lands with the test or lint rule that would have caught it.
- **Tests come from a different agent than the code**, written from the contract, and are proven able to fail:
  red against a deliberately broken implementation first, then a mutation run against the real one.
- **An interface change that removes or renames a type ports the existing suites in the same stage.** A suite that
  no longer imports is no gate at all, and nothing goes red to say so: its tests simply stop being collected.
- **Structure and behaviour in separate commits**: a refactor lands with identical outputs, a change of behaviour on
  its own.
- **Ceremony scales with the task.** A new system gets interface first, review, then implementer and contract tests in
  parallel; a change you can describe in one sentence just gets made, with its test.
- **Reviewers look for correctness and contract gaps only**, never "anything that could be better": that is how
  abstraction layers, defensive code and tests for impossible cases get added.
- **Locally, run what the change touches**: the targeted tests for it, every file in the "Structural gates" table, and
  pyright on the touched files. Subagents run only the tests their change touches; the full suite runs in the pull request's
  checks, not on the shared box.
- **Cleanup is a standing pass** over merged code (duplication, drift from `docs/systems.md`), not only review before.
- **The orchestrator edits the shared single-file docs** (`systems.md`, the decisions index, the board's issues,
  `CLAUDE.md`, this file) from the doc deltas its writers report; a writer edits the decision file for its own system.

## Structural gates

A gate with a ledger holds a per-file count, seeded at what the code had when the gate arrived. It fails when a file is
over its held count or new, and when it is under ("stale, lower it"), so the ledger always equals the code. Never raise
a count; split, reduce or report. The ledgers are generated (`--write`) and live apart from hand-edited files: `app/tests/held/`
for the Python-run gates, `app/client/gates/held/` for the client's.

| Gate | Limit | Ledger |
|---|---|---|
| `app/tests/test_file_size.py` (Python and client source) | 300 lines | `file_size.json` |
| `app/tests/test_function_size.py` (Python) | 80 lines per function | none (its held list is empty and stays empty) |
| `app/client/gates/function-size.mjs` (client, run by `npm test`) | 80 lines | `function_size.json` |
| `app/tests/test_suppressions.py` | counts of `# pyright: ignore`, `# type: ignore`, `# noqa`, `cast(`, `@ts-ignore`, `@ts-expect-error`, `as unknown as`; each names its rule and a ` -- reason` on its line | `suppressions.json` |
| `app/tests/test_save_fields.py` | the fields of `Save`; a new engine part has its own state type (`systems.md`, "The engine") | `save_fields.json` |
| `app/tests/test_boundaries.py` | package-to-package imports of `ashfall_app`: a new edge fails until added to `ALLOWED` | none (the list is in the test) |
| `app/tests/test_doc_citations.py` | backticked paths in this file and `systems.md`, and symbols in `systems.md`, must resolve; `<!--planned-->` after a reference skips it while its target is missing and fails once it exists; `<!--external-->` is never checked | none |
| `app/tests/test_decision_citations.py` | a decision title quoted after `decisions.md` (or bare, closing a parenthesis) is an index entry or starts exactly one heading or bold lead in `docs/decisions/`; the index and those files' `##` headings agree | none |

The engine's own import rules (stdlib only, no clock or I/O) stay in `tests/engine_contract/test_purity.py`.
`app/tests/test_household_names.py` fails when any tracked file names the household that runs the game (its people,
pets, network, towns, hosts); the names are the CI secret `OSTMERE_HOUSEHOLD_NAMES`, so it skips everywhere but CI.
Moving a held string to another file moves its `KEPT` entry with it, read from CI's "stale" and "over" output (paths
and counts, never the names). Test fixtures use neutral site names (`site-a`, `site-b`), never a real one.

## Scope and test budget

A single-player web game with an API, played by its owner. **A pull request's CI takes about 5 minutes of wall clock**
(a docs-only one about a minute), and the nightly full run is where the whole-game simulations live. The yardstick is
an outside one, never the suite's own history: a unit test costs milliseconds, 0.05 s at most. Each job's
`timeout-minutes` in `ci.yml` is its budget, so a job that outgrows it goes red instead of quietly slowing every pull
request. Locally, and in every subagent, run the tests a change touches plus the structural gates; CI runs the rest.

Test depth follows risk. The engine, saves, catch-up maths, the content loader and its checks, accounts and anything
that can lose a player's progress get behaviour-level tests written first, blind where they are a contract. Routes,
registrations and config plumbing get one smoke test per entry point. The client's look gets render-and-look, never a
snapshot assertion. One-off tools get none.

## Fast from the start

habits' suite grew slow and had to be sped up after the fact; here speed is a gate from the first test, while the
suite still runs in seconds.

- **Every test has a time budget**, held like the function-size gate (`app/tests/time_gate.py`, a plugin
  `app/tests/conftest.py` registers): 4 s of wall clock per test over setup, call and teardown, and 10 s per shared
  (class/module/package/session) fixture, timed on its own by name and taken out of the test's charge. HELD and
  HELD_FIXTURES start and stay empty. Wall clock, because setup and waiting are what a person waits on: the CPU-only gate
  it replaced timed the call alone, and speed commits moved cost into fixtures where nothing measured it. Tests marked
  `playthrough`, and the plays they set up, are budgeted by their CI job's timeout instead. pytest.ini's `timeout = 6`
  is the hang guard above the budget.
- **Time never comes from the wall in a test**: a timeout, lease or retry takes an injected clock
  (`app/tests/fake_clock.py`) or a tiny timeout, and an unreachable dependency is a fake that fails at once. The one
  real wait kept is db/test_failover's silent-host smoke test (libpq times the connect itself), at a 1 s URL timeout.
- **A performance test asserts a count, never a time** (the forecast's instants, `app/tests/dayone/test_dayone_forecast.py`);
  what a unit of work costs is the engine bench's question.
- **Whoever writes a test makes it fast before committing it**: run it under the gate, look at the slowest
  durations, and speed the test up, never the limit. The usual cause: sampling the engine from time zero at every
  point (each `value()`/`advance()` re-simulates from the save's time), which turns a linear check quadratic. Carry
  each sample forward from the last instead; the engine's invariant 1 (engine `DESIGN.txt`, "INVARIANTS") makes the
  two equivalent.
- **The shipped content is loaded once per session** (`shipped_opening`, `app/tests/conftest.py`): `create_app()` loads
  and checks every chapter, ~0.2 s (about 0.8 s on a slow CI node) that every app-booting test would otherwise
  pay, twice in a test that builds two.
- **Property tests run at two depths:** the fast Hypothesis profile on every push, the deep one on a schedule.
- **Scripted playthroughs are played once per test session and shared** (`app/tests/opening/routes.py`): a test reads
  a play or a moment of one, never plays its own. Tests that read one are marked `playthrough`. A pull request plays
  only the opening's representative routes (`playthrough-smoke`); the full run plays the rest of the chapters, and the
  nightly deep run every route and seed. Of the bugs that reached `main` in a sample of the old repo's fixes, none
  needed a simulation to catch, while the nightly lane caught balance breaks on `main`; that is why they live there.
- **Week two's chapters play on from saved ends, so its job grows by one chapter per chapter**
  (`app/tests/weektwo/ends.py`): each chapter starts from the saved end of the one before, and the rebased saves are
  read, not replayed from the start. The saves are not in git: `python tools/chapter_saves.py --write` (from `app/`,
  with `PYTHONPATH=.`, about 11 minutes) writes them under `~/.cache/ashfall/chapter-saves/<key>/`, the key hashing
  what they depend on (`ends.key()`: the rules, the engine's source, the play code). The typical route's heavy-step readings,
  minutes each on day twelve, are saved beside them (`ends.READINGS`), so the counting tests read and do not compute
  them. CI's `chapter-saves` job writes them in parts, one per route chain or readings part, keeps each in the Actions
  cache under that key and hands them to the week-one-saved and week-two jobs as artifacts the readers merge. Week two's job runs one shard per chapter, day
  twelve's typical play in one of its own (`app/tools/weektwo_shards.py`), so a play's readers stay in one job;
  `shards-cover` fails unless the shards select each week-two test exactly once, and hands their names to the job as
  its matrix. With no saves for today's key the plays run from the start, so a local run needs no step; CI sets
  `ASHFALL_REQUIRE_SAVED=1`, which makes a missing or stale save a failure. A saved end is held to today's play link
  by link: a chapter played on must end at its own saved end. Week one's first link is `playthrough-week-one-saved`
  (`app/tests/weekone_saved`): week one's job exports its push routes' plays as an artifact and that job compares them
  with the saved ends, so week one's plays wait on nothing.
- **Where the time goes** (2230 tests, 133 s wall on 2026-10-25): setup 28%, call 64%, teardown 4%; each test's setup is
  about 115 ms (create its database 26 ms, drop it 38 ms, boot the app 85 ms). Tried and left out: caching the opening per
  session (7-8%, inside the box's ~20% run-to-run noise) and one reused database truncated between tests (no gain, and
  three tests rename a table).
- **`tests` runs as two parallel shards** (`app/tools/shards.py`): shard a is `tests/saves`, `tests/accounts` and
  `tests/api_contract`, the heaviest; shard b is everything else, as an `--ignore` of those paths, so a new test
  directory lands in b. The `shards-cover` job fails unless the two collect exactly what one run does.
- **Test jobs install from pip's cache**, keyed on `requirements*.txt`, so a job spends seconds, not minutes, on
  `pip install`.
- **The engine's speed gets a budget in CI, as a diff against the merge-base.** `app/tools/bench_ab.py` runs `reading`
  (every rich save) and `steps` (the decisions route replaying the scripted opening) in alternating processes, four
  rounds on the merge-base's tree and on this one, in the one `engine-bench` job, and fails a workload whose fastest
  CPU-second sample is over 1.12x the base's. CPU type and load cancel, which a fixed budget cannot do: the old ratio to
  a reference workload read `steps` 0.42-0.71 on older server CPUs and 0.79-0.97 on a current desktop CPU. The same code
  against itself reads 0.97-1.04 on a quiet box (rare single attempts reach 1.12 on a busy one), a 15% slowdown planted
  in the decisions route reads 1.145, and 30% reads 1.3. A workload over the limit is measured again on fresh rounds
  and fails only if it is over both times, since a busy neighbour spoils one attempt, not two. Each attempt prints both
  sides' fastest samples in CPU seconds, but nothing gates them, so slow drift is the blind spot: each pull request is compared
  with its parent, and slowdowns under 12% add up. When touching the step path, read the printed absolute numbers. If a live step gets slow, look first at `rebuild`'s per-store `net`/`line`/`aimed_stack` and at `events()`.

## Deploys with two builds live

While a deploy rolls, the old and the new pods answer at once, and the gateway balances per request, so one page's
requests reach both builds. What holds:

- Every response, errors included, names the build that answered in `X-Ashfall-Build`
  (`app/ashfall_app/api/CONTRACT.txt`).
- The bundle's path names its build, and a page loads only its own (`docs/systems.md`, Page shell). There is no
  unversioned /build/ path. The web pods' probes read `/webz` (the image's bundle, never the assets volume).
- A save is written by one request at a time (its row is locked for the transaction), and only forward. Builds are
  ordered by content release, the release lock's number, which every change of the rules raises. A pod asked for a
  save last written by a later release answers `save_unavailable` and writes nothing, and the page asks again until a
  newer pod answers (`app/ashfall_app/saves/load.py`). The app does not start while a live save fails to rebase under
  its rules.
- Nothing shared between pods lives in process memory; the only per-pod state is a log-flood guard
  (`client_errors.RateLimit`) and the cap on recovery words hashed at once (`app/ashfall_app/accounts/words.py`), both
  per pod by design.

## Rules from day one

habits is still partway through reworking its code to these rules, so its code mixes the old way and the new. Take
its rules, and the parts its queue and its systems inventory show as done; before copying one of its files as
an example, check which side it is on.

- **Postgres from the first table**, Postgres 18 with C collation (seeded orders depend on byte sort). SQL lives only in
  `db/`, through SQLAlchemy Core into typed records; the first migration is an Alembic revision; tests run against a
  Postgres service, a database per test. habits began on SQLite and is still paying for raw SQL outside `db/`.
- **The schema changes only by a new Alembic revision** in `app/ashfall_app/db/alembic/versions/`, never by editing one
  that shipped; `app/ashfall_app/db/tables.py` is the same schema for queries, held equal by `tests/db/test_shape.py`.
  `python -m ashfall_app.db migrate` (the pod's migrate init container) runs every revision in one transaction under an
  advisory lock and refuses a database not in C collation; each revision waits at most 5 s for a table's lock. A
  database already past the build's revisions (a rollback) is left as it is (log `migrate.ahead`, exit 0), and the app
  refuses to start on one behind its newest (`db.behind`). The old pod serves until the new one is ready, so a
  revision is expand-then-contract: the build already running must still work on the new schema.
- **A test that needs a database asks for `pg_url`** (its own, migrated) or `pg_empty`, copied from a template
  migrated once per run (`app/tests/pg.py`). CI's `tests` shards each run a postgres:18.6 service, production's version; locally, run a throwaway
  postgres:18.6 container and pass its URL as ASHFALL_TEST_PG. Without it those tests skip locally and fail in CI.
- **The web process only answers requests.** Background loops are `python -m ashfall_app.jobs <name>` run by a worker
  Deployment or CronJobs; migrations are their own command in an init container. A job claims its work before doing it.
  Nothing that must be shared between pods lives in process memory.
- **Typed and checked.** Pyright strict on every package (`ashfall_app`, `tests`, `tools`, `tools/scene`), gating CI, no
  held count; an ignore comment that is no longer needed is itself an error. The client is TypeScript from its
  first file, source in `src/` and output in a gitignored `build/`, bundled; API types are generated from `openapi.json`
  and CI fails when they drift.
- **Measured smooth on a big screen before a client change ships.** A page that is fine in a small headless window
  ran at 3 fps on a 4K monitor: canvases drawn at window size × pixel ratio every frame, a hidden animation
  still running, glows repainting. Every client release records frame rate and main-thread time per frame at
  3840×2160 with a pixel ratio of 2, front page and game screen (Playwright with CDP or rAF sampling), and ships only
  near 60 fps.
- **A long cache only on a URL that changes with its content.** `/assets/` once went out `immutable` for a year
  under fixed names; fixing the header later did nothing for browsers that already held the old files, and a player's
  Firefox kept drawing the first scene. Assets are requested by versioned URLs (a content hash or the build in the
  query), so a new file is a new URL and no cached copy can outlive its build.
- **Generated files never share a directory with hand-edited ones.**
- **A release never strands a save.** The release lock (`app/ashfall_app/opening/released/ids.json`, written only by
  `app/tools/content_lock.py --write`) holds every content id ever released; renames go in `opening/renames.toml`.
  Adding, retuning, rewording, raising a cap or moving a card is safe; renaming or removing an id needs a mapping (a
  card is retired, never removed); reusing an id, lowering a cap, changing a released threshold or trigger outcome, or
  bumping the save format (`engine.codec.FORMAT`) without an upgrade is forbidden. `tests/opening/test_released.py` and the server's start both check
  it, and the `saves-forward` CI job loads the previous commit's opening-depth saves with the pushed code. The classes in full:
  engine `DESIGN.txt`, "Release lock".
- **Loading is the whole promise to a save in progress.** A change may move where a running game stands (a card it
  already shows, the order two beats land in), and no code, flag or date check is added to keep one game, or the games
  of one period, as they were (it's an alpha, and habits bloated on exactly those one-offs). Avoid surprising
  changes by design; when one lands in someone's game, tell them.
- **A value the server and the page both need lives in one data file** (or the server serves it). Never a copy on each
  side, never one side reading the other's source.
- **Logs** are logfmt to stdout through one setup used by every entry point (habits' `logs.py`): each run's start,
  finish, counts and failures; ids and counts, never player text or secrets, held by a test that plants values. Anything
  stored outside stdout has a retention limit its writer enforces.
- **One injectable clock**, and a time zone per save; never `now()` in SQL or a hard-coded zone.
- **Small functions in small files**, held by the size gates above.
- **Shared systems sit behind a service locator** with Null Object defaults, from the first one.
- **Bulk assets live on the RWX assets volume, never in git or the image**, licensed or not: audio, sprite
  sheets, tiles, generated art and their manifests, mounted read-only and served at `/assets/`. Git holds the code
  that makes or picks them (a generator, a seed command), never its output. Small UI files (favicon, icons, a web
  font) stay in git. An image nothing references any more is removed, not kept.
- **Accounts are the app's own** (anonymous cookie sessions and a device transfer code, no external sign-in); tests
  sign in through sessions, never a trusted header.
- **Sums from Postgres are typed explicitly**: `sum()` over bigint comes back as `Decimal`.

## Shared machines

The host, the CI runners and the cluster are shared with whatever other sessions are working:
before a suite, a test container, a pipeline or an API burst, check who else is busy and coordinate only on real
contention (method and limits in the `fanout-craft` skill, `references/shared-resources.md`<!--external-->). Research that lands under `docs/research/` is sent to the habits session too,
the parts that apply to it.

## Where things are

| What | Where |
|---|---|
| Repo, CI, queue | GitHub, Actions ("The pipeline" above); the queue is the Ostmere: Work board, https://github.com/users/egg82/projects/2 |
| Live site | https://ostmere.yggdrasil.pub (deploy: the cluster repo, via Flux) |
| Research downloads (Widman map stamps, Gessner scans) | outside the repo |
| Design canvas (six phone screens) | https://claude.ai/artifact/H6Foqa7diKmwDS1KGKJuxC, source in `docs/design/canvas/` |
| Redesign comparison (six designs and the merge) | https://claude.ai/artifact/3zBFvQDBec1J6UWPqCuc6s, the chosen design in `docs/design/redesign/` |
| Look test canvas | https://claude.ai/artifact/1EDLESML2xgre6iuvonRt1, source in `docs/design/look-test-canvas/` |
| Writing and model tests | https://claude.ai/artifact/WbXhGSQedRy2SnN2gM3rNd, source in `docs/research/writing-test/` |
| Strawman doc (superseded by `decisions.md` where they differ) | https://claude.ai/code/artifact/571817bb-99df-498c-be29-3202fe5ef76e |
