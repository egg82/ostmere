"""The states each of a chapter's text keys shows in, on the played routes: the source of the line writers' brief, as
daytwo/lines.py is for day two, read off any chapter file and any route played past B4. A line key's states are where
its line fired; a label's (a card's, a lane's, an offer's and its answers', an aim's, a feature's, a level's pay) where
it was on screen during a visit. A state is the route, the visit (counted from the chapter's first), present or on
return, the capped cards done, the answers given, the queue's length. A key with no state was never shown
on any route played. Ids only (CLAUDE.md, "Never spoil the owner")."""
import tomllib
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from ashfall_app.engine import Save, Unlock, UnlockKind, View
from ashfall_app.engine.work import completions
from ashfall_app.opening.schema import DAY_TWO, Opening
from tests.dayone.player import DayOnePlayer

DAY_THREE = DAY_TWO.parent / "day_three.toml"


def chapter_keys(path: Path) -> tuple[str, ...]:
    """Every text key the chapter file adds."""
    with path.open("rb") as f:
        return tuple(tomllib.load(f)["text"])


def _has(save: Save, kind: UnlockKind, id_: str) -> bool:
    return Unlock(kind, id_) in save.unlocked


def state(name: str, p: DayOnePlayer, save: Save, t: int, first_visit: int) -> str:
    v = next((v for v in p.visits if v.start <= t <= v.end), None)
    back = v is None or (t == v.start and v.gap > 0)
    v = v or next((v for v in p.visits if v.start >= t), None)
    where = "after the last visit" if v is None else f"V{v.index - first_visit + 1} " + ("on return" if back else "present")
    capped = sum(1 for c in p.rules.cards if c.cap is not None and completions(save, p.rules, c.id) >= c.cap)
    answers = sorted(u.id for u in save.unlocked if u.kind is UnlockKind.ANSWER)
    return f"{name} {where} | {capped} capped done | answers {answers or 'none'} | queue {len(save.queue)}"


def shown(o: Opening, v: View, save: Save) -> set[str]:
    """The label keys of `o` on screen in this view."""
    keys: set[str] = set()
    open_cards = {x.card for x in v.cards}
    for card in o.cards:
        if card.id in open_cards:
            keys |= {k for k in (card.label_key, card.upside_key) if k is not None}
    for lane in o.lanes:
        if any(b.lane == lane.id for b in v.lanes):
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


def states(plays: Mapping[str, DayOnePlayer], keys: tuple[str, ...], o: Opening, first_visit: Mapping[str, int],
           from_t: Mapping[str, int]) -> dict[str, set[str]]:
    """Each key with the states it showed or fired in, on these plays from `from_t`'s time on."""
    ours = set(keys)
    found: dict[str, set[str]] = defaultdict(set)
    for name, p in plays.items():
        start, first = from_t[name], first_visit[name]
        for ln in p.lines:
            if ln.time >= start and ln.key in ours:
                found[ln.key].add(state(name, p, _after(p, ln.time), ln.time, first))
        for s, v in p.history:
            if s.time >= start and any(x.start <= s.time <= x.end for x in p.visits):
                for k in shown(o, v, s) & ours:
                    found[k].add(state(name, p, s, s.time, first))
    return {k: found.get(k, set()) for k in keys}


def _after(p: DayOnePlayer, t: int) -> Save:
    """The first save of the play at or after `t` (a line fired while away is read at the return)."""
    return next(s for s, _ in p.history if s.time >= t)


def report(plays: Mapping[str, DayOnePlayer], keys: tuple[str, ...], o: Opening, first_visit: Mapping[str, int],
           from_t: Mapping[str, int]) -> list[str]:
    out = ["", f"line states ({len(keys)} keys; routes: {', '.join(plays)})"]
    for key, found in states(plays, keys, o, first_visit, from_t).items():
        out.append(f"  {key}: {'never shown on these routes' if not found else ''}")
        out += [f"      {x}" for x in sorted(found)]
    return out
