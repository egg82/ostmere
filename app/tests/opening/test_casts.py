"""A role cast from per-lane counts (api/contract/casting.txt, "CASTING"): the loader's side. The `casts` part names a role and
town-card patterns; the loader gives it every candidate lane's feature and cards, refuses a text naming the role where it
can show before the cast, and the content serves each role's lanes."""
import pytest

from ashfall_app.api.service import Game
from ashfall_app.engine import CardId, FeatureId, LaneId
from ashfall_app.opening import convert
from ashfall_app.opening.cast_checks import check_cast_text, check_casts
from ashfall_app.opening.casts import candidates, with_cast_picks
from ashfall_app.opening.checks import check_content, check_opening
from ashfall_app.opening.entries import ConditionEntry, OutcomeEntry, TriggerEntry, UnlockEntry
from ashfall_app.opening.lane_entries import LaneLabelEntry
from ashfall_app.opening.move_entries import CastEntry
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset

PATTERNS = ["{lane}_forage", "{lane}_gather"]
LINE = "line.cast_test"


def then(o: Opening, **text: str) -> Opening:
    return o.model_copy(update={"text": {**o.text, **text}, "line_kinds": {**o.line_kinds, **{k: "story" for k in text if k.startswith("line.")}}})


def casting(o: Opening, role: str = "scout", patterns: list[str] | None = None, line: str | None = None,
            where: str = "t_cast_test") -> Opening:
    """`o` with one more trigger that casts `role` by `patterns`, its line `line` when given."""
    out = OutcomeEntry(casts=[CastEntry(role=role, patterns=PATTERNS if patterns is None else patterns)],
                       line_keys=[] if line is None else [line])
    trigger = TriggerEntry(id=where, when=ConditionEntry(test="after_time", value=1), outcome=out)
    return with_cast_picks(o.model_copy(update={"triggers": [*o.triggers, trigger]}))


