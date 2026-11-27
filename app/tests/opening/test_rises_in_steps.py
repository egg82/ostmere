"""StoreInfo.rises_in_steps on the shipped content: a store nothing that runs makes (no card lands or flows it, no
standing action flows it) rises only by events, a step at a time, so a rule on it cannot flip at one level on a flow
(contract/the-client-may.txt, "a store rule"). Hurt, which only a lost fight adds to, is one; a store a card or a standing action makes
is not."""
from ashfall_app.api.content_models import Content
from ashfall_app.opening.makers import card_makers, standing_makers
from ashfall_app.opening.schema import Opening
from tests.shipped_ruleset import ShippedRuleset


def served(content: Content) -> dict[str, bool]:
    return {s.store: s.rises_in_steps for s in content.store_infos}


def test_hurt_rises_in_steps_and_a_made_store_does_not(shipped_ruleset: ShippedRuleset) -> None:
    got = served(shipped_ruleset.make_game(shipped_ruleset.opening, shipped_ruleset.rs).content())
    assert got["hurt"] is True
    assert got["clay"] is False


def test_a_store_only_a_standing_action_flows_does_not(shipped_ruleset: ShippedRuleset) -> None:
    o: Opening = shipped_ruleset.opening
    flowed = [s.id for s in o.stores if standing_makers(o, s.id) and not card_makers(o, s.id)]
    assert flowed, "control: the shipped content has a store only a standing action makes"
    got = served(shipped_ruleset.make_game(o, shipped_ruleset.rs).content())
    assert not any(got[s] for s in flowed)
