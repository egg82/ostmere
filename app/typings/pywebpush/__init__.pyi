from typing import Any

import requests
from py_vapid import Vapid01

class WebPushException(Exception):
    response: requests.Response | None

def webpush(
    subscription_info: dict[str, Any],
    data: str | None = ...,
    vapid_private_key: Vapid01 | str | None = ...,
    vapid_claims: dict[str, Any] | None = ...,
    ttl: int = ...,
    timeout: float | None = ...,
    requests_session: requests.Session | None = ...,
) -> requests.Response: ...
