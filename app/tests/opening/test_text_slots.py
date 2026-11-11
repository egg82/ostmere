"""A text holds only slots its key's kind is filled with (api/CONTRACT.txt, "Text and numbers"): a lane's person, `{found}`
on a find line, `{pct}` on what pays a change, and so on. A slot nothing fills shows its braces on the page, so the loader
refuses it, naming the key and the slot."""
import pytest

from ashfall_app.opening.checks import check_opening
from ashfall_app.opening.name_checks import SLOT
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening


@pytest.fixture(scope="module")
def opening() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def with_text(o: Opening, key: str, text: str) -> Opening:
    assert key in o.text, key
    return o.model_copy(update={"text": {**o.text, key: text}})


def line_key(o: Opening) -> str:
    return next(k for t in o.triggers for k in t.outcome.line_keys if not SLOT.findall(o.text[k]))


def pays_key(o: Opening) -> str:
    return next(lv.pays_key for k in o.skills for lv in k.levels if "{pct}" in o.text[lv.pays_key])


def test_shipped_content_passes(opening: Opening):
    check_opening(opening)


@pytest.mark.parametrize("slot", ["{zzz}", "{n9}", "{pct}", "{n}", "{d}"])
def test_a_line_holding_a_slot_nothing_fills_is_refused(opening: Opening, slot: str):
    key = line_key(opening)
    with pytest.raises(ValueError, match=rf"text {key}.*{slot}"):
        check_opening(with_text(opening, key, f"It waits {slot} of it."))


def test_a_ui_text_holding_an_unknown_slot_is_refused(opening: Opening):
    with pytest.raises(ValueError, match=r"text ui.rate.per_minute.*\{zzz\}"):
        check_opening(with_text(opening, "ui.rate.per_minute", "{n} {zzz}"))


def test_the_slots_a_kind_is_filled_with_are_accepted(opening: Opening):
    check_opening(with_text(opening, pays_key(opening), "better, {pct} and {pct_b}"))
    check_opening(with_text(opening, "ui.rate.per_minute", "{n} a minute"))
    lane = next(x.id for x in opening.lanes if x.name_key is not None)
    check_opening(with_text(opening, line_key(opening), f"{{{lane}}} sits down."))
