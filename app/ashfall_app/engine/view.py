"""The read model: everything a client needs to draw a save, derived and never stored. Reading writes nothing.

The client samples these segments against its clock until `next_event`; it never simulates. Semantics: DESIGN.txt,
"Read model" and part "CARDS", "Card panel".
"""
from dataclasses import dataclass, field

from .api import next_event
from .cards import CardDef
from .counts import is_completed, work_segment
from .events import Event
from .fightview import FightView, fight_views
from .gates import is_unlocked, shown_chips, store_cap
from .gone import is_left
from .heldentries import held_views
from .ids import HANDS, CardId, ChipId, LaneId, MixId, StoreId
from .index import index
from .motion import store_segment
from .mixes import flatten_shares
from .modifiers import Run, RunKind
from .needs import store_need
from .phaseview import skill_bar
from .plan import (
    OrderState, lane_order, mix_order, order_states, running_mix_id, running_town_mix_id, town_mix_order,
)
from .mixruns import mix_entries, mix_gains, town_entries
from .rates import Running, contribution, lane_state, running, unlocked_standing
from .rules import Rules
from .rules_check import features
from .segments import Segment, reach_time
from .cardsides import card_costs
from .coverage import all_covered, covered
from .units import BP
from .state import Save
from .offerstate import answer_card, answer_given, is_shown
from .unlocks import PRESENT_ONLY, Unlock, UnlockKind, unlock_key
from .viewparts import (
    AnswerView, CardView, CompletedCard, Contribution, HeldView, LaneBar, LedgerLine, Need, OfferView, RunBy,
    SkillBar, StandingBar,
)
from .decisions import cuts_in
from .inputs import input_whole
from .work import blocker, completions, effective_cap, greyed, starved, tap_seconds


@dataclass(frozen=True)
class View:
    time: int
    next_event: Event | None
    ledger: tuple[LedgerLine, ...]
    skills: tuple[SkillBar, ...]
    standing: tuple[StandingBar, ...]
    """Every unlocked standing action no leave stopped, makers and consumers alike, in rules.standing order."""
    lanes: tuple[LaneBar, ...]
    """The lanes the player can see, in rules order: HANDS always, another lane once some card on it is unlocked and
    until its person leaves; a free one is listed with card None."""
    cards: tuple[CardView, ...]
    """Unlocked cards not completed, in rules.cards order: the card panel. A left lane's cards are in neither list."""
    completed: tuple[CompletedCard, ...]
    """Unlocked completed cards, in rules.cards order: the Completed tab."""
    greyed_mixes: tuple[MixId, ...]
    """Saved mixes holding a completed card, in save.mixes order: drawn grey, editable or deletable only."""
    chips: tuple[ChipId, ...]
    """Chips shown now, in rules.chips order."""
    chips_seen: tuple[ChipId, ...]
    """Chips shown at any time in the save (Save.chips_seen), now included, in rules.chips order."""
    unlocked: tuple[Unlock, ...]
    """The effective unlock set, sorted by unlock_key (DESIGN.txt, "Unlocks")."""
    runs_out_at: int | None
    """When the running mix first runs a store it costs to empty: the earliest empties_at among falling ledger lines
    that a card of the flattened running mix costs. None: no running mix, a greyed one, or it runs indefinitely."""
    all_covered: bool
    """No ledger line needs the player: none falling uncovered and none starved (coverage.all_covered). Live, so not
    the end on its own: ended_at is."""
    ended_at: int | None
    """When the end happened (Save.ended_at; DESIGN.txt, "The end"), or None. Once set it never clears."""
    running_mix: MixId | None
    """The mix the hands run now: the first order on now whose mix is not greyed, else the player's own (save.active)
    (DESIGN.txt, "Order mix")."""
    mix_order: int | None
    """The index into save.orders of the order whose mix runs; None while the player's own mix runs."""
    orders_on: tuple[bool, ...]
    """orders_on[i]: orders[i]'s condition holds now (its latch)."""
    order_states: tuple[OrderState, ...]
    """order_states[i]: where orders[i] stands now, why it is off when it is (plan.order_states)."""
    offers: tuple[OfferView, ...] = ()
    """Every shown offer, in rules order (DESIGN.txt, "Read model" in part "TOWNSFOLK, INSTALLED RULES AND OFFERS")."""
    fights: tuple[FightView, ...] = ()
    """One per unlocked fight runner, cards then standing, each in rules order (DESIGN.txt, "FIGHTS", "View")."""
    running_town_mix: MixId | None = field(default=None, repr=False)
    """The town mix running now: the first order on now whose verb is a SwitchMix of a town mix that is not greyed;
    None when nobody runs shares (DESIGN.txt, "THE TOWN'S MIX"). running_mix reads hands mixes alone. Left out of the
    repr, with town_mix_order, so the recorded fingerprints (tests/cards_contract) stay those of a game with no town."""
    town_mix_order: int | None = field(default=None, repr=False)
    """The index into save.orders of the order whose town mix runs; None when none does."""
    held: tuple[HeldView, ...] = field(default=(), repr=False)
    """The cards whose while_running entries are held now, in rules.cards order (DESIGN.txt, "ENTRIES HELD WHILE A
    CARD RUNS"). Left out of the repr, like the town's, so the recorded fingerprints stay those of a game with none."""


