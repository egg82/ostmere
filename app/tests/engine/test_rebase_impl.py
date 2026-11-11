"""The rebase's implementation choices beside the blind contract suite (engine_contract/test_rebase.py): the manifest,
the format chain, renames reaching every id, and the steps that keep what a save earned (DESIGN.txt, part SAVES
ACROSS RELEASES)."""
import json
from dataclasses import replace

import pytest

from ashfall_app.engine import (
    BP, FORMAT, OLDEST_FORMAT, UPGRADES, ActionId, AtLeast, AtMost, CardCount, CardDef, CardId, CardShare, ChipDef,
    ChipId, Flow, FlowKind, IdKind, LaneDef, LaneId, LaneSpeed, LineKey, Mix, MixId, Modifier, ModifierKind,
    Order, Outcome, PacingCurve, QueueEntry, RateRef, RebaseError, Rename, Rules, Running, Save, SaveMix, SetOrders,
    SetQueue, SkillDef, SkillId, SkillLevel, SourceId, StandingDef, StateFormatError, StoreCap, StoreDef, StoreId,
    StoreValue, SwitchMix, TapCard, TriggerDef, TriggerId, Unlock, UnlockKind, Unlocked, WorkRef, advance, decide,
    encode, new_save, rebase, rebase_logged,
)
from ashfall_app.engine import upgrade as upgrade_module
from ashfall_app.engine.codec import Json

Q = 3_600_000


def world(p: str = "", lay_s: int = 40, extra_trigger: bool = False) -> Rules:
    """Small rules touching every kind of id; `p` prefixes every id, so world("n") is world() with all ids renamed."""
    def s(x: str) -> StoreId:
        return StoreId(p + x)
    wood, food, fire = s("wood"), s("food"), ActionId(p + "fire")
    chop, lay = CardId(p + "chop"), CardId(p + "lay")
    rack, skill, chip = LaneId(p + "rack"), SkillId(p + "skill"), ChipId(p + "cold")
    triggers = [TriggerDef(TriggerId(p + "t_wood"), AtLeast(StoreValue(wood), 2 * Q, 2 * Q),
                           Outcome(unlocks=(Unlock(UnlockKind.FEATURE, p + "ledger"),),
                                   modifiers=(Modifier(RateRef(chop, FlowKind.MAKE, wood), ModifierKind.MUL_BP, 15_000,
                                                       SourceId(p + "axe")),),
                                   lines=(LineKey("t_wood.line"),)))]
    if extra_trigger:
        triggers.append(TriggerDef(TriggerId(p + "t_new"), AtLeast(StoreValue(wood), 0, 0),
                                   Outcome(stores=(), lines=(LineKey("t_new.line"),))))
    return Rules(
        stores=(StoreDef(wood, 50 * Q, Q), StoreDef(food, 50 * Q, 10 * Q)),
        skills=(SkillDef(skill),),
        standing=(StandingDef(fire, costs=(Flow(food, 1000),)),),
        curve=PacingCurve((10 * Q, 20 * Q)),
        lanes=(LaneDef(rack),),
        cards=(CardDef(chop, 10, skill=skill, xp_per_hour=1000, makes=(Flow(wood, 36_000),)),
               CardDef(lay, lay_s, lane=rack, cap=5),
               CardDef(CardId(p + "old"), 5)),
        chips=(ChipDef(chip, AtMost(StoreValue(food), 5 * Q, 6 * Q),
                       (Modifier(LaneSpeed(rack), ModifierKind.MUL_BP, 5_000, SourceId(p + "cold")),),
                       LineKey("cold.on"), LineKey("cold.off")),),
        triggers=tuple(triggers),
        opening=None,
    )


