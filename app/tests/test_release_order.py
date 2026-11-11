"""Two builds mid-deploy, through HTTP, on one database: the older serves the released content (today's opening, at the
lock's release), the newer the release after it, a numbers-only retune of it (tests/saves/changes.py, retuned_opening)
that the older could rebase back from without an error. Once the newer has written a save, the older answers 503
save_unavailable for it and writes nothing (CONTRACT.txt, "Saves across releases and pods"): builds are ordered by
release, never by digest alone."""
from collections.abc import Callable, Generator
from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from ashfall_app import main
from ashfall_app.api.service import Game
from ashfall_app.db.tables import saves
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.ruleset import ruleset
from tests.game_client import RATE_KEY, SITE
from tests.saves.changes import retuned_opening
from tests.shipped_ruleset import ShippedRuleset

Built = tuple[Ruleset, Game]


def built_ruleset(built: Built) -> Callable[..., Ruleset]:
    return lambda *_: built[0]


def built_game(built: Built) -> Callable[..., Game]:
    return lambda *_: built[1]


@contextmanager
def app(pg_url: str, build: str, opening: Opening, release: int, built: Built) -> Generator[FastAPI]:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DATABASE_URL", pg_url)
        mp.setenv("ASHFALL_RATE_KEY", RATE_KEY)
        mp.setenv("BUILD_VERSION", build)
        mp.setattr(main, "checked_opening", lambda: opening)
        mp.setattr(main, "load_lock", lambda: load_lock().model_copy(update={"release": release}))
        mp.setattr(main, "ruleset", built_ruleset(built))
        mp.setattr(main, "Game", built_game(built))
        made = main.create_app()
    with TestClient(made, base_url=SITE):
        yield made


def row(a: FastAPI) -> tuple[object, ...]:
    with a.state.db.engine.connect() as conn:
        return tuple(conn.execute(select(saves)).one())


@pytest.fixture(scope="module")
def retuned() -> Opening:
    return retuned_opening()


RELEASE = load_lock().release


@pytest.fixture(scope="module")
def builds(shipped_opening: Opening, shipped_ruleset: ShippedRuleset, retuned: Opening) -> tuple[Built, Built]:
    """Each build's Ruleset and Game, built once in setup: the older's is the session's shipped one under its name, the
    newer's the real builders' on the retune, a release on."""
    old = shipped_ruleset.ruleset(shipped_opening, shipped_ruleset.renames, "old", RELEASE)
    new = ruleset(retuned, shipped_ruleset.renames, "new", RELEASE + 1)
    return (old, shipped_ruleset.make_game(shipped_opening, old)), (new, Game(retuned, new))


def test_after_a_later_release_writes_a_save_the_earlier_one_never_does(pg_url: str, shipped_opening: Opening, retuned: Opening,
                                                                        builds: tuple[Built, Built]):
    with (app(pg_url, "old", shipped_opening, RELEASE, builds[0]) as older,
          app(pg_url, "new", retuned, RELEASE + 1, builds[1]) as newer):
        old_page = TestClient(older, base_url=SITE, headers={"Origin": SITE})
        made = old_page.post("/api/saves").json()
        save = made["save"]["save_id"]
        tap = {"decision": {"kind": "tap_card", "card": "stand_up"}, "after": 0}
        assert old_page.post(f"/api/saves/{save}/decisions", json=tap).status_code == 200
        new_page = TestClient(newer, base_url=SITE, headers={"Origin": SITE}, cookies=old_page.cookies)
        r = new_page.post(f"/api/saves/{save}/advance")
        assert r.status_code == 200 and r.json()["rules_digest"] != made["step"]["rules_digest"], r.text
        written = row(newer)
        for path in ("advance", "open"):
            r = old_page.post(f"/api/saves/{save}/{path}")
            assert (r.status_code, r.json()["code"], r.headers["retry-after"]) == (503, "save_unavailable", "3"), r.text
        r = old_page.post(f"/api/saves/{save}/decisions", json={**tap, "after": 1})
        assert (r.status_code, r.json()["code"]) == (503, "save_unavailable")
        assert row(older) == written   # the older build wrote nothing
        assert new_page.post(f"/api/saves/{save}/decisions", json={**tap, "after": 1}).status_code in (200, 422)
