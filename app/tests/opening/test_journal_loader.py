"""The journal's loader and unlocks (api/CONTRACT.txt, "JOURNAL", acceptance 1 to 4), on fixtures/journal.toml merged onto
the opening alone, its own journal taken out (bookless.py). Each refusal is the fixture edited to break it, beside the unedited control that loads."""
from collections.abc import Callable
from pathlib import Path

import pytest

from ashfall_app.engine import (
    AtLeast, EntryId, IdKind, NoteId, Rename, Rules, Save, TriggerId, Unlock, Unlocked, UnlockKind, advance, encode,
    new_save, rebase, TriggerDef,
)
from ashfall_app.opening.lock import snapshot
from ashfall_app.opening.lock_checks import problems
from ashfall_app.opening.renames import RenameEntry, engine_renames, load_renames
from ashfall_app.opening.schema import Opening, load_opening, to_rules
from tests.opening.bookless import bookless_opening

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "journal.toml"
TEXT = FIXTURE.read_text()
PAGE_A, PAGE_B = EntryId("j_page_a"), EntryId("j_page_b")
A1, A2, B1 = NoteId("j_note_a1"), NoteId("j_note_a2"), NoteId("j_note_b1")


def written(path: Path, text: str) -> Path:
    path.write_text(text)
    return path


def edited(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = TEXT
    for old, new in edits:
        assert text.count(old) == 1, f"anchor is not unique: {old!r}"
        text = text.replace(old, new)
    return written(tmp_path / FIXTURE.name, text)


def appended(tmp_path: Path, toml: str, words: str = "") -> Path:
    """The fixture with `toml` before its [text] table and `words` (text lines) at its head."""
    return edited(tmp_path, ("\n[text]\n", f"\n{toml}\n[text]\n{words}"))


def load(*paths: Path) -> Opening:
    return load_opening(bookless_opening(), paths)


def rules_of(*paths: Path) -> Rules:
    return to_rules(load(*paths))


def trigger(r: Rules, note: NoteId) -> TriggerDef:
    return next(t for t in r.triggers if t.id == TriggerId(f"note_{note}"))


def unlocked(s: Save, kind: UnlockKind) -> set[str]:
    return {u.id for u in s.unlocked if u.kind is kind}


# ---------- 1: the fixture loads, and the loader makes the triggers ----------

def test_the_fixture_loads_with_the_loader_made_note_triggers():
    r = rules_of(FIXTURE)
    first, later, other = trigger(r, A1), trigger(r, A2), trigger(r, B1)
    assert set(first.outcome.unlocks) == {Unlock(UnlockKind.ENTRY, PAGE_A), Unlock(UnlockKind.NOTE, A1)}
    assert first.requires == ()
    assert set(other.outcome.unlocks) == {Unlock(UnlockKind.ENTRY, PAGE_B), Unlock(UnlockKind.NOTE, B1)}
    assert later.outcome.unlocks == (Unlock(UnlockKind.NOTE, A2),)
    assert later.requires == (AtLeast(Unlocked(Unlock(UnlockKind.ENTRY, PAGE_A)), 1, 1),)
    assert first.outcome.lines == later.outcome.lines == ()


def test_the_notes_are_ordered_and_their_hands_resolved():
    o = load(FIXTURE)
    assert [(n.id, n.hand) for n in o.notes] == [(A1, None), (A2, "pencil"), (B1, None)]
    assert [(e.id, e.hand) for e in o.entries] == [(PAGE_A, "ink"), (PAGE_B, "pencil")]


# ---------- 2: planted, each fails the load naming its ids ----------

def second_chapter(tmp_path: Path, body: str) -> Path:
    return written(tmp_path / "later.toml", f"version = 1\n{body}")


def stray_note(tmp_path: Path) -> tuple[Path, ...]:
    return (appended(tmp_path, '[[notes]]\nid = "j_stray"\nentry = "j_nowhere"\ngate = { test = "after_time", value = 5 }',
                     'j_stray = "No page for me."\n'),)


def note_before_its_entry(tmp_path: Path) -> tuple[Path, ...]:
    early = appended(tmp_path, '[[notes]]\nid = "j_early"\nentry = "j_late"\ngate = { test = "after_time", value = 5 }',
                     'j_early = "Too soon."\n')
    late = second_chapter(tmp_path, '[[entries]]\nid = "j_late"\nsection = "places"\nsketch = "j_sketch_c"\nhand = "ink"\nrunners = []\n'
                          '[[notes]]\nid = "j_late_note"\nentry = "j_late"\ngate = { test = "after_time", value = 6 }\n'
                          '[text]\nj_late_note = "On time."\n')
    return early, late


def entry_without_note(tmp_path: Path) -> tuple[Path, ...]:
    return (appended(tmp_path, '[[entries]]\nid = "j_bare"\nsection = "places"\nsketch = "j_sketch_c"\nhand = "ink"\nrunners = []'),)


def runner_without_fight(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('runners = []', 'runners = ["t_tend"]')),)


