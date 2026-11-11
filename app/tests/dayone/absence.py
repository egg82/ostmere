"""The absence ladder: from a leave point of a played route, the player is gone 1 h to 7 days and the engine runs on;
the return's arrivals are counted from served data (the two views and the lines the step emitted), placed as the
page places them, and timed by the arrival queue's own rules (arrival_rules.py). Beats by number only.

    python -m tests.dayone.report --absence
"""
from collections import Counter
from collections.abc import Mapping, Sequence, Set as AbstractSet
from dataclasses import dataclass

from ashfall_app.engine import Line, Rules, Save, UnlockKind, View, advance_logged, view
from ashfall_app.opening.entries import ConditionEntry
from tests.dayone import arrival_rules as ar
from tests.dayone import capcheck, caploss
from tests.dayone.beats import STORY
from tests.dayone.human import HumanPlayer, human_day
from tests.dayone.schedules import HOUR
from tests.opening.playthrough import opening

ABSENCES_H = (1, 8, 24, 72, 168)
KINDS = ("line", "feature", "chip", "store", "skill", "card", "level")
ARRIVING = {UnlockKind.FEATURE, UnlockKind.STORE, UnlockKind.SKILL, UnlockKind.CARD}
BEHIND_LEDGER = ("skill", "card", "level")
"""The kinds the page shows after the ledger's lines (game/arrivals.ts KIND_ORDER; a level's burst is a skill's)."""


@dataclass(frozen=True)
class Return:
    hours: int
    counts: dict[str, int]
    reveal_ms: int
    squeezed: int
    lost: float | None = None
    """The share of what every store made that its cap dropped (caploss.py), for the hours it measures."""
    gathered: tuple[tuple[str, float], ...] = ()
    """Each gathered store that lost any of its making, with its share, as the cap-loss check reads it (capcheck.py:
    the camp store apart), for the hours that check measures."""

    @property
    def total(self) -> int:
        return sum(self.counts.values())


@dataclass(frozen=True)
class Point:
    label: str
    after_end_h: float
    returns: tuple[Return, ...]


def place(chips: Mapping[str, tuple[str, bool]], lines: Sequence[tuple[str, str | None]], shown: AbstractSet[str],
          repeats: AbstractSet[str]) -> list[str]:
    """Where each line goes, as game/awaylines.ts places it: "band", "log" or "none". `chips`: line key to (chip, is
    its on-line); `lines`: (key, card); `shown`: the chips shown after; `repeats`: the uncapped cards."""
    chip_of = [chips.get(key) if card is None else None for key, card in lines]
    last = {c[0]: i for i, c in enumerate(chip_of) if c is not None}
    out: list[str] = []
    for i, (_, card) in enumerate(lines):
        c = chip_of[i]
        if c is not None:
            out.append("log" if c[1] or (last[c[0]] == i and c[0] not in shown) else "none")
        else:
            out.append("log" if card is not None and card in repeats else "band")
    return out


def band_lines(rules: Rules, lines: tuple[Line, ...], before: View, after: View) -> list[Line]:
    chips = {str(k): (str(c.id), k == c.on_line) for c in rules.chips for k in (c.on_line, c.off_line) if k is not None}
    repeats = {c.card for c in (*before.cards, *after.cards) if c.cap is None}
    where = place(chips, [(ln.key, ln.card) for ln in lines], set(after.chips), repeats)
    return [ln for ln, w in zip(lines, where) if w == "band"]


def rule_words(when: ConditionEntry, store: str) -> str:
    """An order card's condition as game/storerule.ts ruleWhen words it (a count is one word, whatever its value)."""
    text, o = opening().text, opening()
    label = text[next(s.label_key for s in o.stores if s.id == store)]
    band = when.release is not None and when.release != when.value
    key = ("ui.rule.below" if when.test == "at_most" else "ui.rule.reaches") + ("_until" if band else "")
    return text[key].replace("{store}", label).replace("{n}", "1").replace("{m}", "1")


def ledger_hold_ms(after: View, store: str) -> int:
    """A ledger line's reading time as ui/ledger.ts holds it on arrival: its name and rate, and on a red line with an
    order card offered, the offer's sentence (condition, arrow, task) and its two-word button."""
    o, text = opening(), opening().text
    words = [text[next(s.label_key for s in o.stores if s.id == store)], "+0/min"]
    line = next((ln for ln in after.ledger if str(ln.store) == store), None)
    unlocked = {(u.kind.value, str(u.id)) for u in after.unlocked}
    offered = [c for c in o.order_cards if c.store == store and c.chip is None and c.tap_card is not None
               and (c.offered_after is None or (c.offered_after.unlock_kind, c.offered_after.id) in unlocked)]
    if line is not None and (line.starved or (line.falling and not line.covered)) and offered:
        card = offered[-1]   # game/cues.ts offeredCard: the last one offered
        task = text[next(c.label_key for c in o.cards if c.id == card.tap_card)]
        words += [rule_words(card.when, store), "→", task, "two words"]
    return ar.reading_ms(" ".join(words))


def ledger_holds(before: View, after: View) -> list[int]:
    """The reading hold of each store the return unlocks that the ledger draws: with the ledger on, the Camp store
    excepted (it is the Camp bar)."""
    if not any(u.kind is UnlockKind.FEATURE and str(u.id) == "ledger" for u in after.unlocked):
        return []
    camp = opening().camp
    old = {u for u in before.unlocked if u.kind is UnlockKind.STORE}
    new = {str(u.id) for u in after.unlocked if u.kind is UnlockKind.STORE and u not in old}
    return [ledger_hold_ms(after, s) for s in sorted(new - {camp.store if camp else ""})]


