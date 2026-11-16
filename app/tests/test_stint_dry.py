"""A goal stint whose card runs out of input hands the hands back at that instant (engine DESIGN.txt, "Queue mix"): the
entry leaves the queue, the player's own mix runs on, and the rule log says why (Ended.DRY)."""
from ashfall_app import engine as e
from ashfall_app.engine import BP, CardId, CardShare, Mix, MixId, QueueEntry, SaveMix, SetQueue, SwitchMix
from ashfall_app.engine.plan import running_mix_id
from tests.test_goal_rows import running, world

STINT = MixId("stint")
UNTIL = e.AtLeast(e.SkillLevel(e.SkillId("k")), 2, 2)
DRY_AT = 600
"""`saw` costs 6 logs an hour at a full share: one log lasts ten minutes."""


def _queued(shares: dict[str, int], logs: int) -> tuple[e.Rules, e.Save]:
    r, s = world(logs=logs)
    s = running(r, s, {"chop": BP})
    mix = Mix(STINT, tuple(CardShare(CardId(c), bp) for c, bp in shares.items()))
    s = e.decide(s, r, 0, SaveMix(mix))
    return r, e.decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(STINT), UNTIL),)))


def test_a_stint_whose_input_runs_dry_hands_the_hands_back_at_that_instant() -> None:
    r, s = _queued({"saw": BP}, 1)
    assert running_mix_id(s, r) == STINT, "control: the stint runs"
    before = e.advance(s, r, DRY_AT - 1)
    assert running_mix_id(before, r) == STINT and len(before.queue) == 1, "control: it holds until the input is gone"
    at = e.advance(s, r, DRY_AT)
    assert at.queue == () and running_mix_id(at, r) == MixId("m")
    assert e.view(at, r).skills[0].xp.rate > 0, "the player's mix is working, not idle"


def test_the_log_says_a_dry_stint_ended_and_a_stint_with_input_reports_nothing() -> None:
    r, s = _queued({"saw": BP}, 1)
    order = e.Order(UNTIL, SwitchMix(STINT))
    changes = e.advance_logged(s, r, DRY_AT + 60).rule_changes
    assert [(c.time, c.order, c.on, c.ended) for c in changes] == [(DRY_AT, order, False, e.Ended.DRY)]
    r, s = _queued({"saw": BP}, 40)
    assert e.advance_logged(s, r, 3600).rule_changes == (), "control: no input ran dry"


def test_a_card_the_players_own_mix_runs_too_does_not_end_the_stint() -> None:
    """The stint's card is what it puts on the hands over the player's mix; an input the player's mix would run dry
    as well is not the stint's doing."""
    r, s = world()
    s = running(r, s, {"saw": BP})
    s = e.decide(s, r, 0, SaveMix(Mix(STINT, (CardShare(CardId("saw"), BP // 2), CardShare(CardId("chop"), BP // 2)))))
    s = e.decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(STINT), UNTIL),)))
    assert len(e.advance(s, r, 3000).queue) == 1