def played(r: Rules, p: str = "") -> Save:
    """A save holding a mix, orders and a queue on every subject kind, a tap on the rack, card work, a
    fired trigger, a latched chip and modifiers aimed at every target kind."""
    chop, lay, wood = CardId(p + "chop"), CardId(p + "lay"), StoreId(p + "wood")
    s = new_save(r, (Modifier(WorkRef(chop), ModifierKind.ADD_BP, 100, SourceId(p + "boots")),
                     Modifier(StoreCap(wood), ModifierKind.ADD_BP, 100, SourceId(p + "shed")),
                     Modifier(RateRef(ActionId(p + "fire"), FlowKind.COST, StoreId(p + "food")), ModifierKind.ADD_BP,
                              100, SourceId(p + "hearth"))))
    s = decide(s, r, 0, SaveMix(Mix(MixId("mine"), (CardShare(chop, 6000),))))
    s = decide(s, r, 0, SwitchMix(MixId("mine")))
    s = decide(s, r, 0, SetOrders((
        Order(AtLeast(SkillLevel(SkillId(p + "skill")), 3, 3), TapCard(lay)),
        Order(AtLeast(CardCount(lay), 9, 9), TapCard(lay)),
        Order(AtLeast(Running(ActionId(p + "fire")), 2, 2), TapCard(lay)),
        Order(AtLeast(Unlocked(Unlock(UnlockKind.FEATURE, p + "ledger")), 2, 2), TapCard(lay)),
    )))
    s = decide(s, r, 0, SetQueue((QueueEntry(SwitchMix(MixId("mine")), AtLeast(StoreValue(StoreId(p + "food")), 49 * Q, 49 * Q)),)))
    s = decide(s, r, 100, TapCard(lay))
    return advance(decide(s, r, 30_000, TapCard(lay)), r, 30_010)


def renames(p: str) -> tuple[Rename, ...]:
    return tuple(Rename(k, x, p + x) for k, x in (
        (IdKind.STORE, "wood"), (IdKind.STORE, "food"), (IdKind.STANDING, "fire"), (IdKind.CARD, "chop"),
        (IdKind.CARD, "lay"), (IdKind.CARD, "old"), (IdKind.LANE, "rack"), (IdKind.SKILL, "skill"),
        (IdKind.CHIP, "cold"), (IdKind.TRIGGER, "t_wood"), (IdKind.FEATURE, "ledger"), (IdKind.SOURCE, "axe"),
        (IdKind.SOURCE, "boots"), (IdKind.SOURCE, "shed"), (IdKind.SOURCE, "hearth"), (IdKind.SOURCE, "cold")))


def test_the_world_reaches_every_kind_of_state():
    s = played(world())
    assert any(ls.card is not None for ls in s.lanes) and s.cards and s.mixes and s.queue
    assert s.fired[0] and s.chips[0], (s.fired, s.chips)


def test_renaming_every_id_gives_the_save_played_under_the_renamed_rules():
    """Renames reach every id: the old save, rebased onto world("n") with every id renamed, is the save the same play
    gives under world("n")."""
    old, new = world(), world("n")
    assert rebase(encode(played(old), old), new, renames("n")) == played(new, "n")


def test_the_manifest_is_the_rules_slice():
    r = world()
    doc = json.loads(encode(new_save(r), r))
    assert doc["manifest"] == {
        "stores": [{"id": "wood", "cap": 50 * Q}, {"id": "food", "cap": 50 * Q}], "skills": ["skill"],
        "standing": ["fire"], "lanes": ["rack"],
        "cards": [{"id": "chop", "work_s": 10, "lane": "hands", "cap": None},
                  {"id": "lay", "work_s": 40, "lane": "rack", "cap": 5},
                  {"id": "old", "work_s": 5, "lane": "hands", "cap": None}],
        "chips": ["cold"], "triggers": ["t_wood"], "features": ["ledger"], "offers": []}


def test_a_dropped_id_raises_and_names_it():
    old = world()
    s = played(old)
    with pytest.raises(RebaseError) as e:
        rebase(encode(s, old), replace(old, chips=()))
    assert (e.value.kind, e.value.id) == (IdKind.CHIP, "cold")


def test_a_fired_trigger_stays_fired_and_lands_nothing_again():
    """A retuned trigger (its condition changed) that had fired: still fired, its outcome not applied twice."""
    old = world()
    s = played(old)
    new = replace(old, triggers=(TriggerDef(old.triggers[0].id, AtLeast(StoreValue(StoreId("wood")), Q, Q),
                                            old.triggers[0].outcome),))
    step = rebase_logged(encode(s, old), new, ())
    assert step.save.fired == (True,) and step.lines == ()
    assert step.save.modifiers == s.modifiers


def test_a_new_trigger_fires_at_the_save_time_with_its_line():
    old, new = world(), world(extra_trigger=True)
    s = played(old)
    step = rebase_logged(encode(s, old), new, ())
    assert step.save.fired == (True, True)
    assert [(ln.time, ln.seq, ln.key) for ln in step.lines] == [(s.time, 0, "t_new.line")]


