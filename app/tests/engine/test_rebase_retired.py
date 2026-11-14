"""A retired trigger (DESIGN.txt, "Renames", "Rebase" step 4): a save whose rules declared a trigger the new rules have
retired rebases, keeping everything that trigger's outcome landed; without the retirement it raises as any missing id
does, and a retirement of a trigger the new rules still declare changes nothing."""
import pytest

from ashfall_app.engine import IdKind, RebaseError, Rename, Retired, TriggerId, encode, rebase
from tests.engine.test_rebase_impl import played, world


def test_a_save_that_fired_a_retired_trigger_rebases_keeping_what_it_landed():
    r, r2 = world(extra_trigger=True), world()
    s = played(r)
    assert s.fired[[t.id for t in r.triggers].index(TriggerId("t_new"))]   # control: the trigger fired
    with pytest.raises(RebaseError) as e:
        rebase(encode(s, r), r2)
    assert (e.value.kind, e.value.id) == (IdKind.TRIGGER, "t_new")
    got = rebase(encode(s, r), r2, (Retired(TriggerId("t_new")),))
    assert got.fired == (s.fired[[t.id for t in r.triggers].index(TriggerId("t_wood"))],)
    assert set(s.unlocked) <= set(got.unlocked) and got.time == s.time
    assert [st.segment.start_value for st in got.stores] == [st.segment.start_value for st in s.stores]


def test_a_retirement_follows_the_renames():
    r, r2 = world(extra_trigger=True), world()
    renames = (Rename(IdKind.TRIGGER, "t_new", "t_newer"), Retired(TriggerId("t_newer")))
    assert rebase(encode(played(r), r), r2, renames).time == played(r).time


def test_a_retirement_of_a_trigger_still_declared_changes_nothing():
    r, r2 = world(), world(extra_trigger=True)
    s = played(r)
    plain, retired = rebase(encode(s, r), r2), rebase(encode(s, r), r2, (Retired(TriggerId("t_wood")),))
    assert retired == plain and retired.fired[0] == s.fired[0]
