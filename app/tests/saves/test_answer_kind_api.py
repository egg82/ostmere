"""The wire's answer_kind order verb on a test chapter with a kind (tests/opening/fixtures/askkinds.toml; CONTRACT.txt,
"Offers"): an order naming a declared kind and role is stored and served back as sent; one naming a role the kind
does not have, or a kind no offer declares, is a 422 that writes nothing; the player cannot send it as a decision;
Content.offer_infos carries each offer's kind and each answer's role."""
from collections.abc import Iterator
from pathlib import Path

import pytest

from ashfall_app import main
from ashfall_app.db import saves as rows
from ashfall_app.opening.schema import CHAPTERS, Opening, load_opening
from tests.game_client import GameClient, game_client

FIXTURE = Path(__file__).resolve().parent.parent / "opening" / "fixtures" / "askkinds.toml"


def order(kind: str, role: str) -> dict[str, object]:
    return {"kind": "set_orders", "orders": [
        {"when": {"kind": "after_time", "at": 0}, "then": {"kind": "answer_kind", "offer_kind": kind, "role": role}}]}


@pytest.fixture
def kinded(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[GameClient]:
    def opening() -> Opening:
        return load_opening(chapters=(*CHAPTERS, FIXTURE))
    monkeypatch.setattr(main, "checked_opening", opening)
    with game_client(pg_url, monkeypatch) as found:
        yield found


def written(game: GameClient, save_id: int) -> tuple[int, object]:
    with game.app.state.db.engine.begin() as conn:
        return len(rows.decisions_after(conn, save_id, 0)), rows.save(conn, save_id, None)


def test_a_declared_kind_and_role_is_stored_as_an_order(kinded: GameClient):
    save_id = kinded.begin()["save"]["save_id"]
    r = kinded.decide(save_id, order("q_ask", "yes"), 0)
    assert r.status_code == 200, r.text
    assert written(kinded, save_id)[0] == 1


@pytest.mark.parametrize("kind, role", [("q_ask", "maybe"), ("no_such_kind", "yes")])
def test_a_role_not_of_the_kind_is_a_422_that_writes_nothing(kinded: GameClient, kind: str, role: str):
    save_id = kinded.begin()["save"]["save_id"]
    before = written(kinded, save_id)
    kinded.clock.tick(50)
    r = kinded.decide(save_id, order(kind, role), 0)
    assert r.status_code == 422, r.text
    assert written(kinded, save_id) == before


def test_the_player_cannot_send_it_as_a_decision(kinded: GameClient):
    save_id = kinded.begin()["save"]["save_id"]
    before = written(kinded, save_id)
    r = kinded.decide(save_id, {"kind": "answer_kind", "offer_kind": "q_ask", "role": "yes"}, 0)
    assert r.status_code == 422, r.text
    assert written(kinded, save_id) == before


def test_content_serves_each_offers_kind_and_each_answers_role(kinded: GameClient):
    content = kinded.client.get("/api/content").json()
    by_id = {o["offer"]: o for o in content["offer_infos"]}
    assert by_id["q_first"]["kind"] == "q_ask"
    assert [(a["answer"], a["role"]) for a in by_id["q_second"]["answers"]] == [("q_second_no", "no"), ("q_second_yes", "yes")]
    unkinded = [o for o in content["offer_infos"] if o["kind"] is None]
    assert unkinded and all(a["role"] is None for o in unkinded for a in o["answers"])
