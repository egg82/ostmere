"""Reminders across accounts: a join moves the joining account's devices, and the one mention's flag
(AccountPresentation.reminder_mentioned) ORs across the browsers of an account."""
from collections.abc import Iterator

import pytest

from tests.accounts.devices import Browser, Site, code_of, site
from tests.reminders.wire import PUSH, on


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def owner(s: Site, endpoint: str) -> int | None:
    found: int | None = s.scalar("SELECT account_id FROM reminder_devices WHERE endpoint = :e", e=endpoint)
    return found


def account_of(b: Browser) -> int:
    save = b.begin()["save"]["save_id"]
    found: int = b.site.scalar("SELECT account_id FROM saves WHERE id = :i", i=save)
    return found


def test_a_merge_moves_the_devices_to_the_surviving_account(s: Site):
    a, b = Browser(s), Browser(s)
    a.play()
    b.play()
    assert b.http.put("/api/reminders", json=on(PUSH + "b")).status_code == 200
    there = account_of(a)
    r = b.join(code_of(a.code()), merge=True)
    assert r.status_code == 200, r.text
    assert owner(s, PUSH + "b") == there


def test_a_join_from_an_account_with_no_progress_keeps_its_device(s: Site):
    a, b = Browser(s), Browser(s)
    a.play()
    b.begin()
    assert b.http.put("/api/reminders", json=on(PUSH + "b")).status_code == 200
    there = account_of(a)
    assert b.join(code_of(a.code())).status_code == 200
    assert owner(s, PUSH + "b") == there


def test_the_mention_flag_ors_across_two_browsers_of_one_account(s: Site):
    a, b = Browser(s), Browser(s)
    a.play()
    assert b.join(code_of(a.code())).status_code == 200
    assert a.me()["account"]["presentation"]["reminder_mentioned"] is False
    r = a.http.put("/api/me/presentation", json={"reminder_mentioned": True})
    assert r.status_code == 200 and r.json()["presentation"]["reminder_mentioned"] is True
    r = b.http.put("/api/me/presentation", json={"reminder_mentioned": False, "devices_opened": True})
    assert r.status_code == 200, r.text
    assert r.json()["presentation"]["reminder_mentioned"] is True
    assert b.me()["account"]["presentation"]["reminder_mentioned"] is True
