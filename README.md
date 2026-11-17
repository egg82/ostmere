# The Breaking of Ostmere

A single-player idle game for the browser, with a dark fantasy story that runs from the first tap to an actual
ending. You gather, build and put people to work, and everything keeps going while you're away. When you come back the
stores are full, the work is done and the next piece of the story is waiting. It's at https://ostmere.yggdrasil.pub.

It's a one-person project, made mostly with Claude Code and published as it stands. The whole story is in this
repository under `content/`, so if you mean to play, stay out of that folder.

## Run it locally

You need Docker or Podman. The image is `ghcr.io/egg82/ostmere` (also `egg82/ostmere` on Docker Hub, linux/amd64);
`dev` is the latest green `main`. Saves live in Postgres 18, created with the C locale.

```sh
docker network create ostmere
docker run -d --name ostmere-db --network ostmere -e POSTGRES_PASSWORD=change-me \
  -e POSTGRES_INITDB_ARGS="--locale=C --encoding=UTF8" postgres:18.6

DB=postgresql://postgres:change-me@ostmere-db/postgres
docker run --rm --network ostmere -e DATABASE_URL=$DB ghcr.io/egg82/ostmere:dev python -m ashfall_app.db migrate

docker run -d --name ostmere --network ostmere -p 8080:8080 -e DATABASE_URL=$DB \
  -e ASHFALL_JOIN_KEY=$(openssl rand -hex 32) -e ASHFALL_RATE_KEY=$(openssl rand -hex 32) \
  ghcr.io/egg82/ostmere:dev
```

Then open http://localhost:8080. Your first visit creates an anonymous account kept in a cookie; there are no
passwords. Don't change `ASHFALL_JOIN_KEY` between restarts: transfer codes and recovery words are hashed under it.
The app never migrates on start, so run `migrate` with each new image before you start it.

The art isn't in the repository. `tools/scene/` draws the scene from the Time Fantasy sprite packs, which are sold
separately, and the app serves whatever is mounted at `/assets` (or the directory named by `ASSETS_DIR`).

These settings are optional and off until set:

| Feature | Settings |
|---|---|
| Reminders to play (web push) | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` (a `mailto:` or `https:` contact for whoever runs it), and `python -m ashfall_app.jobs reminders` run every few minutes |
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

The server is Python 3.12 and FastAPI, in `app/ashfall_app/`. The browser client is TypeScript, in `app/client/`.
The economy runs on a small discrete-event engine in `app/ashfall_app/engine/`, which imports nothing outside
itself.

```sh
cd app
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q    # database tests skip unless ASHFALL_TEST_PG names a throwaway Postgres 18
pyright
cd client && npm ci && npm run typecheck && npm test && npm run build
```

Before a pull request, run `app/tools/gates.sh` from the repo root as well. It runs the structural gates: file and
function size, import boundaries and a time limit per test. GitHub Actions runs the full suite on every pull
request, and the scripted playthroughs nightly and on pull requests labelled `playthroughs`.
`docs/engineering.md` has the details.

- `docs/decisions.md`: the design decisions, indexed, with one file per system in `docs/decisions/`.
- `docs/systems.md`: each system, the question it answers and where it lives.
- `docs/core-loop.md`: an early sketch of the core loop.
- What's next: the Ostmere: Work board, top first (https://github.com/users/egg82/projects/2).

## License

AGPL-3.0, in [`LICENSE`](LICENSE). Run it, change it, share it. If you distribute or serve a modified copy, you
publish its source under the same licence and keep the copyright notices.
