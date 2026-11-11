# Saves

Several saves, kept on the server, carried across deploys and failovers.

## Multiple saves, each its own run

Several save slots, each its own seed: a different map, different arrivals and townsfolk with their own Claude-written
souls, different mini-stories, threats and timings, and room for a different build (magic-heavy, town-first,
combat-led). The main story's spine stays the same, so a second run knows the big beats; what varies is everything
around them, and some content in `content/` varies per save so a replay still surprises a little. Saves run side by
side on their own clocks; since nothing waits on the player, two saves never ask for twice the attention. Longevity
comes from replays like these and from expansions.

## Developed live, forward-only by preference

As with habits: players are told it is in heavy development; a change prefers to apply forward only, so what a save
already has keeps its timing and nothing already shown changes under the player; a retroactive change stays possible
when genuinely needed. **No machinery for it:** no per-change start dates or flags on saves (habits went too far
with those and it became too much). When a change needs to be retroactive, just make it. **A deploy never resets
a game:** a save made under older rules loads under the new ones (the preview, which keeps no save, restarted a
friend's game when content shipped while their tab sat idle).
The forward-only line is a save's last write, not the deploy: time away runs under the rules in force when the player
returns, which is fine while the game is still being developed.

## Saves never die with a device

Saves live on the server with the account, backed up. Lost progress (a PC reset, a cleared browser) ends idle games like Progress
Knight and A Dark Room. **The server writes the save on every decision; the page never holds the only copy** (the preview
kept its game only in the page, so an update's reload, a closed tab or a browser discarding it lost the game). Time
needs no saving, since loading advances a save to now, so there is no autosave timer and no save-before-close step
(browsers do not reliably run one): a close, a reload, a self-update or a crash loses nothing, the log's lines included
(the preview's reload kept the game but cleared its log).

## A database failover is replayed once, or answered 503

The app runs at two sites against one writable Postgres; a failover turns the old primary read-only or drops its
connections, and loses at most a few seconds of acked writes (a lost decision answers 409 `stale`). The pool's check
refuses a read-only connection (`db/writable.py`), so one never starts a request. A failover error that escapes a
handler (`db/failover.py`) is replayed once at the route class (`api/replay.py`) unless a write of that run reached
COMMIT, because a lost COMMIT cannot be told from a taken one; then, or when the replay meets one too, the answer is 503
`save_unavailable` with Retry-After. A checkout waits at most the pool's budget and is not replayed.
The first read-only connection a checkout meets drains the whole pool: the pool backs off between failed checks, so
refusing the demoted member's idle connections one at a time would spend the budget. A connect to one host gives up
after 3 s (`connect_timeout`, unless the URL sets one), so a lost site that drops packets costs libpq that long per
connection rather than the kernel's TCP timeout. A query already running on a server whose packets vanish errors after
about 6 s (`tcp_user_timeout`, with keepalives for an idle connection; `TCP_SETTINGS` in `db/engine.py`, each unless the
URL sets its own) and is classified a failover, where the kernel would retry for some fifteen minutes; they detect a lost
peer and bound no statement, so a long healthy query completes. `podman pause` does not prove this (the host kernel still
acknowledges); `app/tools/silent_vanish.sh` drops the packets inside the server's network namespace, locally only.
A request runs on one pool checkout (`db/unit.py`, opened by the route class), since each checkout pays the read-only
check and a BEGIN and a round trip from the second site is ~11 ms. A block that writes still commits where it ends, so
what a replay can tell about a COMMIT is unchanged; plain reads (the session lookup, `/api/me`) join the transaction
of the block after them. The daily session renewal runs after the write commits, in its own transaction on the same
connection: inside the write's, a failed renewal would abort the applied write, and its account row lock, taken after
the save's, could deadlock against the empty-account prune, which locks accounts and then deletes their saves. A
forecast or dry run gives its connection back before its replay. A decision holds its save's row lock over four round
trips: the lock, the tries count (`db/tries.py` `take`, trim, count and insert as one statement), the step's write
(`db/step.py`: the row, lines, decision log, day snapshot and the repeats' read as one statement) and the COMMIT. The
lock serialises the save's read-modify-write, its tries count and its lines' numbering, so nothing moves out from under it
and the count stays before the decision is run (a refusal wins over an invalid verb). Rejected: psycopg's pipeline mode
(SQLAlchemy reads each statement's result as it is sent, so a statement inside a pipeline raises `ResourceClosedError`). Rejected: one transaction for every block of a
request (a block that raises would roll back an earlier block's write that used to commit on its own).
Rejected: a retry at each `engine.begin()` (the writes are spread over some twenty such sites, several in one
request, so a retry there cannot know what an earlier one committed); an ASGI middleware (it sees no route, and its
replay would have to rebuild the body the route class already holds).

## Saves and the page shell, as built

How these stand today, moved from their rows in `systems.md`.

Saves: a save under older rules is rebased when it next loads (format upgrades chained, then renames: engine
`DESIGN.txt`, "Rebase"), by data it carries (a manifest of the rules it was written under) and content's renames
table: forward-only with no per-change flags. The release lock (`engineering.md`) keeps every rebase total. A
retroactive change is a later data migration. Stored in Postgres (`app/ashfall_app/db/tables.py`): the save's state
with its decision log, lines and day snapshots, and each rules digest's manifest once, put back into a row stored
without it when it is read (`app/ashfall_app/db/manifests.py`). A build writes rows without its manifest once its
start finds it held (`app/ashfall_app/saves/manifest.py`); `python -m ashfall_app.saves strip` does the same for older
rows and deletes the manifests no row names (`app/ashfall_app/saves/strip.py`). Built:
`app/ashfall_app/saves/interface.py` (null: no database), one transaction per write holding the row, rebased forward at
load and never written by an older build than last wrote it (`app/ashfall_app/saves/load.py`). A long absence is caught
up in bounded slices (Game Loop's catch-up, bailing after a budget): each request advances for at most a few seconds of
wall time, writes and commits that slice, and the page asks again until one reaches now
(`app/ashfall_app/saves/service.py`; engine `DESIGN.txt`, "Bounded advance"; CONTRACT.txt, "Catching up"). Several
per account (`app/ashfall_app/saves/games.py`): a capped count of live saves, new games under the shared limiter, a
deleted save held and then deleted for good by a later write; the in-game Games sheet (`app/client/src/ui/games.ts`)
lists, starts, switches, deletes and restores them, and the front page's list (`app/client/src/ui/places.ts`) selects,
opens, starts and deletes them through the same delete flow (`app/client/src/ui/gamedelete.ts`). A save's stored view
is read without opening it (the Saves interface's stored read, `GET /api/saves/{save_id}/view`): not advanced, nothing
written, so a page can draw every save before any is opened.

Page shell: TypeScript, bundled, served at /build/<build>/ so a page only ever runs its own build's bundle. What a load
opens is `entry` in `app/client/src/begin.ts`: the front page, or the game at once when the address names a live save,
a join link came, or the device's "skip the front page" choice (`app/client/src/app/straight.ts`, local storage, off
when it throws) is on. The front page (`app/client/src/ui/frontdress.ts`) draws the game's own Scene on its stage:
cropped around the fire at a whole-number scale (`app/client/src/scene/crop.ts`, `app/client/src/scene/focus.ts`), lit
by the visitor's hour (`app/client/src/scene/light.ts`), a canned moment of the camp working for a first visit or New
game (`app/client/src/ui/glimpse.ts`) and the selected save's own stored view otherwise; each save in the list is a
still of its own view (`app/client/src/ui/places.ts`). A boot that fails (the bundle asked of another build
mid-deploy) reloads once after two seconds, then every thirty while visible (`app/ashfall_app/static/index.html`). A
request with no answer in `REQUEST_TIMEOUT_MS` (ten seconds, `app/client/src/api/api.ts`) is given up as a network
failure, so the session asks again behind the reconnecting state whatever holds the connection. The self-update
(`app/client/src/app/selfupdate.ts`) reloads at a quiet moment when a Step's build, or /page-config.json's, is not the
one it booted with. The page's files (`app/ashfall_app/web/page.py`: the shell, `app/ashfall_app/static/privacy.html`,
robots.txt, llms.txt, the fonts under `app/ashfall_app/static/fonts/`, so no visitor's address goes to a font host) are
served by the web pods (`app/ashfall_app/web/app.py`, no database or secret), and by the app too for a run without
them; the edge sends the server's paths, which `app/ashfall_app/web/app.py` lists, to the app.
