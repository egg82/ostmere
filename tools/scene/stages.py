"""The moments the previews composite, each a State of facts and store levels, and the page's rule for whether a
layer's condition holds in one, with the kinds of condition it knows."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    """A moment to composite: the facts that hold (project:, pushes:, running:, chip:, feature:) and store levels."""
    facts: frozenset[str] = frozenset()
    stores: tuple[tuple[str, int], ...] = ()

    def then(self, add: Iterable[str] = (), drop: Iterable[str] = (), **stores: int) -> State:
        return State((self.facts - frozenset(drop)) | frozenset(add), tuple({**dict(self.stores), **stores}.items()))


UP = State(frozenset({"pushes:stand_up@1", "pushes:stand_up@2", "pushes:stand_up@3", "project:look_around"}))
"""Facts are the v2 card ids (app/ashfall_app/opening/opening.toml); `feature:stool` is the stool's unlock."""
STAGES: dict[str, State] = {"1_start": State(), "1b_standing_dark": State(UP.facts - {"project:look_around"})}
STAGES["2_gathering"] = UP.then({"running:gather_wood"}, damp_wood=2)
STAGES["3_scavenging"] = STAGES["2_gathering"].then({"running:scavenge", "pushes:clear_spot@2"}, {"running:gather_wood"},
                                                    damp_wood=5, stones=4)
STAGES["4_drying"] = STAGES["3_scavenging"].then({"running:lay_to_dry"}, {"running:scavenge"}, damp_wood=4, stones=7)
STAGES["5_fire_lit"] = STAGES["4_drying"].then({"project:lay_to_dry", "project:ring_it", "project:strike_fire"},
                                               {"running:lay_to_dry"}, damp_wood=6, stones=1, dry_wood=2)
STAGES["6_stool_built"] = STAGES["5_fire_lit"].then({"running:lay_to_dry", "feature:stool"}, damp_wood=9, dry_wood=4)
STAGES["7_fireback_built"] = STAGES["6_stool_built"].then({"project:build_fireback"}, dry_wood=1)
STAGES["8_dusk"] = STAGES["7_fireback_built"].then({"end:showing"})
STAGES["9_knapping"] = STAGES["5_fire_lit"].then({"running:knap_edge"})
STAGES["9_roasting"] = STAGES["5_fire_lit"].then({"running:roast_roots"})
STAGES["9_knapping_stool"] = STAGES["6_stool_built"].then({"running:knap_edge"})
STAGES["9_roasting_stool"] = STAGES["6_stool_built"].then({"running:roast_roots"})
STAGES["9_reading"] = STAGES["6_stool_built"].then({"running:read_by_fire"})
STAGES["9_resting"] = STAGES["5_fire_lit"].then({"running:rest"})
STAGES["9_birch"] = STAGES["5_fire_lit"].then({"project:woodcutting"})
STAGES["9_reading_no_stool"] = STAGES["5_fire_lit"].then({"running:read_by_fire"})
# Day one (app/ashfall_app/opening/day_one.toml; the list is content/team/day-one.md's, Art). `running:night` stands
# for the night grade's condition.
STAGES["10_night"] = STAGES["8_dusk"].then({"running:night", "running:sit_up"})
STAGES["11_morning"] = STAGES["10_night"].then({"feature:morning", "project:look_out"}, {"running:night", "running:sit_up"})
STAGES["11_looking_out"] = STAGES["10_night"].then({"feature:morning", "running:look_out"}, {"running:night", "running:sit_up"})
STAGES["12_snares"] = STAGES["11_morning"].then({f"pushes:set_snare@{n}" for n in (1, 2, 3)} | {"running:set_snare"})
STAGES["13_builds"] = STAGES["12_snares"].then({"feature:lean_to", "feature:larder", "running:build_smoke_rack"},
                                               {"running:set_snare"})
