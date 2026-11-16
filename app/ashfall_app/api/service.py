"""The game's wire side with no web in it: content from the opening, and the engine's saves and lines as the API's
Steps and Views. The saves themselves are the Saves system's (saves/); routes call this to speak the contract.
"""
from collections.abc import Callable

from .. import engine as e
from ..accounts import codes
from ..opening import convert as authored
from ..opening.goals import goal_defs
from ..opening.eaters import bonus_bp
from ..opening.makers import card_makes, card_takes, made_by
from ..opening.entries import CardEntry, FightEntry, ModifierEntry, OrderCardEntry
from ..opening.feature_entries import FeatureCardEntry
from ..opening.refs import outcomes
from ..opening.stake_checks import reach_modifiers, reach_stops
from ..opening.schema import Opening
from ..saves.interface import Played, Ruleset
from ..saves.journal import ComposedDay
from ..saves.journal_rules import DIARY_HAND, Look
from . import convert
from .goalrows import goal_rows
from .levels import levels
from .ruledry import order_dry
from .goals import goals
from .line_causes import line_infos, offer_cause, worded_stores
from .line_models import PeopleBand, PeopleInfo
from .sources import sources, store_sources
from . import content_models as cm
from . import journal_models as jm
from .limits import MAX_MIXES, MAX_OR_ELSE, MAX_ORDERS, MAX_QUEUE, MAX_UNLESS
from . import models as w


PLAIN = Look(DIARY_HAND, None)
"""How a note is drawn whose slot gives no hand or sketch (a crowd's mention), or whose subject the content dropped."""
FORECAST_S = 6 * 3600
"""How far ahead a view forecasts levels and full stores (CONTRACT.txt, "Forecast"): past it the page draws no time."""


class Game:
    def __init__(self, opening: Opening, rs: Ruleset) -> None:
        self._rs = rs
        self._content = _content(opening, rs.rules, rs.digest)
        self._sources = store_sources(opening)
        self._goals = goal_defs(opening, rs.rules)

    def content(self) -> cm.Content:
        return self._content

    @property
    def content_tag(self) -> str:
        """The ETag of the content: it names the build as well as the rules, since a rewording keeps the digest."""
        return f'"{self._rs.build}-{self._rs.digest}"'

    def verb(self, decision: w.Decision) -> e.Verb:
        return convert.verb(decision, self._rs.rules)

    def view(self, save: e.Save) -> w.View:
        rules = self._rs.rules
        v = e.view(save, rules)
        open_goals = goals(save, rules, v, self._goals)
        return convert.view(save, v, sources(save, rules, v, self._sources), open_goals,
                            goal_rows(save, rules, v, open_goals), order_dry(save, rules, v), levels(save, rules))

    def forecast(self, played: Played, stop: Callable[[], bool]) -> w.ForecastAnswer:
        """The save's forecast from now (it replays hours of the save, so it has its own call: CONTRACT.txt,
        "Forecast")."""
        save, rules = played.save, self._rs.rules
        shown = tuple(e.StoreId(u.id) for u in save.unlocked if u.kind is e.UnlockKind.STORE)
        f = e.forecast(save, rules, save.time + FORECAST_S, shown, stop)
        return w.ForecastAnswer(decisions=played.decisions, forecast=convert.forecast(f))

    def step(self, played: Played) -> w.Step:
        return w.Step(
            save_id=played.save_id, decisions=played.decisions, rules_digest=self._rs.digest, build=self._rs.build,
            view=self.view(played.save),
            lines=[w.LogLine(at=ln.time, seq=ln.seq, key=ln.key, card=ln.card) for ln in played.lines],
            failed_tap=played.failed,
            repeats=w.Repeats(taps=[w.RepeatedTap(card=c, count=n) for c, n in played.repeats.taps],
                              switches=[w.RepeatedSwitch(chip=chip, mix_id=mix, count=n)
                                        for chip, mix, n in played.repeats.switches]),
            rule_runs=[w.RuleRun(order=convert.order(r.order),
                                 starts=r.starts, on_at=r.on_at, on_level=r.on_level, off_at=r.off_at,
                                 off_level=r.off_level, ended=None if r.ended is None else r.ended.value,
                                 made=[cm.Amount(store=st, quantity=n) for st, n in r.made])
                       for r in played.rule_runs],
            catching_up_to=played.catching_up_to, journal_days=self.journal_days(played.days))

    def journal_days(self, days: tuple[ComposedDay, ...]) -> list[jm.JournalDay]:
        """The written ones of `days`, each note in the hand and with the sketch its slot names now."""
        looks = {} if self._rs.journal is None else self._rs.journal.looks
        return [jm.JournalDay(day=d.day, day_notes=[
            jm.DayNote(subject=n.subject, slot=jm.Slot(n.slot), key=n.key, hand=jm.Hand(look.hand), sketch=look.sketch)
            for n in d.notes for look in (looks.get((n.subject, n.slot), PLAIN),)],
            marks=[jm.Mark(k) for k in d.marks]) for d in days if d.notes]


