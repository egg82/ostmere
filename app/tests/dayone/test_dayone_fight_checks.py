"""The checks past the fights (fightchecks.py, cures.py) on fixture rules (fightworld.py): a fight card's drawn landing
comes true when the hands tap it and none is claimed while the mix runs it; a store a standing fight takes to nothing has a card in reach
that puts it up; the wound a lost fight leaves, shown as a chip, has a cure on offer. Each is judged on a non-empty
set and goes red on a planted fight."""
from dataclasses import replace

import pytest

from ashfall_app.engine import Rules, RunBy, Save, TapCard, View, advance, decide, new_save, value, view
from tests.dayone import cures, fightchecks, sinkchecks
from tests.dayone.fightworld import CHIP, HUNT, HUNT_S, WOOD, mixed, rules
from tests.dayone.fightchecks import fight_landings, threat_stores_unreached

H = 3600


def tapped(r: Rules) -> Save:
    return decide(new_save(r), r, 0, TapCard(HUNT))


@pytest.fixture(params=["tapped", "mixed"])
def running(request: pytest.FixtureRequest) -> tuple[Save, Rules]:
    r = rules()
    return (tapped(r) if request.param == "tapped" else mixed(r, HUNT)), r


def tapping(s: Save, r: Rules) -> bool:
    return next(c for c in view(s, r).cards if c.card == HUNT).by is RunBy.TAP


def test_a_tapped_fight_cards_drawn_landing_comes_true_and_a_mixed_one_claims_none(running: tuple[Save, Rules]):
    s, r = running
    card = next(c for c in view(s, r).cards if c.card == HUNT)
    assert card.completes_at == (HUNT_S if card.by is RunBy.TAP else None), "a tap draws the landing; a share claims none"
    assert fight_landings(s, r) == (1, [])


def test_a_landing_drawn_a_second_early_is_caught(running: tuple[Save, Rules], monkeypatch: pytest.MonkeyPatch):
    """The page shows the fight paid a second before it is: the card looked at pays on looking. A share given that
    time claims a landing, which none may."""
    s, r = running
    real = fightchecks.view

    def early(save: Save, rules: Rules) -> View:
        v = real(save, rules)
        return replace(v, cards=tuple(replace(c, completes_at=HUNT_S - 1) if c.card == HUNT else c for c in v.cards))

    tap = tapping(s, r)
    monkeypatch.setattr(fightchecks, "view", early)
    assert fight_landings(s, r) == (1, [f"{HUNT} drawn landing at t={HUNT_S - 1}, not kept" if tap
                                        else f"{HUNT} share claims a landing at t={HUNT_S - 1}"])


def test_a_landing_that_comes_a_second_late_is_caught(running: tuple[Save, Rules], monkeypatch: pytest.MonkeyPatch):
    s, r = running
    assert fight_landings(s, r) == (1, [])

    def late(save: Save, rules: Rules, t: int) -> Save:
        return advance(save, rules, t - 1)

    tap = tapping(s, r)
    monkeypatch.setattr(sinkchecks, "advance", late)
    assert fight_landings(s, r) == (1, [f"{HUNT} drawn landing at t={HUNT_S}, not kept"] if tap else []), \
        "a share claims no landing, so a late one breaks nothing"


def test_a_fight_not_running_draws_no_landing():
    r = rules()
    assert fight_landings(new_save(r), r) == (0, [])


def raided(r: Rules) -> Save:
    """Nothing in the mix, the raids run, and the wood store is long empty."""
    return advance(new_save(r), r, 40 * H)


def test_a_store_a_threat_took_to_nothing_has_a_card_that_puts_it_up():
    r = rules()
    s = raided(r)
    assert value(s, r, WOOD, s.time) == 0, "the raids emptied the wood"
    assert threat_stores_unreached(s, r) == (1, [])


def test_a_store_a_threat_took_to_nothing_with_nothing_to_put_it_up_is_caught():
    r = rules(gathers=False)
    s = raided(r)
    assert threat_stores_unreached(s, r) == (1, [f"{WOOD} empty at t={s.time}, taken by raid: nothing in reach puts it up"])


def test_a_threat_whose_store_is_not_empty_judges_nothing():
    r = rules()
    assert threat_stores_unreached(new_save(r), r) == (0, [])


def wounded(r: Rules) -> tuple[Save, View]:
    """The hunt run until a lost fight has left its wound and the chip shows."""
    s = mixed(r, HUNT)
    for _ in range(40):
        s = advance(s, r, s.time + HUNT_S)
        v = view(s, r)
        if str(CHIP) in [str(c) for c in v.chips]:
            return s, v
    raise AssertionError("no fight was lost in forty hunts")


def test_a_lost_fights_wound_chip_has_a_cure_on_offer():
    r = rules()
    s, v = wounded(r)
    assert cures.cured(s, r, v, str(CHIP))


def test_a_wound_with_nothing_to_tend_it_is_caught():
    r = rules(tends=False)
    s, v = wounded(r)
    assert not cures.cured(s, r, v, str(CHIP))
