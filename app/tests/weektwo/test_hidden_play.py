"""The guard on a play built in a test's body (tests/weektwo/routes.py, `refuse_hidden_play`): `play_of` places a test by its
fixtures, so a play it builds itself is paid in whichever shard the test falls into."""
import pytest

from tests.weektwo import routes


def test_a_play_built_in_a_test_body_is_refused_with_the_tests_id():
    nodeid = routes.hidden_play_in
    assert nodeid and nodeid.endswith("test_a_play_built_in_a_test_body_is_refused_with_the_tests_id")
    with pytest.raises(AssertionError, match=nodeid):
        routes.from_saved("eight", "typical", seed=987654)   # a seed no other test plays, so a cache miss
    with pytest.raises(AssertionError, match=nodeid):
        routes.played("eight", "typical", seed=987654)


@pytest.mark.weektwo_shard("eight")
def test_a_test_naming_its_shard_may_build_its_own_play():
    assert routes.hidden_play_in is None
