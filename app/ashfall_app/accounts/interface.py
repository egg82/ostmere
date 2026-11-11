"""Accounts and sign-in (docs/systems.md): who is asking. An account is a browser, held by a session cookie; it is made
only when the player begins a game, and another browser joins it by a transfer code or its recovery words. The
implementation is service.py, on Postgres; NullAccounts answers when the app has no database (who is asking cannot be
told and no account can be made or joined: AccountsUnavailable). Callers hold this interface, never the
implementation.

The HTTP side (the cookie, the CSRF guard) is cookies.py and csrf.py; this answers from a token and an address."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ..db.reminders import Window

type Json = dict[str, object]


@dataclass(frozen=True)
class NewAccount:
    account_id: int
    token: str
    """The new session's token, for the cookie; stored only hashed."""


@dataclass(frozen=True)
class Seen:
    """A live session as `who` found it."""

    account_id: int
    session_id: int
    last_seen_at: datetime


@dataclass(frozen=True)
class Device:
    """One of an account's sessions, as its list shows it. Never the token or its hash."""

    session_id: int
    label: str
    """Browser and system, e.g. "Firefox on Linux" (labels.py)."""
    created_at: datetime
    last_seen_at: datetime
    this_device: bool
    """The session that asked."""


@dataclass(frozen=True)
class PresentationKept:
    """A presentation write: what was stored before it, and what is stored now."""

    before: Json
    after: Json


@dataclass(frozen=True)
class About:
    """An account as the page sees it."""

    presentation: Json
    lessons: bool
    """The lessons setting: lessons run in every game of the account."""
    has_words: bool
    words_due: bool
    """No recovery words, a decision on a save, and the account made at least three days ago."""


@dataclass(frozen=True)
class Subscription:
    """A browser's Web Push subscription as its page sends it, with the device's IANA time zone."""

    endpoint: str
    p256dh: str
    auth: str
    tz: str


@dataclass(frozen=True)
class NewCode:
    code: str
    """As shown: "ABCD-EFGH". Stored only hashed."""
    expires_in_s: int


@dataclass(frozen=True)
class Kept:
    """Games a join left on this browser's old account."""

    saves: int
    """Its live saves."""
    words: str | None
    """New recovery words for that account, made by this join because it had none; None when it already had some."""


@dataclass(frozen=True)
class Joined:
    account_id: int
    """The account this browser now belongs to."""
    moved: int
    """Saves that became that account's."""
    token: str | None
    """A new session's token when the browser had no live session (set its cookie); None when its own moved."""
    kept: Kept | None = None
    """Set by a join with `keep` whose browser had games: they stayed on the old account."""


@dataclass(frozen=True)
class MergeSummary:
    here: int
    there: int
    there_newest_game_time: int | None
    max_saves: int
    words_replaced: bool
    """Both accounts have recovery words, so a merge ends this browser's (the named account's are kept)."""


class Limited(Exception):
    """Too many tries just now (accounts/limits.py); `scope` says which limit, `retry_after_s` when to try again (None:
    not said)."""

    def __init__(self, scope: str, retry_after_s: int | None = None) -> None:
        super().__init__(f"limited ({scope})")
        self.scope = scope
        self.retry_after_s = retry_after_s


class NoSuchCode(Exception):
    """A join named no account: the code or words were never made, are used, expired or replaced, or are neither."""


class ConfirmMerge(Exception):
    """A join from a browser whose own account has progress, without `merge`: nothing changed."""

    def __init__(self, summary: MergeSummary) -> None:
        super().__init__("this browser's account has progress of its own")
        self.summary = summary


class MergeFull(Exception):
    """A join from a browser whose own account has progress, when both accounts' live saves together would pass
    max_saves: nothing changed, `merge` or not."""

    def __init__(self, summary: MergeSummary) -> None:
        super().__init__("the two accounts' live saves together pass the cap")
        self.summary = summary


class AccountsUnavailable(Exception):
    """No database, or (for codes, words and joins) no join key: nothing can be made or changed."""


