"""The cap-loss readout (docs/design/banked-time-plan.md, item 2): from a chapter's last decision, what each gathered
store loses to its cap over an 8 h and a 24 h absence. A person reads it; nothing fails on it. Gathered: a store some
card on a lane makes. A tally store is made only by a fight's line, never a card's makes, so it is out by construction;
the camp store is passed in, since its levels pace the story by design. 72 h is in the day readouts (caploss.ABSENCE_H).
Store ids only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Collection

from ashfall_app.engine import Rules, Save
from tests.dayone import caploss

HOURS = (8, 24)


def gathered(rules: Rules, apart: Collection[str] = ()) -> frozenset[str]:
    """The stores some card makes, by a make flow or by its outcome's stores (paid as a rate), less `apart`."""
    made = {str(f.store) for c in rules.cards for f in c.makes} | {str(a.store) for c in rules.cards for a in c.outcome.stores}
    return frozenset(made) - set(apart)


def losses(save: Save, rules: Rules, apart: Collection[str] = ()) -> dict[int, dict[str, caploss.StoreLoss]]:
    """Each gathered store's making and loss over an absence of each of HOURS from `save`. Fails when no gathered store
    was sampled, since a readout of nothing would read as no loss anywhere."""
    away = caploss.absences(save, rules, HOURS)
    sampled = gathered(rules, apart) & set(away[HOURS[0]])
    assert sampled, "no gathered store was sampled"
    return {h: {s: away[h][s] for s in sorted(sampled)} for h in HOURS}


def lines(save: Save, rules: Rules, apart: Collection[str] = ()) -> list[str]:
    """One row per absence: each gathered store that lost any of its making, with the share the cap dropped."""
    return [f"  cap loss at the end, away {h} h: "
            + (", ".join(f"{s} {100 * x.share:.0f}%" for s, x in found.items() if x.lost) or "none")
            for h, found in losses(save, rules, apart).items()]
