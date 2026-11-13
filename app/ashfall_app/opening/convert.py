"""An Opening's authoring units (whole items, seconds) to the engine's Rules (fixed point). Pure."""
from dataclasses import replace
from typing import TYPE_CHECKING

from ..engine import (
    BP, HANDS, ActionId, FightDef, WhileRunning, HeldSpeed, SideDef, SideId, SideStrength, ThreatDef, ThreatId, ThreatStrength, AfterTime, AnswerDef, AnswerId, KindId, OfferDef, OfferId, RoleId, Amount, AtLeast, AtMost, CapRaise, CardCount, CardDef, CardId, ChipDef, ChipId,
    Condition, Join, Leave, MixId, FeatureId, Flow, FlowKind, LaneDef, LaneId, LaneRules, LaneSpeed, LineKey, Modifier, ModifierKind, Outcome, PacingCurve,
    RateRef, RuleInstall, Rules, Runner, Running, SkillDef, SkillId, SkillLevel, SourceId, StandingDef, StoreCap, StoreDef,
    StoreId, StoreValue, Subject, Target, TriggerDef, TriggerId, Unlock, Unlocked, UnlockKind, WorkRef, ceil_div,
    per_hour, units,
)
from ..engine.units import QUANTITY_SCALE
from .prestige import node_def, prestige_def

if TYPE_CHECKING:
    from .camp_entries import CampEntry, CampLevelEntry
    from .entries import (
        CardEntry, ChipEntry, ConditionEntry, FlowEntry, ItemAmount, ModifierEntry,
        FightEntry, OutcomeEntry, StandingEntry, TriggerEntry, UnlockEntry, WhileRunningEntry,
    )
    from .offer_entries import OfferEntry
    from .schema import Opening


def build_rules(o: "Opening") -> Rules:
    cards = {c.id for c in o.cards}
    ruled = {LaneId(x.id) for x in o.lanes if x.ruled}
    return Rules(
        stores=tuple(StoreDef(StoreId(s.id), units(s.cap_items), units(s.initial_items)) for s in o.stores),
        skills=tuple(SkillDef(SkillId(s.id)) for s in o.skills),
        standing=tuple(_standing(a) for a in o.standing),
        sides=tuple(SideDef(SideId(s.id), s.base) for s in o.sides),
        threats=tuple(ThreatDef(ThreatId(t.id), t.base) for t in o.threats),
        curve=PacingCurve(tuple(units(n) for n in o.curve_items)),
        lanes=tuple(LaneDef(LaneId(x.id), x.ruled) for x in o.lanes),
        cards=tuple(_with_camp(_with_lifts(_card(c, cards), o.camp), o.camp, ruled) for c in o.cards),
        chips=tuple(_chip(c, cards) for c in o.chips),
        triggers=tuple(_trigger(t, cards) for t in o.triggers) + _camp_triggers(o.camp, cards)
        + tuple(_offer_trigger(x, cards) for x in o.offers) + _note_triggers(o, cards),
        opening=tuple(unlock(u) for u in o.start),
        end=FeatureId(o.end_feature),
        offers=tuple(_offer(x, cards) for x in o.offers),
        prestige=prestige_def(o.prestige), nodes=tuple(node_def(n, cards) for n in o.nodes),
    )


def _offer(x: "OfferEntry", cards: set[str]) -> OfferDef:
    answers = tuple(AnswerDef(AnswerId(a.id), _outcome(a.outcome, cards), None if a.role is None else RoleId(a.role))
                    for a in x.answers)
    return OfferDef(OfferId(x.id), answers, None if x.kind is None else KindId(x.kind))


def offer_trigger_id(offer: str) -> TriggerId:
    """The trigger the loader makes to show an offer."""
    return TriggerId(f"offer_{offer}")


def _offer_trigger(x: "OfferEntry", cards: set[str]) -> TriggerDef:
    """Shows the offer once its gate and requires hold, writing its lines."""
    return TriggerDef(offer_trigger_id(x.id), condition(x.gate, cards),
                      Outcome(unlocks=(Unlock(UnlockKind.OFFER, x.id),), lines=tuple(LineKey(k) for k in x.line_keys)),
                      tuple(condition(c, cards) for c in x.requires))


