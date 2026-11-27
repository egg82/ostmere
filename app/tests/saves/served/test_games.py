"""Games on one account through the app with a clock the test moves (tests/accounts/devices.py): a deleted save is
held for its days and then deleted for good by a later write, never sooner and never by a separate job; a join takes
every save of the account with it; and what the writes log."""
from collections.abc import Iterator
from datetime import timedelta

import pytest

from tests.accounts.devices import Browser, Site, code_of, site

KEPT = timedelta(days=30)


@pytest.fixture
def s(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Site]:
    with site(pg_url, monkeypatch) as found:
        yield found


def deleted(b: Browser, save_id: int) -> None:
    r = b.http.post(f"/api/saves/{save_id}/delete")
    assert r.status_code == 200, r.text


def stored(s: Site, save_id: int) -> tuple[int, int]:
    """(save rows, line rows) the database still holds for the save."""
    return (s.scalar("SELECT count(*) FROM saves WHERE id = :i", i=save_id),
            s.scalar("SELECT count(*) FROM save_lines WHERE save_id = :i", i=save_id))


def test_a_save_held_past_its_days_goes_at_the_next_write_and_one_within_them_stays(s: Site):
    b = Browser(s)
    b.play()
    old, young = b.begin()["save"]["save_id"], b.begin()["save"]["save_id"]
    for i in (old, young):   # a line on each, so their going with the save can be seen
        s.run("INSERT INTO save_lines (save_id, n, at, key) VALUES (:i, 1000, 0, 'k')", i=i)
    deleted(b, old)
    s.clock.tick(days=10)
    deleted(b, young)
    s.clock.tick(seconds=(KEPT - timedelta(days=10)).total_seconds() + 1)   # old: past its days; young: within
    assert stored(s, old)[0] == 1, "deleted for good with nothing written since"
    assert b.http.post(f"/api/saves/{old}/restore").json()["code"] == "not_found"   # past purge_at: not restorable
    assert [d["save"]["save_id"] for d in b.http.get("/api/saves").json()["deleted"]] == [young]
    b.begin()
    assert stored(s, old) == (0, 0), "a save held past its days outlived the next write"
    assert stored(s, young)[0] == 1 and stored(s, young)[1] > 0
    r = b.http.post(f"/api/saves/{young}/restore")
    assert r.status_code == 200, r.text


def test_a_delete_also_clears_what_is_past_its_days(s: Site):
    b = Browser(s)
    b.play()
    old, other = b.begin()["save"]["save_id"], b.begin()["save"]["save_id"]
    deleted(b, old)
    s.clock.tick(days=31)
    deleted(b, other)
    assert stored(s, old)[0] == 0 and stored(s, other)[0] == 1


def test_a_save_just_deleted_is_kept_whole(s: Site):
    b = Browser(s)
    b.play()
    gone = b.begin()["save"]["save_id"]
    lines = stored(s, gone)[1]
    deleted(b, gone)
    assert stored(s, gone) == (1, lines)


def test_a_join_takes_every_save_of_the_account_deleted_ones_included(s: Site):
    a, other = Browser(s), Browser(s)
    first = a.play()
    second = a.begin()["save"]["save_id"]
    gone = a.begin()["save"]["save_id"]
    deleted(a, gone)
    joined = other.join(code_of(a.code()))
    assert joined.status_code == 200, joined.text
    listed = other.http.get("/api/saves").json()
    assert sorted(x["save_id"] for x in listed["saves"]) == sorted([first, second])
    assert [d["save"]["save_id"] for d in listed["deleted"]] == [gone]


def test_each_write_logs_one_line_with_ids_and_counts(s: Site, capsys: pytest.CaptureFixture[str]):
    b = Browser(s)
    b.play()
    gone = b.begin()["save"]["save_id"]
    capsys.readouterr()
    deleted(b, gone)
    assert b.http.post(f"/api/saves/{gone}/restore").status_code == 200
    out = capsys.readouterr().out
    assert "event=save.deleted" in out and f"save={gone}" in out and "event=save.restored" in out
    token = b.session()
    assert token and token not in out