STAGES["13_building_lean_to"] = STAGES["12_snares"].then({"running:build_lean_to"}, {"running:set_snare"})
STAGES["13_building_larder"] = STAGES["12_snares"].then({"feature:lean_to", "running:build_larder"}, {"running:set_snare"})
STAGES["14_smoking"] = STAGES["13_builds"].then({"feature:smoke_rack", "running:smoke_catch"}, {"running:build_smoke_rack"})
STAGES["15_prints"] = STAGES["14_smoking"].then({"feature:prints"}, {"running:smoke_catch"})
STAGES["16_arrival"] = STAGES["15_prints"].then({"feature:n1"})
STAGES["16_walking_in"] = STAGES["15_prints"].then({"running:take_stock"})
# Day two (app/ashfall_app/opening/day_two.toml; the list is content/team/day-two.md's, Art). Her lane always runs a
# task, so each stage names one.
STAGES["17_her_row"] = STAGES["16_arrival"].then({"running:n1_forage"})
STAGES["18_stool"] = STAGES["17_her_row"].then({"running:give_stool"})
STAGES["19_night_two"] = STAGES["17_her_row"].then({"project:give_stool", "feature:n1_named", "feature:dusk_2",
                                                    "feature:night_2", "feature:night_2_sound"})
STAGES["20_morning_three"] = STAGES["19_night_two"].then({"feature:morning_3"})
STAGES["21_room_for_two"] = STAGES["20_morning_three"].then({"project:make_room", "running:build_shelter",
                                                             "running:n1_gather"}, {"running:n1_forage"})
STAGES["21_building_woodstack"] = STAGES["21_room_for_two"].then({"feature:n1_shelter", "running:build_woodstack"},
                                                                 {"running:build_shelter"})
STAGES["22_offer"] = STAGES["21_room_for_two"].then({"feature:n1_shelter", "feature:woodstack", "running:n1_cut"},
                                                    {"running:build_shelter", "running:n1_gather"})
STAGES["23_walk"] = STAGES["22_offer"].then({"running:walk_ridge", "running:n1_scavenge"}, {"running:n1_cut"})
STAGES["23_she_walks"] = STAGES["22_offer"].then({"running:n1_walk_ridge"}, {"running:n1_cut"})
STAGES["24_news"] = STAGES["22_offer"].then({"feature:cart_news", "running:n1_forage"}, {"running:n1_cut"}, walk=1)
# Day three (app/ashfall_app/opening/day_three.toml; the list is content/team/day-three.md's, Art). Facts the page
# reads off the view: the trip's card running puts the figure away, a staged build's pushes show its stages.
STAGES["25_edge"] = STAGES["24_news"].then({"running:walk_edge"})
STAGES["26_track"] = STAGES["24_news"].then({"project:walk_edge", "feature:track_open", "running:field_track",
                                             "pushes:field_track@1"})
STAGES["26_track_home"] = STAGES["26_track"].then({"pushes:larder_floor@1", "running:larder_floor", "pushes:field_track@3"},
                                                  {"running:field_track"})
STAGES["27_night_three"] = STAGES["26_track_home"].then({"action:evening_3", "feature:night_3", "pushes:larder_floor@2",
                                                         "pushes:rack_roof@1", "pushes:raised_bed@1"}, {"running:larder_floor"})
STAGES["28_hearth"] = STAGES["27_night_three"].then({"feature:morning_4", "pushes:clay_hearth@1", "pushes:larder_floor@3",
                                                     "pushes:rack_roof@2", "pushes:raised_bed@2", "project:watch_fire",
                                                     "feature:dead_field", "running:clay_hearth"})
STAGES["28_digging"] = STAGES["28_hearth"].then({"running:dig_clay"}, {"running:clay_hearth"})
STAGES["29_stranger"] = STAGES["28_hearth"].then({"feature:stay_offer", "pushes:clay_hearth@3", "pushes:field_track@6"},
                                                 {"running:clay_hearth"})
STAGES["30_three"] = STAGES["29_stranger"].then({"feature:n2_joined", "pushes:raised_bed@3", "pushes:clay_hearth@4",
                                                 "pushes:watch_fire@2", "project:n2_build_bay"})
STAGES["30_bay_going_up"] = STAGES["29_stranger"].then({"feature:n2_joined", "running:n2_build_bay"}, {"running:n1_forage"})
STAGES["31_warm_ground"] = STAGES["30_three"].then({"action:evening_4", "feature:night_4", "feature:warm_ground"})
# Days four to seven (app/ashfall_app/opening/{day_four,day_five,b7,day_six}.toml; the lists are
# content/team/days-four-to-seven.md's, Art, with combat-open.md C9 and banked-time-open.md BT3).
STAGES["32_fog"] = STAGES["31_warm_ground"].then({"feature:morning_5", "feature:fog_5", "feature:fog_open", "running:woodshed",
                                                  "pushes:woodshed@1", "running:n1_forage"})
