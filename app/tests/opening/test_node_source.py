"""The loader refuses content whose modifier is sourced as a node's rank entry is (NODE_PREFIX): only a pick makes
one (engine pickentries.pick_source)."""
import pytest

from ashfall_app.engine import InvalidRulesError
from ashfall_app.opening.schema import to_rules
from tests.opening.edited import edited

CAMP = 'source = "camp_1"'


def test_the_edit_that_makes_a_node_prefixed_source_reaches_the_rules():
    """The control: a source that merely looks like the prefix loads, so the edit below is what the refusal answers."""
    to_rules(edited(lambda d: d.replace(CAMP, 'source = "nodes_camp_1"')))


def test_a_content_source_starting_with_the_node_prefix_is_refused():
    with pytest.raises(InvalidRulesError, match="node source"):
        to_rules(edited(lambda d: d.replace(CAMP, 'source = "node:camp_1"')))
