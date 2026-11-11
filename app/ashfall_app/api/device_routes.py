"""Moving an account to another device (CONTRACT.txt, "Moving to another device"): a transfer code with its link and QR
code, recovery words, and the join that either one makes. Each asks the Accounts system (services.py); what it
raises becomes the contract's error. Every answer here, errors included, is no-store (route.py)."""
from collections.abc import Generator
from contextlib import contextmanager

from fastapi import APIRouter, Path, Request

from .. import services
from ..accounts import cookies
from ..accounts.interface import AccountsUnavailable, ConfirmMerge, Limited, MergeFull, NoSuchCode, Seen
from ..accounts.interface import MergeSummary as Held
from . import qr, session
from .devices_models import Device, Devices, Joined, JoinRequest, Kept, RecoveryWords, TransferCode
from .error_models import ApiError, MergeSummary
from .errors import confirm_merge, no_account, no_such_code, not_found, rate_limited, too_many_saves, unavailable
from .save_routes import account

NO_STORE = frozenset({"/api/me/transfer-code", "/api/me/words", "/api/join", "/api/me/devices",
                      "/api/me/devices/{device_id}", "/api/reminders"})
JOIN_FRAGMENT = "/#join="
WORDS_LABEL = "Ostmere"

_MAKE_ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ApiError, "description": "no_account"},
    429: {"model": ApiError, "description": "rate_limited (Retry-After)"},
    503: {"model": ApiError, "description": "save_unavailable: no database or no join key (Retry-After)"},
}
_JOIN_ERRORS: dict[int | str, dict[str, object]] = {
    404: {"model": ApiError, "description": "no_such_code"},
    409: {"model": ApiError, "description": "confirm_merge or too_many_saves, with `merge`"},
    422: {"model": ApiError, "description": "invalid_decision: a request that does not fit the models"},
    429: _MAKE_ERRORS[429],
    503: _MAKE_ERRORS[503],
}


_LIST_ERRORS: dict[int | str, dict[str, object]] = {
    401: _MAKE_ERRORS[401],
    503: {"model": ApiError, "description": "save_unavailable: no database (Retry-After)"},
}
_REMOVE_ERRORS: dict[int | str, dict[str, object]] = {**_LIST_ERRORS,
    404: {"model": ApiError, "description": "not_found: no such device of this account"}}


@contextmanager
def answered() -> Generator[None]:
    """The Accounts system's refusals as the contract's errors."""
    try:
        yield
    except NoSuchCode as ex:
        raise no_such_code() from ex
    except ConfirmMerge as ex:
        raise confirm_merge(_summary(ex.summary)) from ex
    except MergeFull as ex:
        raise too_many_saves(ex.summary.max_saves, _summary(ex.summary)) from ex
    except Limited as ex:
        raise rate_limited("too many tries just now: try again later", ex.retry_after_s) from ex
    except AccountsUnavailable as ex:
        raise unavailable(str(ex)) from ex


def _summary(s: Held) -> MergeSummary:
    return MergeSummary(here=s.here, there=s.there, there_newest_game_time=s.there_newest_game_time,
                        max_saves=s.max_saves, words_replaced=s.words_replaced)


def add_device_routes(router: APIRouter, public_url: str) -> None:
    site = public_url.rstrip("/")

    @router.post("/me/transfer-code", response_model=TransferCode, operation_id="make_transfer_code",
                 responses=_MAKE_ERRORS)
    def make_transfer_code(request: Request) -> TransferCode:
        """A code that joins one other browser to this account, once, within ten minutes; it ends the previous one."""
        found = session.account(request)
        with answered():
            made = services.of(request).accounts.make_code(found)
        if made is None:
            raise no_account()
        url = site + JOIN_FRAGMENT + made.code
        return TransferCode(transfer_code=made.code, expires_in_s=made.expires_in_s, join_url=url, qr=qr.rows(url))

    @router.post("/me/words", response_model=RecoveryWords, operation_id="make_recovery_words",
                 responses=_MAKE_ERRORS)
    def make_recovery_words(request: Request) -> RecoveryWords:
        """New recovery words for this account; the old ones stop working."""
        found = session.account(request)
        with answered():
            words = services.of(request).accounts.make_words(found)
        if words is None:
            raise no_account()
        return RecoveryWords(words=words, label=WORDS_LABEL)

    @router.post("/join", response_model=Joined, operation_id="join", responses=_JOIN_ERRORS)
    def join(request: Request, body: JoinRequest) -> Joined:
        """This browser joins the account a transfer code or recovery words name."""
        accounts = services.of(request).accounts
        token = cookies.read(request, cookies.SESSION)
        with answered():
            joined = accounts.join(token, body.typed, body.merge, session.address(request), session.label(request),
                                   keep=body.keep)
            about = accounts.about(joined.account_id)
        if joined.token is not None:
            session.sign_in(request, joined.token)
        if about is None:
            raise no_such_code()
        kept = None if joined.kept is None else Kept(saves=joined.kept.saves, words=joined.kept.words, label=WORDS_LABEL)
        return Joined(moved=joined.moved, account=account(about), kept=kept)

    @router.get("/me/devices", response_model=Devices, operation_id="list_devices", responses=_LIST_ERRORS)
    def list_devices(request: Request) -> Devices:
        """The account's devices, one per browser that holds a session of it."""
        return _devices(request, session.seen(request))

    @router.delete("/me/devices/{device_id}", response_model=Devices, operation_id="remove_device",
                   responses=_REMOVE_ERRORS)
    def remove_device(request: Request, device_id: int = Path(ge=1, le=2**53)) -> Devices:
        """Signs one device out from any of them: its session ends and its next request has no account. Removing the
        browser asking signs it out too (its cookie is ended). Answers the devices left."""
        here = session.seen(request)
        if not services.of(request).accounts.remove_device(here.account_id, device_id):
            raise not_found("no such device of yours")
        if device_id == here.session_id:
            cookies.clear(request, cookies.SESSION)
        return _devices(request, here)


def _devices(request: Request, here: Seen) -> Devices:
    found = services.of(request).accounts.devices(here.account_id, here.session_id)
    return Devices(devices=[Device(device_id=d.session_id, label=d.label, created_at=d.created_at,
                                   last_seen_at=d.last_seen_at, this_device=d.this_device) for d in found])
