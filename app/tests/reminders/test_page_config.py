"""/page-config.json's reminders: offered with a well-formed VAPID public key, null without one."""
import base64

from ashfall_app.page_config import page_config
from tests.game_client import GameClient

KEY = base64.urlsafe_b64encode(b"\x04" + bytes(range(64))).decode().rstrip("=")


def test_a_well_formed_key_offers_reminders_with_the_absences():
    found = page_config({"VAPID_PUBLIC_KEY": KEY}).reminders
    assert found is not None
    assert found.public_key == KEY and found.after_hours == [12, 24, 72, 168]


def test_no_key_or_a_malformed_one_offers_none():
    assert page_config({}).reminders is None
    assert page_config({"VAPID_PUBLIC_KEY": "abc"}).reminders is None
    assert page_config({"VAPID_PUBLIC_KEY": KEY[:-4]}).reminders is None


def test_the_route_names_reminders_even_when_null(game: GameClient):
    """A page tells "not available here" (null) from a build before reminders (no key at all)."""
    found = game.client.get("/page-config.json").json()
    assert "reminders" in found and found["reminders"] is None
