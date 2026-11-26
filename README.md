# The Breaking of Ostmere

**Play it: https://ostmere.yggdrasil.pub**

A single-player idle game for the browser, with a dark fantasy story that runs from the first tap to an ending. It
keeps running while you're away: close the tab, and when you come back it tells you what your people did. It's a one-person project, made mostly with Claude Code and published as it stands.

![The opening on a desktop: the scene on the left, the first cards on the right](docs/images/desktop.webp)

The whole story is in this repository under `content/`, so if you mean to play, stay out of that folder.

## What you do

You start with almost nothing and a few things to do. The game is a set of small systems, each introduced by a short
lesson on its real controls the first time it matters. You can skip any lesson.

- **Cards.** Every kind of work is a card. Tap one to do it by hand. It shows what it takes, what it makes and how long
  it runs, and a card that can't run yet says what it waits for.
- **Mixes.** When tapping by hand gets tedious, pick several cards and split your time between them. They all progress
  at once at different rates, and a live ledger shows what the mix uses and makes per hour as you change the shares.
  Mixes are saved with a name, so you can keep one for each purpose and switch between them. Tapping a card by hand
  pauses the mix while your hands are busy.
- **Rules.** A rule is a tapped-together "when this happens, do that": when a
  store runs low, switch to the mix that refills it. Rules are kept in priority order. The first whose condition holds takes the hands, and when it lets go
  your own mix comes back.
- **Plan and Next.** Next, in the Rules tab, is a short queue for what the hands do after the current job. Plan adds a
  card or a mix to it, including a card that isn't ready yet, which waits its turn and runs once it is.
- **People.** Once someone joins you, their row in the Town opens a page of their own: their cards, the mix that
  splits their time, and the rules that run them.
- **The Book.** Where the game writes things down. The Chronicle lists what happened and what caused it, with a summary
  of the time since you were last here. The Journal holds the notes the game writes as you learn things.

![The same opening on a phone](docs/images/phone.webp)

---

# For developers

Everything below is for running, deploying and changing the code.

## Run it locally

You need Docker or Podman (substitute `podman` for `docker` below). The image is `ghcr.io/egg82/ostmere` (also
`egg82/ostmere` on Docker Hub, linux/amd64); `dev` is the latest `main` that passed CI. Saves live in Postgres 18,
created with the C locale.

```sh
docker network create ostmere
docker run -d --name ostmere-db --network ostmere -e POSTGRES_PASSWORD=change-me \
  -e POSTGRES_INITDB_ARGS="--locale=C --encoding=UTF8" postgres:18.6
until docker exec ostmere-db pg_isready; do sleep 1; done

DB=postgresql://postgres:change-me@ostmere-db/postgres   # the password is POSTGRES_PASSWORD, above
docker run --rm --network ostmere -e DATABASE_URL=$DB ghcr.io/egg82/ostmere:dev python -m ashfall_app.db migrate

docker run -d --name ostmere --network ostmere -p 8080:8080 -e DATABASE_URL=$DB \
  -e ASHFALL_JOIN_KEY=$(openssl rand -hex 32) ghcr.io/egg82/ostmere:dev
```

Then open http://localhost:8080. Your first visit creates an anonymous account kept in a cookie; there are no
passwords. `ASHFALL_JOIN_KEY` is 64 hex characters, and transfer codes and recovery words are hashed under it: without
a valid one the game runs but refuses both, and changing it between restarts invalidates the ones already issued.
`ASHFALL_RATE_KEY` is optional (any string) and keys rate limiting.

The app never migrates on start. If the database is behind the image, it refuses to start (`SchemaBehind`), so run
`migrate` with each new image first. To start over: `docker rm -fv ostmere ostmere-db && docker network rm ostmere`.

The art isn't in the repository. `tools/scene/` draws the scene from the Time Fantasy sprite packs, which are sold
separately, and the app serves whatever is mounted at `/assets` (or the directory named by `ASSETS_DIR`): the scene, the
journal's sketches and the sound. Without it the game still plays, silent, with the scene drawn as an empty frame.

These settings are optional and off until set:

| Feature | Settings |
|---|---|
| Reminders to play (web push) | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` (a `mailto:` or `https:` contact for whoever runs it), and `python -m ashfall_app.jobs reminders` run every few minutes |
| Lines written by Claude | `ANTHROPIC_API_KEY`. Without it every line comes from the authored stand-ins; with it Claude words them, and any failed call falls back to the stand-in (`app/ashfall_app/writer/live.py`) |
| Your own address in device-transfer links | `ASHFALL_PUBLIC_URL` (default https://ostmere.yggdrasil.pub) |
| Analytics (Umami) | `ASHFALL_UMAMI_SCRIPT_URL`, `ASHFALL_UMAMI_WEBSITE_ID` |
| Log detail | `LOG_LEVEL` (default `info`); logs are one `key=value` line per event |

## Deploying your own

I run it on Kubernetes across two sites. The manifests live in a separate repository, and Flux deploys each new
`main-<sha>-<timestamp>` image tag. Anything that runs a container will do, as long as
`python -m ashfall_app.db migrate` finishes before the new version starts (an init container, say). The same image
also runs `python -m ashfall_app.web`, a page-only server that keeps the page loading while the app or the database
is down. You can skip it.

## Working on it

The server is Python 3.12 and FastAPI, in `app/ashfall_app/`. The browser client is TypeScript, in `app/client/`
(Node 22 or newer). The economy runs on a small discrete-event engine in `app/ashfall_app/engine/`, which imports
nothing outside itself. The code and the cluster still say `ashfall`, the game's working title.

```sh
cd app
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q    # database tests skip unless ASHFALL_TEST_PG names a throwaway Postgres 18
pyright
cd client && npm ci && npm run typecheck && npm test && npm run build
cd ../..               # back to the repository root
```

For the database tests, run a throwaway container and point `ASHFALL_TEST_PG` at it (`docs/engineering.md` says how
CI does it):

```sh
docker run -d --name ostmere-testdb -p 5433:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:18.6
export ASHFALL_TEST_PG=postgresql://postgres@127.0.0.1:5433/postgres
```

Before a pull request, run `app/tools/gates.sh` from anywhere (it needs the dev requirements installed and `npm ci`
done). It runs the structural gates: file and function size, import boundaries and a time limit per test. GitHub
Actions runs the full suite on every pull request, plus the playthroughs of the chapters it touches (or a smoke play
for a shared change); the whole-game playthroughs run nightly and on pull requests labelled `playthroughs`.
`docs/engineering.md` has the details.

- `docs/decisions.md`: the design decisions, indexed, with one file per system in `docs/decisions/`.
- `docs/systems.md`: each system, the question it answers and where it lives.
- `docs/core-loop.md`: an early sketch of the core loop.
- What's next: the Ostmere: Work board, top first (https://github.com/users/egg82/projects/2).

## License

AGPL-3.0, in [`LICENSE`](LICENSE). If you distribute or serve a modified copy, you
publish its source under the same licence and keep the copyright notices.
