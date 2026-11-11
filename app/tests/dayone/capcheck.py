"""The cap-loss check (docs/design/banked-time-plan.md, item 2): from a chapter's last decision, an 8 h and a 24 h
absence lose at most half of what each gathered store makes to its cap. Gathered: a store some card on a lane makes.
A tally store is made only by a fight's line, never a card's makes, so it is out by construction; the camp store is
passed in, since its levels pace the story by design. 72 h is reported, not checked (caploss.ABSENCE_H). Store ids only
(CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Collection

from ashfall_app.engine import Rules, Save
from tests.dayone import caploss

HOURS = (8, 24)
LIMIT = 0.5
"""The largest share of a gathered store's making an absence may lose."""


def gathered(rules: Rules, apart: Collection[str] = ()) -> frozenset[str]:
    """The stores some card makes, by a make flow or by its outcome's stores (paid as a rate), less `apart`."""
    made = {str(f.store) for c in rules.cards for f in c.makes} | {str(a.store) for c in rules.cards for a in c.outcome.stores}
    return frozenset(made) - set(apart)


def failing(save: Save, rules: Rules, apart: Collection[str] = ()) -> dict[str, tuple[int, ...]]:
    """Each gathered store losing more than LIMIT of its making over an absence from `save`, with the hours it does.
    Fails when no gathered store was sampled, since a check of nothing would pass every chapter."""
    away = caploss.absences(save, rules, HOURS)
    sampled = gathered(rules, apart) & set(away[HOURS[0]])
    assert sampled, "no gathered store was sampled"
    found = {s: tuple(h for h in HOURS if away[h][s].share > LIMIT) for s in sorted(sampled)}
    return {s: hs for s, hs in found.items() if hs}


def problems(found: dict[str, tuple[int, ...]]) -> list[str]:
    return [f"{s} loses over {LIMIT:.0%} of its making away {' and '.join(f'{h} h' for h in hs)}"
            for s, hs in found.items()]
