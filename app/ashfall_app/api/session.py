"""Who a request is (CONTRACT.txt, "Accounts and sessions"): the account its session cookie names, from the Accounts
system. Looking changes nothing; a write that succeeded renews the session and its cookie (renew, called by the route
class), so a GET or a refused write never writes."""
import logging

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from .. import services
from ..accounts import cookies, labels
from ..accounts.interface import AccountsUnavailable, Seen
from ..accounts.sessions import LIFETIME
from .errors import no_account, unavailable

COOKIE_AGE_S = int(LIFETIME.total_seconds())
_TOKEN = "ashfall_session_token"   # request.state: the token of the live session this request was recognised by
_SEEN = "ashfall_session_seen"   # request.state: that session as the one read of it found it
_log = logging.getLogger("ashfall.game")


def who(request: Request) -> int | None:
    """The request's account, or None with no live session (503 without a database)."""
    token = cookies.read(request, cookies.SESSION)
    try:
        found = services.of(request).accounts.who(token)
    except AccountsUnavailable as ex:
        raise unavailable(str(ex)) from ex
    if found is None:
        return None
    setattr(request.state, _TOKEN, token)
    setattr(request.state, _SEEN, found)
    return found.account_id


def account(request: Request) -> int:
    """The request's account; 401 no_account without one."""
    found = who(request)
    if found is None:
        raise no_account()
    return found


async def renew(request: Request) -> None:
    """After a write succeeded: renew the session it was recognised by, and its cookie, at most daily. Best effort,
    off the event loop: a failure is logged and never changes the answer to a write that was applied."""
    token, seen = getattr(request.state, _TOKEN, None), getattr(request.state, _SEEN, None)
    if not isinstance(token, str) or not isinstance(seen, Seen):
        return
    try:
        renewed = await run_in_threadpool(services.of(request).accounts.renew, seen)
    except Exception:   # the write is already committed: whatever the renewal hit must not answer it
        _log.warning("session.renew_failed", extra={"fields": {"account": seen.account_id}}, exc_info=True)
        return
    if renewed:
        cookies.queue(request, cookies.SESSION, token, COOKIE_AGE_S)


def seen(request: Request) -> Seen:
    """The request's live session; 401 no_account without one."""
    account(request)
    found = getattr(request.state, _SEEN)
    assert isinstance(found, Seen)
    return found


def label(request: Request) -> str:
    """The device label of the browser asking (accounts/labels.py)."""
    return labels.label(request.headers.get("user-agent", ""))


def sign_in(request: Request, token: str) -> None:
    """A new session's cookie on this response."""
    cookies.queue(request, cookies.SESSION, token, COOKIE_AGE_S)


def address(request: Request) -> str:
    """The client's address as uvicorn's proxy headers left it, for the account limit only (never logged)."""
    return request.client.host if request.client else ""