def test_a_retuned_card_keeps_completions_and_its_bar_fraction():
    old, new = world(), world(lay_s=70)
    s = played(old)
    w = next(cs.work.start_value for cs in s.cards if cs.card == "lay")
    n, rem = divmod(w, 40 * BP)
    assert n >= 1 and rem > 0, (n, rem)
    got = next(cs.work.start_value for cs in rebase(encode(s, old), new, ()).cards if cs.card == "lay")
    assert got == n * 70 * BP + rem * 70 // 40


def test_a_card_moved_off_its_lane_frees_the_lane_and_keeps_its_work():
    old = world()
    s = played(old)
    assert next(ls for ls in s.lanes if ls.lane == "rack").card == "lay"
    moved = replace(old, cards=tuple(CardDef(c.id, c.work_s, cap=c.cap) if c.id == "lay" else c for c in old.cards))
    s2 = rebase(encode(s, old), moved, ())
    assert next(ls for ls in s2.lanes if ls.lane == "rack").card is None
    assert next(cs for cs in s2.cards if cs.card == "lay").work.start_value == next(
        cs for cs in s.cards if cs.card == "lay").work.start_value


def test_a_new_store_and_skill_start_fresh_and_old_ones_keep_their_values():
    old = world()
    s = played(old)
    new = replace(old, stores=(StoreDef(StoreId("stone"), 9 * Q, 4 * Q), *old.stores),
                  skills=(*old.skills, SkillDef(SkillId("new_skill"))))
    s2 = rebase(encode(s, old), new, ())
    values = {st.store: st.segment.start_value for st in s2.stores}
    assert values[StoreId("stone")] == 4 * Q and all(values[st.store] == st.segment.start_value for st in s.stores)
    assert [st.skill for st in s2.skills] == ["skill", "new_skill"] and s2.skills[1].xp.start_value == 0


def test_a_rename_cycle_raises():
    old = world()
    with pytest.raises(RebaseError):
        rebase(encode(played(old), old), world("n"), (Rename(IdKind.STORE, "wood", "x"), Rename(IdKind.STORE, "x", "wood")))


def test_same_rules_is_decode_whatever_the_renames():
    r = world()
    s = played(r)
    assert rebase(encode(s, r), r, renames("n")) == s and rebase_logged(encode(s, r), r, renames("n")).lines == ()


@pytest.mark.parametrize("fmt", [OLDEST_FORMAT - 1, FORMAT + 1, 0, "4", True])
def test_a_format_outside_the_readable_range_raises(fmt: Json):
    r = world()
    doc = json.loads(encode(new_save(r), r))
    doc["format"] = fmt
    with pytest.raises(StateFormatError):
        rebase(json.dumps(doc, sort_keys=True, separators=(",", ":")), world("n"), renames("n"))


@pytest.mark.parametrize("edit", ["reformat", "drop_manifest", "short_chips", "bad_manifest"])
def test_a_text_no_encode_gave_raises(edit: str):
    r = world()
    doc = json.loads(encode(played(r), r))
    if edit == "drop_manifest":
        del doc["manifest"]
    elif edit == "short_chips":
        doc["save"]["chips"] = []
    elif edit == "bad_manifest":
        doc["manifest"]["cards"][0]["extra"] = 1
    text = json.dumps(doc) if edit == "reformat" else json.dumps(doc, sort_keys=True, separators=(",", ":"))
    with pytest.raises(StateFormatError):
        rebase(text, world("n"), renames("n"))


def test_upgrades_chain_from_the_oldest_format(monkeypatch: pytest.MonkeyPatch):
    """Every format from OLDEST_FORMAT below FORMAT has an entry; a chain runs each in turn, and a gap raises."""
    assert upgrade_module.missing_upgrades() == [] and all(f in UPGRADES for f in range(OLDEST_FORMAT, FORMAT))

    def step(env: Json) -> Json:
        assert isinstance(env, dict)
        return {**env, "format": FORMAT + 1, "seen": True}
    monkeypatch.setattr(upgrade_module, "FORMAT", FORMAT + 1)
    monkeypatch.setattr(upgrade_module, "UPGRADES", {FORMAT: step})
    assert upgrade_module.upgrade({"format": FORMAT}) == {"format": FORMAT + 1, "seen": True}
    monkeypatch.setattr(upgrade_module, "UPGRADES", {})
    assert upgrade_module.missing_upgrades() == list(range(OLDEST_FORMAT, FORMAT + 1))
    with pytest.raises(StateFormatError):
        upgrade_module.upgrade({"format": FORMAT})