STAGES["33_sign"] = STAGES["32_fog"].then({"feature:fog_2h", "feature:wolf_sign", "pushes:woodshed@2", "running:n2_watch"},
                                          {"running:woodshed"})
STAGES["34_stone_hand"] = STAGES["33_sign"].then({"action:night_5", "feature:night_5", "feature:arcana", "pushes:woodshed@3",
                                                  "running:hand_on_stone"}, {"running:n2_watch", "running:n1_forage"})
STAGES["35_ridge"] = STAGES["34_stone_hand"].then({"feature:morning_6", "feature:ridge", "pushes:hearth_stones@1",
                                                   "pushes:hearth_stones@2"}, {"running:hand_on_stone"})
STAGES["35_pair"] = STAGES["35_ridge"].then({"feature:pair_offer", "pushes:hearth_stones@3"})
STAGES["36_bay_going_up"] = STAGES["35_pair"].then({"running:make_bay2"})
STAGES["36_five"] = STAGES["35_pair"].then({"feature:pair_joined", "pushes:n3_dig_bed@1", "pushes:n3_dig_bed@2",
                                            "feature:turned_ground", "project:make_bay2"})
STAGES["36_digging"] = STAGES["36_five"].then({"running:n3_dig_bed"}, {"running:n3_gather"})
STAGES["37_wolves"] = STAGES["36_five"].then({"action:night_6", "feature:night_6", "feature:wolves", "pushes:n3_dig_bed@3"},
                                             {"running:n3_dig_bed"}, smoked=27, catch=13, b7_clock=10)
STAGES["38_bare_rack"] = STAGES["37_wolves"].then({"feature:combat"}, {}, smoked=0, catch=0, b7_clock=0)
STAGES["39_hunt"] = STAGES["38_bare_rack"].then({"feature:morning_7", "running:hunt_wolf", "project:make_spear",
                                                 "feature:first_pelt", "pushes:pelt_bedding@1"}, {}, pelt=1, smoked=4)
STAGES["40_night_seven"] = STAGES["39_hunt"].then({"action:night_7", "feature:night_7", "project:give_pelt",
                                                   "pushes:pelt_bedding@2", "pushes:pelt_bedding@3"}, {"running:hunt_wolf"},
                                                  pelt=3, smoked=18)
# Days eight and nine (app/ashfall_app/opening/{day_eight,day_nine}.toml; the list is content/team/week-two.md's, Art).


def _built(card: str, n: int) -> set[str]:
    return {f"pushes:{card}@{k}" for k in range(1, n + 1)}


STAGES["41_drift"] = STAGES["40_night_seven"].then({"feature:drift", "action:ashfall", "running:n3_pick", "project:woodcutting"} | _built("palisade", 2),
                                                   {"running:n3_dig_bed"}, drift_left=330, bloom=1990, stakes=9)
STAGES["42_ash_roofs"] = STAGES["41_drift"].then({"chip:ash_laden", "running:n4_cord", "running:palisade"} | _built("palisade", 3),
                                                 {"running:n3_pick"}, drift_left=320, stakes=14)
STAGES["42_roofs_cleared"] = STAGES["42_ash_roofs"].then({"feature:roofs_cleared", "running:n3_ash_ground"},
                                                         {"chip:ash_laden", "running:palisade"}, ash=4, ashed_ground=1)
STAGES["43_pack_gap"] = STAGES["42_roofs_cleared"].then({"feature:pack_near", "action:pack"} | _built("palisade", 5),
                                                        {"running:n4_cord", "running:n3_ash_ground"}, stakes=4)
STAGES["44_journal"] = STAGES["43_pack_gap"].then({"feature:b9", "action:b9_clock"}, b9_clock=3, pack_fought=1)
STAGES["45_ring_half"] = STAGES["44_journal"].then({"action:snare_4", "action:e2_strip", "running:n4_cord"}
                                                   | _built("palisade", 6) | _built("gap_fire", 2), b9_clock=9, e2_clock=6)
