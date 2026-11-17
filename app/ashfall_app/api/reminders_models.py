"""Wire models of reminders (CONTRACT.txt, "Reminders"). The conventions of models.py hold here."""
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AfterValidator, BaseModel, Field, model_validator

from ..reminders.config import after_hours
from ..reminders.push_hosts import is_push_service
from .models import Request

type Hour = Annotated[int, Field(ge=0, le=23)]
type Key = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+={0,2}$")]


def _offered(hours: int) -> int:
    if hours not in after_hours():
        raise ValueError(f"after_hours is one of {list(after_hours())}")
    return hours


def _push_service(endpoint: str) -> str:
    if not is_push_service(endpoint):
        raise ValueError("endpoint is not a browser push service")
    return endpoint


def _zone(tz: str) -> str:
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as ex:
        raise ValueError("tz is not an IANA time zone") from ex
    return tz


type Endpoint = Annotated[str, Field(max_length=1024), AfterValidator(_push_service)]


class ReminderWindow(Request):
    """When a reminder may come: once the player has been away `after_hours`, at a local hour from `send_from_hour` up
    to `send_until_hour` (past midnight when from is later than until; equal: any hour)."""

    after_hours: Annotated[int, AfterValidator(_offered)]
    """One of /page-config.json's reminders.after_hours."""
    send_from_hour: Hour
    send_until_hour: Hour


class ReminderOn(Request):
    """This browser's push subscription (PushSubscription.toJSON()'s endpoint and keys) and its time zone."""

    endpoint: Endpoint
    p256dh: Key
    auth: Key
    tz: Annotated[str, Field(min_length=1, max_length=64), AfterValidator(_zone)]
    """The device's IANA zone (Intl.DateTimeFormat().resolvedOptions().timeZone): the window's hours are its."""
    window: ReminderWindow | None = None
    """The absence reminder's window; null, that reminder off. Null with hands_free null: refresh a browser already on
    (keys, zone, its account) and answer its choice; 404 when it is not on."""
    hands_free: bool | None = None
    """The hands-free notice on or off; null with a window: off."""

    @model_validator(mode="after")
    def _something_on(self) -> "ReminderOn":
        if self.window is None and self.hands_free is False:
            raise ValueError("turn something on, or DELETE to turn this browser off")
        return self

    @property
    def refresh(self) -> bool:
        return self.window is None and self.hands_free is None


class ReminderOff(Request):
    endpoint: Annotated[str, Field(min_length=1, max_length=1024)]


class Reminder(BaseModel):
    window: ReminderWindow | None
    """Null: the absence reminder is off (the hands-free notice is on)."""
    hands_free: bool
