"""Every verb the engine can decide has a kind to log it under (saves/write.KINDS), and a decision answering an offer
is served, not a 500: the route reads KINDS before it applies the verb."""
from collections.abc import Iterator
from dataclasses import replace
from functools import cache
from typing import get_args

import pytest

from ashfall_app import engine as e
from ashfall_app import main
from ashfall_app.db import saves as rows
from ashfall_app.opening.schema import CHAPTERS, Opening, load_opening
from ashfall_app.saves import write
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.ruleset import ruleset
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.renames import load_renames
from tests.game_client import GameClient, game_client

OFFER, ANSWER = "o_cart", "o_cart_go"


def test_every_verb_has_a_kind():
    verbs = get_args(e.Verb.__value__)
    assert len(verbs) > 1
    assert [v for v in verbs if v not in write.KINDS] == []


@cache
def day_two_opening() -> Opening:
    return load_opening(chapters=CHAPTERS)


@pytest.fixture(scope="module")
def day_two_rs() -> Ruleset:
    return ruleset(day_two_opening(), load_renames(), "dev", load_lock().release)


@pytest.fixture
def day_two(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[GameClient]:
    """The app on the opening, day one and day two."""
    monkeypatch.setattr(main, "checked_opening", day_two_opening)
    with game_client(pg_url, monkeypatch) as found:
        yield found


def shown(game: GameClient, rs: Ruleset) -> tuple[int, int]:
    """A new save's id and decisions count, its offer shown (the offer's unlock is in the save's set)."""
    save_id = game.begin()["save"]["save_id"]
    save = e.new_save(rs.rules)
    held = sorted((*save.unlocked, e.Unlock(e.UnlockKind.OFFER, OFFER)), key=e.unlock_key)
    with game.app.state.db.engine.begin() as conn:
        rows.write(conn, save_id, game.clock(), write.written(replace(save, unlocked=tuple(held)), 0, rs))
    return save_id, 0


def test_a_valid_answer_is_served(day_two: GameClient, day_two_rs: Ruleset):
    save_id, after = shown(day_two, day_two_rs)
    r = day_two.decide(save_id, {"kind": "answer_offer", "offer": OFFER, "answer": ANSWER}, after)
    assert r.status_code == 200, r.text


def test_an_unknown_offer_is_refused_as_invalid(day_two: GameClient, day_two_rs: Ruleset):
    save_id, after = shown(day_two, day_two_rs)
    r = day_two.decide(save_id, {"kind": "answer_offer", "offer": "no_such_offer", "answer": ANSWER}, after)
    assert r.status_code == 422, r.text
