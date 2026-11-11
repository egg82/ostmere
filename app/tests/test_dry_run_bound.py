"""A dry run takes at most 8 decisions (api/CONTRACT.txt, "Request limits"); the page sends at most 2."""
from typing import Any

import pytest
from pydantic import ValidationError

from ashfall_app.api.saves_models import DryRunRequest

TAP: dict[str, Any] = {"kind": "tap_card", "card": "stand_up"}


def test_the_bound_leaves_room_for_the_page():
    DryRunRequest.model_validate({"decisions": [TAP] * 8})


def test_a_dry_run_is_at_most_8_decisions():
    with pytest.raises(ValidationError):
        DryRunRequest.model_validate({"decisions": [TAP] * 9})
