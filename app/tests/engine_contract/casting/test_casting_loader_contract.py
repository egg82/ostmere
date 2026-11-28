"""The loader's refusals and acceptances for a cast (api/contract/casting.txt, "CASTING", "Content" and "Loader
refusals"). Written blind from that part; the plain chapter loads in every test (the control the refusal edits)."""
from pathlib import Path

import pytest

from casting_world import LEAD, kills, opening_of, refused, rules_of

OTHER_OUTCOME = ('[[triggers]]\nid = "t_second"\nwhen = {{ test = "after_time", value = 400 }}\n'
                 'outcome = {{ casts = [{casts}] }}\n\n')


def second(casts: str) -> str:
    return OTHER_OUTCOME.format(casts=casts)


@kills(15)
@pytest.mark.parametrize("role, why", [("t_a", "a lane"), ("n", "a slot"), ("card", "a slot"), ("pct", "a slot")])
def test_a_role_that_is_a_lane_id_or_a_slot_the_page_fills_is_refused(tmp_path: Path, role: str, why: str):
    refused(tmp_path, rf"casts {role}, which names a lane or a slot the page fills elsewhere",
            casts=f'{{ role = "{role}", label_key = "t_role", patterns = ["{{lane}}_chop"] }}')


@kills(15)
def test_a_role_named_for_the_hands_lane_is_refused(tmp_path: Path):
    refused(tmp_path, r"casts hands, which names a lane or a slot the page fills elsewhere",
            casts='{ role = "hands", label_key = "t_role", patterns = ["{lane}_chop"] }')


@kills(16)
def test_a_role_cast_by_a_second_outcome_is_refused_naming_it(tmp_path: Path):
    refused(tmp_path, r"casts lead, which another outcome already casts", extra=second(LEAD))


@kills(16)
def test_a_role_named_twice_in_one_outcome_is_refused(tmp_path: Path):
    refused(tmp_path, r"casts lead, which another outcome already casts", casts=f"{LEAD}, {LEAD}")


@kills(17)
def test_a_pattern_that_is_no_town_cards_id_is_refused_naming_role_and_pattern(tmp_path: Path):
    refused(tmp_path, r"casts lead by \{lane\}_nothing, which is no town card's id pattern",
            casts='{ role = "lead", label_key = "t_role", patterns = ["{lane}_nothing"] }')


@kills(17)
def test_a_pattern_is_the_town_cards_id_written_exactly_so_a_lanes_own_card_id_is_no_pattern(tmp_path: Path):
    refused(tmp_path, r"casts lead by t_a_chop, which is no town card's id pattern",
            casts='{ role = "lead", label_key = "t_role", patterns = ["t_a_chop"] }')


@kills(18)
def test_a_pattern_named_twice_is_refused(tmp_path: Path):
    refused(tmp_path, r"casts lead by \{lane\}_chop twice",
            casts='{ role = "lead", label_key = "t_role", patterns = ["{lane}_chop", "{lane}_haul", "{lane}_chop"] }')


def test_a_cast_with_no_patterns_is_refused_at_the_entry(tmp_path: Path):
    refused(tmp_path, "patterns", casts='{ role = "lead", label_key = "t_role", patterns = [] }')


@kills(15)
@pytest.mark.parametrize("role", ["1lead", "le-ad", "_lead"])
def test_a_role_that_is_not_a_word_starting_with_a_letter_is_refused_naming_it(tmp_path: Path, role: str):
    refused(tmp_path, rf"casts {role}, which is not a word of letters, digits and underscores",
            casts=f'{{ role = "{role}", label_key = "t_role", patterns = ["{{lane}}_chop"] }}')


def test_an_empty_role_is_refused(tmp_path: Path):
    refused(tmp_path, "which is not a word of letters, digits and underscores", casts='{ role = "", label_key = "t_role", patterns = ["{lane}_chop"] }')


@kills(19)
def test_a_cards_outcome_may_not_cast(tmp_path: Path):
    card = ('[[cards]]\nid = "t_odd"\npresentation = "action"\nlabel_key = "t_c_chop"\nupside_key = "t_up"\nwork_s = 10\n'
            'makes = [{ store = "t_heap", items_per_hour = 2 }]\noutcome = { casts = [' + LEAD + '] }\n\n')
    refused(tmp_path, r"only a trigger's or an answer's outcome casts a role", casts=None, extra=card)


