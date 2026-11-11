"""Postgres text holds no U+0000, so one in a string a request stores would be a 500 at the write. The wire models refuse
it first (api/CONTRACT.txt, "Request limits"): 422 invalid_decision, before any limit try is spent or anything written."""
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import text

from ashfall_app.api.saves_models import AccountPresentation, DecisionRequest
from ashfall_app.feedback.routes import FeedbackRequest
from tests.game_client import GameClient

NUL = "a\x00b"
MIX: dict[str, Any] = {"kind": "save_mix", "mix": {"id": NUL, "components": []}}


def test_a_feedback_text_with_a_nul_is_refused():
    with pytest.raises(ValidationError):
        FeedbackRequest.model_validate({"text": NUL})
    FeedbackRequest.model_validate({"text": "a\nb\tc é"})


def test_a_switch_offers_mix_id_with_a_nul_is_refused():
    with pytest.raises(ValidationError):
        AccountPresentation.model_validate({"switch_offered": [{"chip": "c", "mix_id": NUL}]})
    AccountPresentation.model_validate({"switch_offered": [{"chip": "c", "mix_id": "my mix é"}]})


def test_a_saved_mixs_id_with_a_nul_is_refused():
    with pytest.raises(ValidationError):
        DecisionRequest.model_validate({"decision": MIX, "after": 0})


def test_feedback_with_a_nul_is_422_and_spends_no_try(game: GameClient):
    r = game.client.post("/api/feedback", json={"text": NUL})
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", r.text
    with game.app.state.db.engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM tries WHERE kind LIKE 'feedback%'")).scalar_one() == 0


def test_a_decision_and_a_dry_run_with_a_nul_are_422(game: GameClient):
    save_id = game.begin()["save"]["save_id"]
    r = game.decide(save_id, MIX, after=0)
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", r.text
    r = game.client.post(f"/api/saves/{save_id}/dry-run", json={"decisions": [MIX]})
    assert r.status_code == 422 and r.json()["code"] == "invalid_decision", r.text