def sketch_with_slash(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('sketch = "j_sketch_a"', 'sketch = "../a/b"')),)


def no_book(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('[journal]\nfeature = "book"\n', "")),)


def book_twice(tmp_path: Path) -> tuple[Path, ...]:
    return FIXTURE, second_chapter(tmp_path, '[journal]\nfeature = "book"\n')


def book_without_label(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('feature = "book"', 'feature = "mix"')),)


def note_text_with_digit(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('"A page that is only words."', '"A page of 2 words."')),)


def sketch_of_a_note_with_slash(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('sketch = "j_note_sketch"', 'sketch = "n/s"')),)


DAYS_PAGE = '[[entries]]\nid = "j_day"\nsection = "days"\nhand = "ink"\nrunners = []\n'
"""A days page with no sketch: text alone."""


def days_note(beat: str) -> str:
    return f'[[notes]]\nid = "j_day_1"\nentry = "j_day"\ngate = {{ test = "after_time", value = 50 }}\n{beat}'


def with_days(tmp_path: Path, beat: str) -> tuple[Path, ...]:
    return (appended(tmp_path, DAYS_PAGE + days_note(beat), 'j_day_1 = "Retold."\n'),)


def days_note_without_beat(tmp_path: Path) -> tuple[Path, ...]:
    return with_days(tmp_path, "")


def days_note_with_bad_beat(tmp_path: Path) -> tuple[Path, ...]:
    return with_days(tmp_path, 'beat = "B 5"')


def beat_on_another_section(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('id = "j_note_b1"\n', 'id = "j_note_b1"\nbeat = "B5"\n')),)


def unknown_section(tmp_path: Path) -> tuple[Path, ...]:
    return (edited(tmp_path, ('section = "places"', 'section = "recipes"')),)


PLANTS = [
    (stray_note, ["j_stray", "j_nowhere"]),
    (note_before_its_entry, ["j_early", "j_late"]),
    (entry_without_note, ["j_bare"]),
    (runner_without_fight, ["j_page_b", "t_tend"]),
    (sketch_with_slash, ["j_page_a", "../a/b"]),
    (sketch_of_a_note_with_slash, ["j_note_a2", "n/s"]),
    (no_book, ["j_page_a", "[journal]"]),
    (book_twice, ["[journal]", "twice"]),
    (book_without_label, ["mix", "label_key"]),
    (note_text_with_digit, ["j_note_b1", "digit"]),
    (days_note_without_beat, ["j_day_1", "beat"]),
    (days_note_with_bad_beat, ["j_day_1", "B 5"]),
    (beat_on_another_section, ["j_note_b1", "B5"]),
    (unknown_section, ["section"]),
]


@pytest.mark.parametrize("plant,named", PLANTS, ids=[p.__name__ for p, _ in PLANTS])
def test_each_planted_journal_fault_fails_the_load_naming_its_ids(tmp_path: Path, plant: Callable[[Path], tuple[Path, ...]], named: list[str]):
    with pytest.raises(ValueError) as e:
        load(*plant(tmp_path))
    for word in named:
        assert word in str(e.value), (word, str(e.value))


def test_the_control_without_a_plant_loads():
    assert len(load(FIXTURE).entries) == 2


def test_a_days_page_with_no_sketch_and_a_beat_on_its_note_loads(tmp_path: Path):
    o = load(*with_days(tmp_path, 'beat = "B5"'))
    day = next(e for e in o.entries if e.id == "j_day")
    assert (day.section, day.sketch) == ("days", None)
    assert next(n for n in o.notes if n.id == "j_day_1").beat == "B5"
    assert {e.id: e.section for e in o.entries} == {PAGE_A: "creatures", PAGE_B: "places", "j_day": "days"}


