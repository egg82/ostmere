"""The simulated players offer an order card as the page does (game/ledger/cues.ts): not once its offered_until is
unlocked. Read off the loaded card (fixtures/seasonturn.toml, edited to give it an offered_after too), never by id."""
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from ashfall_app.engine import Unlock, UnlockKind, new_save
from ashfall_app.opening.schema import OPENING, Opening, load_opening, to_rules
from tests.daythree import content, moves
from tests.opening.playthrough import offering

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seasonturn.toml"
AFTER, UNTIL = Unlock(UnlockKind.FEATURE, "t_open_f"), Unlock(UnlockKind.FEATURE, "t_turned")


def loaded(tmp_path: Path, until: bool = True) -> Opening:
    text = FIXTURE.read_text()
    anchor = 'tap_card = "t_clear"\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + 'offered_after = { unlock_kind = "feature", id = "t_open_f" }\n')
    text = text.replace('[[features]]\nid = "t_turned"', '[[features]]\nid = "t_open_f"\n\n[[features]]\nid = "t_turned"')
    if not until:
        text = text.replace('offered_until = { unlock_kind = "feature", id = "t_turned" }\n', "")
    path = tmp_path / FIXTURE.name
    path.write_text(text)
    return load_opening(OPENING, (path,))


def test_a_card_is_offered_between_its_after_and_its_until(tmp_path: Path):
    card = next(c for c in loaded(tmp_path).order_cards if c.store == "t_heap")

    def held(*have: Unlock) -> Callable[[str, str], bool]:
        return lambda k, i: Unlock(UnlockKind(k), i) in have

    assert not offering(card, held())
    assert offering(card, held(AFTER))
    assert not offering(card, held(AFTER, UNTIL))


def test_a_route_sets_the_card_until_its_until_and_a_field_less_copy_to_the_end(tmp_path: Path):
    for until, still_set in ((True, False), (False, True)):
        op = loaded(tmp_path, until)
        r = to_rules(op)
        (offer,) = content.order_cards(op, ("t_heap",))
        later = replace(content.day_three(), order_cards=(offer,))
        save = replace(new_save(r), unlocked=(AFTER, UNTIL))
        assert (moves.order_card(save, later) is not None) is still_set
        assert moves.order_card(replace(save, unlocked=(AFTER,)), later) is not None
