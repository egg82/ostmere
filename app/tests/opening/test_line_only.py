"""A line-only trigger (opening/line_only_checks.py): it says its line once and gates nothing. The loader refuses one whose
outcome does more than tell lines, or that a condition names, beside a control that loads."""
from pathlib import Path

import pytest

from ashfall_app.opening.schema import OPENING, load_opening

TEXT = OPENING.read_text()
SAYS = '[[triggers]]\nid = "t_says_once"\n{mark}when = {{ test = "at_least", subject_kind = "skill_level", id = "scavenging", value = 2 }}\noutcome = {{ {outcome} }}\n'


def loaded(tmp_path: Path, mark: str = "line_only = true\n", outcome: str = 'line_keys = ["l_flint"]', extra: str = ""):
    path = tmp_path / "opening.toml"
    path.write_text(TEXT + "\n" + SAYS.format(mark=mark, outcome=outcome) + extra)
    return load_opening(path)


def test_a_line_only_trigger_that_tells_lines_loads(tmp_path: Path):
    assert any(t.id == "t_says_once" and t.line_only for t in loaded(tmp_path).triggers)


@pytest.mark.parametrize("outcome", ['stores = [{ store = "flint", items = 1 }], line_keys = ["l_flint"]',
                                     'unlocks = [{ unlock_kind = "chip", id = "tired" }]'])
def test_a_line_only_trigger_that_does_more_than_tell_lines_fails_the_load(tmp_path: Path, outcome: str):
    with pytest.raises(ValueError, match="trigger t_says_once.*more than tell lines"):
        loaded(tmp_path, outcome=outcome)


def test_the_same_outcome_unmarked_loads(tmp_path: Path):
    """The control: the marker is what the check reads."""
    assert loaded(tmp_path, mark="", outcome='stores = [{ store = "flint", items = 1 }], line_keys = ["l_flint"]')


def test_a_condition_naming_a_line_only_trigger_fails_the_load(tmp_path: Path):
    waits = ('[[triggers]]\nid = "t_waits"\nwhen = { test = "at_least", subject_kind = "lane_rules", id = "t_says_once", '
             'value = 1 }\noutcome = { line_keys = ["l_flint"] }\n')
    with pytest.raises(ValueError, match="trigger t_waits.*t_says_once"):
        loaded(tmp_path, extra=waits)
