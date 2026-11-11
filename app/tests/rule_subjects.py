"""Every subject a rule may watch that the page has shown is one the full condition editor offers (docs/design/
opening-screen.md, "The condition editor"), at every save of a play, read off the wire View and Content the page gets.
A player who meets a need and goes to write a rule for it finds it there, not later.

Shown, per subject (`shown`): a chip once the band has drawn it (on, its offered_after held), and from then on, since
the player who met it may write its rule after it clears; a store once the ledger could draw its line (the ledger is
open, the store neither the Camp's nor hidden), and from then on, as the ledger keeps a line; the Camp while its line
is held; a skill while its bar is drawn; a task's count while its card is in play. A store under two items is left out:
no band fits it, so no rule can watch it, at any time. Offered (`offered`): the page's ruleoffers.offeredSubjects and
whenChoices(full) on the same view, mirrored here because the CI image that runs the plays has no node.

Problems name the subject and the minute of play only (CLAUDE.md, "Never spoil the owner")."""
from collections.abc import Iterable
from functools import cache

from ashfall_app.api import content_models as cm
from ashfall_app.api import convert
from ashfall_app.api import models as w
from ashfall_app.engine import Save, View
from tests.daythree.content import opening3
from tests.shipped_ruleset import ShippedRuleset

LEDGER_FEATURE = "ledger"


@cache
def content() -> cm.Content:
    """The wire Content of the plays' content (opening3: every chapter written)."""
    sr = ShippedRuleset(opening3())
    return sr.make_game(sr.opening, sr.rs).content()


def wire(history: Iterable[tuple[Save, View]]) -> list[w.View]:
    """The wire Views of a play's saves, as the page gets them."""
    return [convert.view(save, v) for save, v in history]


def _unlocked(view: w.View, category: str, id_: str) -> bool:
    return any(u.category == category and u.id == id_ for u in view.unlocked)


def drawn_chips(content: cm.Content, view: w.View) -> set[str]:
    """The chips the band draws: on in the view, with their offered_after (if any) held (game/shown.ts shownChips)."""
    after = {c.chip: c.offered_after for c in content.chip_infos}
    return {c for c in view.chips if (a := after.get(c)) is None or _unlocked(view, a.category, a.id)}


def _band_fits(content: cm.Content, line: w.LedgerLine) -> bool:
    return line.cap >= 2 * content.scales.quantity_per_item


def drawable_lines(content: cm.Content, view: w.View) -> set[str]:
    """The stores whose ledger line the page may draw (ui/ledger.ts): the ledger open, not the Camp's, not hidden, and
    with room for a band."""
    if not _unlocked(view, "feature", LEDGER_FEATURE):
        return set()
    camp = content.camp.store if content.camp is not None else None
    hidden = {s.store for s in content.store_infos if s.hidden}
    return {l.store for l in view.ledger if l.store != camp and l.store not in hidden and _band_fits(content, l)}


def shown_now(content: cm.Content, view: w.View) -> set[str]:
    """The subjects the page draws in `view` that stay shown only while drawn: the Camp, skills, tasks in play."""
    camp = content.camp.store if content.camp is not None else None
    found = {f"level:{s.skill}" for s in view.skills if _unlocked(view, "skill", s.skill)}
    found |= {f"count:{c.card}" for c in view.cards}
    if camp is not None and any(l.store == camp for l in view.ledger) and _unlocked(view, "store", camp):
        found.add("camp")
    return found


def offered(content: cm.Content, view: w.View) -> set[str]:
    """Every subject the full editor offers in `view` (game/ruleoffers.ts: whenChoices(full) and offeredSubjects)."""
    camp = content.camp.store if content.camp is not None else None
    stores = {l.store for l in view.ledger if l.store != camp and _unlocked(view, "store", l.store) and _band_fits(content, l)}
    found = {f"store:{s}" for s in stores} | {f"chip:{c}" for c in _offered_chips(content, view)}
    found |= {f"level:{s.skill}" for s in view.skills} | {f"count:{c.card}" for c in view.cards}
    if camp is not None and any(l.store == camp for l in view.ledger) and _unlocked(view, "store", camp):
        found.add("camp")
    return found


def _offered_chips(content: cm.Content, view: w.View) -> set[str]:
    """Every chip on a store the band has drawn in the save (shown.ts seenChips): seen, its offered_after held."""
    seen = drawn_chips(content, view.model_copy(update={"chips": view.chips_seen}))
    return {c.chip for c in content.chip_infos if c.chip in seen and c.when.kind != "after_time"
            and c.when.watched.kind == "store_value"}


def unoffered(content: cm.Content, views: Iterable[w.View]) -> list[str]:
    """One problem per subject, at the first view where it was shown and not offered."""
    kept: set[str] = set()
    problems: dict[str, str] = {}
    for view in views:
        kept |= {f"chip:{c}" for c in drawn_chips(content, view)} | {f"store:{s}" for s in drawable_lines(content, view)}
        for subject in sorted((kept | shown_now(content, view)) - offered(content, view)):
            problems.setdefault(subject, f"{subject} shown and not offered at minute {view.at // 60}")
    return list(problems.values())