def test_an_authored_outcome_cannot_unlock_an_entry(tmp_path: Path):
    """Only the loader's note triggers write the journal: a card's or trigger's outcome that does is refused."""
    text = TEXT.replace('{ unlock_kind = "feature", id = "combat" }', '{ unlock_kind = "feature", id = "combat" }, '
                        '{ unlock_kind = "entry", id = "j_page_b" }')
    with pytest.raises(ValueError, match="only a note's trigger"):
        load(written(tmp_path / "unlocks_entry.toml", text))


# ---------- 3: the unlocks land as the gates say ----------

def at(r: Rules, t: int) -> Save:
    return advance(new_save(r), r, t)


def test_a_save_reaching_a_first_notes_gate_holds_the_entry_and_note_from_that_instant():
    r = rules_of(FIXTURE)
    assert unlocked(at(r, 199), UnlockKind.ENTRY) == set()
    s = at(r, 200)
    assert unlocked(s, UnlockKind.ENTRY) == {PAGE_A} and A1 in unlocked(s, UnlockKind.NOTE)


def test_a_later_note_whose_gate_holds_first_waits_for_the_entry_then_lands_at_its_instant():
    r = rules_of(FIXTURE)
    early = at(r, 150)   # a2's gate (100) holds; its page does not exist yet
    assert unlocked(early, UnlockKind.NOTE) == set()
    s = at(r, 200)
    assert unlocked(s, UnlockKind.NOTE) == {A1, A2}
    assert unlocked(at(r, 300), UnlockKind.ENTRY) == {PAGE_A, PAGE_B}


# ---------- 4: renames and the release lock ----------

RENAMED = (("j_page_a", "j_leaf_a"), ("j_note_a1", "j_line_a1"))


def renamed_entries() -> list[RenameEntry]:
    pairs = [("entry", "j_page_a", "j_leaf_a"), ("note", "j_note_a1", "j_line_a1")]
    return [RenameEntry.model_validate({"kind": k, "from": a, "to": b}) for k, a, b in pairs]


def test_a_renamed_entry_and_note_carry_their_unlocks_across_a_rebase(tmp_path: Path):
    old = rules_of(FIXTURE)
    s = at(old, 300)
    text = TEXT
    for a, b in RENAMED:
        text = text.replace(a, b)
    new = rules_of(written(tmp_path / "journal.toml", text))
    renames = (*engine_renames(renamed_entries()), Rename(IdKind.TRIGGER, "note_j_note_a1", "note_j_line_a1"))
    got = rebase(encode(s, old), new, renames)
    assert unlocked(got, UnlockKind.ENTRY) == {"j_leaf_a", "j_page_b"}
    assert unlocked(got, UnlockKind.NOTE) == {"j_line_a1", "j_note_a2", "j_note_b1"}


def test_a_note_rename_in_the_file_carries_its_trigger_rename(tmp_path: Path):
    path = written(tmp_path / "renames.toml", '[[renames]]\nkind = "note"\nfrom = "x"\nto = "y"\n')
    assert Rename(IdKind.TRIGGER, "note_x", "note_y") in set(engine_renames(load_renames(path)))


def test_a_released_note_that_goes_needs_its_mapping_and_a_mapped_one_does_not(tmp_path: Path):
    was = snapshot(load(FIXTURE), rules_of(FIXTURE), load_renames())
    gone = edited(tmp_path, ('[[notes]]\nid = "j_note_a2"\nentry = "j_page_a"\ngate = { test = "after_time", value = 100 }\n'
                             'hand = "pencil"\nsketch = "j_note_sketch"\n', ""), ('j_note_a2 = "A later thing, in pencil, with a small drawing."\n', ""))
    now = snapshot(load(gone), rules_of(gone), load_renames())
    ps = problems(was, now, load_renames())
    assert any(p.cls == "needs_mapping" and "note j_note_a2" in p.message for p in ps), ps
    mapped = [*load_renames(), RenameEntry.model_validate({"kind": "note", "from": "j_note_a2", "to": "j_note_b1"})]
    assert not any(p.cls == "needs_mapping" and "note j_note_a2" in p.message for p in problems(was, now, mapped))