STAGES["45_smoke"] = STAGES["45_ring_half"].then(_built("palisade", 9), {"running:n4_cord"}, b9_clock=20, e2_clock=0,
                                                 stakes=20)
STAGES["46_ring_closed"] = STAGES["45_smoke"].then({"feature:ring_closed", "feature:safety", "action:stranger_clock"}
                                                   | _built("palisade", 12),
                                                   b9_clock=30, stakes=6)
# Day eleven (app/ashfall_app/opening/day_eleven.toml; the list is content/team/week-two.md's, Art).
STAGES["47_family"] = STAGES["46_ring_closed"].then({"action:stranger_clock", "running:make_hut"}, stranger_clock=20,
                                                    stakes=0)
STAGES["47_they_build"] = STAGES["47_family"].then({"running:n5_build_hut"}, {"running:make_hut"})
STAGES["47_joined"] = STAGES["47_family"].then({"feature:family_joined", "action:z1_clock", "project:make_hut"},
                                               {"running:make_hut"}, stranger_clock=80, stakes=9)
STAGES["48_guard"] = STAGES["47_joined"].then({"project:arm_n2", "running:n2_guard", "running:n6_posts"}, guard_made=1,
                                              stranger_clock=200, z1_clock=100)
STAGES["48_guard_n7"] = STAGES["47_joined"].then({"project:arm_n7", "running:n7_guard"}, guard_made=1,
                                                 stranger_clock=200, z1_clock=100)
STAGES["48_count"] = STAGES["48_guard"].then(drop={"running:n6_posts"}, stranger_clock=410)
STAGES["49_dusk"] = STAGES["48_count"].then({"action:night_12"}, stranger_clock=440)
STAGES["49_vigil"] = STAGES["49_dusk"].then({"project:keep_vigil", "pushes:keep_vigil@1", "feature:b11"},
                                            stranger_clock=460, night_12=20)
# Day twelve (app/ashfall_app/opening/day_twelve.toml; the list is content/team/week-two.md's, Art).
STAGES["50_pyre"] = STAGES["49_vigil"].then({"feature:dig", "action:dig_clock", "action:morning_13", "running:dig_cellar"},
                                           dig_clock=1, morning_13=10)
STAGES["50_dig"] = STAGES["50_pyre"].then({"pushes:dig_cellar@1"}, dig_clock=3, morning_13=20)
STAGES["50_sign"] = STAGES["50_dig"].then({"action:bear_season", "pushes:dig_cellar@2"}, {"running:dig_cellar"},
                                          dig_clock=5, bear_sign=6)
STAGES["50_hunt"] = STAGES["50_sign"].then({"running:hunt_bear"})
STAGES["50_steps"] = STAGES["50_sign"].then({"project:hunt_bear", "pushes:dig_cellar@3", "running:dig_cellar"},
                                            bear_sign=5, tallow=2)
STAGES["50_cellar"] = STAGES["50_steps"].then({"pushes:dig_cellar@4", "project:dig_cellar", "feature:cellar",
                                              "running:tallow_lamps", "pushes:tallow_lamps@1"}, {"running:dig_cellar"},
                                             tallow=0)
STAGES["51_lamps"] = STAGES["50_cellar"].then(_built("tallow_lamps", 3) | {"project:tallow_lamps"},
                                            {"running:tallow_lamps"}, drift_clock=140)
STAGES["51_sitter"] = STAGES["51_lamps"].then({"feature:sitter"}, drift_clock=150)
STAGES["52_night_fourteen"] = STAGES["51_sitter"].then({"action:night_14"}, drift_clock=163, night_14=20)
STAGES["52_week_end"] = STAGES["52_night_fourteen"].then({"project:sit_last_night", "feature:week_two_end"})
# Day fifteen (app/ashfall_app/opening/day_fifteen.toml; content/team/week-three.md, Art): the hall's states.
STAGES["56_hall_raised"] = STAGES["52_week_end"].then({"running:hall"} | _built("hall", 2))
STAGES["56_hall_walls"] = STAGES["56_hall_raised"].then(_built("hall", 4))
STAGES["56_hall_roofing"] = STAGES["56_hall_walls"].then(_built("hall", 6))
STAGES["57_hall_built"] = STAGES["56_hall_roofing"].then(_built("hall", 8) | {"project:hall"}, {"running:hall"})
# Builds finished on the day each can be (day-three.md, week-two.md and week-three.md, Art), then all of them at once.
STAGES["31_stack_shelf"] = STAGES["31_warm_ground"].then(_built("wood_stack", 3) | _built("pot_shelf", 3)
                                                         | {"project:wood_stack", "project:pot_shelf"})
