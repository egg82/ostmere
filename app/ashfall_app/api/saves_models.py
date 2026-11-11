"""Wire models of accounts and saves (CONTRACT.txt, ENDPOINTS): who this browser is, its saves, and the requests that
move them. The game's own shapes (Step, View, Decision) are models.py; the conventions there hold here."""
from datetime import datetime
from typing import Annotated, TypeGuard

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .limits import MAX_DRY_RUN, MAX_GAME_SECOND, MAX_LIST, MAX_NAME, MAX_SAVE_ID, NO_NUL
from .models import Decision, Request, Step, View

type Name = Annotated[str, Field(max_length=MAX_NAME, pattern=NO_NUL)]
type Id = Annotated[str, Field(min_length=1, max_length=MAX_NAME, pattern=r"^[A-Za-z0-9_.:-]+$")]
"""A lesson, card, store or note as the page names it: ASCII letters, digits and `_ . : -`, so an entry weighs at most
MAX_NAME bytes. A Name is free text (a mix's own name)."""
type SaveId = Annotated[int, Field(ge=1, le=MAX_SAVE_ID)]
"""A save's id as a request names it: a path or body value past what the database stores is 422, never a lookup."""
RETIRED_ACCOUNT_FIELDS = frozenset({"rule_seen", "mix_offered", "lessons", "lesson_ends"})


def _is_object(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


class OfferedSwitch(BaseModel):
    """A repeated switch (models.RepeatedSwitch) whose rule offer the player has answered."""

    model_config = ConfigDict(extra="forbid")
    chip: Id
    mix_id: Name


class LessonEnd(BaseModel):
    """How a lesson ended: for a round of testers, a skip clustered on one step marks it to cut."""

    model_config = ConfigDict(extra="forbid")
    lesson: Id
    skipped: bool
    step: int = Field(ge=0, le=99)
    """The index of the step it ended on (the last, when done)."""
    longest_wait_s: int = Field(ge=0, le=86400)
    """The longest the player stayed on one step, in seconds."""


class Visit(BaseModel):
    """A return after time away: the game second the player last saw the save, and the one the return came to."""

    model_config = ConfigDict(extra="forbid")
    left: int = Field(ge=0, le=MAX_GAME_SECOND)
    back: int = Field(ge=0, le=MAX_GAME_SECOND)


class AccountPresentation(BaseModel):
    """What the page keeps about the player across saves. What gates a lesson or a lesson's hint is the save's
    (SavePresentation), so a new game teaches everything again."""

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _drop_retired(cls, data: object) -> object:
        """A page of the build before lessons were per save still sends these; they are accepted and never stored."""
        if not _is_object(data):
            return data
        return {k: v for k, v in data.items() if k not in RETIRED_ACCOUNT_FIELDS}

    rules_opened: bool = False
    """The Rules tab has been opened."""
    devices_opened: bool = False
    """The "Another device" sheet has been opened."""
    reminder_mentioned: bool = False
    """The one row pointing at the reminders setting has been drawn: it is never drawn again for this account."""
    ledger_lines: list[Id] = Field(default=[], max_length=MAX_LIST)
    """The stores whose ledger line the page has shown: once shown, a line stays."""
    mix_stopped: list[Id] = Field(default=[], max_length=MAX_LIST)
    """The cards whose "the mix stopped" fix the player has answered: each card's is offered once."""
    switch_offered: list[OfferedSwitch] = Field(default=[], max_length=MAX_LIST)
    """The repeated switches whose rule offer the player has answered: each is offered once."""
    journal_read: list[Id] = Field(default=[], max_length=MAX_LIST)
    """The notes on pages the player has turned to (CONTRACT.txt, "JOURNAL"): kept for the account, so a note read in one
    game is read in the next."""


class SavePresentation(BaseModel):
    """What the page keeps about one save: its teaching (the lessons and what gates them or their hints) and its returns."""

    model_config = ConfigDict(extra="forbid")
    rule_seen: bool = False
    """A rule has been seen on and then off in this save: writing rules is open, and the cap rule's lesson may come."""
    mix_offered: list[Id] = Field(default=[], max_length=MAX_LIST)
    """The cards whose "your mix could take it" dot the player has touched: each is marked once."""
    lessons: list[Id] = Field(default=[], max_length=MAX_LIST)
    """The lessons done or skipped in this save (the page's game/lessons.ts ids): each comes once."""
    lesson_ends: list[LessonEnd] = Field(default=[], max_length=MAX_LIST)
    """Where each lesson in `lessons` ended, once each."""
    visits: list[Visit] = Field(default=[], max_length=MAX_LIST)
    """The returns after a long time away, one per `left`: what the Log splits its entries at."""


class AccountSettings(BaseModel):
    """The player's own choices for every game of the account. A write replaces them whole."""

    model_config = ConfigDict(extra="forbid")
    lessons: bool = True
    """Lessons run (and their hints show): on until the player turns them off."""


class Account(BaseModel):
    presentation: AccountPresentation
    settings: AccountSettings
    has_words: bool
    """The account has recovery words."""
    words_due: bool
    """No recovery words yet, a decision on a save, and the account at least 3 days old: worth a dot."""


class SaveInfo(BaseModel):
    save_id: int
    number: int | None
    """The account's count of its games: 1 for the first; null for one begun before numbers, until next written."""
    decisions: int
    game_time: int
    """The save's game time when it was last written."""
    ended_at: int | None
    started_at: datetime
    """When it was begun (wall time, UTC)."""
    played_at: datetime
    """When it was last written (wall time, UTC)."""
    camp_level: int | None
    """Camp levels landed when last written; null for one not written since the build before this field."""


class DeletedSave(BaseModel):
    save: SaveInfo
    deleted_at: datetime
    purge_at: datetime
    """deleted_at + Games.kept_days: from then on the save may be gone for good."""


class Games(BaseModel):
    """The account's saves (CONTRACT.txt, "Games on one account")."""

    saves: list[SaveInfo]
    """The live saves, the most recently played first."""
    deleted: list[DeletedSave]
    """The deleted saves still held, the most recently deleted first."""
    max_saves: int
    """The most live saves an account holds."""
    kept_days: int
    """How long a deleted save is held."""


class Me(BaseModel):
    account: Account | None
    """Null: this browser has no account (it makes one by beginning a game)."""
    saves: list[SaveInfo]
    """The live saves, the most recently played first."""
    max_saves: int
    """The most live saves an account holds (Games.max_saves); a list of that many offers no new game."""
    kept_days: int
    """How long a deleted save is held (Games.kept_days)."""


class NewSave(BaseModel):
    save: SaveInfo
    presentation: SavePresentation
    """What the page keeps about its teaching: nothing yet."""
    step: Step


class PastLine(BaseModel):
    n: int
    """The line's place in the save's whole log, from 0."""
    at: int
    key: str


class Opened(BaseModel):
    save: SaveInfo
    was: View
    """The save as it was last written, at that time: what the player last saw."""
    history: list[PastLine]
    """The save's last 200 lines before this open, oldest first."""
    presentation: SavePresentation
    """What the page has kept about this save's teaching."""
    step: Step
    """The save advanced to now, with the lines that arrived while away."""


class DecisionRequest(Request):
    decision: Decision
    after: int = Field(ge=0)
    """The Step.decisions the page last saw."""


class DryRunRequest(Request):
    decisions: list[Decision] = Field(max_length=MAX_DRY_RUN)
