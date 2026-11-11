"""Delivery of one Web Push message, behind a `Sender` so the job runs with a Null Object where there are no keys."""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

import requests
from py_vapid import Vapid01
from pywebpush import WebPushException, webpush

from .config import Config
from .push_hosts import is_push_service

TTL_SECONDS = 12 * 3600
"""A reminder the phone could not take by morning is not worth delivering."""

type Kind = Literal["ok", "gone", "error"]


@dataclass(frozen=True)
class Delivery:
    """`gone`: the push service says the subscription no longer exists. `error`: anything else that went wrong; `status`
    is the HTTP status when there was one and `why` names the failure (a refused endpoint, an HTTP status, the type of a
    network error), never a message, which can carry the endpoint."""

    kind: Kind
    status: int | None = None
    why: str = ""


class Sender(Protocol):
    def send(self, endpoint: str, p256dh: str, auth: str, payload: Mapping[str, str]) -> Delivery: ...


class NullSender:
    """Nobody to deliver with (no VAPID keys): every send fails and keeps its device."""

    def send(self, endpoint: str, p256dh: str, auth: str, payload: Mapping[str, str]) -> Delivery:
        return Delivery("error", why="no_sender")


class WebPushSender:
    def __init__(self, cfg: Config, allowed: Callable[[str], bool] = is_push_service) -> None:
        self._cfg = cfg
        self._allowed = allowed

    def send(self, endpoint: str, p256dh: str, auth: str, payload: Mapping[str, str]) -> Delivery:
        """A push service answers for itself, so a redirect is never followed (max_redirects 0 raises at the first
        one): an endpoint cannot hand the server's request on to another address."""
        if not self._allowed(endpoint):
            return Delivery("error", why="not_a_push_service")
        try:
            with requests.Session() as session:
                session.max_redirects = 0
                webpush(
                    subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
                    data=json.dumps(dict(payload)),
                    vapid_private_key=Vapid01.from_raw(self._cfg.private_key.encode()),
                    vapid_claims={"sub": self._cfg.subject},
                    ttl=TTL_SECONDS,
                    timeout=10,
                    requests_session=session,
                )
            return Delivery("ok")
        except WebPushException as e:
            status = e.response.status_code if e.response is not None else None
            if status in (404, 410):
                return Delivery("gone", status)
            return Delivery("error", status, "http" if status is not None else type(e).__name__)
        except Exception as e:   # network trouble, bad subscription keys: keep the device
            return Delivery("error", None, type(e).__name__)