def refused(o: Opening, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        check_casts(o)


def test_a_cast_passes_the_checks_and_the_loader_gives_it_every_person_and_their_cards(shipped_opening: Opening):
    o = casting(shipped_opening)
    check_opening(o)
    (cast,) = [c for t in o.triggers for c in t.outcome.casts]
    people = [x.id for x in o.lanes if x.ruled and not x.pooled and not x.station and x.name_key is not None]
    assert candidates(o) == people and people[:3] == ["n1", "n2", "n3"] and "g_field" not in people and "pot" not in people
    assert [p.lane for p in cast.picks] == people and cast.picks[1].feature == "scout_n2"
    counted = {p.lane: p.counted for p in cast.picks}
    assert counted["n2"] == ["n2_forage", "n2_gather"] and counted["n1"] == [None, None]
    engine = convert.build_rules(o)
    made = next(t for t in engine.triggers if t.id == "t_cast_test").outcome.casts[0]
    assert made.role == "scout" and made.picks[1].counted == (CardId("n2_forage"), CardId("n2_gather"))
    assert made.picks[1].feature == FeatureId("scout_n2") and made.picks[0].lane == LaneId("n1")


def test_a_group_or_a_station_is_never_a_candidate_whatever_it_is_named(shipped_opening: Opening):
    """Control: planted names make both look like people; the group's own check, which refuses that, is not run."""
    named = [x.model_copy(update={"name_key": "name_n2"}) if x.id in ("g_field", "pot") else x for x in shipped_opening.lanes]
    o = shipped_opening.model_copy(update={"lanes": named})
    assert next(x for x in o.lanes if x.id == "pot").name_key == "name_n2"
    assert candidates(o) == candidates(shipped_opening) and len(candidates(o)) > 10


def test_the_content_serves_each_role_with_its_lanes_in_join_order(shipped_opening: Opening):
    o = casting(shipped_opening)
    infos = Game(o, ruleset(o, "test", 1)).content().cast_infos
    assert [i.role for i in infos] == ["scout"]
    assert [(x.lane, x.feature) for x in infos[0].lanes][:2] == [("n1", "scout_n1"), ("n2", "scout_n2")]
    assert Game(shipped_opening, ruleset(shipped_opening, "test", 1)).content().cast_infos == []


def test_the_part_declares_the_features_a_condition_or_a_label_may_name(shipped_opening: Opening):
    o = casting(shipped_opening)
    ok = o.model_copy(update={"aims": [*o.aims, o.aims[0].model_copy(update={
        "id": "aim_cast_test", "after": UnlockEntry(unlock_kind="feature", id="scout_n2")})]})
    check_opening(ok)
    unknown = o.model_copy(update={"aims": [*o.aims, o.aims[0].model_copy(update={
        "id": "aim_cast_test", "after": UnlockEntry(unlock_kind="feature", id="scout_g_field")})]})
    with pytest.raises(ValueError, match="unknown feature scout_g_field"):
        check_opening(unknown)


def test_the_refusals(shipped_opening: Opening):
    o = shipped_opening
    refused(casting(o, role="n2"), "casts n2, which names a lane or a slot the page fills elsewhere")
    refused(casting(o, role="card"), "casts card, which names a lane or a slot the page fills elsewhere")
    refused(casting(o, role="two words"), "casts two words, which is not a word")
    refused(casting(o, patterns=["{lane}_nothing"]), "casts scout by {lane}_nothing, which is no town card's id pattern")
    refused(casting(o, patterns=["{lane}_forage", "{lane}_forage"]), "casts scout by {lane}_forage twice")
    twice = casting(casting(o), where="t_cast_again")
    refused(twice, "trigger t_cast_again: casts scout, which another outcome already casts")
    with pytest.raises(ValueError):
        CastEntry(role="scout", patterns=[])
    with pytest.raises(ValueError, match="the loader's"):
        CastEntry.model_validate({"role": "scout", "patterns": PATTERNS, "picks": []})
    card = o.cards[0].model_copy(update={"outcome": OutcomeEntry(casts=[CastEntry(role="scout", patterns=PATTERNS)])})
    refused(o.model_copy(update={"cards": [card, *o.cards[1:]]}), f"card {card.id}: only a trigger's or an answer's outcome casts")


def test_a_town_cards_requires_read_its_own_lanes_feature(shipped_opening: Opening):
    entry = next(t for t in shipped_opening.town_cards if t.id == "{lane}_forage")
    gated = entry.model_copy(update={"requires": [ConditionEntry(
        test="at_least", subject_kind="unlocked", unlock_kind="feature", id="scout_{lane}", value=1)]})
    cards = {c.lane: c for c in (gated.card(x) for x in gated.lanes)}
    assert cards["n2"].requires[0].id == "scout_n2" and cards["n3"].requires[0].id == "scout_n3"
    assert entry.card("n2").requires == [] or all(r.id != "scout_n2" for r in entry.card("n2").requires)


def with_slot(o: Opening, line: str | None = None) -> Opening:
    """`o` with a text whose line holds the role's slot, and a trigger that casts the role, telling `line`."""
    return casting(then(o, **{LINE: "{scout} looks up."}), line=line)


def text_refused(o: Opening, key: str) -> None:
    with pytest.raises(ValueError, match=rf"text {key}: holds the slot \{{scout\}}, which can show before scout is cast"):
        check_content(o)


def test_the_slot_is_allowed_in_the_casting_outcomes_lines(shipped_opening: Opening):
    check_opening(with_slot(shipped_opening, LINE))


def test_the_slot_in_a_text_that_can_show_before_the_cast_fails_naming_the_key(shipped_opening: Opening):
    o = with_slot(shipped_opening)
    elsewhere = TriggerEntry(id="t_other", when=ConditionEntry(test="after_time", value=2), outcome=OutcomeEntry(line_keys=[LINE]))
    text_refused(o.model_copy(update={"triggers": [*o.triggers, elsewhere]}), LINE)
    card = o.cards[0]
    label = then(o, **{"label.cast_test": "{scout}'s turn"})
    labelled = label.model_copy(update={"cards": [card.model_copy(update={"label_key": "label.cast_test"}), *o.cards[1:]]})
    text_refused(labelled, "label.cast_test")


def test_the_slot_is_allowed_where_a_feature_of_the_role_gates_it(shipped_opening: Opening):
    o = with_slot(shipped_opening)
    gate = ConditionEntry(test="at_least", subject_kind="unlocked", unlock_kind="feature", id="scout_n2", value=1)
    elsewhere = TriggerEntry(id="t_other", when=gate, outcome=OutcomeEntry(line_keys=[LINE]))
    check_content(o.model_copy(update={"triggers": [*o.triggers, elsewhere]}))
    at_most = elsewhere.model_copy(update={"when": gate.model_copy(update={"test": "at_most"})})
    text_refused(o.model_copy(update={"triggers": [*o.triggers, at_most]}), LINE)
    n2 = next(x for x in o.lanes if x.id == "n2")
    label = LaneLabelEntry(after=UnlockEntry(unlock_kind="feature", id="scout_n2"), label_key=LINE)
    laned = o.model_copy(update={"lanes": [x.model_copy(update={"later_labels": [*x.later_labels, label]}) if x is n2 else x
                                           for x in o.lanes]})
    check_cast_text(laned, [("lane n2", LINE)])
    with pytest.raises(ValueError, match="holds the slot"):
        check_cast_text(laned, [("lane n3", LINE)])


def test_a_slot_of_a_role_nothing_casts_fails_as_any_unknown_slot(shipped_opening: Opening):
    with pytest.raises(ValueError, match=r"holds the slot \{scout\}, which nothing fills"):
        check_content(then(shipped_opening, **{"line.unused_cast": "{scout} waits."}))
