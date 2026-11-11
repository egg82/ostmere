"""A bounded advance resumes exactly (engine DESIGN.txt, "Bounded advance", invariant 73): the newest golden end save,
advanced three game hours in slices of K instants with encode and decode between them, ends where one unbounded call
does, with the same lines and rule changes in turn."""
from pathlib import Path

from ashfall_app.engine import Line, RuleChange, advance_logged, decode, encode, rebase
from ashfall_app.opening.renames import engine_renames, load_renames
from ashfall_app.opening.schema import Opening, to_rules

GOLDEN = Path(__file__).resolve().parent / "golden"
SPAN_S = 10_800
K = 7


def _end_save() -> Path:
    newest = max(GOLDEN.glob("f*"), key=lambda d: int(d.name[1:]))
    return next(p for p in sorted(newest.glob("*.json")) if "-end" in p.name)


def _every(k: int):
    n = [0]

    def stop() -> bool:
        n[0] += 1
        return n[0] % k == 0

    return stop


def test_slices_with_a_round_trip_between_equal_one_advance(shipped_opening: Opening):
    rules = to_rules(shipped_opening)
    save = rebase(_end_save().read_text().strip(), rules, engine_renames(load_renames()))
    t = save.time + SPAN_S
    whole = advance_logged(save, rules, t)
    lines: list[Line] = []
    changes: list[RuleChange] = []
    slices, stop, text = 0, _every(K), encode(save, rules)
    while True:
        step = advance_logged(decode(text, rules), rules, t, stop)
        slices += 1
        lines += step.lines
        changes += step.rule_changes
        text = encode(step.save, rules)
        if not step.stopped_short:
            break
        assert step.save.time < t
    assert slices > 3   # control: the day really was cut, more than once
    assert any(ln.time < t for ln in lines) and changes   # control: there were lines and rule changes to compare
    assert text == encode(whole.save, rules)
    assert tuple(lines) == whole.lines
    assert tuple(changes) == whole.rule_changes