def note_trigger_id(note: str) -> TriggerId:
    """The trigger the loader makes to write a note."""
    return TriggerId(f"note_{note}")


def _note_triggers(o: "Opening", cards: set[str]) -> tuple[TriggerDef, ...]:
    """Each note's trigger: its gate and requires, unlocking the note, and for its entry's first note the entry as well.
    A later note also requires the entry, so it is never a note on a page that is not there."""
    first: dict[str, str] = {}
    for n in o.notes:
        first.setdefault(n.entry, n.id)
    out: list[TriggerDef] = []
    for n in o.notes:
        is_first = first[n.entry] == n.id
        unlocks = (Unlock(UnlockKind.ENTRY, n.entry),) * is_first + (Unlock(UnlockKind.NOTE, n.id),)
        entry = AtLeast(Unlocked(Unlock(UnlockKind.ENTRY, n.entry)), 1, 1)
        requires = tuple(condition(c, cards) for c in n.requires) + (() if is_first else (entry,))
        out.append(TriggerDef(note_trigger_id(n.id), condition(n.gate, cards), Outcome(unlocks=unlocks), requires))
    return tuple(out)


def camp_trigger_id(n: int) -> TriggerId:
    """The trigger that lands Camp level n (1-based)."""
    return TriggerId(f"camp_{n}")


def _with_camp(card: CardDef, camp: "CampEntry | None", ruled: set[LaneId]) -> CardDef:
    """Every hands card, and every card on a ruled lane, fills the camp store by its work: a make flow at a full share,
    so a tap and a mix share count by the time they take."""
    if camp is None or (card.lane != HANDS and card.lane not in ruled):
        return card
    return replace(card, makes=card.makes + (Flow(StoreId(camp.store), per_hour(camp.items_per_hour)),))


def camp_lands(lv: "CampLevelEntry") -> bool:
    """A level the loader makes a trigger for: every level but a held one nothing lifts."""
    return not lv.held or bool(lv.lifted_by)


def camp_cap(camp: "CampEntry") -> int:
    """The camp store's cap in items: one under the first held level a step lifts (the bar holds just below its
    marker), else the last level's at_items."""
    lifted = [lv.at_items for lv in camp.levels if lv.held and lv.lifted_by]
    return lifted[0] - 1 if lifted else camp.levels[-1].at_items


def to_camp_id(n: int) -> TriggerId:
    """The trigger that raises the camp cap for Camp level n (1-based) once level n - 1 lands."""
    return TriggerId(f"to_camp_{n}")


def camp_chain(camp: "CampEntry") -> list[tuple[int, str | None, int]]:
    """The camp cap's steps in order (engine DESIGN.txt, "THE CAMP"): (level n, the lifting card or None for the step
    to_camp_n, the raise in bp). Each step's target is exact, the least add that reaches a level or the greatest that
    stays under a held one, and its raise is that target less the previous step's, so the raises telescope."""
    first = next((i for i, lv in enumerate(camp.levels) if lv.held and lv.lifted_by), None)
    if first is None:
        return []
    base = units(camp_cap(camp))
    steps: list[tuple[int, str | None, int]] = []
    prev = 0
    for n, lv in enumerate(camp.levels[first:], start=first + 1):
        reach = ceil_div(units(lv.at_items) * BP, base) - BP
        if n > first + 1:
            target = reach - 1 if lv.held else reach
            steps.append((n, None, target - prev))
            prev = target
        if lv.held and lv.lifted_by:
            steps += [(n, card, reach - prev) for card in lv.lifted_by]
            prev = reach
    return steps


def _camp_raise(camp: "CampEntry", bp: int, source: str) -> Modifier:
    return Modifier(StoreCap(StoreId(camp.store)), ModifierKind.ADD_BP, bp, SourceId(source))


