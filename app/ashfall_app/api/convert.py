"""The engine's types to the wire models (a View, a Step) and the wire decisions back to engine verbs.

Both directions are plain field copies: no rule lives here. Names are qualified (`e.` engine, `w.` wire) because the two
sides share most of them.
"""
from collections.abc import Iterable, Mapping, Sequence

from .. import engine as e
from . import models as w
from .sources import Source


def segment(s: e.Segment) -> w.Segment:
    return w.Segment(start=s.start, start_value=s.start_value, rate=s.rate, limit=s.limit)


def unlock(u: e.Unlock) -> w.Unlock:
    return w.Unlock(category=w.UnlockKind(u.kind.value), id=u.id)


def subject(s: e.Subject) -> w.Subject:
    match s:
        case e.StoreValue():
            return w.StoreValue(store=s.store)
        case e.SkillLevel():
            return w.SkillLevel(skill=s.skill)
        case e.CardCount():
            return w.CardCount(card=s.card)
        case e.Unlocked():
            return w.Unlocked(unlock=unlock(s.unlock))
        case e.Running():
            return w.Running(runner=s.runner)
        case e.LaneRules():
            raise ValueError("a lane-rules condition is only a trigger's, never in a save")


def condition(c: e.Condition) -> w.Condition:
    match c:
        case e.AfterTime():
            return w.AfterTime(at=c.time)
        case e.AtLeast():
            return w.AtLeast(watched=subject(c.subject), value=c.value, release=c.release)
        case e.AtMost():
            return w.AtMost(watched=subject(c.subject), value=c.value, release=c.release)


def order_verb(v: e.OrderVerb) -> w.OrderVerb:
    if isinstance(v, e.TapCard):
        return w.TapCard(card=v.card)
    if isinstance(v, e.AnswerOffer):
        return w.AnswerOffer(offer=v.offer, answer=v.answer)
    if isinstance(v, e.AnswerKind):
        return w.AnswerKind(offer_kind=v.kind, role=v.role)
    return w.SwitchMix(mix_id=v.mix)


def mix(m: e.Mix) -> w.Mix:
    parts: list[w.CardShare | w.SubMix] = [
        w.CardShare(card=c.card, share_bp=c.share_bp) if isinstance(c, e.CardShare)
        else w.SubMix(mix_id=c.mix, share_bp=c.share_bp) for c in m.components]
    return w.Mix(id=m.id, components=parts)


def _blocker(b: e.Blocker | None) -> w.Blocker | None:
    return None if b is None else w.Blocker(condition=condition(b.condition), ready_at=b.ready_at)


def _ledger(lines: Iterable[e.LedgerLine]) -> list[w.LedgerLine]:
    return [w.LedgerLine(
        store=ln.store, segment=segment(ln.segment), net_per_hour=ln.net_per_hour,
        contributions=[w.Contribution(runner=c.runner, per_hour=c.per_hour) for c in ln.contributions],
        empties_at=ln.empties_at, fills_at=ln.fills_at, falling=ln.falling, covered=ln.covered, starved=ln.starved,
        cap=ln.cap)
        for ln in lines]


def _lanes(lanes: Iterable[e.LaneBar]) -> list[w.LaneBar]:
    return [w.LaneBar(
        lane=b.lane, running_card=b.card, completes_at=b.completes_at, order=b.order) for b in lanes]


def _need(card: str, n: e.Need, sources: Mapping[tuple[str, str], Source]) -> w.Need:
    src = sources.get((card, str(n.store)))
    return w.Need(store=n.store, quantity=n.quantity, segment=segment(n.segment),
                  gate=None if src is None or src.gate is None else condition(src.gate),
                  makers=[] if src is None else list(src.makers), spent=src is not None and src.spent)


def _cards(cards: Iterable[e.CardView], sources: Mapping[tuple[str, str], Source]) -> list[w.Card]:
    return [w.Card(
        card=c.card, completions=c.completions, cap=c.cap, bar=segment(c.bar), bar_total=c.bar_total,
        by=None if c.by is None else w.RunBy(c.by.value), completes_at=c.completes_at, share_bp=c.share_bp,
        run=None if c.run is None else w.RunKind(c.run.value), blocker=_blocker(c.blocker), tap_s=c.tap_s,
        needs=[_need(c.card, n, sources) for n in c.needs], cuts_in=c.cuts_in,
        spent_store=c.spent_store, gained=[w.SpentShare(card=g.card, share_bp=g.share_bp) for g in c.gained])
        for c in cards]


