"""Workings as data (Catalogue, Spells' first slice): a chapter's `[[workings]]` entry names a working's axes (the kind
moved from and to, the distance, the link) and the loader expands it to one ordinary CardEntry, as town.py does for a
town card. Its tithe, the ash it makes, is a pure function of the axes read from `working_rules.toml`, so a new working
is a data row. The engine sees only the cards."""
import tomllib
from functools import cache
from pathlib import Path

from pydantic import Field, model_validator

from .entries import CardEntry, Entry, ItemAmount, OutcomeEntry

RULES = Path(__file__).resolve().parent / "working_rules.toml"


class KindRow(Entry):
    from_: str = Field(alias="from")
    to: str
    tithe: int = Field(ge=0)


class LinkRow(Entry):
    id: str
    discount: int = Field(ge=0)


class WorkingRules(Entry):
    version: int
    tithe_store: str
    floor: int = Field(ge=0)
    distance_step: int = Field(ge=0)
    kinds: list[KindRow]
    links: list[LinkRow]

    @model_validator(mode="after")
    def _unique(self) -> "WorkingRules":
        pairs = [(k.from_, k.to) for k in self.kinds]
        ids = [x.id for x in self.links]
        if len(set(pairs)) != len(pairs) or len(set(ids)) != len(ids):
            raise ValueError("working rules: a kind pair or a link is listed twice")
        return self


@cache
def load_rules(path: Path = RULES) -> WorkingRules:
    with path.open("rb") as f:
        return WorkingRules.model_validate(tomllib.load(f))


def tithe(rules: WorkingRules, from_kind: str, to_kind: str, distance: int, link: str) -> int:
    """The ash a working pays. Raises ValueError for a pair or a link the table has no row for."""
    base = next((k.tithe for k in rules.kinds if (k.from_, k.to) == (from_kind, to_kind)), None)
    if base is None:
        raise ValueError(f"no tithe rule for moving {from_kind} into {to_kind}")
    discount = next((x.discount for x in rules.links if x.id == link), None)
    if discount is None:
        raise ValueError(f"no tithe rule for the link {link!r}")
    return max(rules.floor, base + distance * rules.distance_step - discount)


class WorkingEntry(Entry):
    """A working: a hands card of the magic lane that takes `input` and pays its tithe. `tithe`, if the author states
    it, must equal the computed one."""

    id: str
    label_key: str
    upside_key: str | None = None
    work_s: int = Field(ge=1)
    skill: str
    xp_per_hour: int = Field(default=0, ge=0)
    input: ItemAmount | None = None
    from_kind: str
    to_kind: str
    distance: int = Field(ge=0)
    link: str = "none"
    tithe: int | None = None

    def card(self, rules: WorkingRules) -> CardEntry:
        paid = tithe(rules, self.from_kind, self.to_kind, self.distance, self.link)
        if self.tithe is not None and self.tithe != paid:
            raise ValueError(f"working {self.id}: declares a tithe of {self.tithe}, the rules compute {paid}")
        return CardEntry(
            id=self.id, only_player="magic", presentation="action", label_key=self.label_key,
            upside_key=self.upside_key, work_s=self.work_s, skill=self.skill, xp_per_hour=self.xp_per_hour,
            inputs=[self.input] if self.input else [],
            outcome=OutcomeEntry(stores=[ItemAmount(store=rules.tithe_store, items=paid)]),
        )


def expand(entries: list[WorkingEntry]) -> list[CardEntry]:
    """One card per working, in file order; a collision shows as a duplicate id, which check_opening refuses naming it."""
    rules = load_rules()
    return [e.card(rules) for e in entries]
