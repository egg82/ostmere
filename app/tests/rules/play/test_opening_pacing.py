"""The opening's drip (docs/decisions.md, "The opening is fun first"): either craft first reaches the end, and tapping
extra early never reaches the end sooner than its steps. The one check on gates and repeated taps is test_tap_gates.py.
How the opening moves (effort between new things, runs of taps, what a day away opens, how the crafts show) is its
readout (report.py), never a threshold."""
import pytest

from ashfall_app.engine import CardId, TapCard, UnlockKind, advance_logged, decide_logged
from tests.rules.play.playthrough import CRAFTS, Player
from tests.rules.play.routes import EagerForager

pytestmark = pytest.mark.playthrough

# ---------- the choice ----------

def test_either_craft_first_reaches_the_end(typical: Player, fireback_first: Player):
    for p, craft in ((typical, CRAFTS[0]), (fireback_first, CRAFTS[1])):
        built = [v.card for _, _, v in p.decisions if isinstance(v, TapCard) and v.card in CRAFTS]
        assert built[0] == craft and set(built) == set(CRAFTS)


ORDER_LINES = {CRAFTS[0]: "l_stool_first", CRAFTS[1]: "l_fireback_first"}
CRAFT_LINES = {CRAFTS[0]: "l_stool", CRAFTS[1]: "l_fireback"}
"""The line on what the player built first, as reading by the fire starts with the other not built."""


def test_the_craft_built_first_gets_its_line_once_as_reading_starts(typical: Player, fireback_first: Player):
    for p, craft in ((typical, CRAFTS[0]), (fireback_first, CRAFTS[1])):
        keys: list[str] = [ln.key for ln in p.lines]
        assert [k for k in keys if k in ORDER_LINES.values()] == [ORDER_LINES[craft]]
        read = next(t for t, _, v in p.decisions if isinstance(v, TapCard) and v.card == "read_by_fire")
        assert next(ln.time for ln in p.lines if ln.key == ORDER_LINES[craft]) == read
        assert keys.index(CRAFT_LINES[craft]) < keys.index(ORDER_LINES[craft])
        assert keys.index(ORDER_LINES[craft]) < keys.index("l_read")


def test_both_crafts_built_before_reading_get_neither_line(typical: Player):
    p = typical.at(lambda q: q.completed(CRAFTS[0]))
    s, r, lines = p.save, p.rules, list[str]()
    for card in (CRAFTS[1], "read_by_fire"):
        tapped = decide_logged(s, r, s.time, TapCard(CardId(card)))
        step = advance_logged(tapped.save, r, s.time + 30)
        s, lines = step.save, lines + [ln.key for ln in (*tapped.lines, *step.lines)]
    assert "l_read" in lines and not set(lines) & set(ORDER_LINES.values())


# ---------- tapping ahead ----------

def test_tapping_extra_early_cannot_reach_the_end_before_its_steps(eager_forager: EagerForager):
    p = eager_forager   # routes.EagerForager: forages by hand to a full store whenever foraging is open
    forage = p.card("forage")
    assert forage is not None and forage.completions >= 6   # the probe did forage extra (by hand and by its rule)
    assert p.end_at is not None and all(p.completed(c) for c in (*CRAFTS, "roast_roots"))
    assert p.has(UnlockKind.FEATURE, "keeps_going")
