"""One notification to one device, and what its answer does to the device: a gone subscription deletes the row, any
other failure keeps it. Each send that does not go is one log line, never with its endpoint or keys."""

import logging
from collections.abc import Mapping
from typing import Literal

from sqlalchemy import Engine

from .. import logs
from ..db import reminders as store
from .sender import Sender

log = logging.getLogger("ashfall.reminders")


def deliver(engine: Engine, sender: Sender, device: store.Target, payload: Mapping[str, str],
            kind: str) -> Literal["ok", "gone", "error"]:
    """`kind` names what was sent in the log lines (reminder, notice)."""
    delivery = sender.send(device.endpoint, device.p256dh, device.auth, payload)
    if delivery.kind == "gone":
        logs.info(log, "reminders.gone", device=device.id, kind=kind, status=delivery.status)
        with engine.begin() as conn:
            store.delete_device(conn, device.id)
    elif delivery.kind == "error":
        logs.warning(log, "reminders.send_failed", device=device.id, kind=kind, status=delivery.status,
                     why=delivery.why)
    return delivery.kind
