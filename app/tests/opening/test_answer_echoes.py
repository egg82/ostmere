"""An answer's echo is one authored field (`echo` on an answer) that the loader expands (opening/echoes.py): a line that
refers back to the offer and a lasting modifier named for the answer, a set number of game hours after the answer."""
from dataclasses import replace

import pytest

from ashfall_app.engine import SECONDS_PER_HOUR, Unlock, UnlockKind, advance, encode, new_save, rebase
from ashfall_app.opening.clocks import with_moment_clocks
from ashfall_app.opening.echoes import with_answer_echoes
from ashfall_app.opening.offer_entries import AnswerEntry
from ashfall_app.opening.schema import Opening, to_rules


def echoed(o: Opening) -> list[AnswerEntry]:
    found = [a for x in o.offers for a in x.answers if a.echo is not None]
    assert len(found) > 10, "found almost no echoes: the check is blind"
    return found


def unexpanded(o: Opening) -> Opening:
    """`o` as the chapters author it: no echo trigger, and no clock store or action behind one."""
    clocks = {f"echo_{a.id}_clock" for a in echoed(o)}
    return o.model_copy(update={
        "triggers": [t for t in o.triggers if not t.id.startswith("t_echo_")],
        "stores": [s for s in o.stores if s.id not in clocks], "standing": [s for s in o.standing if s.id not in clocks],
        "offers": [x.model_copy(update={"answers": [a.model_copy(update={"outcome": a.outcome}) for a in x.answers]})
                   for x in o.offers],
    })


def test_every_echo_is_two_triggers_and_expanding_twice_changes_nothing(shipped_opening: Opening):
    ids = [t.id for t in shipped_opening.triggers]
    for a in echoed(shipped_opening):
        assert f"t_echo_{a.id}_start" in ids and f"t_echo_{a.id}" in ids
    again = with_answer_echoes(shipped_opening)
    assert [t.id for t in again.triggers] == ids


def test_the_loader_makes_what_the_field_names(shipped_opening: Opening):
    o = with_moment_clocks(with_answer_echoes(unexpanded(shipped_opening)))
    by_id = {t.id: t for t in o.triggers}
    for a in echoed(shipped_opening):
        e = a.echo
        assert e is not None
        late = by_id[f"t_echo_{a.id}"]
        assert late.when.id == f"echo_{a.id}_clock" and late.when.value == e.after_h * 20
        assert late.outcome.line_keys == [e.line_key] and late.outcome.modifiers == [e.modifier]
        assert any(u.id == f"echo_{a.id}_clock" for u in by_id[f"t_echo_{a.id}_start"].outcome.unlocks)


def test_an_echo_modifier_must_name_its_answer(shipped_opening: Opening):
    o = unexpanded(shipped_opening)
    one = echoed(o)[0]
    assert one.echo is not None
    wrong = one.model_copy(update={"echo": one.echo.model_copy(update={"modifier": one.echo.modifier.model_copy(update={"source": "someone_else"})})})
    offers = [x.model_copy(update={"answers": [wrong if a.id == one.id else a for a in x.answers]}) for x in o.offers]
    with pytest.raises(ValueError, match="not the answer"):
        with_answer_echoes(o.model_copy(update={"offers": offers}))


def test_the_echo_lands_after_its_hours_and_not_before_and_a_save_that_answered_before_gets_it(shipped_opening: Opening):
    rules = to_rules(shipped_opening)
    for a in echoed(shipped_opening):
        e = a.echo
        assert e is not None
        s = new_save(rules)
        s = rebase(encode(replace(s, unlocked=(*s.unlocked, Unlock(UnlockKind.ANSWER, a.id))), rules), rules)
        start = s.time
        def landed(t: int) -> bool:
            return any(str(m.source) == a.id for m in advance(s, rules, t).modifiers)
        assert not landed(start + e.after_h * SECONDS_PER_HOUR - 600), a.id
        assert landed(start + e.after_h * SECONDS_PER_HOUR + SECONDS_PER_HOUR), a.id
