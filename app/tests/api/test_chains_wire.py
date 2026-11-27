"""A working's chain on the wire (api/contract/spells.txt, "SPELLS"), on tests/rules/fixtures/chains.toml merged onto the
opening: the content's chain and group, the view's reach and chained tally, and one LogLine per link in the Step that
carries the completion. The length itself is the engine's (tests/engine/test_chains_impl.py)."""
from dataclasses import replace
from functools import cache
from pathlib import Path

from ashfall_app import engine as e
from ashfall_app.api import models as w
from ashfall_app.api.service import Game
from ashfall_app.api.world import content_models as cm
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules
from ashfall_app.saves.interface import Played
from ashfall_app.saves.ruleset import ruleset

FIXTURE = Path(__file__).resolve().parent.parent / "rules" / "fixtures" / "chains.toml"
JUMP, PROWL = e.CardId("t_jump"), e.ActionId("t_prowl")


@cache
def opening() -> Opening:
    return load_opening(OPENING, (FIXTURE,))


@cache
def rules() -> e.Rules:
    """The fixture with its working, its fight and combat open from the start, and the working's input left out (the
    opening starts with no stones)."""
    base = to_rules(opening())
    assert base.opening is not None
    opened = (*base.opening, e.Unlock(e.UnlockKind.CARD, JUMP), e.Unlock(e.UnlockKind.ACTION, PROWL),
              e.Unlock(e.UnlockKind.FEATURE, e.FeatureId("combat")))
    cards = tuple(replace(c, inputs=()) if c.id == JUMP else c for c in base.cards)
    return replace(base, opening=opened, cards=cards)


@cache
def game() -> Game:
    return Game(opening(), replace(ruleset(opening(), "test", 1), rules=rules()))


def _cast(at: int) -> w.Step:
    """Tap the working at `at` and advance to its landing (the opening's chips may slow the hands: the view says when)."""
    r = rules()
    s = e.decide(e.advance(e.new_save(r), r, at), r, at, game().verb(w.TapCard(card=JUMP)))
    lands = next(c.completes_at for c in game().view(s).cards if c.card == JUMP)
    assert lands is not None
    step = e.advance_logged(s, r, lands)
    return game().step(Played(1, 1, step.save, step.lines))


def test_the_content_serves_the_chain_and_the_group() -> None:
    c = game().content()
    assert [x.chain for x in c.card_infos if x.chain is not None] == [
        cm.ChainInfo(runner="t_prowl", link_line_keys=["t_link_1", "t_link_next"])]
    assert [x.members for x in c.threat_infos if x.threat == "t_pack"] == [4]


def test_the_view_serves_the_reach_before_the_tap() -> None:
    r = rules()
    wire = game().view(e.advance(e.new_save(r), r, 0))
    assert wire.chains == [w.Chain(card="t_jump", runner="t_prowl", up_to=w.Strength(
        value=2, sources=[w.StrengthEntry(source=None, form=w.StrengthKind.BASE, amount_bp=2, share_bp=None)]))]
    assert w.View.model_validate(wire.model_dump()) == wire


def test_a_landing_sends_min_of_due_and_reach_lines_and_raises_chained_only() -> None:
    seen: set[int] = set()
    for at in (0, 600, 1200, 1800, 2400):
        step = _cast(at)
        prowl = next(f for f in step.view.fights if f.runner == "t_prowl")
        k = min(4 - prowl.fought % 4, 2)   # due from the served fought (chained 0 before this cast), reach 2
        links = [ln for ln in step.lines if ln.card == "t_jump"]
        assert [ln.key for ln in links] == ["t_link_1", "t_link_next"][:k] and prowl.chained == k
        assert len({ln.at for ln in links}) <= 1 and prowl.lost <= prowl.fought
        seen.add(k)
    assert seen == {1, 2}   # control: both a chain cut by due and one cut by reach were seen
