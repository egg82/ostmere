"""Every status chip shown in day one has a cure on offer (cures.py): a chip that tells the player to act always has
something to act with, or its content says it has none on purpose."""
import pytest

from tests.dayone.conftest import PLAY_TIMEOUT_S
from tests.dayone.routes import plays

pytestmark = [pytest.mark.playthrough, pytest.mark.timeout(PLAY_TIMEOUT_S)]


@pytest.mark.parametrize("day_uncured", plays(), indirect=True, ids=lambda r: f"{r[0]}-{r[1]}")
def test_every_chip_shown_has_a_cure(day_uncured: list[str]):
    assert day_uncured == []
