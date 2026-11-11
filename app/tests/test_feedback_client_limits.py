"""One client cannot fill feedback's site-wide cap (api/CONTRACT.txt, "POST /api/feedback"): an IPv4 address with many
accounts, or an IPv6 /48 with many /64s, meets a limit of its own first, and another client still gets through."""
from fastapi.testclient import TestClient

from ashfall_app.feedback import service
from tests.game_client import SITE, GameClient

STRANGER = "198.51.100.7"


def browser(game: GameClient, host: str) -> TestClient:
    return TestClient(game.app, base_url=SITE, headers={"Origin": SITE}, client=(host, 5000))


def send(c: TestClient) -> int:
    return c.post("/api/feedback", json={"text": "words"}).status_code


def test_one_ipv4_address_with_many_accounts_does_not_fill_the_site_wide_cap(game: GameClient):
    sent = 0
    for _ in range(6):
        c = browser(game, "203.0.113.9")
        assert c.post("/api/saves").status_code == 200
        sent += sum(send(c) == 204 for _ in range(service.PER_WHO))
    assert sent < service.OVERALL // 2
    assert send(browser(game, STRANGER)) == 204


def test_one_ipv6_48_with_many_64s_does_not_fill_the_site_wide_cap(game: GameClient):
    sent = sum(send(browser(game, f"2001:db8:1:{n:x}::1")) == 204 for n in range(8) for _ in range(service.PER_WHO))
    assert sent < service.OVERALL // 2
    assert send(browser(game, STRANGER)) == 204


def test_a_client_under_its_limits_is_heard(game: GameClient):
    c = browser(game, "203.0.113.9")
    assert [send(c) for _ in range(service.PER_WHO)] == [204] * service.PER_WHO
    assert send(c) == 429
