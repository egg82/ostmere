# The Breaking of Ostmere

A single-player idle game, played in the browser at https://ostmere.yggdrasil.pub.

- Design rules: `docs/decisions.md`, the index of `docs/decisions/`, one file per system; the core loop: `docs/core-loop.md`.
- The code's systems and their boundaries: `docs/systems.md`.
- What's next: `docs/open-work.md`.
- How it is built and shipped: `docs/engineering.md`.

The app is in `app/` (Python, FastAPI; the browser client is TypeScript in `app/client/`). Run its checks with
`cd app && pip install -r requirements.txt -r requirements-dev.txt && python -m pytest -q && pyright`.
Tests that need a database skip unless `ASHFALL_TEST_PG` holds the URL of a throwaway Postgres 17; CI always runs them.
