"""The allow-list of push services (reminders/push_hosts.py)."""
import pytest

from ashfall_app.reminders.push_hosts import is_push_service


@pytest.mark.parametrize("endpoint", [
    "https://fcm.googleapis.com/fcm/send/abc",
    "https://updates.push.services.mozilla.com/wpush/v2/abc",
    "https://web.push.apple.com/abc",
    "https://wns2-par02p.notify.windows.com/w/?token=abc",
])
def test_a_browsers_own_push_service_is_accepted(endpoint: str):
    assert is_push_service(endpoint)


@pytest.mark.parametrize("endpoint", [
    "https://evil.example/fcm/send/abc",
    "http://fcm.googleapis.com/fcm/send/abc",
    "https://fcm.googleapis.com.evil.example/abc",
    "https://evil.example/.push.apple.com",
    "https://user@fcm.googleapis.com/abc",
    "https://fcm.googleapis.com:8443/abc",
    "https://evil.example\\@fcm.googleapis.com/abc",
    "https://127.0.0.1/abc",
    "https://169.254.169.254/latest",
    "",
])
def test_anything_else_is_refused(endpoint: str):
    assert not is_push_service(endpoint)
