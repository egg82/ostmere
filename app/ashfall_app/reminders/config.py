"""Whether push is on: both VAPID keys present and well formed, and the operator's contact (`VAPID_SUBJECT`, a `mailto:`
or `https:` URL that push services may use to reach whoever runs the deployment) set."""

import base64
import json
import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from .. import logs

log = logging.getLogger("ashfall.reminders")


@dataclass(frozen=True)
class Config:
    public_key: str
    private_key: str
    subject: str


def _b64url(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


@cache
def after_hours() -> tuple[int, ...]:
    """The absences a player may pick, in hours (choices.json): the page shows these and a PUT takes only these."""
    found: list[int] = json.loads(Path(__file__).with_name("choices.json").read_text(encoding="utf-8"))
    return tuple(found)


def _decodes(s: str, size: int) -> bool:
    try:
        raw = _b64url(s)
    except ValueError:
        return False
    return len(raw) == size and (size != 65 or raw[0] == 4)


def public_key(env: Mapping[str, str] = os.environ) -> str | None:
    """The VAPID public key a page subscribes with, when it is set and well formed: the web tier holds only this one."""
    pub = env.get("VAPID_PUBLIC_KEY", "").strip()
    return pub if pub and _decodes(pub, 65) else None


def load_config(env: Mapping[str, str] = os.environ) -> Config | None:
    """Both keys valid and a subject set, or push is off: half a configuration is no configuration."""
    pub = env.get("VAPID_PUBLIC_KEY", "").strip()
    priv = env.get("VAPID_PRIVATE_KEY", "").strip()
    subject = env.get("VAPID_SUBJECT", "").strip()
    if not pub or not priv or not subject:
        return None
    ok = public_key(env) is not None and _decodes(priv, 32)
    if not ok:
        logs.warning(log, "reminders.config_bad", why="vapid_keys_malformed", push="off")
        return None
    return Config(pub, priv, subject)
