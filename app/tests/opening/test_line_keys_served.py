"""Content.line_infos (api/CONTRACT.txt, "The client may"): every key a story line can carry is served, each once, so the
page's story strip can keep room for the tallest. The oracle walks the engine's Rules for every field typed LineKey,
independently of the list the service builds, and adds the content's start and end lines, which no engine event writes."""
import dataclasses
import typing

import pytest
from fastapi.testclient import TestClient

from ashfall_app.api.content_models import Content
from ashfall_app.engine import Rules
from ashfall_app.main import create_app
from tests.opening.playthrough import opening, opening_rules


def _line_fields(cls: type) -> list[str]:
    hints = typing.get_type_hints(cls)
    return [f.name for f in dataclasses.fields(cls) if "LineKey" in str(hints[f.name])]


def engine_line_keys(value: object, found: set[str]) -> set[str]:
    """Every value of a LineKey-typed field anywhere under `value` (dataclasses, tuples, lists, dicts)."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for name in _line_fields(type(value)):
            got: object = getattr(value, name)
            found.update(k for k in (got if _is_seq(got) else (got,)) if isinstance(k, str))
        for f in dataclasses.fields(value):
            engine_line_keys(getattr(value, f.name), found)
    elif _is_seq(value):
        for v in value:
            engine_line_keys(v, found)
    elif _is_map(value):
        for v in value.values():
            engine_line_keys(v, found)
    return found


def _is_seq(value: object) -> typing.TypeGuard[tuple[object, ...] | list[object]]:
    return isinstance(value, (tuple, list))


def _is_map(value: object) -> typing.TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def served() -> Content:
    return Content.model_validate(TestClient(create_app()).get("/api/content").json())


@pytest.fixture(scope="module")
def content() -> Content:
    """/api/content as served, and the cached opening and its rules, all built once."""
    opening_rules()
    return served()


def test_every_story_line_key_is_served_once(content: Content) -> None:
    o = opening()
    rules: Rules = opening_rules()
    want = engine_line_keys(rules, set()) | set(o.start_line_keys) | set(o.end_line_keys)
    assert len(want) > 50, "the walk found the content's lines"   # control: the oracle saw the shipped lines
    served_keys = [i.key for i in content.line_infos]
    assert set(served_keys) >= want, f"not served: {sorted(want - set(served_keys))}"
    assert len(served_keys) == len(set(served_keys)), "each key once"
    texts = {t.key for t in content.text_entries}
    assert set(served_keys) <= texts, "every served line key has its text"


def test_the_walk_finds_a_planted_line() -> None:
    """Control: a card line and an outcome's line planted in the Rules are each found."""
    rules = opening_rules()
    card = rules.cards[0]
    planted = dataclasses.replace(card, lines=(*card.lines, "planted.line"),
                                  outcome=dataclasses.replace(card.outcome, lines=("planted.outcome",)))
    found = engine_line_keys(dataclasses.replace(rules, cards=(planted, *rules.cards[1:])), set())
    assert {"planted.line", "planted.outcome"} <= found
