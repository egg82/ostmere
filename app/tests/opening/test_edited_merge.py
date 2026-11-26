"""A test's own merge (edited.py) runs the loader's expansions, so content built through it is the shipped content."""
from ashfall_app.opening.schema import Opening
from tests.opening.edited import edited


def test_the_test_merge_expands_everything_the_loader_does(shipped_opening: Opening):
    mine = edited(check=False)
    for part in ("triggers", "stores", "standing"):
        assert [x.id for x in getattr(mine, part)] == [x.id for x in getattr(shipped_opening, part)], part
