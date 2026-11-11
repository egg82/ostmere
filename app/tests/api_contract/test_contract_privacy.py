"""No cookie, session token, client address or save state in a log line (logs.py: "Never in a line"), over a play
through every kind of answer, ok and refused."""
import pytest

from tests.api_contract import rows
from tests.api_contract.site import SET_NO_ORDERS, Browser, Pod, begun, ok, ready_tap


def test_no_log_line_carries_the_session_the_address_or_the_state(pg_url: str, pod_a: Pod, pod_b: Pod,
                                                                   capsys: pytest.CaptureFixture[str]):
    capsys.readouterr()
    b = Browser(pod_a, "203.0.113.77")
    save_id, s0 = begun(b)
    token = b.session()
    assert token
    tap = ready_tap(s0["view"])
    assert tap is not None
    ok(b.decide(save_id, tap, 0))
    two = b.page_on(pod_b)
    assert two.decide(save_id, SET_NO_ORDERS, 0).status_code == 409
    assert two.decide(save_id, {"kind": "tap_card", "card": "no-such-card"}, 1).status_code == 422
    ok(two.open(save_id))
    assert two.open(f"{save_id}9999").status_code in (404, 422)
    assert Browser(pod_a, "203.0.113.77", origin="https://evil.example").begin().status_code == 403
    assert Browser(pod_a, "203.0.113.78", cookie=token + "x").advance(save_id).status_code == 401
    out = capsys.readouterr().out
    state = str(rows.scalar(pg_url, "SELECT state FROM saves"))
    token_hash = bytes(rows.scalar(pg_url, "SELECT token_hash FROM sessions")).hex()
    assert "event=" in out, "no log line was captured: this test would be blind"
    for name, secret in (("session token", token), ("token hash", token_hash), ("client address", "203.0.113.7"),
                         ("save state", state), ("save state", state[:40]), ("save state", '"manifest":')):
        assert secret not in out, f"a log line carries the {name}"