def _fight(f: e.FightDef | None, entry: FightEntry | None) -> cm.FightInfo | None:
    if f is None:
        return None
    return cm.FightInfo(side=f.side, threat=f.threat, loses=[cm.Amount(store=a.store, quantity=a.quantity) for a in f.loses],
                        wounds=[cm.Amount(store=a.store, quantity=a.quantity) for a in f.wounds],
                        won_line_keys=[] if entry is None else list(entry.won_line_keys),
                        lost_line_keys=[] if entry is None else list(entry.lost_line_keys))


def _finds(o: Opening) -> list[cm.FindInfo]:
    return [cm.FindInfo(line_key=t.outcome.found_line_key, store=t.outcome.stores[0].store,
                        quantity=e.units(t.outcome.stores[0].items))
            for t in o.triggers if t.outcome.found_line_key is not None]


def _content(o: Opening, rules: e.Rules, digest: str) -> cm.Content:
    cards = {x.id for x in o.cards}
    card_fights = {c.id: c.fight for c in rules.cards}
    standing_fights = {a.id: a.fight for a in rules.standing}
    replacements = {u.id: u.replaced_by for _, out in outcomes(o) for u in out.unlocks if u.replaced_by is not None}
    return cm.Content(
        rules_digest=digest,
        scales=cm.Scales(quantity_per_item=e.QUANTITY_SCALE, rate_per_item_hour=e.RATE_SCALE, bp=e.BP),
        limits=cm.Limits(max_orders=MAX_ORDERS, max_queue=MAX_QUEUE, max_mixes=MAX_MIXES, max_unless=MAX_UNLESS, max_or_else=MAX_OR_ELSE, reserved_mix_prefix=e.TOWN_PREFIX),
        text_entries=[cm.TextEntry(key=k, text=t) for k, t in o.text.items()],
        store_infos=[cm.StoreInfo(store=s.id, label_key=s.label_key, cap=e.units(s.cap_items), made_by=made_by(o, s.id),
                                  hidden=s.hidden, tally=s.tally, clock=s.clock, bonus_bp=bonus_bp(o, s.id))
                     for s in o.stores],
        side_infos=[cm.SideInfo(side=s.id, label_key=s.label_key) for s in o.sides],
        threat_infos=[cm.ThreatInfo(threat=t.id, label_key=t.label_key) for t in o.threats],
        find_infos=_finds(o),
        standing_infos=[cm.StandingInfo(action=a.id, label_key=a.label_key, skill=a.skill,
                                        fight=_fight(standing_fights.get(e.ActionId(a.id)), a.fight)) for a in o.standing],
        card_infos=[cm.CardInfo(
            card=c.id, lane=c.lane, presentation=cm.CardPresentation(c.presentation), label_key=c.label_key,
            upside_key=c.upside_key, change_bp=[v for v, _ in _card_slots(c, o)], work_s=c.work_s,
            kept=_kept_infos(c, o),
            inputs=[cm.Amount(store=i.store, quantity=authored.amount(i).quantity) for i in c.inputs],
            makes=card_makes(c), takes=card_takes(c), reach=_reach(o, c), drains=[d.store for d in c.drains],
            skill_needs=[cm.SkillNeed(skill=r.id, level=r.value) for r in c.requires
                         if r.subject_kind == "skill_level" and r.test == "at_least" and r.id is not None],
            step_needs=[cm.StepNeed(card=r.id, count=r.value) for r in c.requires
                        if r.subject_kind == "card_count" and r.test == "at_least" and r.id is not None],
            glows=c.glows, fight=_fight(card_fights.get(e.CardId(c.id)), c.fight), replaced_by=replacements.get(c.id))
            for c in o.cards],
        chip_infos=[cm.ChipInfo(chip=c.id, label_key=c.label_key, tone=c.tone,
                               when=convert.condition(authored.condition(c.when, cards)), cost_key=c.cost_key,
                               change_bp=_changes(c.effects),
                               on_line_key=c.on_line_key, off_line_key=c.off_line_key,
                               offered_after=None if c.offered_after is None
                               else convert.unlock(authored.unlock(c.offered_after))) for c in o.chips],
        feature_infos=[cm.FeatureInfo(feature=f.id, hint_key=f.hint_key, label_key=f.label_key,
                                      feature_card=_card(f.card))
                       for f in o.features],
        order_cards=[cm.OrderCard(
            store=c.store, when=convert.condition(authored.condition(c.when, cards)),
            then=_card_verb(c),
            offered_after=None if c.offered_after is None else convert.unlock(authored.unlock(c.offered_after)),
            chip=c.chip, after_end=c.after_end)
            for c in o.order_cards],
        skill_infos=[cm.SkillInfo(skill=s.id, label_key=s.label_key,
                                 levels=[cm.LevelPays(level=lv.level, pays_key=lv.pays_key,
                                                      change_bp=_level_changes(o, s.id, lv.level),
                                                      speeds=_level_speeds(o, s.id, lv.level))
                                         for lv in s.levels])
                     for s in o.skills],
        node_infos=[cm.NodeInfo(node=n.id, skill=n.skill, label_key=n.label_key, change=cm.NodeChange(
            target=cm.NodeTarget(n.changes.target), id=n.changes.id, store=n.changes.store)) for n in o.nodes],
        lane_infos=[cm.LaneInfo(lane=e.HANDS, label_key=o.hands_label_key, ruled=False, later_labels=[], name_key=None,
                                told=None),
                    *(cm.LaneInfo(lane=x.id, label_key=x.label_key, ruled=x.ruled, later_labels=[
                        cm.LaneLabel(after=convert.unlock(authored.unlock(lb.after)), label_key=lb.label_key)
                        for lb in x.later_labels], name_key=x.name_key, told=x.told) for x in o.lanes)],
        offer_infos=_offer_infos(o),
        offer_kinds=[cm.OfferKindInfo(kind=k.kind, roles=[cm.KindRole(role=r.role, label_key=r.label_key) for r in k.roles])
                     for k in o.offer_kinds],
        end_line_keys=list(o.end_line_keys),
        line_infos=line_infos(o),
        journal=_journal(o),
        aim_infos=[cm.AimInfo(aim=a.id, text_key=a.text_key,
                              after=None if a.after is None else convert.unlock(authored.unlock(a.after)))
                   for a in o.aims],
        camp=None if o.camp is None else cm.CampInfo(
            store=o.camp.store, camp_levels=[cm.CampLevel(at=e.units(lv.at_items), pays_key=lv.pays_key, held=lv.held,
                                                        lifted_by=list(lv.lifted_by), pays_from=_units_or_none(lv.pays_from),
                                                        pays_to=_units_or_none(lv.pays_to),
                                                        change_bp=[] if lv.held else _changes(lv.modifiers),
                                                        names=[] if lv.held else _named(lv.modifiers, cards))
                                        for lv in o.camp.levels]),
        people=None if o.people is None else PeopleInfo(
            came=[PeopleBand(at_least=b.at_least, keys=list(b.keys)) for b in o.people.came],
            went=[PeopleBand(at_least=b.at_least, keys=list(b.keys)) for b in o.people.went]),
        first_mix=cm.FirstMix(feature=o.first_mix.feature, card_ids=list(o.first_mix.cards)),
        game_mix_ids=sorted({j.mix for _, out in outcomes(o) for j in out.joins}),
        transfer_code_s=int(codes.LIFETIME.total_seconds()))


