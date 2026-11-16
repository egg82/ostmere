"""Uvicorn's entry point: `ashfall_app.main:create_app`, the composition root: it loads the content, connects the
database, wires the systems into the service locator (services.py) and mounts the API and the page."""

import logging
import os
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from . import client_errors, logs, page_config
from .head import HeadAsGet
from .accounts.body_limit import BodyLimit
from .accounts.cookies import CookieMiddleware
from .accounts.csrf import CsrfMiddleware
from .accounts.service import PgAccounts
from .api.routes import PUBLIC_URL, routes as game_routes
from .api.service import Game
from .build_header import name_every_answer
from .clock import Clock, system
from .db import engine as db
from .feedback.routes import routes as feedback_routes
from .feedback.service import PgFeedback
from .old_host import OldHostRedirect
from .opening.lock import load_lock
from .opening.lock_checks import release_problems
from .opening.renames import load_renames
from .opening.schema import Opening, load_opening
from .saves.check import check
from .saves.interface import MAX_SAVES, Ruleset
from .saves.manifest import registered
from .saves.ruleset import ruleset
from .saves.service import PgSaves
from .services import Services
from .web import page

HERE = Path(__file__).parent
CHANGES = HERE / "build" / "changes.txt"   # written by CI before the image build (.github/workflows/ci.yml); absent locally


class Health(BaseModel):
    status: str
    version: str


class Change(BaseModel):
    date: str
    subject: str


def read_changes(path: Path) -> list[Change]:
    """The recent commits CI wrote, one `YYYY-MM-DD subject` per line; none when the file is missing."""
    if not path.is_file():
        return []
    changes: list[Change] = []
    for line in path.read_text().splitlines():
        date, _, subject = line.partition(" ")
        if subject:
            changes.append(Change(date=date, subject=subject))
    return changes


def checked_opening() -> Opening:
    opening = load_opening()
    found = release_problems(opening)
    if found:   # tests/opening/test_released.py holds the same check in CI: a deploy never gets here
        raise ValueError("the opening breaks the release lock: " + "; ".join(f"{p.cls}: {p.message}" for p in found))
    return opening


def wire(database: db.Database | None, rs: Ruleset, clock: Clock) -> Services:
    """The systems on the database, after every live save is checked to rebase under these rules (a build that would
    strand a save does not start, so the build before it keeps serving) and this build's manifest is stored; their
    nulls without a database."""
    if database is None:
        return Services()
    if check(database.engine, rs).failed:
        database.close()
        raise RuntimeError("saves.check: a live save does not rebase under this build's rules")
    rs = registered(database.engine, rs)
    key = rate_key()
    accounts = PgAccounts(database.engine, clock, key, join_key(os.environ), max_saves=MAX_SAVES)
    return Services(accounts=accounts, saves=PgSaves(database.engine, rs, clock))


def join_key(env: Mapping[str, str]) -> bytes | None:
    """ASHFALL_JOIN_KEY, 32 bytes as 64 hex characters; None (codes, words and joins refused) when it is missing or
    not that, logged by its state only."""
    raw = env.get("ASHFALL_JOIN_KEY", "").strip()
    try:
        key = bytes.fromhex(raw)
    except ValueError:
        key = b""
    state = "ok" if len(key) == 32 else ("missing" if not raw else "invalid")
    (logs.info if state == "ok" else logs.warning)(logging.getLogger("ashfall.app"), "app.join_key", state=state)
    return key if state == "ok" else None


def rate_key() -> bytes | None:
    return os.environ.get("ASHFALL_RATE_KEY", "").encode() or None


def create_app(clock: Clock = system) -> FastAPI:
    logs.setup()
    opening = checked_opening()
    rs = ruleset(opening, load_renames(), os.environ.get("BUILD_VERSION", "dev"), load_lock().release)
    game = Game(opening, rs)
    logs.info(logging.getLogger("ashfall.app"), "app.start", rules=rs.digest, version=rs.build, release=rs.release)
    database = db.from_env(os.environ)
    services = wire(database, rs, clock)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield
        if database is not None:
            database.close()

    app = FastAPI(title="Ashfall", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.db = database   # None without DATABASE_URL: the systems are their nulls
    app.state.services = services
    app.add_middleware(GZipMiddleware, minimum_size=page.GZIP_MIN)
    app.add_middleware(HeadAsGet)
    app.add_middleware(logs.RequestClock)
    app.add_middleware(CookieMiddleware)
    app.add_middleware(BodyLimit)
    app.add_middleware(CsrfMiddleware)
    app.add_middleware(OldHostRedirect)   # outermost: the old host never reaches a route
    version = rs.build
    name_every_answer(app, version, "app")
    app.include_router(game_routes(game, os.environ.get("ASHFALL_PUBLIC_URL", "") or PUBLIC_URL))
    app.include_router(page_config.routes())
    app.include_router(client_errors.routes())
    sink = None if database is None else PgFeedback(database.engine, clock, rs.build, rs.release, rate_key())
    app.include_router(feedback_routes(sink))
    changes = read_changes(CHANGES)
    page.serve_bundle(app, version)

    @app.get("/healthz", response_model=Health, tags=["ops"])
    def healthz() -> Health:
        return Health(status="ok", version=version)

    @app.get("/changes", response_model=list[Change], tags=["ops"])
    def recent_changes() -> list[Change]:
        return changes

    page.serve_shell(app, version)
    return app
