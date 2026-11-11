"""The states each of day two's text keys shows in, on the played routes: the source of the line writers' brief
(content/team/day-two.md, "Line moments"). A line key's states are where its line fired; a label's (a card's, her row's,
the offer's and its answers', an aim's, the end card's, a level's pay) where it was on screen during a visit. A state is
the route, day two's visit, present or on return, the story's clock (afternoon, evening, night, day 3), the builds
done, the answer given and her task. A key with no state was never shown on any route played. Ids only."""
import tomllib
from collections import defaultdict
from functools import cache

from ashfall_app.engine import AfterTime, Save, TapCard, Unlock, UnlockKind, View
from ashfall_app.opening.schema import DAY_TWO
from tests.daytwo import content as c
from tests.daytwo.player import DayTwoPlayer


@cache
def day_two_keys() -> tuple[str, ...]:
    """Every text key day_two.toml adds."""
    with DAY_TWO.open("rb") as f:
        return tuple(tomllib.load(f)["text"])


def _has(save: Save, kind: UnlockKind, id_: str) -> bool:
    return Unlock(kind, id_) in save.unlocked


def clock(save: Save) -> str:
    if _has(save, UnlockKind.FEATURE, "morning_3"):
        return "day 3"
    if _has(save, UnlockKind.FEATURE, "night_2"):
        return "night"
    if _has(save, UnlockKind.FEATURE, "dusk_2"):
        return "evening"
    return "afternoon"


def builds(save: Save) -> str:
    done = [b.split("_", 1)[1] for b, f in (("build_shelter", "n1_shelter"), ("build_woodstack", "woodstack"))
            if _has(save, UnlockKind.FEATURE, f)]
    return "+".join(done) or "none built"


def answered(save: Save) -> str:
    for a in (c.GO, c.SHE_GOES):
        if _has(save, UnlockKind.ANSWER, a):
            return a.removeprefix("o_cart_")
    return "open" if _has(save, UnlockKind.OFFER, c.OFFER) else "no offer"


def her_task(save: Save) -> str:
    card = next((o.then.card for o in save.orders if isinstance(o.when, AfterTime) and isinstance(o.then, TapCard)
                 and o.then.card in c.TASKS), None)
    return "her task " + ("none" if card is None else card.removeprefix("n1_"))


def state(name: str, p: DayTwoPlayer, save: Save, t: int) -> str:
    first = p.b3_visit() or 1
    v = next((v for v in p.visits if v.start <= t <= v.end), None)
    back = v is None or (t == v.start and v.gap > 0)
    v = v or next((v for v in p.visits if v.start >= t), None)
    where = "after the last visit" if v is None else f"V{v.index - first + 1} " + ("on return" if back else "present")
    return f"{name} {where} | {clock(save)} | {builds(save)} | {answered(save)} | {her_task(save)}"


def shown(v: View, save: Save) -> set[str]:
    """The day-two label keys on screen in this view."""
    o = c.opening2()
    keys: set[str] = set()
    open_cards = {x.card for x in v.cards}
    for card in o.cards:
        if card.id in open_cards:
            keys |= {k for k in (card.label_key, card.upside_key) if k is not None}
    if any(b.lane == c.LANE for b in v.lanes):
        lane = next(x for x in o.lanes if x.id == c.LANE)
        later = [x for x in lane.later_labels if _has(save, UnlockKind(x.after.unlock_kind), x.after.id)]
        keys.add(later[-1].label_key if later else lane.label_key)
    for offer in o.offers:
        if any(x.offer == offer.id and x.answer is None for x in v.offers):
            keys |= {offer.text_key, *(k for a in offer.answers for k in (a.label_key, a.cost_key))}
    aims = [a for a in o.aims if a.after is None or _has(save, UnlockKind(a.after.unlock_kind), a.after.id)]
    if aims:
        keys.add(aims[-1].text_key)
    for f in o.features:
        if f.card is not None and _has(save, UnlockKind.FEATURE, f.id):
            keys |= {f.card.title_key, *f.card.line_keys, f.card.button_key}
    pays = {(s.id, lv.level): lv.pays_key for s in o.skills for lv in s.levels}
    keys |= {pays[(str(b.skill), b.level + 1)] for b in v.skills if (str(b.skill), b.level + 1) in pays}
    return keys


def states(plays: dict[str, DayTwoPlayer]) -> dict[str, set[str]]:
    """Each day-two key with the states it showed or fired in, on these plays (from B3's landing on)."""
    ours = set(day_two_keys())
    found: dict[str, set[str]] = defaultdict(set)
    for name, p in plays.items():
        b3 = p.landed_at["B3"]
        for ln in p.lines:
            if ln.time >= b3 and ln.key in ours:
                found[ln.key].add(state(name, p, _after(p, ln.time), ln.time))
        for s, v in p.history:
            if s.time >= b3 and any(x.start <= s.time <= x.end for x in p.visits):
                for k in shown(v, s) & ours:
                    found[k].add(state(name, p, s, s.time))
    return {k: found.get(k, set()) for k in day_two_keys()}


def _after(p: DayTwoPlayer, t: int) -> Save:
    """The first save of the play at or after `t` (a line fired while away is read at the return)."""
    return next(s for s, _ in p.history if s.time >= t)


def report(plays: dict[str, DayTwoPlayer]) -> list[str]:
    out = ["", f"day two line states ({len(day_two_keys())} keys; routes: {', '.join(plays)})"]
    for key, found in states(plays).items():
        out.append(f"  {key}: {'never shown on these routes' if not found else ''}")
        out += [f"      {x}" for x in sorted(found)]
    return out
