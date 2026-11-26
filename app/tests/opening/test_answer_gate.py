"""Every answer keeps a consequence (opening/answer_checks.py): the answers of an offer differ by a lasting part, and
each role of a kinded offer names a tally. What fails in the shipped content is held in tests/held/answers.json, per
offer or kind, and the list only shrinks: `python -m tests.opening.test_answer_gate --write` (from app/) lowers it
once one is fixed; never run it to let a new one through."""
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from ashfall_app.engine import (
    QUANTITY_SCALE as Q, Rules, Save, StoreId, Unlock, UnlockKind, encode, new_save, rebase,
)
from ashfall_app.opening.answer_checks import check_tally_stores, unlasting_offers, untallied_kinds
from ashfall_app.opening.entries import OutcomeEntry
from ashfall_app.opening.offer_entries import KindRoleEntry
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, Opening, load_opening, to_rules
from tests.held_ledger import Ledger, dump, load, problems, tally, total

HELD = Path(__file__).resolve().parents[1] / "held/answers.json"


def full() -> Opening:
    return load_opening(chapters=(*CHAPTERS, *IN_WRITING))


def ledger(o: Opening) -> Ledger:
    return tally([*((x, "answers do not differ") for x in unlasting_offers(o)),
                  *((k, "role names no tally") for k in untallied_kinds(o))])


@pytest.fixture(scope="module")
def content() -> Opening:
    return full()


def test_every_answer_differs_by_a_lasting_part_and_every_role_is_counted(content: Opening):
    assert len(content.offers) > 40 and content.offer_kinds, "checked almost no offers: the check is blind"
    found = problems(ledger(content), load(HELD), "give the answers a sourced modifier, an unlock something reads, "
                     "or a role tally (opening/answer_checks.py)", "python -m tests.opening.test_answer_gate --write")
    assert not found, "\n".join(found)


def test_the_arrival_offers_pass_and_the_held_ones_fail(content: Opening):
    failing = set(unlasting_offers(content))
    assert not failing & {"o_stay", "o_pair", "o_family", "o_cart"}
    assert {"o_pelt", "j_steps"} <= failing
    assert untallied_kinds(content) == ["work"]


def with_outcomes(o: Opening, offer: str, outcome: OutcomeEntry) -> Opening:
    """`o` with every answer of `offer` given one outcome."""
    offers = [x.model_copy(update={"answers": [a.model_copy(update={"outcome": outcome}) for a in x.answers]})
              if x.id == offer else x for x in o.offers]
    return o.model_copy(update={"offers": offers})


def test_answers_with_one_outcome_are_found_and_a_sourced_difference_is_not(content: Opening):
    one = next(a.outcome for x in content.offers if x.id == "o_bank" for a in x.answers)
    assert "o_bank" not in unlasting_offers(content) and "o_bank" in unlasting_offers(with_outcomes(content, "o_bank", one))


def without_tally(o: Opening, kind: str) -> Opening:
    kinds = [k.model_copy(update={"roles": [r.model_copy(update={"tally": None}) for r in k.roles]})
             if k.kind == kind else k for k in o.offer_kinds]
    return o.model_copy(update={"offer_kinds": kinds})


def test_a_role_with_no_tally_is_found_and_the_tally_alone_separates_the_answers(content: Opening):
    unread = content.model_copy(update={"triggers": [t for t in content.triggers if not t.id.startswith("t_kept_")]})
    assert not {"o_pair", "o_family"} & set(unlasting_offers(unread))
    bare = without_tally(unread, "arrival")
    assert untallied_kinds(bare) == ["arrival", "work"]
    assert {"o_pair", "o_family"} <= set(unlasting_offers(bare))


def with_roles(o: Opening, roles: list[KindRoleEntry]) -> Opening:
    kinds = [k.model_copy(update={"roles": roles}) if k.kind == "arrival" else k for k in o.offer_kinds]
    return o.model_copy(update={"offer_kinds": kinds})


def test_a_tally_must_be_a_declared_hidden_tally_store_of_its_own_role(content: Opening):
    check_tally_stores(content)
    own, other = "own_hands", "left_to_them"

    def roles(a: str, b: str) -> list[KindRoleEntry]:
        return [KindRoleEntry(role="self", label_key="k_arrival_self", tally=a),
                KindRoleEntry(role="other", label_key="k_arrival_other", tally=b)]
    for bad, match in [(roles(own, own), "shares tally own_hands"), (roles("nothing", other), "not a declared hidden tally"),
                       (roles("arrivals", other), "not a declared hidden tally")]:
        with pytest.raises(ValueError, match=match):
            check_tally_stores(with_roles(content, bad))


def test_each_answer_adds_one_to_its_roles_tally_and_a_save_that_answered_before_counts_at_rebase(content: Opening):
    new = to_rules(content)
    ids = {"tally_o_stay_room": "own_hands", "tally_o_stay_his": "left_to_them", "tally_o_pair_room": "own_hands",
           "tally_o_pair_hers": "left_to_them", "tally_o_family_room": "own_hands", "tally_o_family_theirs": "left_to_them"}
    assert {str(t.id) for t in new.triggers if str(t.id).startswith("tally_")} == set(ids)
    old = replace(new, triggers=tuple(t for t in new.triggers if str(t.id) not in ids),
                  stores=tuple(s for s in new.stores if str(s.id) not in set(ids.values())))
    s = new_save(old)
    given = {Unlock(UnlockKind.ANSWER, a) for a in ("o_stay_room", "o_pair_hers", "o_family_room")}
    answered = rebase(encode(replace(s, unlocked=(*s.unlocked, *given)), old), new)
    assert {name: _value(answered, new, name) for name in ("own_hands", "left_to_them")} == {"own_hands": 2, "left_to_them": 1}
    assert _value(rebase(encode(s, old), new), new, "own_hands") == 0


def _value(save: Save, rules: Rules, store: str) -> int:
    return next(st.segment.start_value for st in save.stores if st.store == StoreId(store)) // Q


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        led = ledger(full())
        HELD.write_text(dump(led))
        print(f"wrote {HELD.name}: {total(led)} held")
