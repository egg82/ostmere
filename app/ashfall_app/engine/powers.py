"""A side's or a threat's strength now: its base under the entries aimed at it (DESIGN.txt, "FIGHTS")."""
from .gates import base_stack
from .modifiers import SideStrength, ThreatStrength
from .rules import Rules
from .state import Save
from .strengthmath import StrengthExplanation, explain_over


def explain_strength(save: Save, rules: Rules, target: SideStrength | ThreatStrength) -> StrengthExplanation:
    """The strength of an id the rules declare, with every entry behind it. The odds entries aim at rates, never at a
    strength, so the stack without them gives the same answer."""
    return explain_over(base_stack(save, rules), rules, target)


def strength(save: Save, rules: Rules, target: SideStrength | ThreatStrength) -> int:
    return explain_strength(save, rules, target).value
