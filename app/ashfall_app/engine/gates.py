"""What the unlock set and the chips let through: who may run, be seen, or change a rate. Reads only; DESIGN.txt,
"Unlocks", "Chips" and "Store caps". work.py exposes the same functions to the rest of the engine."""
from math import prod

from .heldentries import held_entries, held_part, holders
from .ids import CardId, ChipId, StoreId
from .index import index
from .memo import PartsMemo, SaveMemo
from .pickentries import pick_entries
from .odds import has_fights, is_odds, kept_speeds, odds_entries, odds_source
from .modifiers import LaneSpeed, Modifier, ModifierKind, StoreCap, WorkRef
from .rules import Rules
from .state import Save
from .unlocked import is_unlocked
from .unlocks import Unlock, UnlockKind
from .units import BP


_STACK: SaveMemo[tuple[Modifier, ...]] = SaveMemo()
_INPUTS: SaveMemo[tuple[object, ...]] = SaveMemo(4)
"""stack_inputs by save: asked a dozen times of one save (every line, cap and term), and the lanes scan costs most."""
_CAPS: PartsMemo[dict[StoreId, list[Modifier]]] = PartsMemo()
_CAP_OF: PartsMemo[dict[StoreId, int]] = PartsMemo()


def _cap_entries(entries: tuple[Modifier, ...]) -> dict[StoreId, list[Modifier]]:
    out: dict[StoreId, list[Modifier]] = {}
    for m in entries:
        if isinstance(m.target, StoreCap):
            out.setdefault(m.target.store, []).append(m)
    return out


def shown_chips(save: Save, rules: Rules) -> tuple[ChipId, ...]:
    """Chips unlocked and latched, in rules.chips order."""
    return tuple(c.id for c, on in zip(rules.chips, save.chips)
                 if on and is_unlocked(save, rules, Unlock(UnlockKind.CHIP, c.id)))


def chip_modifiers(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    shown = set(shown_chips(save, rules))
    return tuple(m for c in rules.chips if c.id in shown for m in c.effects)


def base_stack(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    """The save's modifiers, the shown chips', the held entries of the cards that run, then the prestige picks'
    entries: everything but the fights' odds entries."""
    return save.modifiers + chip_modifiers(save, rules) + held_entries(save, rules) + pick_entries(save, rules)


def effective_stack(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    return _STACK.get(save, rules, lambda: _with_odds(save, rules))


def _with_odds(save: Save, rules: Rules) -> tuple[Modifier, ...]:
    base = base_stack(save, rules)
    return base + odds_entries(save, rules, base) if has_fights(rules) else base


def tap_speed(save: Save, rules: Rules, card: CardId) -> tuple[Modifier, ...]:
    """The effective stack's entries a tap of `card` started now runs at to its end: those aimed at its lane's
    LaneSpeed or its WorkRef, in the stack's order (LaneState.speed)."""
    aims = (LaneSpeed(index(rules).cards[card].lane), WorkRef(card))
    return tuple(m for m in effective_stack(save, rules)
                 if m.target in aims or (is_odds(m) and m.source == odds_source(card)))


def stack_inputs(save: Save, rules: Rules) -> tuple[object, ...]:
    """All that effective_stack reads but the chips' latches, for a PartsMemo of what is built from the stack alone,
    which takes save.chips as its `same`: each change of a latch is a new tuple, equal to one an advance that flips a
    chip on and off has seen before. The fights' odds entries read the lanes only through the speeds a tap kept
    (odds.kept_speeds), so a tap that starts or lands no fight leaves the parts as they were. When a card declares
    while_running the stack also reads the lanes' taps and the running mixes: the held entries stand for that state
    (heldentries.held_part). With prestige set it reads the picks' entries too, one object while the picks are
    unchanged (pickentries.pick_entries)."""
    return _INPUTS.get(save, rules, lambda: (rules, save.modifiers, save.unlocked, *kept_speeds(save, rules),
                                             *((held_part(save, rules),) if holders(rules) else ()),
                                             *((pick_entries(save, rules),) if rules.prestige is not None else ())))


def store_cap(save: Save, rules: Rules, store: StoreId) -> int:
    """The store's cap now: StoreDef.cap under the entries aimed at StoreCap(store), as modified_rate combines them
    (adds summed, muls multiplied in), rounded down. Only the save's stack and the prestige picks' entries aim at a cap,
    never a chip, so each cap is kept while the rules, the save's stack and the picks' entries are the same objects."""
    picked = pick_entries(save, rules)
    kept = _CAP_OF.get((rules, save.modifiers, picked), dict)
    cap = kept.get(store)
    if cap is None:
        cap = kept[store] = _store_cap(save, rules, store, picked)
    return cap


def _store_cap(save: Save, rules: Rules, store: StoreId, picked: tuple[Modifier, ...]) -> int:
    base = index(rules).stores[store].cap
    aimed = _CAPS.get((save.modifiers, picked), lambda: _cap_entries(save.modifiers + picked)).get(store, [])
    if not aimed:
        return base
    muls = [m.amount_bp for m in aimed if m.kind is ModifierKind.MUL_BP]
    add_factor = max(0, BP + sum(m.amount_bp for m in aimed if m.kind is ModifierKind.ADD_BP))
    return base * add_factor * prod(muls) // BP ** (1 + len(muls))

