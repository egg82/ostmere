"""Content.line_infos' causes (api/CONTRACT.txt, "Line causes"): each line key is served with what writes it, read from
where the content authors the key. One case per place a key can be authored, on the shipped content, and a key
planted in a second place fails the load."""
import pytest

from ashfall_app.api.decision_models import AtLeast, SkillLevel, StoreValue
from ashfall_app.api.line_causes import line_infos
from ashfall_app.api.line_models import AnswerCause, CampCause, LineCause, RunnerCause, SkillCause, WhenCause
from ashfall_app.opening.schema import Opening
from tests.opening.playthrough import opening


@pytest.fixture(scope="module")
def causes() -> dict[str, LineCause | None]:
    return {i.key: i.cause for i in line_infos(opening())}


def test_a_cards_line_names_the_card(causes: dict[str, LineCause | None]) -> None:
    card = next(c for c in opening().cards if c.line_keys)
    assert causes[card.line_keys[0]] == RunnerCause(runner=card.id)


def test_a_fights_pool_line_names_its_runner(causes: dict[str, LineCause | None]) -> None:
    action = next(a for a in opening().standing if a.fight is not None and a.fight.won_line_keys)
    assert action.fight is not None
    assert causes[action.fight.won_line_keys[0]] == RunnerCause(runner=action.id)


def test_a_beats_line_names_what_it_waited_on(causes: dict[str, LineCause | None]) -> None:
    beat = next(t for t in opening().triggers
                if t.when.subject_kind == "store" and t.when.test == "at_least" and t.outcome.line_keys)
    got = causes[beat.outcome.line_keys[0]]
    assert isinstance(got, WhenCause) and isinstance(got.when, AtLeast)
    assert got.when.watched == StoreValue(store=beat.when.id or "")


def test_a_chips_line_names_its_condition(causes: dict[str, LineCause | None]) -> None:
    chip = next(c for c in opening().chips if c.on_line_key)
    got = causes[chip.on_line_key or ""]
    assert isinstance(got, WhenCause) and got.when.kind == chip.when.test


def test_a_camp_levels_line_names_the_level_from_one(causes: dict[str, LineCause | None]) -> None:
    camp = opening().camp
    assert camp is not None
    i, level = next((i, lv) for i, lv in enumerate(camp.levels) if lv.line_keys)
    assert causes[level.line_keys[0]] == CampCause(level=i + 1)


def test_an_answers_line_names_the_offer(causes: dict[str, LineCause | None]) -> None:
    offer, key = next((x, k) for x in opening().offers for a in x.answers for k in a.outcome.line_keys)
    assert causes[key] == AnswerCause(offer=offer.id)


def test_a_line_several_levels_share_names_the_skill_alone(causes: dict[str, LineCause | None]) -> None:
    by_key: dict[str, list[str]] = {}
    for t in opening().triggers:
        if t.when.subject_kind == "skill_level":
            for k in t.outcome.line_keys:
                by_key.setdefault(k, []).append(t.when.id or "")
    key, skills = next((k, s) for k, s in by_key.items() if len(s) > 1)
    assert causes[key] == SkillCause(skill=skills[0])
    one = next(k for k, s in by_key.items() if len(s) == 1)
    got = causes[one]
    assert isinstance(got, WhenCause) and isinstance(got.when, AtLeast) and isinstance(got.when.watched, SkillLevel)


def test_the_ends_lines_have_no_cause(causes: dict[str, LineCause | None]) -> None:
    assert opening().end_line_keys, "control: the content has an end"
    assert all(causes[k] is None for k in opening().end_line_keys)


def test_a_key_written_by_two_cards_fails_the_load() -> None:
    o = opening()
    a, b = [c for c in o.cards if c.line_keys][:2]
    planted = b.model_copy(update={"line_keys": [*b.line_keys, a.line_keys[0]]})
    o2: Opening = o.model_copy(update={"cards": [planted if c is b else c for c in o.cards]})
    with pytest.raises(ValueError, match="written in two places"):
        line_infos(o2)
