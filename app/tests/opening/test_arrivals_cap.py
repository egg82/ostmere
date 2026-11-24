"""A raised cap on a count store (docs/design/week-four-plan.md, item 9), on fixtures/arrivals_cap.toml merged onto the
opening alone: a turn's outcome carries a sourced x2 cap entry on the arrivals' count, so an arrival past the base cap
counts and a gate past it fires; the loader's cap reading (offer_caps.offer_cap) sees the raised cap once the turn is
unlocked, and the count is never drawn. Each control is the fixture without the entry, or a reader of the base cap."""
from pathlib import Path

from ashfall_app.engine import QUANTITY_SCALE as Q, Rules, Save, StoreId, Unlock, UnlockKind, advance, new_save, view
from ashfall_app.opening.entries import UnlockEntry
from ashfall_app.opening.offer_caps import offer_cap
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "arrivals_cap.toml"
ARRIVALS, STORE = StoreId("t_arrivals"), "t_arrivals"
FIVE = Unlock(UnlockKind.FEATURE, "t_five")
TURNED = UnlockEntry(unlock_kind="feature", id="t_turned")
ENTRY = ', modifiers = [{ target = "cap", id = "t_arrivals", kind = "mul_bp", amount_bp = 20000, source = "t_turn" }]'


def loaded(tmp_path: Path, without_entry: bool = False) -> Opening:
    text = FIXTURE.read_text()
    if without_entry:
        assert text.count(ENTRY) == 1
        text = text.replace(ENTRY, "")
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return load_opening(OPENING, (path,))


def count(s: Save) -> int:
    return next(st.segment.start_value for st in s.stores if st.store == ARRIVALS) // Q


def reaches(o: Opening, value: int, base_only: bool = False) -> bool:
    """Whether a gate at `value` on the count can be met once the turn is unlocked: by the cap the store has then, or
    (the planted reader) by the store's own."""
    cap = next(s.cap_items for s in o.stores if s.id == STORE) if base_only else offer_cap(o, STORE, TURNED)
    return value <= cap


def test_the_arrival_past_the_base_cap_counts_and_the_gate_past_it_fires(tmp_path: Path):
    r = to_rules(loaded(tmp_path))
    assert [count(advance(new_save(r), r, t)) for t in (300, 400, 500, 600)] == [3, 3, 4, 5]
    assert FIVE not in advance(new_save(r), r, 599).unlocked and FIVE in advance(new_save(r), r, 600).unlocked


def test_without_the_entry_the_count_stops_at_the_base_cap_and_the_gate_never_fires(tmp_path: Path):
    r = to_rules(loaded(tmp_path, without_entry=True))
    s = advance(new_save(r), r, 1000)
    assert count(s) == 3 and FIVE not in s.unlocked


def test_the_loaders_cap_reading_is_the_raised_one(tmp_path: Path):
    assert offer_cap(loaded(tmp_path), STORE, TURNED) == 6 and offer_cap(loaded(tmp_path), STORE, None) == 3
    assert reaches(loaded(tmp_path), 5)


def test_a_reader_of_the_base_cap_flags_the_gate_and_the_entryless_content_flags_it_too(tmp_path: Path):
    assert not reaches(loaded(tmp_path), 5, base_only=True)
    assert not reaches(loaded(tmp_path, without_entry=True), 5)


def test_nothing_draws_the_count(tmp_path: Path):
    r: Rules = to_rules(loaded(tmp_path))
    s = advance(new_save(r), r, 600)
    assert count(s) == 5 and ARRIVALS not in [line.store for line in view(s, r).ledger]