def _entry(m: e.Modifier, held: dict[str, int]) -> w.StrengthEntry:
    """A held entry is served under its card's id with the card's share; any other keeps its source and no share."""
    card = str(m.source).removeprefix(e.HELD_PREFIX)
    if str(m.source).startswith(e.HELD_PREFIX) and card in held:
        return w.StrengthEntry(source=card, form=w.StrengthKind(m.kind.value), amount_bp=m.amount_bp, share_bp=held[card])
    return w.StrengthEntry(source=m.source, form=w.StrengthKind(m.kind.value), amount_bp=m.amount_bp, share_bp=None)


def _strength(x: e.StrengthExplanation, held: dict[str, int]) -> w.Strength:
    sources = [w.StrengthEntry(source=None, form=w.StrengthKind.BASE, amount_bp=x.base, share_bp=None),
               *(_entry(m, held) for m in (*x.adds, *x.muls))]
    return w.Strength(value=x.value, sources=sources)


def _fights(fights: Iterable[e.FightView], held: Iterable[e.HeldView]) -> list[w.Fight]:
    shares = {str(h.card): h.share_bp for h in held}
    return [w.Fight(runner=f.runner, side=f.side, threat=f.threat, power=_strength(f.power, shares),
                    threat_strength=_strength(f.threat_strength, shares), loss_bp=f.loss_bp, fought=f.fought,
                    lost=f.lost)
            for f in fights]


def view(save: e.Save, v: e.View, sources: Mapping[tuple[str, str], Source] | None = None,
         goals: Sequence[w.Goal] = (), goal_rows: Sequence[w.GoalRow] = (),
         order_dry: Sequence[w.RuleDry | None] = ()) -> w.View:
    """The wire View of an engine View; the player's plan (mixes, orders, queue) is read off the save, where each
    card's needs come from (api/sources.py), the goals (api/goals.py) and their rows (api/goalrows.py) passed in."""
    return w.View(
        at=v.time, next_event_at=None if v.next_event is None else v.next_event.time, ledger=_ledger(v.ledger),
        skills=[w.SkillBar(skill=s.skill, xp=segment(s.xp), level=s.level, level_xp=s.level_xp,
                           next_level_xp=s.next_level_xp, next_level_at=s.next_level_at,
                           prestige=None if s.prestige is None else _prestige(s.prestige)) for s in v.skills],
        standing=[w.StandingBar(action=a.action, run=w.RunKind(a.run.value)) for a in v.standing],
        lanes=_lanes(v.lanes), cards=_cards(v.cards, sources or {}),
        completed=[w.CompletedCard(card=c.card, completions=c.completions) for c in v.completed],
        greyed_mix_ids=list(v.greyed_mixes),
        chips=list(v.chips), chips_seen=list(v.chips_seen), unlocked=[unlock(u) for u in v.unlocked], all_covered=v.all_covered,
        ended_at=v.ended_at,
        runs_out_at=v.runs_out_at,
        mixes=[mix(m) for m in save.mixes], active_mix_id=save.active, running_mix_id=v.running_mix,
        mix_order=v.mix_order,
        running_town_mix_id=v.running_town_mix, town_mix_order=v.town_mix_order, orders_on=list(v.orders_on),
        order_states=[w.OrderState(s.value) for s in v.order_states],
        order_dry=list(order_dry) or [None] * len(save.orders),
        orders=[w.Order(when=condition(o.when), then=order_verb(o.then)) for o in save.orders],
        queue=[w.QueueEntry(verb=order_verb(q.verb), until=condition(q.until)) for q in save.queue],
        offers=[w.Offer(offer=o.offer, answer=o.answer,
                        answers=[w.OfferAnswer(answer=a.answer, card=a.card, takes_s=a.takes_s) for a in o.answers])
                for o in v.offers],
        fights=_fights(v.fights, v.held), goals=list(goals), goal_rows=list(goal_rows))


def _prestige(p: e.SkillPhase) -> w.SkillPrestige:
    return w.SkillPrestige(
        phase=p.phase, level_counted=p.level_counted, at_top=p.at_top, waiting_levels=p.waiting_levels,
        menu_nodes=[w.MenuNode(node=n.node, ranks_taken=n.ranks_taken, ranks=n.ranks, before_value=n.before_value,
                               after_value=n.after_value) for n in p.menu],
        undo_open=p.undo_open, mastered=p.mastered, pick_owed=p.pick_owed, topped_at=p.topped_at,
        picked=[str(n) for n in p.picked], parked=[w.ParkedPick(node=k.node, due=k.due) for k in p.parked])


