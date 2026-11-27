"""An offer kind's label per role (offer_kinds; contract/offers.txt, "Offers"): every kind of offer in the shipped chapters and
the chapters in writing has a label for each role its answers carry, so the rule that answers the kind is worded for
whoever asks. The loader refuses a kind without them; each refusal has a planted case."""
from pathlib import Path

import pytest

from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, OPENING, Opening, load_opening, merge_chapters

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "askkinds.toml"
DECLARED = '''[[offer_kinds]]
kind = "q_ask"
roles = [{ role = "yes", label_key = "q_k_yes" }, { role = "no", label_key = "q_k_no" }]
'''


def variant(tmp_path: Path, *edits: tuple[str, str]) -> Path:
    text = FIXTURE.read_text()
    for old, new in edits:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    path = tmp_path / "askkinds.toml"
    path.write_text(text)
    return path


def test_every_kind_of_offer_has_its_labels(shipped_opening: Opening):
    full = load_opening(OPENING, (*CHAPTERS, *IN_WRITING))
    kinds = {x.kind for x in full.offers if x.kind is not None}
    assert kinds, "no kinded offer in the content: the check scans nothing"
    for kind in kinds:
        roles = {a.role for x in full.offers if x.kind == kind for a in x.answers}
        assert {r.role for k in full.offer_kinds if k.kind == kind for r in k.roles} == roles, kind


def test_the_fixture_is_whole(shipped_opening: Opening, tmp_path: Path):
    merged = merge_chapters(shipped_opening, (variant(tmp_path),))
    assert "q_ask" in [k.kind for k in merged.offer_kinds]


PLANTS = [
    (("\n" + DECLARED, "\n"), "has no label per role"),
    ((DECLARED, DECLARED.replace('role = "no"', 'role = "maybe"')), "labelled roles differ"),
    ((DECLARED, DECLARED.replace('{ role = "no", label_key = "q_k_no" }', '{ role = "yes", label_key = "q_k_no" }')), "share a role"),
    ((DECLARED, DECLARED + DECLARED), "is declared twice"),
    ((DECLARED, DECLARED + DECLARED.replace("q_ask", "q_other")), "no offer has this kind"),
    ((DECLARED, DECLARED.replace("q_k_no", "q_k_missing")), "key 'q_k_missing' is not in text"),
]


@pytest.mark.parametrize("edit,message", PLANTS, ids=["kind not declared", "other roles", "repeated role", "declared twice",
                                                    "kind without offers", "label key not in text"])
def test_a_planted_fault_fails_the_loader(shipped_opening: Opening, tmp_path: Path, edit: tuple[str, str], message: str):
    with pytest.raises(ValueError, match=message):
        merge_chapters(shipped_opening, (variant(tmp_path, edit),))
