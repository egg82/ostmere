"""The game's wire side with no web in it: content from the opening, and the engine's saves and lines as the API's
Steps and Views. The saves themselves are the Saves system's (saves/); routes call this to speak the contract.
"""
from collections.abc import Callable

from .. import engine as e
from ..accounts import codes
from ..opening import convert as authored
from ..opening.goals import goal_defs
from ..opening.eaters import bonus_bp
from ..opening.makers import made_by
from ..opening.entries import CardEntry, FightEntry, ModifierEntry, OrderCardEntry
from ..opening.feature_entries import FeatureCardEntry
from ..opening.refs import outcomes
from ..opening.schema import Opening
from ..saves.interface import Played, Ruleset
from . import convert
from .goalrows import goal_rows
from .ruledry import order_dry
from .goals import goals
from .line_causes import line_infos, offer_cause
from .sources import sources, store_sources
from . import content_models as cm
from .limits import MAX_MIXES, MAX_ORDERS, MAX_QUEUE
from . import models as w


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
                            goal_rows(save, rules, v, open_goals), order_dry(save, rules, v))

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
            rule_runs=[w.RuleRun(order=w.Order(when=convert.condition(r.order.when), then=convert.order_verb(r.order.then)),
                                 starts=r.starts, on_at=r.on_at, on_level=r.on_level, off_at=r.off_at,
                                 off_level=r.off_level, ended=None if r.ended is None else r.ended.value,
                                 made=[cm.Amount(store=st, quantity=n) for st, n in r.made])
                       for r in played.rule_runs],
            catching_up_to=played.catching_up_to)


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
        limits=cm.Limits(max_orders=MAX_ORDERS, max_queue=MAX_QUEUE, max_mixes=MAX_MIXES),
        text_entries=[cm.TextEntry(key=k, text=t) for k, t in o.text.items()],
        store_infos=[cm.StoreInfo(store=s.id, label_key=s.label_key, cap=e.units(s.cap_items), made_by=made_by(o, s.id),
                                  hidden=s.hidden, bonus_bp=bonus_bp(o, s.id))
                     for s in o.stores],
        side_infos=[cm.SideInfo(side=s.id, label_key=s.label_key) for s in o.sides],
        threat_infos=[cm.ThreatInfo(threat=t.id, label_key=t.label_key) for t in o.threats],
        find_infos=_finds(o),
        standing_infos=[cm.StandingInfo(action=a.id, label_key=a.label_key, skill=a.skill,
                                        fight=_fight(standing_fights.get(e.ActionId(a.id)), a.fight)) for a in o.standing],
        card_infos=[cm.CardInfo(
            card=c.id, lane=c.lane, presentation=cm.CardPresentation(c.presentation), label_key=c.label_key,
            upside_key=c.upside_key, change_bp=_card_changes(c, o), work_s=c.work_s,
            inputs=[cm.Amount(store=i.store, quantity=authored.amount(i).quantity) for i in c.inputs],
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
                                 levels=[cm.LevelPays(level=lv.level, pays_key=lv.pays_key, change_bp=_level_changes(o, s.id, lv.level))
                                         for lv in s.levels])
                     for s in o.skills],
        node_infos=[cm.NodeInfo(node=n.id, skill=n.skill, label_key=n.label_key, change=cm.NodeChange(
            target=cm.NodeTarget(n.changes.target), id=n.changes.id, store=n.changes.store)) for n in o.nodes],
        lane_infos=[cm.LaneInfo(lane=e.HANDS, label_key=o.hands_label_key, ruled=False, later_labels=[], name_key=None),
                    *(cm.LaneInfo(lane=x.id, label_key=x.label_key, ruled=x.ruled, later_labels=[
                        cm.LaneLabel(after=convert.unlock(authored.unlock(lb.after)), label_key=lb.label_key)
                        for lb in x.later_labels], name_key=x.name_key) for x in o.lanes)],
        offer_infos=_offer_infos(o),
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
        first_mix=cm.FirstMix(feature=o.first_mix.feature, card_ids=list(o.first_mix.cards)),
        transfer_code_s=int(codes.LIFETIME.total_seconds()))


def _offer_infos(o: Opening) -> list[cm.OfferInfo]:
    hidden = {s.id for s in o.stores if s.hidden}
    cards = {c.id for c in o.cards}
    return [cm.OfferInfo(offer=x.id, text_key=x.text_key, kind=x.kind, line_keys=list(x.line_keys), askers=list(x.askers),
                         cause=offer_cause(x, cards, hidden), waiting_key=x.waiting_key, expiry_key=x.expiry_key,
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


def _card_changes(c: CardEntry, o: Opening) -> list[int]:
    """Its outcome's and finish's changes, then its while_running entries' (each an add_bp on a side or a lane's speed
    at the full share, which the View scales by the card's share now), then those of the standing action it names as
    upside_of."""
    eater = [w for a in o.standing if a.id == c.upside_of for w in a.while_running]
    return list(dict.fromkeys([*_changes([*c.outcome.modifiers, *c.finished.modifiers]),
                               *(w.amount_bp for w in (*c.while_running, *eater))]))


def _level_changes(o: Opening, skill: str, level: int) -> list[int]:
    """The changes of the trigger that lands when `skill` reaches `level`, none when that level pays a find."""
    return _changes([m for t in o.triggers if t.when.test == "at_least" and t.when.subject_kind == "skill_level"
                     and t.when.id == skill and t.when.value == level for m in t.outcome.modifiers])


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
