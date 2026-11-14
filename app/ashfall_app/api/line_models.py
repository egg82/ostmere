"""Wire models of the content's log lines (Content.line_infos): each key's kind and what writes it (CONTRACT.txt, "Line
causes"). The conventions in models.py hold here."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ..opening.line_kinds import LineKind
from .decision_models import Condition


class RunnerCause(BaseModel):
    """A card's run wrote the line (its line, outcome or finish), or a fight on a card or standing action did."""

    kind: Literal["runner"] = "runner"
    runner: str


class WhenCause(BaseModel):
    """What a story beat, an offer's arrival or a chip waited on, as the condition the content wrote for it."""

    kind: Literal["when"] = "when"
    when: Condition


class SkillCause(BaseModel):
    """A level of `skill`: a line several of its levels share (a phase's pool), so the key cannot say which level."""

    kind: Literal["skill"] = "skill"
    skill: str


class CampCause(BaseModel):
    """A Camp level reached: `level` as the Camp bar counts it, from 1."""

    kind: Literal["camp"] = "camp"
    level: int


class AnswerCause(BaseModel):
    """The player's answer to an offer."""

    kind: Literal["answer"] = "answer"
    offer: str


class Mention(BaseModel):
    """A mention line: `lane`'s person joined or left, counted into the day's one line the page words (CONTRACT.txt,
    "People")."""

    lane: str
    way: Literal["joined", "left"]


class PeopleBand(BaseModel):
    """The lines for a day on which at least `at_least` people came (or went), until the next band's."""

    at_least: int
    keys: list[str]


class PeopleInfo(BaseModel):
    came: list[PeopleBand]
    went: list[PeopleBand]


type LineCause = Annotated[RunnerCause | WhenCause | SkillCause | CampCause | AnswerCause, Field(discriminator="kind")]


class LineInfo(BaseModel):
    key: str
    kind: LineKind
    """How the chronicle sets the line and which of its filters holds it (opening/line_kinds.py), authored beside its
    text."""
    cause: LineCause | None
    """What writes the line, read from where its key is authored: one place, or several levels of one skill; null for
    the opening's first lines, the end's, and a beat waiting on a lane's rules."""
    person: bool
    """A story line of an outcome where a `line` person joins or leaves (CONTRACT.txt, "People")."""
    mention: Mention | None
    """Set on a mention line, which has no text of its own: the page counts it into the day's mention."""
