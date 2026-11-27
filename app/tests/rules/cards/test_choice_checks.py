"""The check that no lane offers a job another job on it beats outright (rules/checks/cards/choice_checks.py): structural fields
only, a card retired in its beater's favour (`replaced_by`) excepted."""
import pytest

from ashfall_app.rules.checks.cards.choice_checks import beaten_pairs, beats, check_choices, compared_pairs
from ashfall_app.rules.entries.entries import ItemAmount, UnlockEntry
from ashfall_app.rules.schema import Opening
from tests.rules.play.playthrough import opening


def card(o: Opening, cid: str):
    return next(c for c in o.cards if c.id == cid)


def without_retirement(o: Opening, retired: str) -> Opening:
    """`o` with the unlock that retires `retired` taken out of whichever trigger holds it."""
    def kept(us: list[UnlockEntry]) -> list[UnlockEntry]:
        return [u for u in us if not (u.unlock_kind == "retired" and u.id == retired)]
    triggers = [t.model_copy(update={"outcome": t.outcome.model_copy(update={"unlocks": kept(t.outcome.unlocks)})})
                for t in o.triggers]
    cards = [c.model_copy(update={"finished": c.finished.model_copy(update={"unlocks": kept(c.finished.unlocks)})})
             for c in o.cards]
    return o.model_copy(update={"triggers": triggers, "cards": cards})


def test_the_shipped_content_offers_no_beaten_job_and_the_check_compared_every_lane():
    o = opening()
    pairs = compared_pairs(o)
    lanes = {a.lane for a, _ in pairs}
    assert len(pairs) > 100 and {"hands", "n1", "n2", "n3", "n5", "n6", "n7"} <= lanes
    assert beaten_pairs(o) == []
    check_choices(o)


@pytest.mark.parametrize("retired, beater", [
    ("n1_gather", "n1_cut"), ("n2_gather", "n2_cut"), ("n5_gather", "n5_cut"),
    ("n6_gather", "n6_cut"), ("n7_gather", "n7_cut"),
])
def test_a_beaten_job_left_in_play_is_refused_naming_both_cards(retired: str, beater: str):
    """Each pair is beaten outright and is spared only by its retirement: without it the check fails."""
    o = without_retirement(opening(), retired)
    assert beats(card(o, beater), card(o, retired))
    with pytest.raises(ValueError, match=f"card {retired}: is beaten outright by {beater}"):
        check_choices(o)


@pytest.mark.parametrize("field, value", [
    ("work_s", 6),
    ("inputs", [ItemAmount(store="stones", items=1)]),
    ("requires", "copied"),
    ("skill", "woodcutting"),
    ("outcome", "less"),
])
def test_one_field_against_the_beater_makes_it_a_choice(field: str, value: object):
    """woodcutting over gathering by hand on the hands, with one field turned against woodcutting: slower, an input
    gathering does not take, a requirement it does not wait on, its XP taken by gathering, or less wood."""
    o = opening()
    wood, gather = card(o, "woodcutting"), card(o, "gather_wood")
    assert beats(wood, gather)
    if value == "copied":
        value = card(o, "make_stool").requires
    if field == "skill":
        gather = gather.model_copy(update={"skill": "woodcutting", "xp_per_hour": wood.xp_per_hour + 1})
    elif value == "less":
        more = [ItemAmount(store=s.store, items=s.items * 3) for s in gather.outcome.stores]
        gather = gather.model_copy(update={"outcome": gather.outcome.model_copy(update={"stores": more})})
    else:
        wood = wood.model_copy(update={field: value})
    assert not beats(wood, gather)
