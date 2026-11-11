"""Every log line the opening can carry has a kind: take one line's kind away and the check names that line."""
import pytest

from ashfall_app.opening.line_kinds import check_line_kinds, line_keys
from tests.opening.playthrough import opening


def test_the_shipped_lines_all_have_a_kind() -> None:
    o = opening()
    assert line_keys(o), "control: the opening has log lines"
    check_line_kinds(o)


def test_a_line_with_no_kind_is_named() -> None:
    o = opening()
    key = sorted(set(line_keys(o)) & o.line_kinds.keys())[0]
    bare = o.model_copy(update={"line_kinds": {k: v for k, v in o.line_kinds.items() if k != key}})
    with pytest.raises(ValueError, match=f"line {key}.*has no kind"):
        check_line_kinds(bare)
