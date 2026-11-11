"""GET /api/saves/{id}/view (CONTRACT.txt, ENDPOINTS): the save as last written, at its own time, with nothing written:
the front page draws each save's camp from it before any game is opened."""
from tests.api_contract import rows
from tests.api_contract.site import Browser, Pod, begun, ok, ready_tap, refused


def saved_view(b: Browser, save_id: object):
    return b.http.get(f"/api/saves/{save_id}/view")


def test_the_view_is_the_save_as_written_not_advanced_and_writes_nothing(pg_url: str, pod_a: Pod):
    b = Browser(pod_a)
    save_id, s0 = begun(b)
    tap = ready_tap(s0["view"])
    assert tap is not None, "the first view offers no ready card"
    s1 = ok(b.decide(save_id, tap, s0["decisions"]))
    rows.age_saves(pg_url, 40)   # forty seconds pass unseen: an open would advance to them
    before = rows.the_save_row(pg_url)
    seen = ok(saved_view(b, save_id))
    assert seen == s1["view"] and seen["at"] < 40
    assert rows.the_save_row(pg_url) == before   # updated_at, decisions, state and the rest
    assert ok(saved_view(b, save_id)) == seen


def test_another_account_is_refused_as_the_other_save_routes_do(pod_a: Pod):
    owner = Browser(pod_a)
    save_id, _ = begun(owner)
    stranger = Browser(pod_a)
    begun(stranger)
    refused(stranger.open(save_id), 404, "not_found")
    refused(saved_view(stranger, save_id), 404, "not_found")
    refused(saved_view(Browser(pod_a), save_id), 401, "no_account")
