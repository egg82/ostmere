"""An Opening's authoring units (whole items, seconds) to the engine's Rules (fixed point). Pure."""
from dataclasses import replace
from typing import TYPE_CHECKING

from ...engine import (
    HANDS, ActionId, ChainDef, FightDef, WhileRunning, HeldSpeed, SideDef, SideId, ThreatDef, ThreatId, AnswerDef, AnswerId,
    KindId, OfferDef, OfferId, RoleId, Amount, AtLeast, CapRaise, CardDef, CardId, ChipDef, ChipId, FeatureId, Flow,
    LaneDef, LaneId, LineKey, Outcome, PacingCurve, RuleInstall, Rules, SkillDef, SkillId, StandingDef, StoreDef,
    StoreId, StoreValue, TriggerDef, TriggerId, Unlock, Unlocked, UnlockKind,
    per_hour, units,
)
from ...engine.core.units import QUANTITY_SCALE
from . import move_convert
from .condition_convert import condition, modifier
from .tally_convert import tally_triggers
from .camp_convert import camp_chain, camp_raise, lifts_by_card, camp_lands, with_lifts
from ..prestige import node_def, prestige_def

if TYPE_CHECKING:
    from ..entries.camp_entries import CampEntry
    from ..entries.chip_entries import ChipEntry
    from ..entries.entries import (
        CardEntry, FlowEntry, ItemAmount, FightEntry, OutcomeEntry, StandingEntry, TriggerEntry, UnlockEntry,
        WhileRunningEntry,
    )
    from ..entries.offer_entries import OfferEntry
    from ..schema import Opening


def build_rules(o: "Opening") -> Rules:
    cards = {c.id for c in o.cards}
    ruled = {LaneId(x.id) for x in o.lanes if x.ruled and not x.station}
    lifts = lifts_by_card(o.camp)
    return Rules(
        stores=tuple(StoreDef(StoreId(s.id), units(s.cap_items), units(s.initial_items)) for s in o.stores),
        skills=tuple(SkillDef(SkillId(s.id)) for s in o.skills),
        standing=tuple(_standing(a) for a in o.standing),
        sides=tuple(SideDef(SideId(s.id), s.base) for s in o.sides),
        threats=tuple(ThreatDef(ThreatId(t.id), t.base, t.members) for t in o.threats),
        curve=PacingCurve(tuple(units(n) for n in o.curve_items)),
        lanes=tuple(LaneDef(LaneId(x.id), x.ruled, x.pooled, None if x.group is None else LaneId(x.group)) for x in o.lanes),
        cards=tuple(_with_camp(with_lifts(_card(c, cards), lifts), o.camp, ruled) for c in o.cards),
        chips=tuple(_chip(c, cards) for c in o.chips),
        triggers=tuple(_trigger(t, cards) for t in o.triggers) + _camp_triggers(o.camp, cards)
        + tuple(_offer_trigger(x, cards) for x in o.offers) + _note_triggers(o, cards) + tally_triggers(o),
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


def to_camp_id(n: int) -> TriggerId:
    """The trigger that raises the camp cap for Camp level n (1-based) once level n - 1 lands."""
    return TriggerId(f"to_camp_{n}")


def _camp_triggers(camp: "CampEntry | None", cards: set[str]) -> tuple[TriggerDef, ...]:
    if camp is None:
        return ()
    return tuple(
        TriggerDef(camp_trigger_id(n), AtLeast(StoreValue(StoreId(camp.store)), units(lv.at_items), units(lv.at_items)),
                   Outcome(modifiers=tuple(modifier(m, cards) for m in lv.modifiers),
                           lines=tuple(LineKey(k) for k in lv.line_keys)))
        for n, lv in enumerate(camp.levels, start=1) if camp_lands(lv)) + tuple(
        TriggerDef(to_camp_id(n), AtLeast(StoreValue(StoreId(camp.store)), units(below), units(below)),
                   Outcome(modifiers=(camp_raise(camp, bp, to_camp_id(n)),)))
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
                    per_hour(f.fights_per_hour), tuple(amount(a) for a in f.loses), tuple(amount(a) for a in f.wounds),
                    None if f.chained is None else StoreId(f.chained))


def _card(c: "CardEntry", cards: set[str]) -> CardDef:
    return CardDef(
        id=CardId(c.id), work_s=c.work_s, lane=LaneId(c.lane), skill=None if c.skill is None else SkillId(c.skill),
        xp_per_hour=per_hour(c.xp_per_hour), makes=_flows(c.makes), costs=_flows(c.costs),
        inputs=tuple(amount(a) for a in c.inputs), requires=tuple(condition(x, cards) for x in c.requires),
        outcome=_outcome(c.outcome, cards), cap=c.cap, finished=_outcome(c.finished, cards),
        lines=tuple(LineKey(k) for k in c.line_keys),
        fight=_fight(c.fight),
        chain=None if c.chain is None else ChainDef(ActionId(c.chain.runner), c.chain.reach,
                                                    tuple(LineKey(k) for k in c.chain.link_line_keys)),
        glows=c.glows, while_running=_held(c.while_running),
        drains=tuple(amount(a) for a in c.drains))


def _outcome(o: "OutcomeEntry", cards: set[str]) -> Outcome:
    return Outcome(
        stores=tuple(amount(a) for a in o.stores), unlocks=tuple(unlock(u) for u in o.unlocks),
        modifiers=tuple(modifier(m, cards) for m in o.modifiers),
        raises=tuple(CapRaise(CardId(r.card), r.by) for r in o.raises), starts=tuple(CardId(s) for s in o.starts),
        lines=tuple(LineKey(k) for k in o.line_keys),
        orders=tuple(RuleInstall(CardId(i.tap_card), i.first) for i in o.orders), queues=tuple(CardId(q) for q in o.queues),
        joins=move_convert.joins(o.joins), marks=move_convert.marks(o.marks),
        retire_orders=tuple(CardId(c) for c in o.retire_orders), leaves=move_convert.leaves(o.leaves),
        casts=move_convert.casts(o.casts))


def _chip(c: "ChipEntry", cards: set[str]) -> ChipDef:
    return ChipDef(
        ChipId(c.id), condition(c.when, cards), tuple(modifier(m, cards) for m in c.effects),
        None if c.on_line_key is None else LineKey(c.on_line_key),
        tuple(LineKey(k) for k in c.off_line_keys))


def _trigger(t: "TriggerEntry", cards: set[str]) -> TriggerDef:
    return TriggerDef(TriggerId(t.id), condition(t.when, cards), _outcome(t.outcome, cards),
                      tuple(condition(x, cards) for x in t.requires))
