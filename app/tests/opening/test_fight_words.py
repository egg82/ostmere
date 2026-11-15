"""Every name a fight shows has its words in the content: each side and threat's label, and the label behind each
source of a strength entry (a card, skill, chip, store or feature, the page's lookup order). Ids and keys only."""
from dataclasses import fields, is_dataclass
from typing import Any

from ashfall_app.engine import Modifier, SideStrength, ThreatStrength
from ashfall_app.opening.schema import Opening
from tests.opening.playthrough import opening, opening_rules


def _modifiers(node: Any) -> list[Modifier]:
    if isinstance(node, Modifier):
        return [node]
    if isinstance(node, (tuple, list)):
        return [m for x in node for m in _modifiers(x)]
    if is_dataclass(node) and not isinstance(node, type):
        return [m for f in fields(node) for m in _modifiers(getattr(node, f.name))]
    return []


def _strength_sources() -> set[str]:
    rules = opening_rules()
    return {str(m.source) for m in _modifiers(rules) if isinstance(m.target, (SideStrength, ThreatStrength))}


def unworded(o: Opening, sources: set[str]) -> list[str]:
    """What a fight would show as a bare id or a blank: each label key absent from the text, each source no entry names."""
    keys = {
        **{f"side {x.id}": x.label_key for x in o.sides},
        **{f"threat {x.id}": x.label_key for x in o.threats},
    }
    labelled: dict[str, str | None] = {}
    for group in (o.features, o.stores, o.chips, o.skills, o.cards):
        for x in group:
            labelled.setdefault(x.id, x.label_key)
    bad = [f"{who}: {k}" for who, k in keys.items() if k not in o.text]
    for s in sorted(sources):
        key = labelled.get(s)
        if key is None or key not in o.text:
            bad.append(f"source {s}: no words")
    return bad


def test_every_name_a_fight_shows_has_words() -> None:
    sources = _strength_sources()
    assert any(s for s in sources), "control: the content aims modifiers at fight strengths"
    assert unworded(opening(), sources) == []


def test_a_missing_key_is_caught() -> None:
    o = opening()
    threat = o.threats[0]
    cut = o.model_copy(update={"text": {k: v for k, v in o.text.items() if k != threat.label_key}})
    assert unworded(cut, set()) == [f"threat {threat.id}: {threat.label_key}"]
    assert unworded(o, {"no_such_entry"}) == ["source no_such_entry: no words"]