XTEXT = 't_l_x = "Here."\n'
GATE = '{ test = "at_least", subject_kind = "unlocked", unlock_kind = "feature", id = "%s", value = 1 }'


def after_cast(feature: str, key: str = "t_l_x") -> dict[str, str]:
    """A trigger gated on `feature` whose line is `key`."""
    return dict(extra=f'[[triggers]]\nid = "t_after"\nwhen = {GATE % feature}\noutcome = {{ line_keys = ["{key}"] }}\n\n',
                extra_kinds=f'{key} = "story"\n')


@kills(22)
def test_the_loader_accepts_a_cast_feature_of_a_candidate_lane_wherever_a_feature_is_read(tmp_path: Path):
    """An `unlocked` condition and a lane's later label, before the lane has joined."""
    rules_of(tmp_path, extra_text=XTEXT, **after_cast("lead_t_a"))
    later = '{ after = { unlock_kind = "feature", id = "lead_t_c" }, label_key = "t_later" }'
    rules_of(tmp_path, later=later, extra_text='t_later = "Elder"\n')


@kills(22)
@pytest.mark.parametrize("feature", ["lead_t_p", "lead_t_pot", "lead_hands", "lead_t_none", "other_t_a"])
def test_a_cast_feature_of_a_lane_that_is_not_a_single_person_is_unknown(tmp_path: Path, feature: str):
    rules_of(tmp_path, extra_text=XTEXT, **after_cast("lead_t_a"))
    with pytest.raises(ValueError):
        rules_of(tmp_path, extra_text=XTEXT, **after_cast(feature))


def test_a_role_nothing_casts_declares_no_feature(tmp_path: Path):
    with pytest.raises(ValueError):
        rules_of(tmp_path, casts=None, extra_text=XTEXT, **after_cast("lead_t_a"))


SLOT_TEXT = 't_l_x = "{lead} is here."\n'


def test_the_outcomes_own_lines_may_hold_the_slot(tmp_path: Path):
    opening_of(tmp_path, extra_text='t_l_cast = "{lead} takes it up."\n')


@kills(5, 20)
def test_a_text_elsewhere_that_holds_the_slot_is_refused_naming_key_and_slot(tmp_path: Path):
    plain = dict(extra='[[triggers]]\nid = "t_after"\nwhen = { test = "after_time", value = 400 }\n'
                       'outcome = { line_keys = ["t_l_x"] }\n\n', extra_kinds='t_l_x = "story"\n')
    opening_of(tmp_path, extra_text='t_l_x = "Nobody is here."\n', **plain)
    with pytest.raises(ValueError, match=r"text t_l_x: holds the slot \{lead\}, which can show before lead is cast \(in trigger t_after\)"):
        opening_of(tmp_path, extra_text=SLOT_TEXT, **plain)


@kills(5, 20)
def test_a_label_a_lane_takes_once_a_feature_of_the_role_is_unlocked_may_hold_the_slot(tmp_path: Path):
    later = '{ after = { unlock_kind = "feature", id = "lead_t_c" }, label_key = "t_later" }'
    opening_of(tmp_path, later=later, extra_text='t_later = "{lead} the elder"\n')
    elsewhere = '{ after = { unlock_kind = "card", id = "t_a_chop" }, label_key = "t_later" }'
    with pytest.raises(ValueError, match=r"text t_later: holds the slot \{lead\}"):
        opening_of(tmp_path, later=elsewhere, extra_text='t_later = "{lead} the elder"\n')


@kills(5, 20)
def test_a_text_gated_on_a_feature_of_the_role_may_hold_the_slot_and_one_gated_on_another_role_may_not(tmp_path: Path):
    scout = '{ role = "scout", label_key = "t_role", patterns = ["{lane}_haul"] }'
    opening_of(tmp_path, casts=f"{LEAD}, {scout}", extra_text=SLOT_TEXT, **after_cast("lead_t_a"))
    with pytest.raises(ValueError, match=r"text t_l_x: holds the slot \{lead\}"):
        opening_of(tmp_path, casts=f"{LEAD}, {scout}", extra_text=SLOT_TEXT, **after_cast("scout_t_a"))