def camp_lifts(camp: "CampEntry") -> list[tuple[str, Modifier]]:
    """(card, raise) for each card of each held level's lifted_by: the raise its finish lands (camp_chain)."""
    return [(card, _camp_raise(camp, bp, card)) for _, card, bp in camp_chain(camp) if card is not None]


def _with_lifts(card: CardDef, camp: "CampEntry | None") -> CardDef:
    mods = tuple(m for c, m in camp_lifts(camp) if c == card.id) if camp is not None else ()
    if not mods:
        return card
    return replace(card, finished=replace(card.finished, modifiers=card.finished.modifiers + mods))


def _camp_triggers(camp: "CampEntry | None", cards: set[str]) -> tuple[TriggerDef, ...]:
    if camp is None:
        return ()
    return tuple(
        TriggerDef(camp_trigger_id(n), AtLeast(StoreValue(StoreId(camp.store)), units(lv.at_items), units(lv.at_items)),
                   Outcome(modifiers=tuple(modifier(m, cards) for m in lv.modifiers),
                           lines=tuple(LineKey(k) for k in lv.line_keys)))
        for n, lv in enumerate(camp.levels, start=1) if camp_lands(lv)) + tuple(
        TriggerDef(to_camp_id(n), AtLeast(StoreValue(StoreId(camp.store)), units(below), units(below)),
                   Outcome(modifiers=(_camp_raise(camp, bp, to_camp_id(n)),)))
        for n, card, bp in camp_chain(camp) if card is None for below in [camp.levels[n - 2].at_items])


