"""The session's shipped Ruleset and Game (tests/shipped_ruleset.py) serve a pod under any build name: the rules are
derived once, a build changes only the Ruleset's `build`, and a Game keeps its build in its content tag."""
from ashfall_app.saves.ruleset import ruleset
from tests.shipped_ruleset import ShippedRuleset


def test_builds_differing_only_in_name_share_the_derived_rules(shipped_ruleset: ShippedRuleset):
    s = shipped_ruleset
    a = s.ruleset(s.opening, s.renames, "contract-build-a", s.release)
    b = s.ruleset(s.opening, s.renames, "contract-build-b", s.release)
    assert (a.build, b.build) == ("contract-build-a", "contract-build-b")
    assert a.rules is b.rules and a.digest == b.digest
    assert s.ruleset(s.opening, s.renames, "contract-build-a", s.release) is a


def test_a_build_is_the_real_builders_ruleset_but_for_its_name(shipped_ruleset: ShippedRuleset):
    s = shipped_ruleset
    assert s.ruleset(s.opening, s.renames, "main-abc-1", s.release) == ruleset(s.opening, s.renames, "main-abc-1", s.release)


def test_another_release_gets_its_own_ruleset(shipped_ruleset: ShippedRuleset):
    s = shipped_ruleset
    other = s.ruleset(s.opening, s.renames, "contract-build-a", s.release + 1)
    assert other.release == s.release + 1 and other.rules is not s.rs.rules


def test_a_game_is_kept_per_build_and_names_its_build(shipped_ruleset: ShippedRuleset):
    s = shipped_ruleset
    a = s.ruleset(s.opening, s.renames, "contract-build-a", s.release)
    b = s.ruleset(s.opening, s.renames, "contract-build-b", s.release)
    game_a, game_b = s.make_game(s.opening, a), s.make_game(s.opening, b)
    assert s.make_game(s.opening, a) is game_a and game_a is not game_b
    assert "contract-build-a" in game_a.content_tag and "contract-build-b" in game_b.content_tag
