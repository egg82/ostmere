"""A saved mix is bounded (api/CONTRACT.txt, "Request limits") and flattening nested mixes costs a visit per mix, not
one per path through them (a mix nesting the one below twice, twenty deep, is a million paths)."""
from collections.abc import Iterator
from typing import Any

import pytest
from pydantic import ValidationError

from dataclasses import replace

from ashfall_app import engine as e
from ashfall_app.api.convert import verb
from ashfall_app.api.saves_models import DecisionRequest
from ashfall_app.db import saves as rows
from ashfall_app.db.engine import open_database
from ashfall_app.saves.write import written
from ashfall_app.engine.ids import CardId, MixId
from tests.game_client import GameClient
from tests.shipped_ruleset import ShippedRuleset

SHARE: dict[str, Any] = {"kind": "card_share", "card": "c", "share_bp": 0}
Json = dict[str, Any]


def save_mix(**parts: list[dict[str, Any]]) -> None:
    DecisionRequest.model_validate({"decision": {"kind": "save_mix", "mix": {"id": "m", "components": [], **parts}},
                                    "after": 0})


def test_the_bounds_leave_room_for_what_a_game_holds():
    save_mix(components=[SHARE] * 64)


def test_a_mix_has_at_most_64_components():
    with pytest.raises(ValidationError):
        save_mix(components=[SHARE] * 65)


def stack(depth: int) -> tuple[e.Mix, ...]:
    bottom = e.Mix(MixId("m0"), (e.CardShare(CardId("a"), 7777),))
    return (bottom, *(e.Mix(MixId(f"m{k}"), (e.SubMix(MixId(f"m{k - 1}"), 3333), e.SubMix(MixId(f"m{k - 1}"), 3333)))
                      for k in range(1, depth + 1)))


def test_the_flattened_shares_of_a_nest_are_summed_per_card():
    assert e.flatten_shares(stack(2), MixId("m2")) == (e.CardShare(CardId("a"), 3454),)


class Counted(tuple[e.CardShare | e.SubMix, ...]):
    """Components that count how often a walk reads them: once per mix visited."""

    reads = 0

    def __iter__(self) -> Iterator[e.CardShare | e.SubMix]:
        Counted.reads += 1
        return super().__iter__()


def test_flattening_visits_each_mix_once():
    Counted.reads = 0
    nest = tuple(e.Mix(m.id, Counted(m.components)) for m in stack(14))
    e.flatten_shares(nest, MixId("m14"))
    assert Counted.reads <= 15


def flat_mix(n: int) -> Json:
    return {"kind": "save_mix", "mix": {"id": f"m{n}", "components": [{"kind": "card_share", "card": "stand_up", "share_bp": 1000}]}}


class Decider:
    """One save's decisions in order, each sent after the count the last accepted one returned."""

    def __init__(self, game: GameClient) -> None:
        self.game, self.save, self.done = game, game.begin()["save"]["save_id"], 0

    def __call__(self, decision: Json) -> Any:
        r = self.game.decide(self.save, decision, after=self.done)
        if r.status_code == 200:
            self.done = r.json()["decisions"]
        return r


@pytest.fixture
def at_the_cap(game: GameClient, pg_url: str, shipped_ruleset: ShippedRuleset) -> Decider:
    """A save holding 64 mixes. The engine makes the 64 saves in memory and the row is written once: 64 requests
    would each load, decide and write the save again (1.7 s)."""
    decide = Decider(game)
    database = open_database(pg_url, max_size=2)
    try:
        with database.engine.begin() as conn:
            row = rows.save(conn, decide.save, None)
            assert row is not None
            rs = replace(shipped_ruleset.rs, build=row.build, release=row.release)
            save = e.decode(row.state, rs.rules)
            for n in range(64):
                request = DecisionRequest.model_validate({"decision": flat_mix(n), "after": decide.done})
                save = e.decide(save, rs.rules, save.time, verb(request.decision, rs.rules))
            assert len(save.mixes) == 64, "control: the save is at the cap"
            rows.write(conn, decide.save, row.updated_at, written(save, 64, rs))
    finally:
        database.close()
    decide.done = 64
    return decide


def test_a_save_holds_at_most_64_mixes_and_a_65th_is_answered_422(at_the_cap: Decider):
    decide = at_the_cap
    assert decide(flat_mix(0)).status_code == 200, "control: a saved mix is replaced in place at the cap"
    r = decide(flat_mix(64))
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", r.text
    assert decide({"kind": "delete_mix", "mix_id": "m1"}).status_code == 200
    assert decide(flat_mix(64)).status_code == 200, "control: room again after a delete"


def test_the_page_is_served_the_mix_bound(game: GameClient):
    assert game.client.get("/api/content").json()["limits"]["max_mixes"] == 64