def counts(rules: Rules, before: View, after: View, lines: tuple[Line, ...], text: Mapping[str, str] | None = None
           ) -> tuple[Counter[str], list[int]]:
    """Arrivals by kind, and the reading time of each band line, read in `text` (the shipped opening's unless given the
    text of chapters it lacks)."""
    text = opening().text if text is None else text
    holds = [ar.reading_ms(text[ln.key]) for ln in band_lines(rules, lines, before, after)]
    new = {u for u in after.unlocked if u.kind in ARRIVING} - set(before.unlocked)
    found = Counter({"line": len(holds), "chip": len(set(after.chips) - set(before.chips))})
    found.update(u.kind.value for u in new)
    old = {s.skill: s.level for s in before.skills}
    fresh = {u.id for u in new if u.kind is UnlockKind.SKILL}
    found["level"] = sum(1 for s in after.skills if s.skill not in fresh and s.level > old.get(s.skill, s.level))
    return found, holds


def absences(rules: Rules, save: Save, hours: tuple[int, ...]) -> tuple[Return, ...]:
    """One return per absence, each stepped on from the shorter one (the engine's split invariant: the lines of two
    steps are the lines of one), so the longest costs one run, not the sum."""
    before, at, lines, found = view(save, rules), save, tuple[Line, ...](), list[Return]()
    tally, walked = caploss.Tally(), save
    for h in hours:
        step = advance_logged(at, rules, save.time + h * HOUR)
        at, lines = step.save, lines + step.lines
        after = view(at, rules)
        counted, holds = counts(rules, before, after, lines)
        rest = sum(n for k, n in counted.items() if k != "line")
        behind = sum(counted[k] for k in BEHIND_LEDGER)
        reveal = ar.reveal_ms(holds, rest, ledger_holds(before, after), behind)
        lost, gathered = None, ()
        if h in caploss.ABSENCE_H:
            walked = caploss.run(walked, rules, save.time + h * HOUR, tally)
            lost = caploss.total_share(tally.losses())
            gathered = gathered_losses(tally.losses(), rules) if h in capcheck.HOURS else ()
        found.append(Return(h, {k: counted[k] for k in KINDS}, reveal, ar.squeezed(rest), lost, gathered))
    return tuple(found)


def gathered_losses(losses: Mapping[str, caploss.StoreLoss], rules: Rules) -> tuple[tuple[str, float], ...]:
    """The gathered stores (capcheck.gathered, the camp store apart) that lost any of their making, with each share."""
    camp = opening().camp
    kept = capcheck.gathered(rules, (camp.store,) if camp else ())
    return tuple((s, loss.share) for s, loss in losses.items() if s in kept and loss.lost > 0)


def last_beat(p: HumanPlayer, time: int) -> str:
    seen = [b for b in STORY if b in p.seen_at and p.seen_at[b] <= time]
    return seen[-1] if seen else "none"


def ladder(p: HumanPlayer, visits: tuple[int, ...] | None = None, hours: tuple[int, ...] = ABSENCES_H) -> list[Point]:
    """Each chosen visit's exit (all by default) left for each of `hours`."""
    assert p.end_at is not None
    exits = [v for v in p.visits if visits is None or v.index in visits]
    return [Point(f"V{v.index} after {last_beat(p, v.exit.time)}", (v.exit.time - p.end_at) / HOUR,
                  absences(p.rules, v.exit, hours)) for v in exits if v.exit is not None]


def never_fewer(points: list[Point]) -> list[str]:
    """Each point's longer absence that holds fewer arrivals than a shorter one from the same point."""
    return [f"{pt.label}: {b.hours} h holds {b.total}, {a.hours} h holds {a.total}"
            for pt in points for a, b in zip(pt.returns, pt.returns[1:]) if b.total < a.total]


def lines_of(points: list[Point]) -> list[str]:
    out = [f"{'leave point':22s} {'at +h':>6s} {'away':>5s}  " + " ".join(f"{k:>7s}" for k in KINDS) + "  total  reveal s  squeezed  lost"]
    for pt in points:
        for r in pt.returns:
            out.append(f"{pt.label:22s} {pt.after_end_h:6.2f} {r.hours:4d}h  "
                       + " ".join(f"{r.counts[k]:7d}" for k in KINDS) + f"  {r.total:5d}  {r.reveal_ms / 1000:8.1f}  {r.squeezed:8d}  "
                       + ("   -" if r.lost is None else f"{100 * r.lost:3.0f}%"))
    return out + cap_lines(points)


def cap_lines(points: list[Point]) -> list[str]:
    """Each leave point's gathered stores losing to their caps, as the cap-loss check reads a chapter's end. Day one's
    leave points come before the cap rule is taught and before most sinks exist, so they are reported, never checked."""
    out = ["\ncap loss as capcheck.py reads it, from each leave point (reported; the check reads a chapter's end)"]
    for pt in points:
        for r in pt.returns:
            if r.hours in capcheck.HOURS:
                stores = ", ".join(f"{s} {100 * share:.0f}%" for s, share in r.gathered) or "none"
                out.append(f"{pt.label:22s} {r.hours:4d}h  {stores}")
    return out


def main() -> None:
    print("\n".join(lines_of(ladder(human_day()))))
