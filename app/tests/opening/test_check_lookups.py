"""The content checks build each lookup once per check, never once per reference they test: a lookup rebuilt per
reference makes loading the content quadratic in its size (CI's tests timed out inside check_refs). Counts, not
seconds."""
from collections.abc import Iterator

import pytest

from ashfall_app.opening import checks, refs
from ashfall_app.opening.entries import CardEntry
from ashfall_app.opening.schema import Opening
from tests.opening.playthrough import opening


def test_check_refs_builds_the_id_lists_once(monkeypatch: pytest.MonkeyPatch) -> None:
    o: Opening = opening()
    built: list[int] = []
    real = refs.ids_by_kind

    def counted(x: Opening) -> dict[str, list[str]]:
        built.append(1)
        return real(x)

    monkeypatch.setattr(refs, "ids_by_kind", counted)
    refs.check_refs(o)
    assert built == [1]


class _Scanned(list[CardEntry]):
    """The opening's cards, counting each full pass over them."""
    scans = 0

    def __iter__(self) -> Iterator[CardEntry]:
        _Scanned.scans += 1
        return super().__iter__()


def test_check_opening_reads_the_cards_fewer_times_than_there_are_cards() -> None:
    """Each outcome's installs, queues and joins are checked against the cards and ruled lanes built once."""
    o: Opening = opening()
    _Scanned.scans = 0
    checks.check_opening(o.model_copy(update={"cards": _Scanned(o.cards)}))
    scans, cards = _Scanned.scans, len(o.cards)
    assert scans > 0, "control: the checks read the cards"
    assert scans < cards