def _offer_infos(o: Opening) -> list[cm.OfferInfo]:
    hidden = {s.id for s in o.stores if s.hidden}
    cards, worded = {c.id for c in o.cards}, worded_stores(o)
    return [cm.OfferInfo(offer=x.id, text_key=x.text_key, kind=x.kind, line_keys=list(x.line_keys), askers=list(x.askers),
                         cause=offer_cause(x, cards, worded), waiting_key=x.waiting_key, expiry_key=x.expiry_key,
                         permanence_key=x.permanence_key, answers=[
        cm.AnswerInfo(answer=a.id, label_key=a.label_key, cost_key=a.cost_key, role=a.role,
                      change_bp=_changes(a.outcome.modifiers),
                      gains=[cm.AnswerGain(store=s.store, quantity=e.units(s.items)) for s in a.outcome.stores if s.store not in hidden])
        for a in x.answers]) for x in o.offers]


def _journal(o: Opening) -> cm.JournalInfo | None:
    if o.journal is None:
        return None
    return cm.JournalInfo(feature=o.journal.feature, entries=[
        cm.EntryInfo(entry=x.id, section=cm.Section(x.section), sketch=x.sketch, runners=list(x.runners), notes=[
            cm.NoteInfo(note=n.id, hand=cm.Hand(n.hand or x.hand), sketch=n.sketch) for n in o.notes if n.entry == x.id])
        for x in o.entries])


