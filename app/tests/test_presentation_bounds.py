"""What the page keeps about the player and about a save is bounded (api/CONTRACT.txt, "Request limits"): lists of at
most 512 items, free strings of at most 64 characters."""
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from ashfall_app.api.saves_models import AccountPresentation, SavePresentation
from tests.game_client import GameClient

END: dict[str, Any] = {"lesson": "l", "skipped": False, "step": 0, "longest_wait_s": 0}
LISTS: list[tuple[type[BaseModel], str]] = [
    (AccountPresentation, "ledger_lines"), (AccountPresentation, "mix_stopped"), (AccountPresentation, "journal_read"),
    (SavePresentation, "mix_offered"), (SavePresentation, "lessons"),
]


def test_the_bounds_leave_room_for_what_a_game_holds():
    for model in (AccountPresentation, SavePresentation):
        model.model_validate({f: ["x" * 64] * 512 for m, f in LISTS if m is model})
    AccountPresentation.model_validate({"switch_offered": [{"chip": "c" * 64, "mix_id": "m" * 40}] * 512})
    SavePresentation.model_validate({"lesson_ends": [END] * 512})


@pytest.mark.parametrize(("model", "field"), LISTS)
def test_a_list_of_names_is_at_most_512_items(model: type[BaseModel], field: str):
    with pytest.raises(ValidationError):
        model.model_validate({field: ["a"] * 513})


def test_the_object_lists_are_at_most_512_items():
    with pytest.raises(ValidationError):
        SavePresentation.model_validate({"lesson_ends": [END] * 513})
    with pytest.raises(ValidationError):
        AccountPresentation.model_validate({"switch_offered": [{"chip": "c", "mix_id": "m"}] * 513})


def test_every_free_string_is_at_most_64_characters():
    long = "x" * 65
    for model, field in LISTS:
        with pytest.raises(ValidationError):
            model.model_validate({field: [long]})
    with pytest.raises(ValidationError):
        SavePresentation.model_validate({"lesson_ends": [{**END, "lesson": long}]})
    for body in ({"switch_offered": [{"chip": long, "mix_id": "m"}]}, {"switch_offered": [{"chip": "c", "mix_id": long}]}):
        with pytest.raises(ValidationError):
            AccountPresentation.model_validate(body)


def test_an_oversized_put_is_answered_422_and_logs_no_lines(game: GameClient, capsys: pytest.CaptureFixture[str]):
    save = game.begin()["save"]["save_id"]
    capsys.readouterr()
    body = {"lesson_ends": [{**END, "lesson": f"l{n}"} for n in range(600)]}
    r = game.client.put(f"/api/saves/{save}/presentation", json=body)
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision"
    assert "event=lesson.end" not in capsys.readouterr().out


@pytest.mark.parametrize(("model", "field"), LISTS)
@pytest.mark.parametrize("name", ["\U0001F600", "a b", "café", ""])
def test_a_list_entry_is_an_id_not_free_text(model: type[BaseModel], field: str, name: str):
    with pytest.raises(ValidationError):
        model.model_validate({field: [name]})


def test_an_offered_chip_is_an_id():
    with pytest.raises(ValidationError):
        AccountPresentation.model_validate({"switch_offered": [{"chip": "\U0001F600", "mix_id": "m"}]})


def test_the_ids_a_page_sends_fit():
    ids = ["first_mix", "journal_numbers", "wood", "snare.1", "a-b", "x" * 64]
    for model in (AccountPresentation, SavePresentation):
        model.model_validate({f: ids for m, f in LISTS if m is model})
    AccountPresentation.model_validate({"switch_offered": [{"chip": i, "mix_id": "my mix \U0001F600"} for i in ids]})
