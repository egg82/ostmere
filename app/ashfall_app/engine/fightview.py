"""The read model's fights: one FightView per unlocked fight runner (DESIGN.txt, "FIGHTS", "View")."""
from dataclasses import dataclass

from .counts import completions
from .gates import base_stack, is_unlocked
from .gone import is_left, stopped
from .ids import Runner, SideId, StoreId, ThreatId
from .modifiers import SideStrength, ThreatStrength
from .motion import store_segment
from .cards import FightDef
from .odds import kept_loss_bp, loss_bp
from .rules import Rules
from .state import Save
from .strengthmath import StrengthExplanation, explain_over
from .units import QUANTITY_SCALE
from .unlocks import Unlock, UnlockKind


@dataclass(frozen=True)
class FightView:
    """One unlocked fight runner now. power and threat_strength: the two strengths with every entry behind them.
    loss_bp: the share of fights lost now; for a running tap, the share it started at and pays to its end. fought and
    lost: whole fights since the runner first ran (the tally stores, floored; a card's fought is its completions)."""

    runner: Runner
    side: SideId
    threat: ThreatId
    power: StrengthExplanation
    threat_strength: StrengthExplanation
    loss_bp: int
    fought: int
    lost: int


def fight_views(save: Save, rules: Rules) -> tuple[FightView, ...]:
    """Unlocked fight cards in rules order, then unlocked fight standing actions in rules order, leaving out a card
    whose person has left and a standing action their leaving stopped."""
    cards = [(c.id, c.fight, completions(save, rules, c.id)) for c in rules.cards
             if c.fight is not None and is_unlocked(save, rules, Unlock(UnlockKind.CARD, c.id)) and not is_left(save, c.lane)]
    gone = stopped(save, rules)
    standing = [(a.id, a.fight, _tally(save, rules, a.fight)) for a in rules.standing
                if a.fight is not None and is_unlocked(save, rules, Unlock(UnlockKind.ACTION, a.id)) and a.id not in gone]
    return tuple(_fight_view(save, rules, r, f, fought) for r, f, fought in (*cards, *standing))


def _tally(save: Save, rules: Rules, f: FightDef) -> int:
    return 0 if f.fought is None else _count(save, rules, f.fought)


def _count(save: Save, rules: Rules, store: StoreId) -> int:
    return store_segment(save, rules, store).start_value // QUANTITY_SCALE


def _fight_view(save: Save, rules: Rules, runner: Runner, f: FightDef, fought: int) -> FightView:
    stack = base_stack(save, rules)
    kept = kept_loss_bp(save, runner, f)
    return FightView(runner, f.side, f.threat, explain_over(stack, rules, SideStrength(f.side)),
                     explain_over(stack, rules, ThreatStrength(f.threat)),
                     kept if kept is not None else loss_bp(f, stack, rules), fought, _count(save, rules, f.lost))
