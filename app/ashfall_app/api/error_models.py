"""The API's typed errors (CONTRACT.txt, ERRORS): every error answers an ApiError with one of these codes."""
from enum import StrEnum

from pydantic import BaseModel

from .models import Step


class ErrorCode(StrEnum):
    NO_ACCOUNT = "no_account"
    """401: no live session."""
    CROSS_SITE = "cross_site"
    """403: a write from another site (accounts/csrf.py)."""
    NOT_FOUND = "not_found"
    """404: no such save on this account."""
    NO_SUCH_CODE = "no_such_code"
    """404: POST /api/join named no account (a code used, expired or never made; words replaced or never made)."""
    STALE = "stale"
    """409: another page decided since `after`; ApiError.step is the save now."""
    CATCHING_UP = "catching_up"
    """409: the save is still catching up on time away (Step.catching_up_to); nothing of the request was applied, and
    ApiError.step is the save as this request left it."""
    CONFIRM_MERGE = "confirm_merge"
    """409: POST /api/join from a browser whose own account has progress; ApiError.merge says what each side holds."""
    TOO_MANY_SAVES = "too_many_saves"
    """409: a new game or a restore on an account already holding Games.max_saves live saves; or a join whose two
    accounts together would pass it (ApiError.merge says what each holds)."""
    LAST_SAVE = "last_save"
    """409: deleting the account's only live save."""
    NOT_JSON = "not_json"
    """415: a write whose body is not JSON."""
    TOO_LARGE = "too_large"
    """413: a request body over 256 KiB (accounts/body_limit.py), refused before it is parsed."""
    INVALID_DECISION = "invalid_decision"
    """422: the decision does not fit the save (InvalidVerbError), or the request does not fit the models."""
    RATE_LIMITED = "rate_limited"
    """429: too many new accounts, new games, joins, codes or words just now, or too much feedback."""
    SAVE_UNAVAILABLE = "save_unavailable"
    """503, retryable (Retry-After): no database, a save a later build wrote, one this build cannot rebase, or a database
    failover under the request (a read-only or dropped connection, or no writable member within the checkout budget)
    that cannot be replayed or met the replay too."""


class MergeSummary(BaseModel):
    """What joining would bring together (CONTRACT.txt, "Moving to another device")."""

    here: int
    """This browser's account's live saves."""
    there: int
    """The named account's live saves."""
    there_newest_game_time: int | None
    """The game_time of the named account's most recently played save; null with none."""
    max_saves: int
    """Games.max_saves: the most live saves one account holds, so here + there may not pass it."""
    words_replaced: bool
    """Both accounts have recovery words: a merge ends the words made on this browser's account, and the named
    account's words then restore every game."""


class ApiError(BaseModel):
    """Every error's body (CONTRACT.txt, ERRORS)."""

    code: ErrorCode
    message: str
    """For a developer's console, never shown to the player."""
    step: Step | None = None
    """With stale (the save advanced to now) and catching_up (the save as this request left it) only. Draw it."""
    merge: MergeSummary | None = None
    """With confirm_merge, and with too_many_saves from a join."""
