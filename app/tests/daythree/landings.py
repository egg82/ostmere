"""When the goals on offer land with nobody deciding (counters.py, "decide"; shifts.py). A goal is a capped card on offer."""
from ashfall_app.engine import CardId, Rules, Save, advance, next_event, view
from ashfall_app.engine.work import completions

HORIZON_S = 24 * 3600
"""How far ahead a goal's landing is looked for, in LOOK_S steps; a goal not landing by then lands last."""
LOOK_S = 900


def goals(save: Save, rules: Rules) -> tuple[CardId, ...]:
    """The capped cards on offer: what a player is working toward."""
    return tuple(c.card for c in view(save, rules).cards if c.cap is not None)


def landings(save: Save, rules: Rules, cards: tuple[CardId, ...], left: int = 1) -> dict[CardId, int | None]:
    """When each card next completes with nobody deciding, read on the LOOK_S grid to HORIZON_S. By default that is
    enough to order them: it stops once all but one have landed, and the one left (None) lands last, as first_of reads
    it; `left` = 0 reads every one (None: not within HORIZON_S). Completions change only at events, so it jumps from
    event to the first grid point at or after it (advance is path independent) rather than stepping every LOOK_S."""
    base = {c: completions(save, rules, c) for c in cards}
    found: dict[CardId, int | None] = {c: None for c in cards}
    s, end = save, save.time + HORIZON_S
    while s.time < end and sum(t is None for t in found.values()) > left:
        nxt = next_event(s, rules)
        if nxt is None:
            break
        steps = -(-(nxt.time - save.time) // LOOK_S)
        s = advance(s, rules, save.time + max(steps, 1) * LOOK_S)
        if s.time > end:
            break
        for c in cards:
            if found[c] is None and completions(s, rules, c) > base[c]:
                found[c] = s.time
    return found


def first_of(times: dict[CardId, int | None], a: CardId, b: CardId) -> int:
    """-1 when a lands first, 1 when b does, 0 when together (or neither lands)."""
    ta, tb = times[a], times[b]
    if ta == tb:
        return 0
    if tb is None or (ta is not None and ta < tb):
        return -1
    return 1
