"""The API's typed errors: a GameError raised anywhere in a handler becomes an ApiError body with its status (and
headers: a 503's Retry-After), answered by the route class (route.py)."""
from ..saves.interface import RETRY_AFTER_S
from .error_models import ApiError, ErrorCode, MergeSummary
from .models import Step


class GameError(Exception):
    def __init__(self, status: int, code: ErrorCode, message: str, step: Step | None = None,
                 headers: dict[str, str] | None = None, merge: MergeSummary | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = ApiError(code=code, message=message, step=step, merge=merge)
        self.headers = headers or {}


def no_account() -> GameError:
    return GameError(401, ErrorCode.NO_ACCOUNT, "no live session: begin a game to make an account")


def not_found(message: str) -> GameError:
    return GameError(404, ErrorCode.NOT_FOUND, message)


def no_such_code() -> GameError:
    return GameError(404, ErrorCode.NO_SUCH_CODE, "that code or those words name no account")


def confirm_merge(merge: MergeSummary) -> GameError:
    return GameError(409, ErrorCode.CONFIRM_MERGE, "this browser's account has games of its own", merge=merge)


def too_many_saves(max_saves: int, merge: MergeSummary | None = None) -> GameError:
    """With `merge`: a join whose two accounts' live saves together would pass max_saves."""
    if merge is not None:
        return GameError(409, ErrorCode.TOO_MANY_SAVES, f"together the two accounts would pass {max_saves} live saves",
                         merge=merge)
    return GameError(409, ErrorCode.TOO_MANY_SAVES, f"the account already holds {max_saves} live saves")


def last_save() -> GameError:
    return GameError(409, ErrorCode.LAST_SAVE, "the account's only live save cannot be deleted")


def stale(step: Step) -> GameError:
    return GameError(409, ErrorCode.STALE, "another page decided since: draw this step", step=step)


def catching_up(step: Step) -> GameError:
    return GameError(409, ErrorCode.CATCHING_UP, "still catching up on time away: advance, then ask again", step=step)


def invalid_decision(message: str) -> GameError:
    return GameError(422, ErrorCode.INVALID_DECISION, message)


def rate_limited(message: str = "too many new games just now: try again later",
                 retry_after_s: int | None = None) -> GameError:
    headers = None if retry_after_s is None else {"Retry-After": str(retry_after_s)}
    return GameError(429, ErrorCode.RATE_LIMITED, message, headers=headers)


def unavailable(message: str) -> GameError:
    return GameError(503, ErrorCode.SAVE_UNAVAILABLE, message, headers={"Retry-After": str(RETRY_AFTER_S)})
