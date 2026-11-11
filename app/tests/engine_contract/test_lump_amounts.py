"""A lump's amount depends on the entries aimed at its own line alone (lumps.lump_amount): a stack that changes on
another line leaves it as it was, without working it out again; one aimed at the line changes it."""
import pytest

from ashfall_app.engine import Modifier, ModifierKind, SourceId, new_save
from ashfall_app.engine import lumps
from ashfall_app.engine.modifiers import Explanation, FlowKind, RateRef, Run, WorkRef
from ashfall_app.engine.units import BP, QUANTITY_SCALE as Q
from tests.engine_contract.test_lumps_by_work_contract import A, Y, lump, world

LINE = RateRef(A, FlowKind.MAKE, Y)


def amount(mods: tuple[Modifier, ...]) -> int:
    r = world(lump(7, items=3))
    return lumps.lump_amount(new_save(r, mods), r, r.cards[0], LINE)


def aimed(kind: ModifierKind, bp: int, target: RateRef | WorkRef) -> Modifier:
    return Modifier(target, kind, bp, SourceId("t"))


def test_an_entry_aimed_at_the_line_changes_the_amount():
    assert amount(()) == 3 * Q
    assert amount((aimed(ModifierKind.MUL_BP, 2 * BP, LINE),)) == 6 * Q


def test_a_stack_changing_on_another_line_does_not_work_the_amount_out_again(monkeypatch: pytest.MonkeyPatch):
    r = world(lump(7, items=3))
    first = new_save(r, (aimed(ModifierKind.MUL_BP, 3 * BP // 2, WorkRef(A)),))
    worked: list[RateRef] = []
    real = lumps.modified_rate

    def counting(ref: RateRef, base: int, share_bp: int, stack: tuple[Modifier, ...], run: Run) -> Explanation:
        worked.append(ref)
        return real(ref, base, share_bp, stack, run)
    monkeypatch.setattr(lumps, "modified_rate", counting)
    second = new_save(r, (aimed(ModifierKind.MUL_BP, 2 * BP, WorkRef(A)),))   # building a save reads its amounts
    assert first.modifiers != second.modifiers    # control: the stack did change
    assert lumps.lump_amount(second, r, r.cards[0], LINE) == 3 * Q
    assert worked == []