def amount(a: "ItemAmount") -> Amount:
    """`items` per `every` completions as quantity units; the loader has checked it divides exactly."""
    return Amount(StoreId(a.store), a.items * QUANTITY_SCALE // a.every)


def unlock(u: "UnlockEntry") -> Unlock:
    return Unlock(UnlockKind(u.unlock_kind), u.id)


def _flows(entries: "list[FlowEntry]") -> tuple[Flow, ...]:
    return tuple(_flow(f) for f in entries)


def _flow(f: "FlowEntry") -> Flow:
    """items_per_hour per every_hours hours as a rate; the loader has checked it divides exactly."""
    return Flow(StoreId(f.store), per_hour(f.items_per_hour) // f.every_hours)


def _standing(a: "StandingEntry") -> StandingDef:
    return StandingDef(ActionId(a.id), _flows(a.makes), _flows(a.costs),
                       None if a.skill is None else SkillId(a.skill), per_hour(a.xp_per_hour), _fight(a.fight),
                       _held(a.while_running))


def _held(entries: "list[WhileRunningEntry]") -> tuple[WhileRunning | HeldSpeed, ...]:
    return tuple(_held_one(w) for w in entries)


def _held_one(w: "WhileRunningEntry") -> WhileRunning | HeldSpeed:
    if w.lane is not None:
        return HeldSpeed(LaneId(w.lane), w.amount_bp)
    assert w.side is not None, "WhileRunningEntry names exactly one of side and lane"
    return WhileRunning(SideId(w.side), w.amount_bp)


def _fight(f: "FightEntry | None") -> FightDef | None:
    if f is None:
        return None
    return FightDef(SideId(f.side), ThreatId(f.threat), StoreId(f.lost), None if f.fought is None else StoreId(f.fought),
                    per_hour(f.fights_per_hour), tuple(amount(a) for a in f.loses), tuple(amount(a) for a in f.wounds))


def _card(c: "CardEntry", cards: set[str]) -> CardDef:
    return CardDef(
        id=CardId(c.id), work_s=c.work_s, lane=LaneId(c.lane), skill=None if c.skill is None else SkillId(c.skill),
        xp_per_hour=per_hour(c.xp_per_hour), makes=_flows(c.makes), costs=_flows(c.costs),
        inputs=tuple(amount(a) for a in c.inputs), requires=tuple(condition(x, cards) for x in c.requires),
        outcome=_outcome(c.outcome, cards), cap=c.cap, finished=_outcome(c.finished, cards),
        lines=tuple(LineKey(k) for k in c.line_keys),
        fight=_fight(c.fight),
        glows=c.glows, while_running=_held(c.while_running),
        drains=tuple(amount(a) for a in c.drains))


def _outcome(o: "OutcomeEntry", cards: set[str]) -> Outcome:
    return Outcome(
        stores=tuple(amount(a) for a in o.stores), unlocks=tuple(unlock(u) for u in o.unlocks),
        modifiers=tuple(modifier(m, cards) for m in o.modifiers),
        raises=tuple(CapRaise(CardId(r.card), r.by) for r in o.raises), starts=tuple(CardId(s) for s in o.starts),
        lines=tuple(LineKey(k) for k in o.line_keys),
        orders=tuple(RuleInstall(CardId(i.tap_card), i.first) for i in o.orders), queues=tuple(CardId(q) for q in o.queues),
        joins=tuple(Join(LaneId(j.lane), MixId(j.mix), None if j.card is None else CardId(j.card)) for j in o.joins),
        retire_orders=tuple(CardId(c) for c in o.retire_orders),
        leaves=tuple(Leave(LaneId(x.lane), tuple(ActionId(a) for a in x.stops)) for x in o.leaves))


def _runner(id_: str, cards: set[str]) -> Runner:
    """Standing actions and cards share one id namespace; the opening's card list says which this is."""
    return CardId(id_) if id_ in cards else ActionId(id_)


def _chip(c: "ChipEntry", cards: set[str]) -> ChipDef:
    return ChipDef(
        ChipId(c.id), condition(c.when, cards), tuple(modifier(m, cards) for m in c.effects),
        None if c.on_line_key is None else LineKey(c.on_line_key),
        None if c.off_line_key is None else LineKey(c.off_line_key))


def _trigger(t: "TriggerEntry", cards: set[str]) -> TriggerDef:
    return TriggerDef(TriggerId(t.id), condition(t.when, cards), _outcome(t.outcome, cards),
                      tuple(condition(x, cards) for x in t.requires))


def modifier(m: "ModifierEntry", cards: set[str]) -> Modifier:
    target: Target
    if m.target == "rate":
        assert m.flow is not None
        target = RateRef(_runner(m.id, cards), FlowKind(m.flow), None if m.store is None else StoreId(m.store))
    elif m.target == "work":
        target = WorkRef(CardId(m.id))
    elif m.target == "cap":
        target = StoreCap(StoreId(m.id))
    elif m.target == "side":
        target = SideStrength(SideId(m.id))
    elif m.target == "threat":
        target = ThreatStrength(ThreatId(m.id))
    else:
        target = LaneSpeed(LaneId(HANDS if m.id == HANDS else m.id))
    return Modifier(target, ModifierKind(m.kind), m.amount_bp, SourceId(m.source))


def levels(c: "ConditionEntry") -> tuple[int, int]:
    """(value, release) as the engine reads them: on a store, whole items over `every` in quantity units; on a level,
    count or 0/1, as written. Release defaults to value. Every loader reader of a threshold reads it here; the loader
    has checked a store's divides exactly (refs.py)."""
    release = c.value if c.release is None else c.release
    if c.subject_kind != "store":
        return c.value, release
    return units(c.value) // c.every, units(release) // c.every


def condition(c: "ConditionEntry", cards: set[str]) -> Condition:
    if c.test == "after_time":
        return AfterTime(c.value)
    value, release = levels(c)
    subject = _subject(c, cards)
    return AtLeast(subject, value, release) if c.test == "at_least" else AtMost(subject, value, release)


def _subject(c: "ConditionEntry", cards: set[str]) -> Subject:
    assert c.id is not None
    if c.subject_kind == "store":
        return StoreValue(StoreId(c.id))
    if c.subject_kind == "skill_level":
        return SkillLevel(SkillId(c.id))
    if c.subject_kind == "card_count":
        return CardCount(CardId(c.id))
    if c.subject_kind == "running":
        return Running(_runner(c.id, cards))
    if c.subject_kind == "lane_rules":
        return LaneRules(LaneId(c.id))
    assert c.unlock_kind is not None
    return Unlocked(Unlock(UnlockKind(c.unlock_kind), c.id))
