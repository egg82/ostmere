# The Breaking of Ostmere

A single-player idle game for the browser, with a dark fantasy story that runs from the first tap to a real ending.
You gather, build and set your hands to work, and the game keeps playing while you're away: you come back to full
stores, finished work and the next piece of the story, never a pile of notifications. Play it at
https://ostmere.yggdrasil.pub.

It is one person's game, built mostly with Claude Code and published as it is. The whole story is in this
repository, under `content/`. If you plan to play, don't read that folder.

## Run it locally

You need Docker or Podman. The image is `ghcr.io/egg82/ostmere` (also `egg82/ostmere` on Docker Hub, linux/amd64),
and its `dev` tag is the latest green `main`. Saves live in Postgres 18, created with the C locale.

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

Then open http://localhost:8080. The first visit makes an anonymous account held by a cookie; there are no
passwords. Keep `ASHFALL_JOIN_KEY` the same across restarts, because transfer codes and recovery words are hashed
under it. The app never migrates on start, so run `migrate` with each new image before starting it.

The art is not in the repository. `tools/scene/` draws the scene from the Time Fantasy sprite packs, which are sold
separately, and the app serves whatever is mounted at `/assets` (or the directory in `ASSETS_DIR`).

Optional settings, each off until set:

| Feature | Settings |
|---|---|
| Reminders to play (web push) | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` (a `mailto:` or `https:` contact for whoever runs it), and `python -m ashfall_app.jobs reminders` run every few minutes |
| Your own address in device-transfer links | `ASHFALL_PUBLIC_URL` (default https://ostmere.yggdrasil.pub) |
| Analytics (Umami) | `ASHFALL_UMAMI_SCRIPT_URL`, `ASHFALL_UMAMI_WEBSITE_ID` |
| Log detail | `LOG_LEVEL` (default `info`); logs are one `key=value` line per event |

## Deploying your own

The author runs it on Kubernetes across two sites, from manifests kept in a separate repository, with Flux
deploying each new `main-<sha>-<timestamp>` image tag. Anything that runs a container works, as long as
`python -m ashfall_app.db migrate` runs before each new version starts (an init container, say). The same image
also runs `python -m ashfall_app.web`, a page-only server that keeps the page loading while the app or the database
is down; you can skip it.

## Working on it

The server is Python 3.12 and FastAPI, in `app/ashfall_app/`. The browser client is TypeScript, in `app/client/`.
The game's economy runs on a small discrete-event engine (`app/ashfall_app/engine/`) that imports nothing but
itself.

```sh
cd app
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q    # database tests skip unless ASHFALL_TEST_PG names a throwaway Postgres 18
pyright
cd client && npm ci && npm run typecheck && npm test && npm run build
```

GitHub Actions runs the full suite and the scripted playthroughs on every pull request. `docs/engineering.md`
covers how, and the structural gates CI holds the code to: file and function size, import boundaries, and a time
limit per test.

- `docs/decisions.md`: the design decisions, indexed, with one file per system in `docs/decisions/`.
- `docs/systems.md`: each system, the question it answers and where it lives.
- `docs/core-loop.md`: the core loop.
- `docs/open-work.md`: what's next.

## License

AGPL-3.0 (see [`LICENSE`](LICENSE)). Run it, change it and share it; anyone who distributes or serves a modified copy
publishes its source under the same licence, with the copyright notices kept.