def view(save: Save, rules: Rules) -> View:
    """The read model of `save` at save.time. Only unlocked stores, skills, cards and chips appear (all of them when
    rules.opening is None), in rules order."""
    now = running(save, rules)
    ledger = _ledger(save, rules, now)
    unlocked_cards = [c for c in rules.cards
                      if is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id)) and not is_left(save, c.lane)]
    mixed = _mixed(save, rules)
    return View(
        time=save.time, next_event=next_event(save, rules), ledger=ledger, skills=_skills(save, rules),
        standing=_standing(save, rules, now), lanes=_lanes(save, rules),
        cards=tuple(_card_view(save, rules, now, mixed, c) for c in unlocked_cards
                    if not is_completed(save, rules, c.id)),
        completed=tuple(CompletedCard(c.id, completions(save, rules, c.id)) for c in unlocked_cards
                        if is_completed(save, rules, c.id)),
        greyed_mixes=tuple(m.id for m in save.mixes if greyed(save, rules, m.id)),
        chips=shown_chips(save, rules), chips_seen=tuple(c.id for c, seen in zip(rules.chips, save.chips_seen) if seen),
        unlocked=_unlocked(save, rules), runs_out_at=_runs_out_at(save, rules, ledger),
        all_covered=all_covered(save, rules), ended_at=save.ended_at,
        running_mix=running_mix_id(save, rules), mix_order=mix_order(save, rules), orders_on=save.latches,
        order_states=order_states(save, rules), offers=_offers(save, rules),
        fights=fight_views(save, rules),
        running_town_mix=running_town_mix_id(save, rules), town_mix_order=town_mix_order(save, rules),
        held=held_views(save, rules),
    )


def _ledger(save: Save, rules: Rules, now: Running) -> tuple[LedgerLine, ...]:
    lines: list[LedgerLine] = []
    for d in rules.stores:
        if not is_unlocked(save, rules, Unlock(UnlockKind.STORE, d.id)):
            continue
        parts = tuple(Contribution(a, c) for a, share in now.shares.items()
                      if (c := contribution(save, rules, a, d.id, share, now.runs[a])) != 0)
        seg = store_segment(save, rules, d.id)
        cap = store_cap(save, rules, d.id)
        lines.append(LedgerLine(
            d.id, seg, sum(c.per_hour for c in parts), parts,
            reach_time(seg, 0) if seg.rate < 0 or seg.start_value == 0 else None,
            reach_time(seg, cap) if seg.rate > 0 or seg.start_value == cap else None,
            seg.rate < 0, covered(save, rules, d.id), starved(save, rules, d.id), cap))
    return tuple(lines)


def _runs_out_at(save: Save, rules: Rules, ledger: tuple[LedgerLine, ...]) -> int | None:
    mix = running_mix_id(save, rules)
    if mix is None or greyed(save, rules, mix):
        return None
    ix = index(rules)
    costed = {st for s in flatten_shares(save.mixes, mix) for st in card_costs(ix.cards[s.card])}
    return min((t for ln in ledger if ln.falling and ln.store in costed and (t := ln.empties_at) is not None),
               default=None)


def _skills(save: Save, rules: Rules) -> tuple[SkillBar, ...]:
    return tuple(skill_bar(save, rules, st) for d, st in zip(rules.skills, save.skills)
                 if is_unlocked(save, rules, Unlock(UnlockKind.SKILL, d.id)))


def _standing(save: Save, rules: Rules, now: Running) -> tuple[StandingBar, ...]:
    return tuple(StandingBar(a.id, now.runs[a.id].kind) for a in unlocked_standing(save, rules))


def _lanes(save: Save, rules: Rules) -> tuple[LaneBar, ...]:
    bars: list[LaneBar] = []
    for ls in save.lanes:
        if not _lane_shown(save, rules, ls.lane) or is_left(save, ls.lane):
            continue
        if ls.card is None:
            bars.append(LaneBar(ls.lane, None, None))
            continue
        seg = work_segment(save, ls.card)
        bars.append(LaneBar(ls.lane, ls.card, None if seg.limit is None else reach_time(seg, seg.limit),
                            lane_order(save, rules, ls.lane)))
    return tuple(bars)


