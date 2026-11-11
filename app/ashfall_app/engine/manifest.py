"""The manifest an envelope carries, read back: the ids (and the few numbers) of the rules a save was written under.

Semantics: DESIGN.txt, "Manifest". codec.manifest writes it; rebase reads it here, so Save.chips and Save.fired become
ids and an id the new rules lack can be named.
"""
from dataclasses import dataclass
from typing import Never

from .codec import Json
from .errors import StateFormatError
from .ids import IdKind
from .rules import Rules
from .rules_check import features


@dataclass(frozen=True)
class ManifestCard:
    id: str
    work_s: int
    lane: str
    cap: int | None


@dataclass(frozen=True)
class ManifestOffer:
    id: str
    answers: tuple[str, ...]
    kind: str | None = None
    roles: tuple[str, ...] = ()
    """The role of each answer, in answer order; empty exactly when the offer has no kind."""


@dataclass(frozen=True)
class Manifest:
    stores: tuple[str, ...]
    skills: tuple[str, ...]
    standing: tuple[str, ...]
    lanes: tuple[str, ...]
    cards: tuple[ManifestCard, ...]
    chips: tuple[str, ...]
    triggers: tuple[str, ...]
    features: tuple[str, ...]
    offers: tuple[ManifestOffer, ...]

    def declared(self) -> dict[IdKind, tuple[str, ...]]:
        """Every id these rules declared, by kind (SOURCE is a label, never declared)."""
        return {
            IdKind.STORE: self.stores, IdKind.SKILL: self.skills, IdKind.STANDING: self.standing,
            IdKind.CARD: tuple(c.id for c in self.cards), IdKind.LANE: self.lanes, IdKind.CHIP: self.chips,
            IdKind.TRIGGER: self.triggers, IdKind.FEATURE: self.features,
            IdKind.OFFER: tuple(o.id for o in self.offers), IdKind.ANSWER: tuple(a for o in self.offers for a in o.answers),
        }


def declared(rules: Rules) -> dict[IdKind, frozenset[str]]:
    """Every id `rules` declare, by kind, as Manifest.declared reads a manifest."""
    return {
        IdKind.STORE: frozenset(s.id for s in rules.stores), IdKind.SKILL: frozenset(s.id for s in rules.skills),
        IdKind.STANDING: frozenset(a.id for a in rules.standing), IdKind.CARD: frozenset(c.id for c in rules.cards),
        IdKind.LANE: frozenset(d.id for d in rules.lanes), IdKind.CHIP: frozenset(c.id for c in rules.chips),
        IdKind.TRIGGER: frozenset(t.id for t in rules.triggers), IdKind.FEATURE: frozenset(features(rules)),
        IdKind.OFFER: frozenset(o.id for o in rules.offers),
        IdKind.ANSWER: frozenset(a.id for o in rules.offers for a in o.answers),
    }


def read_manifest(value: Json) -> Manifest:
    """The manifest in an envelope; StateFormatError for any other shape (missing or extra fields, wrong types)."""
    d = _object(value, {"stores", "skills", "standing", "lanes", "cards", "chips", "triggers", "features", "offers"})
    stores = tuple(_object(s, {"id", "cap"}) for s in _list(d["stores"]))
    offers = tuple(_offer_object(o) for o in _list(d["offers"]))
    cards = tuple(_object(c, {"id", "work_s", "lane", "cap"}) for c in _list(d["cards"]))
    for s in stores:
        _int(s["cap"])
    return Manifest(
        stores=tuple(_str(s["id"]) for s in stores),
        skills=_strs(d["skills"]), standing=_strs(d["standing"]), lanes=_strs(d["lanes"]),
        cards=tuple(ManifestCard(_str(c["id"]), _int(c["work_s"]), _str(c["lane"]),
                                 None if c["cap"] is None else _int(c["cap"])) for c in cards),
        chips=_strs(d["chips"]), triggers=_strs(d["triggers"]), features=_strs(d["features"]),
        offers=tuple(_offer(o) for o in offers),
    )


def _offer_object(v: Json) -> dict[str, Json]:
    """A manifest offer: {"id", "answers"}, plus "kind" and "roles" when it has a kind."""
    kinded = isinstance(v, dict) and "kind" in v
    return _object(v, {"id", "answers", "kind", "roles"} if kinded else {"id", "answers"})


def _offer(o: dict[str, Json]) -> ManifestOffer:
    answers, roles = _strs(o["answers"]), _strs(o["roles"]) if "roles" in o else ()
    if "kind" in o and len(roles) != len(answers):
        _bad("roles")
    return ManifestOffer(_str(o["id"]), answers, _str(o["kind"]) if "kind" in o else None, roles)


def _object(v: Json, keys: set[str]) -> dict[str, Json]:
    if not isinstance(v, dict) or set(v) != keys:
        raise StateFormatError("not a manifest")
    return v


def _list(v: Json) -> list[Json]:
    if not isinstance(v, list):
        raise StateFormatError("not a manifest")
    return v


def _strs(v: Json) -> tuple[str, ...]:
    return tuple(_str(x) for x in _list(v))


def _str(v: Json) -> str:
    return v if isinstance(v, str) else _bad("id")


def _int(v: Json) -> int:
    return v if isinstance(v, int) and not isinstance(v, bool) else _bad("number")


def _bad(what: str) -> Never:
    raise StateFormatError(f"not a manifest: {what}")
