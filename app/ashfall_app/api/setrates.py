"""Rates of the setup as set: the engine's own running shares and lines (engine/rates.py) with a tap of the hands set
aside, so the hands' mix runs at its shares (CONTRACT.txt, "Goal rows"). A tap ends in minutes; a goal is hours out,
and a dry run of a mix edit made while a tap runs would otherwise move nothing. A hold keeps the run it had with the
tap in place."""
from fractions import Fraction

from ..engine.ids import HANDS, ActionId, CardId, Runner, SkillId, StoreId
from ..engine.index import index
from ..engine.mixruns import mix_entries
from ..engine.modifiers import FlowKind, RateRef, Run, RunKind
from ..engine.rates import Running, exact_contribution, exact_net, line, running, tapped_cards
from ..engine.rules import Rules
from ..engine.sides import makes
from ..engine.state import Save

_DRY = frozenset({RunKind.PAUSED, RunKind.SPENT})


def as_set(save: Save, rules: Rules) -> Running:
    """running(save) with the hands' tap set aside: the tapped card out, the hands' mix cards at their effective shares,
    a card yielded to the tap running in full, in running order (a mixed card that was tapped back in its mix place)."""
    now = running(save, rules)
    ix = index(rules)
    taps = {c for c in tapped_cards(save, rules) if ix.cards[c].lane == HANDS}
    if not taps:
        return now
    mixed = {card: (share, Run(RunKind.FULL) if run.kind is RunKind.YIELDED else run)
             for card, share, run in mix_entries(save, rules)}
    standing = [r for r in now.shares if r not in ix.cards]
    rest = [r for r in now.shares if r in ix.cards and r not in taps and r not in mixed]
    shares = {r: now.shares[r] for r in standing} | {c: s for c, (s, _) in mixed.items()} | {r: now.shares[r] for r in rest}
    runs = {r: now.runs[r] for r in standing} | {c: run for c, (_, run) in mixed.items()} | {r: now.runs[r] for r in rest}
    return Running(shares, runs, now.gained)


def skill_of(rules: Rules, runner: Runner) -> SkillId | None:
    ix = index(rules)
    card = ix.cards.get(CardId(runner))
    return card.skill if card is not None else ix.standing[ActionId(runner)].skill


def xp_per_hour(save: Save, rules: Rules, now: Running, skill: SkillId) -> int:
    """XP per hour (rate units) the skill gains from every runner of `now` that trains it."""
    return sum(line(save, rules, RateRef(r, FlowKind.XP), s, now.runs[r]).per_hour
               for r, s in now.shares.items() if skill_of(rules, r) == skill)


def net_per_hour(save: Save, rules: Rules, now: Running, store: StoreId) -> int:
    """The store's net per hour (rate units), unclamped, rounded down."""
    return int(exact_net(save, rules, now, store) // 1)


def in_per_hour(save: Save, rules: Rules, now: Running, store: StoreId) -> int:
    """What comes into the store per hour (rate units): its makers' lines alone."""
    made = sum((c for r, s in now.shares.items()
                if (c := exact_contribution(save, rules, r, store, s, now.runs[r])) > 0), Fraction(0))
    return int(made // 1)


def movers(rules: Rules, now: Running, store: StoreId | None, skill: SkillId | None) -> list[Runner]:
    """The runners of `now` that make `store`, or train `skill`, in running order."""
    if store is not None:
        return [r for r in now.shares if store in makes(rules, r)]
    return [r for r in now.shares if skill_of(rules, r) == skill]


def dry_input(now: Running, runners: list[Runner], shown: frozenset[StoreId]) -> StoreId | None:
    """The first store of `shown` one of `runners` waits on, dry (paused or spent on it), in `runners`' order, which
    is running order (standing actions, then the hands' mix in flattened card order, then the town's). A standing
    action paused on a store the ledger never draws (a clock's) names nothing."""
    return next((run.store for r in runners if (run := now.runs[r]).kind in _DRY and run.store in shown), None)
