"""The ceiling on what the Town view asks the player to tune (opening/groups.py, check_town_managed; docs/decisions/people.md,
"The mark: who keeps their own split"), on the shipped chapters: the control loads, and each plant, content that leaves a
newcomer with a bar of their own, goes over the ceiling and is named."""
import pytest

from ashfall_app.opening.checks import check_structure
from ashfall_app.opening.groups import TOWN_MANAGED_MAX, town_managed
from ashfall_app.opening.schema import Opening


def without_marks(o: Opening, *triggers: str) -> Opening:
    assert set(triggers) <= {t.id for t in o.triggers}, triggers
    return o.model_copy(update={"triggers": [t.model_copy(update={"outcome": t.outcome.model_copy(update={"marks": []})})
                                             if t.id in triggers else t for t in o.triggers]})


def marked_join(o: Opening, trigger: str) -> Opening:
    """`trigger`'s joins, each on the person's own forage card and keeping their own split."""
    assert trigger in {t.id for t in o.triggers}, trigger
    return o.model_copy(update={"triggers": [
        t.model_copy(update={"outcome": t.outcome.model_copy(update={"joins": [
            j.model_copy(update={"own_split": True, "card": f"{j.lane}_forage"}) for j in t.outcome.joins]})})
        if t.id == trigger else t for t in o.triggers]})


def test_the_shipped_content_holds_at_most_the_ceiling(shipped_opening: Opening):
    check_structure(shipped_opening)
    own, groups = town_managed(shipped_opening)
    assert own and groups and len(own) + len(groups) <= TOWN_MANAGED_MAX


@pytest.mark.parametrize(("withheld", "owned", "named"), [
    (("t_family_groups",), None, ["n5", "n6", "n7"]),
    (("t_choir_groups_beds", "t_choir_groups_road"), None, ["n8", "n9", "n10"]),
    (("t_cutter_groups_beds", "t_cutter_groups_road"), None, ["n12"]),
    ((), "t_b19", ["n13"]),
], ids=["day eleven's family", "day eighteen's three", "day eighteen's sister", "day twenty-two's stranger"])
def test_a_newcomer_left_with_a_bar_goes_over_the_ceiling_and_is_named(shipped_opening: Opening, withheld: tuple[str, ...],
                                                                       owned: str | None, named: list[str]):
    planted = without_marks(shipped_opening, *withheld) if withheld else marked_join(shipped_opening, owned or "")
    with pytest.raises(ValueError, match=r"the town: \d+ things to manage") as e:
        check_structure(planted)
    assert all(lane in str(e.value) for lane in named)