STAGES["42_flaps"] = STAGES["42_roofs_cleared"].then(_built("hide_flaps", 4) | {"project:hide_flaps"})
STAGES["48_posts_set"] = STAGES["48_count"].then({"project:n6_posts"})
STAGES["58_sown"] = STAGES["57_hall_built"].then(_built("n3_sow", 1))
STAGES["58_green"] = STAGES["58_sown"].then(_built("n3_sow", 3))
STAGES["58_ripe"] = STAGES["58_green"].then(_built("n3_sow", 6) | {"project:n3_sow"})
STAGES["59_hall_hearth"] = STAGES["58_ripe"].then({"project:hall_hearth"})
STAGES["60_road_cut"] = STAGES["59_hall_hearth"].then(_built("cut_road", 3))
STAGES["60_road_half"] = STAGES["60_road_cut"].then(_built("cut_road", 6))
STAGES["60_road_far"] = STAGES["60_road_half"].then(_built("cut_road", 8))
STAGES["61_road_head"] = STAGES["60_road_far"].then(_built("cut_road", 10) | {"project:cut_road"})
STAGES["62_cloths"] = STAGES["61_road_head"].then(_built("cut_over", 3) | {"project:road_cloths"})
STAGES["63_over_top"] = STAGES["62_cloths"].then(_built("cut_over", 6) | {"project:cut_over"})
STAGES["64_all_built"] = STAGES["63_over_top"].then(STAGES["31_stack_shelf"].facts - STAGES["31_warm_ground"].facts
                                                    | STAGES["42_flaps"].facts - STAGES["42_roofs_cleared"].facts
                                                    | {"project:n6_posts"})
# The later people's moments (people_layers.py), each on the finished camp.
_ALL = STAGES["64_all_built"]
STAGES["65_sowing"] = _ALL.then({"running:n3_sow"})
STAGES["65_pulled_rows"] = _ALL.then({"action:rows_black"}, rows_black_left=6)
STAGES["65_sun"] = _ALL.then(torn_clock=3)
STAGES["65_deer"] = _ALL.then(clear_clock=18)
STAGES["65_table"] = _ALL.then({"action:table"})
STAGES["65_pot"] = _ALL.then(choir_clock=3)
STAGES["65_hauling"] = _ALL.then(ashwood_trips=1)
STAGES["65_racks"] = _ALL.then({"running:n3_wash_meat"})
STAGES["65_stone"] = _ALL.then(kept_clock=30)
STAGES["65_stranger"] = _ALL.then({"feature:stranger_home"})
STAGES["65_bedesman"] = STAGES["65_stranger"].then({"feature:bedesman_home"})
STAGES["65_groups"] = _ALL.then({"running:g_field_forage", "running:g_field_pick", "running:g_hearth_watch"})
STAGES["65_singing"] = _ALL.then({"answered:o_choir"}, still_clock=30)
STAGES["65_singing_unanswered"] = _ALL.then(still_clock=30)
STAGES["66_ash_and_cord"] = _ALL.then(drift_clock=12)
STAGES["66_naming"] = STAGES["65_stranger"].then(drift_clock=16, choir_clock=7, sorrel_clock=6)
STAGES["66_bowl"] = _ALL.then(drift_clock=16, choir_clock=7, sorrel_clock=10, kept_clock=8)
STAGES["66_after_the_moments"] = _ALL.then(drift_clock=16, choir_clock=7, sorrel_clock=10, kept_clock=11)
# The one-off moments of people_moments.py, each in its window, by day and by night.
_NIGHT = _ALL.then({"action:night_14"}, night_14=20)
_DAY = _ALL.then({"action:morning_13"}, {"action:night_12", "action:night_14"}, night_12=0, night_14=0)
for _name, _clock in (("shed", "shed_stack_clock"), ("his_watch", "his_watch_clock"), ("old_watch", "old_watch_clock"),
                      ("spear", "spear_clock"), ("thorn", "thorn_clock"), ("caps", "caps_clock"), ("posts", "posts_clock")):
    STAGES[f"67_{_name}"] = State(_DAY.facts, (*_DAY.stores, (_clock, 4)))
    STAGES[f"67_{_name}_night"] = State(_NIGHT.facts, (*_NIGHT.stores, (_clock, 4)))
