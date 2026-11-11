"""Fixtures for the saves service: a database of the test's own, a clock the test moves, today's rules as build b2
(content release 2), and an account to own saves."""
from collections.abc import Iterator
from dataclasses import replace

import pytest
from sqlalchemy import Engine

from ashfall_app.db import accounts
from ashfall_app.db.engine import open_database
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.saves.service import PgSaves
from tests.fake_clock import FakeClock
from tests.saves.changes import RENAMES, changed_opening
from tests.shipped_ruleset import ShippedRuleset


@pytest.fixture
def engine(pg_url: str) -> Iterator[Engine]:
    database = open_database(pg_url, max_size=6)
    yield database.engine
    database.close()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture(scope="session")
def rs(shipped_ruleset: ShippedRuleset) -> Ruleset:
    """Today's rules under build b2 of release 2: the session's shipped Ruleset, which names only a build and a release
    differently, not another build of it (setup under the 6 s limit: 0.33 s here, ~1.7 s on a slow node)."""
    return replace(shipped_ruleset.rs, build="b2", release=2)


@pytest.fixture(scope="session")
def rs_changed() -> Ruleset:
    """The test change (tests/saves/changes.py) as a later build, b3, of release 3."""
    return replace(ruleset(changed_opening(), [], "b3", 3), renames=RENAMES)


@pytest.fixture
def saves(engine: Engine, rs: Ruleset, clock: FakeClock) -> PgSaves:
    return PgSaves(engine, rs, clock)


@pytest.fixture
def account(engine: Engine, clock: FakeClock) -> int:
    with engine.begin() as conn:
        return accounts.create_account(conn, clock())