def _changes(mods: list[ModifierEntry]) -> list[int]:
    """The modifiers' signed changes in basis points (a multiplier of 11000 is +1000, an addition of 5000 is +5000),
    each distinct value once in authored order: what a text's {pct} and {pct_b} slots are filled from."""
    return list(dict.fromkeys(m.amount_bp - (e.BP if m.kind == "mul_bp" else 0) for m in mods))


def _kept_infos(c: CardEntry, o: Opening) -> list[cm.KeptInfo]:
    slots = _card_slots(c, o)
    return [cm.KeptInfo(side=w.side, lane=w.lane, amount_bp=w.amount_bp, slot=slots.index((w.amount_bp, True))) for w in c.while_running]


def _card_slots(c: CardEntry, o: Opening) -> list[tuple[int, bool]]:
    """Its outcome's and finish's changes, then its while_running entries' (each an add_bp on a side or a lane's speed
    at the full share, which the View scales by the card's share now), then those of the standing action it names as
    upside_of, each with whether it is held by the card itself, then, for a reach stake, those its reach pays. A
    distinct (value, held) pair appears once, so a held amount never shares a slot with a change that does not scale."""
    eater = [w for a in o.standing if a.id == c.upside_of for w in a.while_running]
    reach = reach_modifiers(o, c) if c.stake == "reach" else []
    return list(dict.fromkeys([*((v, False) for v in _changes([*c.outcome.modifiers, *c.finished.modifiers])),
                               *((w.amount_bp, True) for w in c.while_running), *((w.amount_bp, False) for w in eater),
                               *((v, False) for v in _changes(reach))]))


def _reach(o: Opening, c: CardEntry) -> cm.ReachInfo | None:
    stops = reach_stops(o, c) if c.stake == "reach" else []
    return cm.ReachInfo(store=stops[0][0], stops=[q for s, q in stops if s == stops[0][0]]) if stops else None


def _level_changes(o: Opening, skill: str, level: int) -> list[int]:
    """The changes of the trigger that lands when `skill` reaches `level`, none when that level pays a find."""
    return _changes(_level_modifiers(o, skill, level))


def _level_modifiers(o: Opening, skill: str, level: int) -> list[ModifierEntry]:
    return [m for t in o.triggers if t.when.test == "at_least" and t.when.subject_kind == "skill_level"
            and t.when.id == skill and t.when.value == level for m in t.outcome.modifiers]


def _level_speeds(o: Opening, skill: str, level: int) -> list[str]:
    """The cards the level's modifiers make faster, in card order: a work entry's card, each card on a lane entry's
    lane."""
    mods = _level_modifiers(o, skill, level)
    works = {m.id for m in mods if m.target == "work"}
    lanes = {m.id for m in mods if m.target == "lane"}
    return [c.id for c in o.cards if c.id in works or c.lane in lanes]


def _named(mods: list[ModifierEntry], cards: set[str]) -> list[w.Unlock]:
    """The cards, standing actions and stores the modifiers name: a rate's runner and store, a work's card, a cap's
    store. A lane's modifier adds nothing: lanes are not unlocked, they show with their cards."""
    found: list[w.Unlock] = []
    for m in mods:
        if m.target in ("rate", "work"):
            found.append(w.Unlock(category=w.UnlockKind.CARD if m.id in cards else w.UnlockKind.ACTION, id=m.id))
        if m.target == "cap":
            found.append(w.Unlock(category=w.UnlockKind.STORE, id=m.id))
        if m.store is not None:
            found.append(w.Unlock(category=w.UnlockKind.STORE, id=m.store))
    return list({(u.category, u.id): u for u in found}.values())


def _card(card: FeatureCardEntry | None) -> cm.FeatureCard | None:
    if card is None:
        return None
    return cm.FeatureCard(title_key=card.title_key, line_keys=list(card.line_keys), button_key=card.button_key)


def _units_or_none(items: int | None) -> int | None:
    return None if items is None else e.units(items)


def _card_verb(c: OrderCardEntry) -> w.OrderVerb:
    if c.tap_card is not None:
        return w.TapCard(card=c.tap_card)
    assert c.switch_mix is not None  # the loader checked exactly one is set
    return w.SwitchMix(mix_id=c.switch_mix)
