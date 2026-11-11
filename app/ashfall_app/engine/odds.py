"""A fight runner's odds as stack entries (DESIGN.txt, "FIGHTS", "The odds entries"): derived from the strengths wherever
the effective stack is read, never stored, except in a HANDS tap's LaneState.speed, which keeps what it started at."""
from .cards import FightDef
from .fightlines import ODDS_PREFIX, fight_costs, fight_makes
from .ids import CardId, Runner, SourceId
from .index import derived
from .modifiers import FlowKind, Modifier, ModifierKind, RateRef, SideStrength, ThreatStrength
from .rules import Rules
from .state import Save
from .strengthmath import explain_over
from .units import BP, ceil_div


def odds_source(runner: Runner) -> SourceId:
    return SourceId(f"{ODDS_PREFIX}{runner}")


def is_odds(m: Modifier) -> bool:
    return str(m.source).startswith(ODDS_PREFIX)


def loss_bp(fight: FightDef, stack: tuple[Modifier, ...], rules: Rules) -> int:
    """The share of fights lost, rounded up so the odds never favour the player: ceil(BP * T / (T + P))."""
    p = explain_over(stack, rules, SideStrength(fight.side)).value
    t = explain_over(stack, rules, ThreatStrength(fight.threat)).value
    return ceil_div(BP * t, t + p)


def _fighters(rules: Rules) -> tuple[tuple[Runner, FightDef, tuple[RateRef, ...], tuple[RateRef, ...]], ...]:
    """Each fight runner with the lines a win pays (its ordinary makes) and the lines a loss charges, in rules order."""
    found: list[tuple[Runner, FightDef, tuple[RateRef, ...], tuple[RateRef, ...]]] = []
    for a in rules.standing:
        if a.fight is not None:
            wins = tuple(RateRef(a.id, FlowKind.MAKE, f.store) for f in a.makes)
            found.append((a.id, a.fight, wins, _losses(a.id, a.fight)))
    for c in rules.cards:
        if c.fight is not None:
            wins = (*(RateRef(c.id, FlowKind.MAKE, f.store) for f in c.makes),
                    *(RateRef(c.id, FlowKind.MAKE, x.store) for x in c.outcome.stores))
            found.append((c.id, c.fight, wins, _losses(c.id, c.fight)))
    return tuple(found)


def _losses(runner: Runner, f: FightDef) -> tuple[RateRef, ...]:
    return (*(RateRef(runner, FlowKind.COST, x.store) for x in fight_costs(f)),
            *(RateRef(runner, FlowKind.MAKE, x.store) for x in fight_makes(f) if x.store != f.fought))


def has_fights(rules: Rules) -> bool:
    return bool(derived(rules, "_fighters", _fighters))


def _kept(save: Save, runner: Runner) -> tuple[Modifier, ...]:
    """The odds entries a HANDS tap of `runner` kept from its start (empty when it is not tapped)."""
    for ls in save.lanes:
        if ls.card == CardId(runner) and ls.speed is not None:
            return tuple(m for m in ls.speed if is_odds(m) and m.source == odds_source(runner))
    return ()


def kept_speeds(save: Save, rules: Rules) -> tuple[object, ...]:
    """What `_kept` reads of the lanes, as parts for a PartsMemo: per fight runner, in rules order, the speed tuple its
    HANDS tap holds (the very object, so it is the same until the tap ends) or None. A lane change that touches none of
    them leaves the odds entries, and so the stack, as they were."""
    return tuple(next((ls.speed for ls in save.lanes if ls.card == CardId(runner) and ls.speed is not None), None)
                 for runner, *_ in derived(rules, "_fighters", _fighters))


def kept_loss_bp(save: Save, runner: Runner, fight: FightDef) -> int | None:
    """The loss_bp a HANDS tap of `runner` started at (read off its kept entry on the lost tally's make line), else None."""
    lost = RateRef(runner, FlowKind.MAKE, fight.lost)
    return next((m.amount_bp for m in _kept(save, runner) if m.target == lost), None)


def odds_entries(save: Save, rules: Rules, stack: tuple[Modifier, ...]) -> tuple[Modifier, ...]:
    """The MUL_BP entries every fight runner's lines carry now: win_bp on what a win brings, loss_bp on what a loss
    costs. `stack` is the effective stack without them."""
    out: list[Modifier] = []
    for runner, fight, wins, losses in derived(rules, "_fighters", _fighters):
        kept = _kept(save, runner)
        if kept:
            out.extend(kept)
            continue
        lose = loss_bp(fight, stack, rules)
        out.extend(Modifier(ref, ModifierKind.MUL_BP, BP - lose, odds_source(runner)) for ref in wins)
        out.extend(Modifier(ref, ModifierKind.MUL_BP, lose, odds_source(runner)) for ref in losses)
    return tuple(out)
