"""Each skill's max level (ticks.max_level) on the shipped rules, and the readout's max line for a reached and an
unreached max."""
from tests.ladder.readout import max_line
from tests.ladder.ticks import max_level
from tests.shipped_ruleset import ShippedRuleset

# ladder-typical's skills at top L22; each track's ranks are counted off prestige.toml (woodcutting 7, scavenging 6, none for wayfinding)
MAX = {"woodcutting": 169, "scavenging": 148, "wayfinding": 22}


def test_max_level_is_one_span_per_rank_of_the_track(shipped_ruleset: ShippedRuleset) -> None:
    rules = shipped_ruleset.ruleset(shipped_ruleset.opening, "ladder-max", shipped_ruleset.release).rules
    got = {str(sk.id): max_level(rules, sk.id) for sk in rules.skills}
    assert {k: got[k] for k in MAX} == MAX


def test_a_max_not_reached_reads_as_not_reached_with_how_far_it_got() -> None:
    assert max_line(169, 21, None) == "    max L169: not by the edge (reached L21)"


def test_a_max_reached_reads_its_time() -> None:
    assert max_line(22, 22, 86400 * 3) == "    max L22: 3.00 d"
