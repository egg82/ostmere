"""Day two's instruments without a play: the story-id reader, B4's presence steps, the line state lists' key set,
her-rule lookup, the edge of written content and the long-wait reading the readout marks. Each shows the instrument can
return a finding."""
from dataclasses import replace

from ashfall_app.engine import AfterTime, CardId, LaneBar, LaneId, Order, TapCard, Unlock, UnlockKind, new_save
from ashfall_app.opening.schema import DAY_ONE, load_opening
from tests.daytwo import checks, content as c, lines
from tests.daytwo.later import LevelAt
from tests.daytwo.player import visit_seen
from tests.daytwo.policy import her_rule_index
from tests.dayone.bands import presence_steps
from tests.dayone.player import VisitRecord


def test_a_new_save_has_landed_none_of_day_two():
    rules = c.rules2()
    assert not c.landed(new_save(rules), rules) & set(c.DAY_TWO_IDS)


def test_the_offer_lands_when_it_shows():
    rules = c.rules2()
    s = new_save(rules)
    shown = replace(s, unlocked=(*s.unlocked, Unlock(UnlockKind.OFFER, c.OFFER)))
    assert "O-cart" in c.landed(shown, rules) and "O-cart" not in c.landed(s, rules)


def test_b4_waits_on_her_arrival_the_night_and_the_offer():
    """Read off the content: the triggers that open a card on B4's way (her row's and the night's), and the offer."""
    assert presence_steps(c.rules2(), checks.B4_WAY, checks.day_one_ids()) == ["t_n1_works", "t_night_2"]
    assert checks.b4_steps() == 3


def test_the_line_lists_cover_every_day_two_key_and_only_those():
    keys = lines.day_two_keys()
    shipped = set(load_opening(chapters=(DAY_ONE,)).text)
    assert keys and not set(keys) & shipped
    assert set(lines.states({})) == set(keys)


def test_the_story_order_check_reads_the_landing_times():
    authored = {b: i for i, b in enumerate(c.STORY)}
    assert checks.story_order(authored) == []
    assert checks.story_order({**authored, "J2": authored["J4"] + 1})
    assert checks.story_order({b: t for b, t in authored.items() if b != "B4"}) == ["never landed: ['B4']"]


def test_a_level_verdict_tells_the_three_cases():
    def at(h: float | None) -> str:
        return LevelAt("B5", "foraging", 10, 4, 4, h).verdict
    assert at(None).startswith("never") and at(0.0).startswith("already") and at(5.0) == "inside day three"
    assert at(500.0) == "past day three"


def test_her_rule_is_found_among_the_players():
    forage = Order(AfterTime(0), TapCard(CardId(c.FORAGE)))
    other = Order(AfterTime(0), TapCard(CardId("rest")))
    assert her_rule_index((other, forage)) == 1 and her_rule_index((other,)) is None


def test_the_edge_is_the_visit_the_last_written_beat_is_seen_in():
    visits = [VisitRecord(i + 1, s, s + 100, 3600) for i, s in enumerate((0, 10_000, 20_000))]
    assert visit_seen(visits, 10_050) == 2 and visit_seen(visits, 5_000) is None and visit_seen(visits, None) is None


def test_a_long_wait_is_a_job_left_landing_past_the_dead_gap():
    walk = LaneBar(LaneId("n1"), CardId("n1_walk_ridge"), 10_000)
    short = LaneBar(LaneId("hands"), CardId("forage"), 100)
    free = LaneBar(LaneId("hands"), None, None)
    assert checks.long_jobs((walk, short, free), 0, 180) == {("n1", "n1_walk_ridge")}
    assert checks.long_jobs((walk,), 9_900, 180) == set()
    assert checks.still_running((walk, free)) == {("n1", "n1_walk_ridge")}
    assert checks.still_running((free,)) == set()


def test_a_long_wait_counts_a_job_started_after_the_exit():
    forage = LaneBar(LaneId("n1"), CardId("n1_forage"), 4)
    walk = LaneBar(LaneId("n1"), CardId("n1_walk_ridge"), 9_000)
    left = (0, (forage,))
    assert checks.waited_on(left, (5_400, (walk,)), 180)
    assert checks.waited_on((0, (walk,)), (8_990, (walk,)), 180)
    assert not checks.waited_on(left, (8_900, (walk,)), 180)
    assert not checks.waited_on(left, (5_400, (forage,)), 180)
    assert not checks.waited_on((0, (walk,)), (9_100, (forage,)), 180)
