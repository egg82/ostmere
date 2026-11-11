"""`replaced_by` on a retired unlock (opening.entries.UnlockEntry): only a retired unlock names one, and the same outcome
unlocks that card; it is served on the retired card's CardInfo, and only on that one."""
import pytest
from fastapi.testclient import TestClient

from ashfall_app.api.content_models import Content
from ashfall_app.main import create_app
from tests.opening.edited import edited

RETIRE = '{ unlock_kind = "retired", id = "gather_wood", replaced_by = "woodcutting" }'


def test_the_card_infos_name_the_replacement_of_the_one_card_the_content_names_it_for() -> None:
    content = Content.model_validate(TestClient(create_app()).get("/api/content").json())
    named = {c.card: c.replaced_by for c in content.card_infos if c.replaced_by is not None}
    assert named == {"gather_wood": "woodcutting"}
    assert len(content.card_infos) > 1


@pytest.mark.parametrize("new, match", [
    (RETIRE.replace('"woodcutting"', '"look_out"'), "gather_wood is replaced by look_out, which the same outcome does not unlock"),
    (RETIRE.replace('"retired"', '"card"'), "replaced_by is on a card unlock"),
])
def test_the_content_check_refuses_a_replacement_the_outcome_does_not_make_or_on_another_kind(new: str, match: str) -> None:
    assert edited(data=lambda part: part).cards
    with pytest.raises(ValueError, match=match):
        edited(data=lambda part: part.replace(RETIRE, new))
