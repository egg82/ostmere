"""The town's shown name grows with the story (api/contract/the-towns-mix.txt, "The town's mix"): a chapter's town_later_labels are
served on the content, and each names an unlock and a text key the content has."""
import pytest

from ashfall_app.api.service import Game
from ashfall_app.rules.checks.run import check_opening
from ashfall_app.rules.entries.entries import UnlockEntry
from ashfall_app.rules.entries.lane_entries import LaneLabelEntry
from ashfall_app.rules.schema import Opening
from ashfall_app.saves.ruleset import ruleset


def labelled(o: Opening, label: LaneLabelEntry) -> Opening:
    return o.model_copy(update={"town_later_labels": [*o.town_later_labels, label]})


def test_the_town_is_named_once_the_first_families_have_come_and_the_content_serves_it(shipped_opening: Opening):
    o = shipped_opening
    assert [(x.after.unlock_kind, x.after.id, o.text[x.label_key]) for x in o.town_later_labels] == [("feature", "family_joined", "Town")]
    served = Game(o, ruleset(o, "test", 1)).content().town_later_labels
    assert [(x.after.id, x.label_key) for x in served] == [("family_joined", "town_title_town")]


def test_a_later_title_must_name_an_unlock_the_content_has(shipped_opening: Opening):
    unlock = UnlockEntry(unlock_kind="feature", id="nobody")
    with pytest.raises(ValueError, match="nobody"):
        check_opening(labelled(shipped_opening, LaneLabelEntry(after=unlock, label_key="town_title_town")))


def test_a_later_title_must_name_a_text_key(shipped_opening: Opening):
    unlock = UnlockEntry(unlock_kind="feature", id="family_joined")
    with pytest.raises(ValueError, match="town_title_nowhere"):
        check_opening(labelled(shipped_opening, LaneLabelEntry(after=unlock, label_key="town_title_nowhere")))
