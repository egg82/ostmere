"""Reminders (CONTRACT.txt, "Reminders"): this browser's push subscription turned on, refreshed or off. The endpoint
travels only in a body, never a URL, so no access log holds it. Each asks the Accounts system (services.py)."""
from fastapi import APIRouter, Request, Response

from .. import services
from ..accounts.interface import AccountsUnavailable, Subscription
from ..db.reminders import Window
from . import session
from .error_models import ApiError
from .errors import not_found, unavailable
from .reminders_models import Reminder, ReminderOff, ReminderOn, ReminderWindow

_ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ApiError, "description": "no_account"},
    422: {"model": ApiError, "description": "invalid_decision: not a push service, an IANA zone or an offered absence"},
    503: {"model": ApiError, "description": "save_unavailable: no database (Retry-After)"},
}
_PUT_ERRORS: dict[int | str, dict[str, object]] = {
    **_ERRORS, 404: {"model": ApiError, "description": "not_found: no window sent and this browser is not on"}}


def add_reminder_routes(router: APIRouter) -> None:
    @router.put("/reminders", response_model=Reminder, operation_id="put_reminder", responses=_PUT_ERRORS)
    def put_reminder(request: Request, body: ReminderOn) -> Reminder:
        """Reminders on for this browser with the window sent, or, with none, its keys refreshed; its window."""
        found = session.account(request)
        sub = Subscription(body.endpoint, body.p256dh, body.auth, body.tz)
        w = body.window
        picked = None if w is None else Window(w.after_hours, w.send_from_hour, w.send_until_hour)
        try:
            kept = services.of(request).accounts.keep_reminder(found, sub, picked)
        except AccountsUnavailable as ex:
            raise unavailable(str(ex)) from ex
        if kept is None:
            raise not_found("reminders are not on for this browser")
        return Reminder(window=ReminderWindow(after_hours=kept.after_hours, send_from_hour=kept.send_from_hour,
                                              send_until_hour=kept.send_until_hour))

    @router.delete("/reminders", status_code=204, response_class=Response, operation_id="delete_reminder",
                   responses=_ERRORS)
    def delete_reminder(request: Request, body: ReminderOff) -> Response:
        """Reminders off for this browser. Answers 204 whether or not it was on."""
        found = session.account(request)
        services.of(request).accounts.drop_reminder(found, body.endpoint)
        return Response(status_code=204)
