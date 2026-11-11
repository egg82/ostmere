"""A strength over a given stack: the formula alone, below gates, so the odds entries can be built from it."""
from dataclasses import dataclass
from math import prod

from .modifiers import Modifier, ModifierKind, SideStrength, ThreatStrength
from .rules import Rules
from .units import BP


@dataclass(frozen=True)
class StrengthExplanation:
    """Why a strength is this number: the formula's inputs, so a reader recomputes `value` exactly. adds and muls hold
    every entry aimed at `target` in stack order with its source kept (chips' effects included)."""

    target: SideStrength | ThreatStrength
    base: int
    adds: tuple[Modifier, ...]
    muls: tuple[Modifier, ...]
    value: int
    """base * max(0, BP + sum(add_bp)) * prod(mul_bp) // BP ** (1 + len(muls)), rounded down once."""


def explain_over(stack: tuple[Modifier, ...], rules: Rules, target: SideStrength | ThreatStrength) -> StrengthExplanation:
    """The strength of an id the rules declare, under the entries of `stack` aimed at it."""
    if isinstance(target, SideStrength):
        base = next(s.base for s in rules.sides if s.id == target.side)
    else:
        base = next(t.base for t in rules.threats if t.id == target.threat)
    aimed = [m for m in stack if m.target == target]
    adds = tuple(m for m in aimed if m.kind is ModifierKind.ADD_BP)
    muls = tuple(m for m in aimed if m.kind is ModifierKind.MUL_BP)
    add_factor = max(0, BP + sum(m.amount_bp for m in adds))
    value = base * add_factor * prod(m.amount_bp for m in muls) // BP ** (1 + len(muls))
    return StrengthExplanation(target, base, adds, muls, value)
