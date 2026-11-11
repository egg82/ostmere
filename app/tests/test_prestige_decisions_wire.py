"""The prestige verbs and nodes on the wire (api/CONTRACT.txt, "PRESTIGE PHASES"): prestige and undo_pick as
decisions (never order verbs) reaching the engine's verbs, a refusal answered 422 invalid_decision, the row's
pick_owed and topped_at, and Content.node_infos as the content authors them."""
import pytest
from pydantic import TypeAdapter, ValidationError

from ashfall_app import engine as e
from ashfall_app.api import convert
from ashfall_app.api import content_models as cm
from ashfall_app.api import models as w
from ashfall_app.api.error_models import ErrorCode
from ashfall_app.api.errors import GameError
from ashfall_app.api.save_routes import answered
from ashfall_app.api.service import Game
from ashfall_app.opening.prestige import NodeChangeEntry, NodeEntry
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.ruleset import ruleset
from tests.engine.test_prestige_impl import A, GATHER, H, RULES, START

DECISION = TypeAdapter[w.Decision](w.Decision)
ORDER_VERB = TypeAdapter[w.OrderVerb](w.OrderVerb)


def test_prestige_undo_pick_and_move_pick_are_decisions_reaching_the_engines_verbs():
    click = DECISION.validate_python({"kind": "prestige", "skill": "gather", "node": "a"})
    undo = DECISION.validate_python({"kind": "undo_pick", "skill": "gather"})
    assert convert.verb(click, RULES) == e.Prestige(GATHER, A)
    assert convert.verb(undo, RULES) == e.UndoPick(GATHER)
    move = DECISION.validate_python({"kind": "move_pick", "skill": "gather", "node": "a", "to": "b"})
    assert convert.verb(move, RULES) == e.MovePick(GATHER, A, e.NodeId("b"))


@pytest.mark.parametrize("verb", [{"kind": "prestige", "skill": "gather", "node": "a"},
                                  {"kind": "undo_pick", "skill": "gather"},
                                  {"kind": "move_pick", "skill": "gather", "node": "a", "to": "b"}])
def test_neither_is_an_order_or_queue_verb(verb: dict[str, str]):
    ORDER_VERB.validate_python({"kind": "tap_card", "card": "x"})   # control: the adapter takes an order verb
    with pytest.raises(ValidationError):
        ORDER_VERB.validate_python(verb)


def test_a_refused_prestige_is_422_invalid_decision_naming_why(shipped_opening: Opening):
    game = Game(shipped_opening, ruleset(shipped_opening, [], "test", 1))
    with pytest.raises(GameError) as found:
        with answered(game):
            e.decide(START, RULES, H, e.Prestige(GATHER, A))
    assert found.value.status == 422 and found.value.body.code is ErrorCode.INVALID_DECISION
    assert "not_at_top" in found.value.body.message


def bar(save: e.Save) -> w.SkillPrestige:
    row = next(b for b in convert.view(save, e.view(save, RULES)).skills if b.skill == GATHER)
    assert row.prestige is not None
    return row.prestige


def test_the_row_serves_topped_at_and_pick_owed():
    below, topped = bar(START), bar(e.advance(START, RULES, 101 * H))
    assert (below.topped_at, below.pick_owed) == (None, False)
    assert (topped.topped_at, topped.at_top, topped.pick_owed) == (100 * H, True, False)
    clicked = e.decide(START, RULES, 101 * H, e.Prestige(GATHER, A))
    assert (bar(clicked).pick_owed, bar(clicked).undo_open) == (False, True)
    undone = bar(e.decide(clicked, RULES, 101 * H, e.UndoPick(GATHER)))
    assert (undone.pick_owed, undone.undo_open, undone.phase) == (True, False, 2)


def test_content_serves_each_node_as_authored(shipped_opening: Opening):
    def content(o: Opening) -> cm.Content:
        return Game(o, ruleset(shipped_opening, [], "test", 1)).content()

    assert [n.node for n in content(shipped_opening).node_infos] == [n.id for n in shipped_opening.nodes]
    nodes = [NodeEntry(id="n_cap", skill="s", label_key="node.cap", changes=NodeChangeEntry(target="cap", id="wood"),
                       ranks=2, per_rank_bp=500),
             NodeEntry(id="n_make", skill="s", label_key="node.make",
                       changes=NodeChangeEntry(target="make", id="c", store="wood"), ranks=1, per_rank_bp=500)]
    served = content(shipped_opening.model_copy(update={"nodes": nodes})).node_infos
    assert [n.model_dump(mode="json") for n in served] == [
        {"node": "n_cap", "skill": "s", "label_key": "node.cap", "change": {"target": "cap", "id": "wood", "store": None}},
        {"node": "n_make", "skill": "s", "label_key": "node.make",
         "change": {"target": "make", "id": "c", "store": "wood"}}]