STAGES["67_seed"] = _DAY.then(pair_3h=24)
STAGES["67_seed_night"] = _NIGHT.then(pair_3h=24)
STAGES["67_sacking"] = _NIGHT.then({"answer:o_pelt_keep", "feature:night_7"})
STAGES["67_none"] = _DAY
for _name, _clock in (("bedding", "bedding_4_clock"), ("pelt_ask", "pelt_ask_clock"), ("stage_7", "stage_7_clock"),
                      ("posts_cord", "posts_cord_clock"), ("n6_posts_done", "n6_posts_done_clock"), ("choir_2", "choir_2_clock"),
                      ("road_pair", "road_pair_clock"), ("fiddle_2", "fiddle_2_clock")):
    STAGES[f"68_{_name}"] = State(_DAY.facts, (*_DAY.stores, (_clock, 4)))
    STAGES[f"68_{_name}_night"] = State(_NIGHT.facts, (*_NIGHT.stores, (_clock, 4)))
STAGES["67_none_night"] = _NIGHT
# The crews' work (people_crews.py): the beds reaped, and the pot and fish worked, by everyone who could be there.
_JOINED = {"joined:" + f"n{n}" for n in (8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22)}
STAGES["69_reaping"] = _ALL.then(_JOINED | {"running:g_field_reap", "running:g_hearth_reap"})
STAGES["69_cooking"] = _ALL.then(_JOINED | {"running:g_road_fungus_stew", "running:g_road_fog_fish"})
STAGES["69_before_the_join"] = _ALL.then({"running:g_field_reap", "running:g_hearth_reap", "running:g_road_fungus_stew"})


def holds(cond: str | None, state: State) -> bool:
    """The page's rule (app/client/src/scene/conditions.ts) over a composite's State."""
    if cond is None or cond == "always":
        return True
    if "|" in cond:
        return any(holds(c, state) for c in cond.split("|"))
    if "&" in cond:
        return all(holds(c, state) for c in cond.split("&"))
    if cond.startswith("store:"):
        store, _, n = cond[len("store:"):].partition("@")
        lo, _, hi = (n or "1").partition("..")
        held = dict(state.stores).get(store, 0)
        return held >= int(lo) and (not hi or held < int(hi))
    return cond in state.facts


CONDITIONS = {
    "always": "shown from the start",
    "project:<id>": "the project has completed at least once",
    "pushes:<id>@<n>": "the project has had at least n of its pushes",
    "running:<id>": "the project is running now (a lane is working on it)",
    "mix:<id>": "the card runs in the active mix (a share above 0, not paused or yielded) and it is its turn at the figure: the mix's cards take turns, each for its share of a 30 s round",
    "store:<id>": "the store holds at least one item",
    "store:<id>@<n>": "the store holds at least n items",
    "store:<id>@<a>..<b>": "the store holds at least a items and fewer than b: a window of a count-up clock",
    "chip:<id>": "the chip is showing",
    "feature:<id>": "the feature is unlocked",
    "action:<id>": "the standing action is unlocked (it runs by itself from then on)",
    "answered:<offer>": "the offer has been answered, by any answer",
    "answer:<answer>": "that answer was the one given",
    "joined:<lane>": "the lane's person has joined the town",
    "left:<lane>": "the lane's person has left the town for good",
    "end:showing": "the end has happened: the end feature was unlocked with every ledger line covered (it never clears)",
    "<a>|<b>|...": "any of the conditions holds",
    "<a>&<b>&...": "all of the conditions hold; binds tighter than |, so a&b|c is (a and b) or c",
}


KINDS = {"always", "project", "pushes", "running", "mix", "store", "end", "chip", "feature", "action", "answered", "answer", "joined", "left"}
"""The condition kinds the page knows (app/client/src/scene/conditions.ts)."""
