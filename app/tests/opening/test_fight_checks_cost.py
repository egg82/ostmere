"""The fight checks read the triggers a few times per fight runner, never once per card they ask about: a card's count
stores read by scanning every trigger, for every card in reach of every runner, made loading the content grow with
cards times triggers, once per chapter. Counts, not seconds."""
from collections.abc import Iterator
from dataclasses import replace

from ashfall_app.engine import TriggerDef
from ashfall_app.opening.fight_checks import check_fight_content
from tests.opening.playthrough import opening_rules


class _Scanned(tuple[TriggerDef, ...]):
    """The triggers, counting each full pass over them."""
    scans = 0

    def __iter__(self) -> Iterator[TriggerDef]:
        _Scanned.scans += 1
        return super().__iter__()


def test_the_fight_checks_scan_the_triggers_fewer_times_than_there_are_cards() -> None:
    shipped = opening_rules()
    rules = replace(shipped, triggers=_Scanned(shipped.triggers))
    _Scanned.scans = 0
    check_fight_content(rules)
    scans, cards = _Scanned.scans, len(rules.cards)
    assert scans > 0, "control: the checks read the triggers"
    assert scans < cards
