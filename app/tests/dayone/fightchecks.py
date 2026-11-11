"""The day-one checks past the fights (docs/design/combat-plan.md, item 10), each a pure function of a save and the rules,
so they read any chapter: a tapped fight card's drawn landing comes true and a mixed one claims none, and a store a
standing threat drains to nothing has something in reach that puts it up. Each returns what it judged beside its
problems, so a route showing no fight reads as blind and not as clean. Problems name ids and seconds only (CLAUDE.md,
"Never spoil the owner")."""
from ashfall_app.engine import Rules, RunBy, Save, StoreId, value, view
from ashfall_app.engine.cure_reading import puts_up
from tests.dayone.cures import raises
from tests.dayone.sinkchecks import landing_kept


def fight_landings(save: Save, rules: Rules) -> tuple[int, list[str]]:
    """(fight cards running, those a share runs that claim a landing, or a tap runs whose drawn landing does not come
    true with nobody deciding)."""
    fighting = {c.id for c in rules.cards if c.fight is not None}
    running = [c for c in view(save, rules).cards if c.card in fighting and c.by is not None]
    claimed = [f"{c.card} share claims a landing at t={c.completes_at}" for c in running
               if c.by is RunBy.MIX and c.completes_at is not None]
    return len(running), claimed + [f"{c.card} drawn landing at t={c.completes_at}, not kept" for c in running
                                    if c.by is RunBy.TAP and c.completes_at is not None
                                    and not landing_kept(save, rules, c.card, c.completes_at)]


def threat_stores_unreached(save: Save, rules: Rules) -> tuple[int, list[str]]:
    """(stores a standing fight takes that stand at nothing, those with no ready card that puts them up)."""
    v = view(save, rules)
    shown, cards = {str(f.runner) for f in v.fights}, {c.id: c for c in rules.cards}
    judged, out = 0, list[str]()
    for a in rules.standing:
        if a.fight is None or str(a.id) not in shown:
            continue
        for taken in a.fight.loses:
            if value(save, rules, StoreId(taken.store), save.time) > 0:
                continue
            judged += 1
            if not any(raises(save, rules, str(taken.store), c.card) for c in v.cards
                       if str(taken.store) in puts_up(rules, cards[c.card])):
                out.append(f"{taken.store} empty at t={save.time}, taken by {a.id}: nothing in reach puts it up")
    return judged, out