class Accounts(Protocol):
    def who(self, token: str | None) -> Seen | None:
        """The session a token names, while it is alive. Changes nothing."""
        ...

    def renew(self, seen: Seen) -> bool:
        """Marks the session used, at most once a day, without reading it again; True when it did (set its cookie
        again). Called only after a write succeeded, so a refused request writes nothing."""
        ...

    def create(self, address: str, label: str | None = None) -> NewAccount:
        """A new account with one session, for a browser with none; Limited past the limits. `label` names the
        device (labels.py); None: unlabelled."""
        ...

    def about(self, account_id: int) -> About | None:
        """What the page keeps about the player, and whether recovery words exist or are due; None for no such
        account."""
        ...

    def keep_presentation(self, account_id: int, sent: Json, cap: int) -> PresentationKept | None:
        """Adds what the page sends to what is stored (presentation.py), under the account's row lock, lists held to
        `cap` entries; None for no such account."""
        ...

    def set_lessons(self, account_id: int, on: bool) -> bool:
        """Turns lessons on or off for every game of the account; False for no such account."""
        ...

    def keep_save_presentation(self, account_id: int, save_id: int, sent: Json, cap: int) -> PresentationKept | None:
        """keep_presentation for one of the account's live saves, under the save's row lock; None when it has no such
        save."""
        ...

    def make_code(self, account_id: int) -> NewCode | None:
        """A new transfer code, ending the account's previous one; None for no such account. Limited past the limit."""
        ...

    def make_words(self, account_id: int) -> str | None:
        """New recovery words ("w1-w2-w3-w4"), replacing the old; None for no such account. Limited past the limit
        or when no turn at hashing comes free."""
        ...

    def join(self, token: str | None, typed: str, merge: bool, address: str, label: str | None = None, *,
             keep: bool = False) -> Joined:
        """The browser of session `token` (None: no live session) joins the account `typed` names (api/CONTRACT.txt,
        "Moving to another device"); with `merge`, a browser whose account has progress moves its saves into that
        account; with `keep`, it leaves them on its old account, whose recovery words are made when it has none. A
        new session is labelled `label`. NoSuchCode, ConfirmMerge, MergeFull, Limited; AccountsUnavailable
        without the join key."""
        ...

    def devices(self, account_id: int, session_id: int) -> list[Device]:
        """The account's sessions, one per browser, most recently used first; `session_id` is the asking one."""
        ...

    def remove_device(self, account_id: int, session_id: int) -> bool:
        """Ends one of the account's sessions, which signs that browser out; False when it is not this account's."""
        ...

    def keep_reminder(self, account_id: int, sub: Subscription, window: Window | None) -> Window | None:
        """Turns reminders on for the browser `sub` names, with `window`; with None, refreshes the keys of a browser
        already on and answers its window, or None when it is not on. Either way the row becomes the account's."""
        ...

    def drop_reminder(self, account_id: int, endpoint: str) -> bool:
        """Turns the browser's reminders off; False when the account held none for it."""
        ...


class NullAccounts:
    def who(self, token: str | None) -> Seen | None:
        raise AccountsUnavailable("no database")

    def renew(self, seen: Seen) -> bool:
        return False

    def create(self, address: str, label: str | None = None) -> NewAccount:
        raise AccountsUnavailable("no database")

    def about(self, account_id: int) -> About | None:
        return None

    def keep_presentation(self, account_id: int, sent: Json, cap: int) -> PresentationKept | None:
        return None

    def set_lessons(self, account_id: int, on: bool) -> bool:
        return False

    def keep_save_presentation(self, account_id: int, save_id: int, sent: Json, cap: int) -> PresentationKept | None:
        return None

    def make_code(self, account_id: int) -> NewCode | None:
        raise AccountsUnavailable("no database")

    def make_words(self, account_id: int) -> str | None:
        raise AccountsUnavailable("no database")

    def join(self, token: str | None, typed: str, merge: bool, address: str, label: str | None = None, *,
             keep: bool = False) -> Joined:
        raise AccountsUnavailable("no database")

    def devices(self, account_id: int, session_id: int) -> list[Device]:
        return []

    def remove_device(self, account_id: int, session_id: int) -> bool:
        return False

    def keep_reminder(self, account_id: int, sub: Subscription, window: Window | None) -> Window | None:
        raise AccountsUnavailable("no database")

    def drop_reminder(self, account_id: int, endpoint: str) -> bool:
        return False