def _lane_shown(save: Save, rules: Rules, lane: LaneId) -> bool:
    """HANDS always; another lane once a card on it is unlocked."""
    return lane == HANDS or any(c.lane == lane and is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id))
                                for c in rules.cards)


def _offers(save: Save, rules: Rules) -> tuple[OfferView, ...]:
    return tuple(OfferView(o.id, answer_given(save, rules, o.id),
                           tuple(AnswerView(a.id, card := answer_card(a), None if card is None
                                            else tap_seconds(save, rules, card)) for a in o.answers))
                 for o in rules.offers if is_shown(save, rules, o.id))


def _unlocked(save: Save, rules: Rules) -> tuple[Unlock, ...]:
    """save.unlocked, or with no opening every id of the rules, every offer and every feature in the vocabulary, with
    the answered and answer unlocks save.unlocked holds."""
    if rules.opening is not None:
        return save.unlocked
    ix = index(rules)
    every = [Unlock(UnlockKind.ACTION, a) for a in ix.standing] + [Unlock(UnlockKind.CARD, c) for c in ix.cards]
    every += [Unlock(UnlockKind.SKILL, s) for s in ix.skill_pos] + [Unlock(UnlockKind.STORE, s) for s in ix.stores]
    every += [Unlock(UnlockKind.CHIP, c) for c in ix.chips] + [Unlock(UnlockKind.FEATURE, f) for f in features(rules)]
    every += [Unlock(UnlockKind.OFFER, o) for o in ix.offers] + [u for u in save.unlocked if u.kind in PRESENT_ONLY]
    return tuple(sorted(every, key=unlock_key))


def _card_view(save: Save, rules: Rules, now: Running, mixed: dict[CardId, tuple[int, Run]], c: CardDef) -> CardView:
    ls = lane_state(save, c.lane)
    by = _run_by(save, c, ls.card == c.id)
    share, run = _mix_share(save, rules, now, mixed, c.id)
    bar = work_segment(save, c.id)
    total = c.work_s * BP
    gained = mix_gains(save, rules).get(c.id, ())
    return CardView(
        card=c.id, completions=completions(save, rules, c.id), cap=effective_cap(save, rules, c.id), bar=bar,
        bar_total=total, by=by, completes_at=_completes_at(bar, by, total),
        share_bp=share - sum(g.share_bp for g in gained), run=run,
        blocker=blocker(save, rules, c.id), tap_s=tap_seconds(save, rules, c.id), needs=_needs(save, rules, c),
        cuts_in=cuts_in(save, rules, c.id), spent_store=mixed[c.id][1].store if run is RunKind.SPENT else None,
        gained=gained)


def _run_by(save: Save, c: CardDef, tapped: bool) -> RunBy | None:
    if tapped:
        return RunBy.TAP
    return RunBy.MIX if work_segment(save, c.id).rate > 0 else None


def _completes_at(bar: Segment, by: RunBy | None, total: int) -> int | None:
    """A tap's landing: it keeps its speed and a rule waits for it (DESIGN.txt, "CURE CUT-IN"). A share claims none: a
    rule that takes the hands yields the mix, so its segment does not hold to its landing."""
    if by is not RunBy.TAP:
        return None
    return reach_time(bar, (bar.start_value // total + 1) * total)


def _mixed(save: Save, rules: Rules) -> dict[CardId, tuple[int, Run]]:
    """Each card of the flattened running mixes (the hands' then the town's) with its share and how it runs there."""
    return {c: (share, run) for c, share, run in (*mix_entries(save, rules), *town_entries(save, rules))}


def _mix_share(save: Save, rules: Rules, now: Running, mixed: dict[CardId, tuple[int, Run]], card: CardId
               ) -> tuple[int, RunKind | None]:
    """The card's share in the flattened running mix (the hands' or the town's, `mixed`) and how it runs there; a
    tap's own entry is the mix's, yielded."""
    if card not in mixed:
        return 0, None
    share, run = mixed[card]
    live: Run | None = now.runs.get(card)
    return share, (live if live is not None and lane_state(save, index(rules).cards[card].lane).card != card
                   else run).kind


def _needs(save: Save, rules: Rules, c: CardDef) -> tuple[Need, ...]:
    want: dict[StoreId, int] = {s: q for s, q in input_whole(save, rules, c) if q > 0}
    want |= {a.store: 1 for a in c.drains}
    for cond in c.requires:
        if (need := store_need(cond)) is not None:
            want[need[0]] = max(want.get(need[0], 0), need[1])
    return tuple(Need(s, q, store_segment(save, rules, s)) for s, q in want.items())
