"""The pauses a change of the running mixes re-decides (engine/design/, "Running dry")."""
from dataclasses import replace

from . import plan
from .ids import CardId, StoreId
from .mixes import flatten_shares
from .rebuild import rebuild
from .rules import Rules
from .sides import costs, makes
from .state import Save


def with_running_mix(before: Save, rules: Rules, after: Save) -> Save:
    """`after`, with its pauses re-decided (re_paused) and rates rebuilt if its running mix is not `before`'s, else as
    given."""
    if (plan.running_mix_id(after, rules), plan.running_town_mix_id(after, rules)) == (
            plan.running_mix_id(before, rules), plan.running_town_mix_id(before, rules)):
        return after
    return re_paused(before, rules, after)


def re_paused(before: Save, rules: Rules, after: Save) -> Save:
    """`after` rebuilt with the pauses a change of the running mixes can move cleared: those on a store a card of
    `before`'s or `after`'s running mixes makes or costs (the dry rule pauses again at once where it is still dry).
    Any other pause stands until its RESUME."""
    moved = _moved(before, rules) | _moved(after, rules)
    return rebuild(replace(after, pauses=tuple(p for p in after.pauses if p.store not in moved)), rules)


def _moved(save: Save, rules: Rules) -> set[StoreId]:
    """The stores a card of the save's running mixes makes or costs."""
    mixes = {plan.running_mix_id(save, rules), plan.running_town_mix_id(save, rules)}
    cards: set[CardId] = {s.card for m in mixes if m is not None for s in flatten_shares(save.mixes, m)}
    return {st for card in cards for st in makes(rules, card) | costs(rules, card)}


def unpaused_candidate(before: Save, after: Save, rules: Rules) -> bool:
    """A change of the running mix cleared the Pause of a card a true order or the queue head would tap (engine/design/,
    "Running dry"): that card turned ready at this instant, so READY falls here and evaluation runs, as it would at the
    Pause's own resume. Without it the card waits for the next unrelated instant, which a player acting on every timer
    reaches sooner (the 2 AM test)."""
    cleared = {p.runner for p in before.pauses} - {p.runner for p in after.pauses}
    return bool(cleared & set(plan.candidates(after, rules)))