def forecast(f: e.Forecast) -> w.Forecast:
    return w.Forecast(horizon_at=f.until,
                      level_ups=[w.ForecastLevel(skill=k, at=t) for k, ts in f.level_ups.items() for t in ts],
                      tops_out=[w.ForecastTop(skill=k, at=t) for k, t in f.tops_out.items()],
                      fills=[w.ForecastFull(store=k, at=t) for k, ts in f.fills.items() for t in ts],
                      empties=[w.ForecastEmpty(store=k, at=t) for k, ts in f.empties.items() for t in ts])


# ---------- wire to engine ----------

def from_subject(s: w.Subject, rules: e.Rules) -> e.Subject:
    match s:
        case w.StoreValue():
            return e.StoreValue(e.StoreId(s.store))
        case w.SkillLevel():
            return e.SkillLevel(e.SkillId(s.skill))
        case w.CardCount():
            return e.CardCount(e.CardId(s.card))
        case w.Unlocked():
            return e.Unlocked(e.Unlock(e.UnlockKind(s.unlock.category.value), s.unlock.id))
        case w.Running():
            return e.Running(_runner(s.runner, rules))


def from_condition(c: w.Condition, rules: e.Rules) -> e.Condition:
    match c:
        case w.AfterTime():
            return e.AfterTime(c.at)
        case w.AtLeast():
            return e.AtLeast(from_subject(c.watched, rules), c.value, c.release)
        case w.AtMost():
            return e.AtMost(from_subject(c.watched, rules), c.value, c.release)


def from_order_verb(v: w.OrderVerb) -> e.OrderVerb:
    if isinstance(v, w.TapCard):
        return e.TapCard(e.CardId(v.card))
    if isinstance(v, w.AnswerOffer):
        return e.AnswerOffer(e.OfferId(v.offer), e.AnswerId(v.answer))
    if isinstance(v, w.AnswerKind):
        return e.AnswerKind(e.KindId(v.offer_kind), e.RoleId(v.role))
    return e.SwitchMix(e.MixId(v.mix_id))


def from_mix(m: w.Mix) -> e.Mix:
    parts: tuple[e.CardShare | e.SubMix, ...] = tuple(
        e.CardShare(e.CardId(c.card), c.share_bp) if isinstance(c, w.CardShare)
        else e.SubMix(e.MixId(c.mix_id), c.share_bp) for c in m.components)
    return e.Mix(e.MixId(m.id), parts)


def verb(d: w.Decision, rules: e.Rules) -> e.Verb:
    match d:
        case w.TapCard():
            return e.TapCard(e.CardId(d.card))
        case w.SwitchMix():
            return e.SwitchMix(e.MixId(d.mix_id))
        case w.SaveMix():
            return e.SaveMix(from_mix(d.mix))
        case w.DeleteMix():
            return e.DeleteMix(e.MixId(d.mix_id))
        case w.SetOrders():
            return e.SetOrders(tuple(e.Order(_page_built(o.when, rules), from_order_verb(o.then)) for o in d.orders))
        case w.SetQueue():
            return e.SetQueue(tuple(e.QueueEntry(from_order_verb(q.verb), _page_built(q.until, rules))
                                    for q in d.entries))
        case w.AnswerOffer():
            return e.AnswerOffer(e.OfferId(d.offer), e.AnswerId(d.answer))
        case w.Prestige():
            return e.Prestige(e.SkillId(d.skill), e.NodeId(d.node))
        case w.UndoPick():
            return e.UndoPick(e.SkillId(d.skill))
        case w.MovePick():
            return e.MovePick(e.SkillId(d.skill), e.NodeId(d.node), e.NodeId(d.to))


def _page_built(c: w.Condition, rules: e.Rules) -> e.Condition:
    """An order's or queue entry's condition: a Running subject is refused (CONTRACT.txt, "Decisions"). The page
    never builds one, and an order that watches what its own switch stops would flip at every instant."""
    if not isinstance(c, w.AfterTime) and isinstance(c.watched, w.Running):
        raise e.InvalidVerbError("an order or queue condition cannot watch whether something is running")
    return from_condition(c, rules)


def _runner(runner: str, rules: e.Rules) -> e.Runner:
    """A wire runner id as the engine's Runner: a CardId when rules.cards has it, else an ActionId (one namespace)."""
    return e.CardId(runner) if any(c.id == runner for c in rules.cards) else e.ActionId(runner)
