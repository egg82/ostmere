"""Two pods of different builds on the test's own database (tests/pg.py), as during a rolling deploy.

ASHFALL_RATE_KEY is set because db/tables.py names it as the key of the rate counter's address HMAC; the contract does
not name it."""
import os
from collections.abc import Iterator

import pytest

from ashfall_app import main
from ashfall_app.opening.schema import Opening
from tests import pg
from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, ok, pod
from tests.shipped_ruleset import ShippedRuleset


@pytest.fixture(scope="session", autouse=True)
def warm_request_paths(shipped_opening: Opening, shipped_ruleset: ShippedRuleset) -> None:
    """Every route family the contract tests call, driven once on a database of its own in setup (not timed). The first
    request of each kind pays for the app's lazy route state and the statements' compilation, which would otherwise be
    charged to whichever test meets it first (about 1.2 s on the slow CI node). Skipped without a test database; the
    tests that need one skip themselves."""
    admin = os.environ.get("ASHFALL_TEST_PG", "")
    if not admin:
        return
    url = pg.create(admin, pg.template(admin))
    try:
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("ASHFALL_RATE_KEY", "warm-request-paths")
            mp.setattr(main, "checked_opening", lambda: shipped_opening)
            mp.setattr(main, "ruleset", shipped_ruleset.ruleset)
            mp.setattr(main, "Game", shipped_ruleset.make_game)
            with pod(url, "warm-request-paths") as warm:
                b = Browser(warm)
                save_id, _ = begun(b)
                begun(b)
                ok(b.me())
                ok(b.http.get("/api/saves"))
                ok(b.open(save_id))
                ok(b.advance(save_id))
                ok(b.http.post(f"/api/saves/{save_id}/forecast"))
                ok(b.decide(save_id, SET_NO_ORDERS, 0))
                ok(b.dry_run(save_id, [SET_NO_ORDERS]))
                ok(b.put_me_presentation({"rules_opened": True}))
                ok(b.put_me_settings({"lessons": True}))
                ok(b.put_save_presentation(save_id, {"rule_seen": True}))
                b.feedback("warm", save_id)
                ok(b.http.post(f"/api/saves/{save_id}/delete"))
                ok(b.http.post(f"/api/saves/{save_id}/restore"))
                b.http.get("/openapi.json")
                b.http.post("/api/saves", headers={"Origin": "https://evil.example"})
    finally:
        pg.drop(url)


@pytest.fixture(autouse=True)
def rate_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ASHFALL_RATE_KEY", "blind-contract-tests")


@pytest.fixture
def pod_a(pg_url: str) -> Iterator[Pod]:
    with pod(pg_url, "contract-build-a") as p:
        yield p


@pytest.fixture
def pod_b(pg_url: str) -> Iterator[Pod]:
    with pod(pg_url, "contract-build-b") as p:
        yield p
