"""WebPushSender against a push service on localhost: what each answer means, and where a request may go."""
from ashfall_app.reminders.sender import Delivery, NullSender, WebPushSender

from tests.reminders.fakepush import push_service, subscription_keys, vapid_config

PAYLOAD = {"title": "t", "body": "b", "url": "/"}


def send(url: str, allowed: bool = True) -> Delivery:
    p256dh, auth = subscription_keys()
    return WebPushSender(vapid_config(), allowed=lambda e: allowed).send(url, p256dh, auth, PAYLOAD)


def test_201_is_delivered():
    with push_service() as (base, seen):
        assert send(base + "/201") == Delivery("ok")
        assert seen.paths == ["/201"]


def test_410_means_the_subscription_is_gone():
    with push_service() as (base, _):
        assert send(base + "/410") == Delivery("gone", 410)


def test_500_is_a_failure_with_its_status():
    with push_service() as (base, _):
        assert send(base + "/500") == Delivery("error", 500, "http")


def test_a_redirect_is_not_followed():
    with push_service() as (elsewhere, other), push_service(redirect_to=elsewhere + "/201") as (base, first):
        outcome = send(base + "/redirect")
        assert outcome.kind == "error" and outcome.status is None
        assert first.paths == ["/redirect"] and other.paths == []


def test_the_default_allow_list_refuses_a_host_that_is_not_a_push_service_before_any_request():
    p256dh, auth = subscription_keys()
    with push_service() as (base, seen):
        assert WebPushSender(vapid_config()).send(base + "/201", p256dh, auth, PAYLOAD) == Delivery(
            "error", None, "not_a_push_service")
        assert seen.paths == []


def test_the_null_sender_delivers_nothing_and_keeps_the_device():
    assert NullSender().send("https://fcm.googleapis.com/x", "p", "a", PAYLOAD).kind == "error"
