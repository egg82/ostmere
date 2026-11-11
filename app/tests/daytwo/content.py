"""Day two's content as the simulator reads it: the rules with day_two.toml merged after the shipped chapters (as
tests/opening/test_day_two.py loads it while day two is in writing), and which content step is which of day two's story
ids, read off a save. The simulator names story moments by these ids only (CLAUDE.md, "Never spoil the owner")."""
from functools import cache

from ashfall_app.engine import CardId, OfferId, Rules, Save, Unlock, UnlockKind
from ashfall_app.engine.work import completions
from ashfall_app.opening.schema import DAY_ONE, DAY_TWO, OPENING, Opening, load_opening, to_rules
from tests.dayone.beats import STORY as DAY_ONE_STORY, landed as day_one_landed
from tests.dayone.sinks import Chapter

TRIGGERED = {"J2": ("t_night_2",), "J3": ("t_morning_3",), "B4": ("t_b4_went", "t_b4_she_went")}
"""Story ids that land when one of these triggers fires."""
STEPS = {"A15": ("give_stool",), "J1": ("give_stool",), "A16": ("make_room",), "J4": ("make_room",),
         "A17": ("build_shelter",), "A18": ("build_woodstack",), "A19": ("walk_ridge", "n1_walk_ridge")}
"""Story ids that land at the first completion of one of these cards (A19: whoever walked)."""
OFFERS = {"O-cart": OfferId("o_cart")}
"""Story ids that land when the offer shows."""
STORY = ("B3", "J1", "J2", "J3", "J4", "B4")
"""Day two's beats in their authored order (beats.yaml, day_two:)."""
DAY_TWO_IDS = (*STEPS, *TRIGGERED, *OFFERS)
OFFER = OfferId("o_cart")
GO, SHE_GOES = "o_cart_go", "o_cart_she_goes"
BUILDS = ("build_shelter", "build_woodstack")
BED = "raised_bed"
"""Day two's comfort: staged, opened by A15's finish; the policies build it then, never while A16 or a build
waits."""
CHAPTER = Chapter(comforts=(CardId(BED),))
"""Day two's sinks as the sink policies read them: the comfort alone (no trip, and the offer is answered by Knobs2)."""
LANE = "n1"
FORAGE, CUT, SCAVENGE, GATHER = "n1_forage", "n1_cut", "n1_scavenge", "n1_gather"
TASKS = (FORAGE, GATHER, CUT, SCAVENGE)
"""Her task's options (the cards on her lane the page offers in `Change`)."""
TASK_FOR = {"damp_wood": CUT, "stones": SCAVENGE, "dry_wood": CUT, "roots": FORAGE}
"""The task that feeds a store a build is short of (dry wood is laid from damp wood on the rack)."""


@cache
def opening2() -> Opening:
    return load_opening(OPENING, (DAY_ONE, DAY_TWO))


@cache
def rules2() -> Rules:
    """One Rules object for every day-two run: the engine caches by the rules' identity."""
    return to_rules(opening2())


def landed(save: Save, rules: Rules) -> set[str]:
    """Day one's landed ids and day two's: a trigger fired, a card's first completion, the offer shown."""
    fired = {t.id for t, f in zip(rules.triggers, save.fired) if f}
    found = day_one_landed(save, rules)
    found |= {b for b, ts in TRIGGERED.items() if fired & set(ts)}
    found |= {b for b, cs in STEPS.items() if any(completions(save, rules, CardId(c)) > 0 for c in cs)}
    found |= {b for b, o in OFFERS.items() if Unlock(UnlockKind.OFFER, o) in save.unlocked}
    return found


def new_beats(seen: set[str]) -> list[str]:
    """Day two's own beats among `seen` (B3 is day one's)."""
    return [b for b in STORY if b in seen and b not in DAY_ONE_STORY]
