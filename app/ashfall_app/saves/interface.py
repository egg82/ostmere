"""Saves (docs/systems.md): each account's games, held by the server and written on every decision and advance. The
implementation is service.py, on Postgres; NullSaves answers when the app has no database (every call is unavailable).
Callers hold this interface, never the implementation. The wire form is the API's (api/CONTRACT.txt); this speaks
the engine's types."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .. import engine as e
from .repeats import RepeatRules, Repeats
from .ruleruns import RuleRun

RETRY_AFTER_S = 3
"""Mid-deploy, how long a page waits before asking again for a save this pod may not write."""
MAX_SAVES = 5
"""The most live saves an account holds (api/CONTRACT.txt, "Games on one account")."""
KEPT_DAYS = 30
"""How long a deleted save is held before it may be deleted for good."""


@dataclass(frozen=True)
class Ruleset:
    """What a pod plays saves under: the content's rules and renames, the opening's first lines, its build, and the
    content release its rules are (the release lock's number, which every content change raises): a save last written
    under a later release is not this pod's to write."""

    rules: e.Rules
    digest: str
    renames: tuple[e.Rename, ...]
    start_lines: tuple[e.LineKey, ...]
    line_renames: dict[str, str]
    """Text keys renamed since a stored line was written, to the key they are now."""
    build: str
    release: int
    camp_triggers: tuple[int, ...] = ()
    """The indexes in rules.triggers of the triggers that land Camp levels: a save's camp level is how many fired."""
    repeats: RepeatRules | None = None
    """How repeats are counted (repeats.py); None counts none."""
    held_manifest: str | None = None
    """These rules' manifest as canonical text, when save_manifests holds it as their digest's (saves/manifest.py
    `registered`): a save written then leaves it out of `state`. None: saves are written whole."""
    retired_lines: frozenset[str] = frozenset()
    """Text keys retired since a stored line was written: such a line is dropped."""


@dataclass(frozen=True)
class Info:
    save_id: int
    number: int | None
    """None for a save begun by the build before numbers, until it is next written."""
    decisions: int
    game_time: int
    ended_at: int | None
    started_at: datetime
    played_at: datetime
    camp_level: int | None
    """None for a save not written since the build before camp levels were kept."""


@dataclass(frozen=True)
class Deleted:
    info: Info
    deleted_at: datetime
    purge_at: datetime


@dataclass(frozen=True)
class Games:
    saves: tuple[Info, ...]
    """Live, the most recently written first."""
    deleted: tuple[Deleted, ...]
    """Held, the most recently deleted first."""


@dataclass(frozen=True)
class Played:
    """A save as just written, and the lines the write added, numbered for one answer ((time, seq) unique)."""

    save_id: int
    decisions: int
    save: e.Save
    lines: tuple[e.Line, ...]
    failed: e.CardId | None = None
    """The card of the decision's failed tap (engine Step.failed), if it was one."""
    repeats: Repeats = Repeats()
    """What the player keeps doing, from the decision log as this write left it (repeats.py)."""
    rule_runs: tuple[RuleRun, ...] = ()
    """What the rules did lately, as this write left it (ruleruns.py)."""
    catching_up_to: int | None = None
    """The game time this request was advancing to when its time budget ended it short (save.time is the last
    instant it resolved), else None: a long absence is caught up one bounded slice per request, so ask again."""


@dataclass(frozen=True)
class PastLine:
    n: int
    at: int
    key: str


@dataclass(frozen=True)
class Opened:
    info: Info
    was: e.Save
    """The save as last written (rebased if the rules changed since), at its own time: what the player last saw."""
    history: tuple[PastLine, ...]
    """Its last HISTORY lines before this open, oldest first."""
    presentation: dict[str, object]
    """What the page keeps about its teaching, as stored (api/CONTRACT.txt, SavePresentation)."""
    played: Played
    """It advanced to now, with what arrived while away."""


class SaveError(Exception):
    pass


class NotFound(SaveError):
    """No such live save on this account."""


class Stale(SaveError):
    """A decision sent after another page's: nothing of it was applied; `played` is the save advanced to now."""

    def __init__(self, played: Played) -> None:
        super().__init__(f"save {played.save_id} has {played.decisions} decisions")
        self.played = played


class Behind(SaveError):
    """The save is still catching up on time away: the decision was not applied (a dry run computed nothing), and
    `played` is the save as this request left it, catching_up_to set. Ask advance until caught up, then decide."""

    def __init__(self, played: Played) -> None:
        super().__init__(f"save {played.save_id} is at {played.save.time} of {played.catching_up_to}")
        self.played = played


class Invalid(SaveError):
    """The decision does not fit the save (InvalidVerbError): nothing was written."""


class TooManySaves(SaveError):
    """The account already holds MAX_SAVES live saves: nothing was made or restored."""


class LastSave(SaveError):
    """The account's only live save cannot be deleted: nothing changed."""


class SaveLimited(SaveError):
    """A limit on saves is reached (or its count could not be taken): `scope` says which, `retry_after_s` when to ask
    again."""

    def __init__(self, scope: str, retry_after_s: int) -> None:
        super().__init__(f"limited ({scope})")
        self.scope = scope
        self.retry_after_s = retry_after_s


class NewGamesLimited(SaveLimited):
    """Too many new games on the account just now: nothing was made."""


class DecisionsLimited(SaveLimited):
    """Too many decisions on the save just now: nothing was applied or written."""


class Unavailable(SaveError):
    """Retryable: no database, a save of a later release, or one this build cannot rebase. Nothing was written."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class Saves(Protocol):
    def create(self, account_id: int) -> tuple[Info, Played]:
        """A new save at game time 0, its clock started now, with the opening's first lines. TooManySaves at
        MAX_SAVES live, NewGamesLimited past the new-game limit."""
        ...

    def list(self, account_id: int) -> list[Info]:
        """The account's live saves, the most recently written first."""
        ...

    def games(self, account_id: int) -> Games:
        """The account's live saves and its held deleted ones."""
        ...

    def delete(self, account_id: int, save_id: int) -> Games:
        """Deletes a live save (held KEPT_DAYS, then deleted for good by a later write). NotFound, LastSave."""
        ...

    def restore(self, account_id: int, save_id: int) -> Games:
        """A held deleted save live again. NotFound, TooManySaves."""
        ...

    def open(self, account_id: int, save_id: int) -> Opened:
        """The save as last written, and played: advanced toward now by one bounded slice (catching_up_to)."""
        ...

    def advance(self, account_id: int, save_id: int) -> Played:
        """The save advanced toward now by one bounded slice and written (catching_up_to when it stopped short).
        Never stale."""
        ...

    def decide(self, account_id: int, save_id: int, verb: e.Verb, after: int) -> Played:
        """Advance to now and apply `verb`, if the save holds exactly `after` decisions (else Stale). An advance that
        stops short is written as a plain advance, the verb not applied: Behind."""
        ...

    def dry_run(self, account_id: int, save_id: int, verbs: tuple[e.Verb, ...]) -> e.Save:
        """The save after these verbs, applied in order now. Nothing is written. Behind when the advance to now
        stops short (its Played is the save as written)."""
        ...

    def stored(self, account_id: int, save_id: int) -> e.Save:
        """The save as last written (rebased in memory if the rules changed since), at its own time, not advanced.
        Nothing is written, nothing counted. NotFound, Unavailable."""
        ...

    def current(self, account_id: int, save_id: int, stop: Callable[[], bool]) -> Played:
        """The save advanced to now in memory, nothing written, no lines, its advance cut by `stop`. Behind when that
        stops short (its Played is the save as written)."""
        ...

    def forecast_stop(self) -> Callable[[], bool]:
        """The stop for one forecast request, made as it begins and passed to both its read (`current`) and its
        replay: the one an advance asks after each instant."""
        ...


class NullSaves:
    def create(self, account_id: int) -> tuple[Info, Played]:
        raise Unavailable("no database")

    def list(self, account_id: int) -> list[Info]:
        return []

    def games(self, account_id: int) -> Games:
        raise Unavailable("no database")

    def delete(self, account_id: int, save_id: int) -> Games:
        raise Unavailable("no database")

    def restore(self, account_id: int, save_id: int) -> Games:
        raise Unavailable("no database")

    def open(self, account_id: int, save_id: int) -> Opened:
        raise Unavailable("no database")

    def advance(self, account_id: int, save_id: int) -> Played:
        raise Unavailable("no database")

    def decide(self, account_id: int, save_id: int, verb: e.Verb, after: int) -> Played:
        raise Unavailable("no database")

    def dry_run(self, account_id: int, save_id: int, verbs: tuple[e.Verb, ...]) -> e.Save:
        raise Unavailable("no database")

    def stored(self, account_id: int, save_id: int) -> e.Save:
        raise Unavailable("no database")

    def current(self, account_id: int, save_id: int, stop: Callable[[], bool]) -> Played:
        raise Unavailable("no database")

    def forecast_stop(self) -> Callable[[], bool]:
        raise Unavailable("no database")
