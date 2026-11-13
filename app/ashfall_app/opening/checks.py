"""What makes a parsed Opening valid beyond its shape: unique ids, every reference known, every `*_key` in `text`,
every fraction exact. Raises ValueError naming the entry. Imports the schema for types only (schema.py calls this)."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..engine import HANDS, QUANTITY_SCALE, TOWN_PREFIX, units
from .aims import check_aims
from .band_checks import check_bands
from .camp_checks import check_camp
from .chip_checks import check_chip_card, check_chips
from .convert import build_rules, levels
from .fight_checks import check_fight_content
from .journal_checks import check_journal
from .keep_checks import check_kept_needs
from .fight_refs import check_fights, fights
from .kind_checks import check_kinds
from .line_kinds import check_line_kinds
from .find_checks import check_finds
from .name_checks import check_names, without_slots
from .phase_pays import check_phase_pays
from .prestige import check_phase_spans, check_tracks
from .refs import check_refs, fail, ids_by_kind, need, offer_cap, outcomes
from .leave_checks import check_leaves
from .replace_checks import check_replacements
from .retire_checks import check_retired_chores
from .season_checks import check_season_turns
from .slot_checks import check_slots
from .tally_checks import check_tallies
from .ui_keys import UI_KEYS

if TYPE_CHECKING:
    from .entries import CardEntry, OrderCardEntry, OutcomeEntry
    from .schema import Opening


def check_opening(o: "Opening") -> None:
    """Unique ids (standing and cards share one namespace), every reference known (a card's lane, skill, stores; an
    order card's tap_card or switch_mix, exactly one, and its `when` an at_most on its store), every `*_key` in `text`
    and the UI_KEYS present, the end feature known and unlocked by something, the camp and the first mix sound, an aim
    from the start (aims.py), every chip's cost said, every fraction exact; then the text's rules and what the fights' cures reach."""
    check_structure(o)
    check_content(o)


def check_structure(o: "Opening") -> None:
    """Everything check_opening checks but the content rules: cheap, so the merge runs it on every chapter's state, and a
    chapter that names an id only a later chapter adds fails there, by name."""
    _check_unique(o)
    _check_parts(o)
    check_chips(o)
    _check_keys(o)
    check_line_kinds(o)
    check_names(o)
    check_finds(o)
    _check_end(o)
    check_camp(o)
    _check_first_mix(o)
    check_refs(o)
    check_kinds(o)
    check_fights(o)
    check_tallies(o)
    check_season_turns(o)
    check_retired_chores(o)
    check_replacements(o)
    check_leaves(o)
    check_aims(o)
    check_journal(o)
    check_bands(o)
    check_kept_needs(o)
    check_phase_pays(o)
    check_tracks(o.nodes)


def check_content(o: "Opening") -> None:
    """The costly checks, which hold of a line or a fight on its own and need no prefix: the text's rules (a digit, a
    slot, a fixed key), a prestige phase outlasting an ordinary absence (prestige.check_phase_spans), and every fight's
    cure reachable (fight_checks.py, which builds the Rules). The merge runs them
    once, on the last state."""
    _check_text(o)
    if o.prestige is not None:
        check_phase_spans(build_rules(o))
    if any(True for _ in fights(o)):
        check_fight_content(build_rules(o))


def _check_unique(o: "Opening") -> None:
    for kind, ids in ids_by_kind(o).items():
        for i in ids:
            if ids.count(i) > 1:
                fail(kind, f"duplicate id {i}")
    if HANDS in ids_by_kind(o)["lane"]:
        fail("lane", "hands always exists and is never declared")
    th = o.curve_items
    if not th or th[0] <= 0 or any(a >= b for a, b in zip(th, th[1:])):
        fail("curve_items", "need thresholds, the first > 0, strictly increasing")


def _check_parts(o: "Opening") -> None:
    ids = ids_by_kind(o)
    for a in o.standing:
        if a.skill is not None:
            need(f"action {a.id}", "skill", a.skill, ids["skill"])
        for f in (*a.makes, *a.costs):
            need(f"action {a.id}", "store", f.store, ids["store"])
    lanes = [*ids["lane"], HANDS]
    ruled = {x.id for x in o.lanes if x.ruled}
    cards = {c.id: c for c in o.cards}
    for c in o.cards:
        where = f"card {c.id}"
        need(where, "lane", c.lane, lanes)
        if c.lane in ruled and (c.skill is not None or c.xp_per_hour):
            fail(where, "a card on a ruled lane trains no skill and earns no XP: townsfolk do not level")
        if c.skill is not None:
            need(where, "skill", c.skill, ids["skill"])
        for f in (*c.makes, *c.costs):
            need(where, "store", f.store, ids["store"])
    for where, out in outcomes(o):
        for q in out.starts:
            need(where, "card", q, ids["card"])
        for r in out.raises:
            need(where, "card", r.card, ids["card"])
    for c in o.cards:
        _check_installs(cards, ruled, f"card {c.id}", c.outcome, installs=False, queues=False)
        _check_installs(cards, ruled, f"card {c.id} finished", c.finished, installs=False, queues=False)
    for t in o.triggers:
        _check_installs(cards, ruled, f"trigger {t.id}", t.outcome, installs=True, queues=False)
    for x in o.offers:
        for a in x.answers:
            _check_installs(cards, ruled, f"answer {a.id}", a.outcome, installs=True, queues=True)
    for where, u in [("start", u) for u in o.start] + [(w, u) for w, out in outcomes(o) for u in out.unlocks]:
        if u.unlock_kind in ("answered", "answer"):
            fail(where, "only an answer adds an answered or answer unlock: gates read them, nothing sets them")
        if u.unlock_kind in ("joined", "left"):
            fail(where, f"only a join adds joined and only a leave adds left: gates read the {u.unlock_kind} unlock")
    for oc in o.order_cards:
        where = f"order card for {oc.store}"
        need(where, "store", oc.store, ids["store"])
        if (oc.tap_card is None) == (oc.switch_mix is None):
            fail(where, "needs exactly one of tap_card and switch_mix")
        if oc.tap_card is not None:
            need(where, "card", oc.tap_card, ids["card"])
        if (oc.when.subject_kind, oc.when.id) != ("store", oc.store) or oc.when.test == "after_time":
            fail(where, "its when must be an at_most or at_least on its own store (the page words it as a level on "
                         "that store)")
        if oc.when.every != 1:
            fail(where, "its when has every: a rule's levels are whole items")
        cap = next((s.cap_items for s in o.stores if s.id == oc.store), None)
        if oc.when.test == "at_least":
            _check_rising_card(o, where, oc, cap)
        elif cap is not None and oc.when.release is not None \
                and levels(oc.when)[1] >= offer_cap(o, oc.store, oc.offered_after) * QUANTITY_SCALE:
            fail(where, "its release is at or past the store's cap when it is offered, so the rule would never let go")
        check_chip_card(o, where, oc)
    for s in o.stores:
        if s.initial_items > s.cap_items:
            fail(f"store {s.id}", "initial_items is past cap_items")


def _check_installs(cards: dict[str, "CardEntry"], ruled: set[str], where: str, out: "OutcomeEntry", installs: bool,
                    queues: bool) -> None:
    """An outcome's installs tap cards on a ruled lane, and only a trigger's or an answer's outcome installs
    (`installs`); only an answer's queues a one-off (`queues`), each a hands card with a cap (engine DESIGN.txt,
    "Installs land once"). `cards` by id and the `ruled` lanes are the opening's, built once by the caller."""
    if out.orders and not installs:
        fail(where, "only a trigger's or an answer's outcome installs a rule")
    for i in out.orders:
        need(where, "card", i.tap_card, list(cards))
        if cards[i.tap_card].lane not in ruled:
            fail(where, f"an installed rule taps {i.tap_card}, which is not on a ruled lane")
    _check_joins(cards, ruled, where, out, installs)
    if out.queues and not queues:
        fail(where, "only an answer's outcome queues a one-off")
    for q in out.queues:
        need(where, "card", q, list(cards))
        if cards[q].lane != HANDS or cards[q].cap is None:
            fail(where, f"a queued one-off is a hands card with a cap; {q} is not")


def _check_joins(cards: dict[str, "CardEntry"], ruled: set[str], where: str, out: "OutcomeEntry", installs: bool
                 ) -> None:
    """A join names a ruled lane, a town mix id and, when it names a card, an uncapped card on that lane; only a
    trigger's or an answer's outcome joins (engine DESIGN.txt, "THE TOWN'S MIX", "Join")."""
    if out.joins and not installs:
        fail(where, "only a trigger's or an answer's outcome joins a person")
    for j in out.joins:
        need(where, "ruled lane", j.lane, list(ruled))
        if not j.mix.startswith(TOWN_PREFIX):
            fail(where, f"a join's mix {j.mix} does not begin {TOWN_PREFIX!r}")
        if j.card is not None:
            need(where, "card", j.card, list(cards))
            if cards[j.card].lane != j.lane or cards[j.card].cap is not None:
                fail(where, f"a join's card {j.card} is not an uncapped card on lane {j.lane}")


def _check_rising_card(o: "Opening", where: str, oc: "OrderCardEntry", cap: int | None) -> None:
    """An at_least card is the rule for a full or rising line, or for a chip that shows while its store is high: it taps
    a card that takes that store (so the rule spends what fills), comes on at a level the store can reach, and lets go
    above 0 (a store never goes under 0)."""
    card = next((c for c in o.cards if c.id == oc.tap_card), None)
    if card is None:
        fail(where, "an at_least card taps a card")
    if not any(a.store == oc.store for a in card.inputs) and not any(f.store == oc.store for f in card.costs):
        fail(where, f"card {card.id} does not take {oc.store}, so the rule would not spend what fills")
    if cap is not None and levels(oc.when)[0] > units(cap):
        fail(where, "its value is past the store's cap, so the rule would never come on")
    if oc.when.release is not None and levels(oc.when)[1] < units(1):
        fail(where, "its release is under one, so the rule would never let go")


# ---------- text keys ----------

def _key_fields(o: "Opening") -> Iterator[tuple[str, str]]:
    for s in o.stores:
        yield f"store {s.id}", s.label_key
    for k in o.skills:
        yield f"skill {k.id}", k.label_key
        yield from ((f"skill {k.id}", lv.pays_key) for lv in k.levels)
    for a in o.standing:
        yield f"action {a.id}", a.label_key
    yield from ((f"side {s.id}", s.label_key) for s in o.sides)
    yield from ((f"threat {t.id}", t.label_key) for t in o.threats)
    yield from ((f"node {n.id}", n.label_key) for n in o.nodes)
    for x in o.lanes:
        yield f"lane {x.id}", x.label_key
        yield from ((f"lane {x.id}", lb.label_key) for lb in x.later_labels)
        yield from ((f"lane {x.id}", k) for k in (x.name_key,) if k is not None)
    for c in o.cards:
        singles = (c.label_key, c.upside_key)
        yield from ((f"card {c.id}", k) for k in (*singles, *c.line_keys) if k is not None)
    for ch in o.chips:
        yield from ((f"chip {ch.id}", k) for k in (ch.label_key, ch.cost_key, ch.on_line_key, ch.off_line_key)
                    if k is not None)
    for f in o.features:
        yield from ((f"feature {f.id}", k) for k in (f.hint_key, f.label_key) if k is not None)
        if f.card is not None:
            yield from ((f"feature {f.id} card", k) for k in (f.card.title_key, *f.card.line_keys, f.card.button_key))
    for where, out in outcomes(o):
        yield from ((where, k) for k in out.line_keys)
    if o.camp is not None:
        for n, lv in enumerate(o.camp.levels, start=1):
            yield from ((f"camp level {n}", k) for k in (lv.pays_key, *lv.line_keys))
    yield from ((f"aim {a.id}", a.text_key) for a in o.aims)
    for x in o.offers:
        yield from ((f"offer {x.id}", k) for k in (x.text_key, *x.line_keys))
        yield from ((f"answer {a.id}", k) for a in x.answers for k in (a.label_key, a.cost_key))
    yield from (("start_line_keys", k) for k in o.start_line_keys)
    yield from (("end_line_keys", k) for k in o.end_line_keys)
    yield from ((f"note {n.id}", n.id) for n in o.notes)
    yield "hands", o.hands_label_key


def _check_keys(o: "Opening") -> None:
    for where, key in _key_fields(o):
        if key not in o.text:
            fail(where, f"key {key!r} is not in text")


def _check_text(o: "Opening") -> None:
    """Text holds words and named slots, never a digit (api/CONTRACT.txt, "Text and numbers"); every fixed ui key
    exists."""
    for key, text in o.text.items():
        if any(map(str.isdigit, without_slots(text))):
            fail(f"text {key}", "holds a digit: a number is a slot")
    for key in UI_KEYS:
        if key not in o.text:
            fail("text", f"missing the fixed key {key!r}")
    check_slots(o, _key_fields(o))


def _check_end(o: "Opening") -> None:
    if o.end_feature not in ids_by_kind(o)["feature"]:
        fail("end_feature", f"unknown feature {o.end_feature}")
    if not any(u.unlock_kind == "feature" and u.id == o.end_feature for _, out in outcomes(o) for u in out.unlocks):
        fail("end_feature", f"no card or trigger unlocks {o.end_feature}")


def _check_first_mix(o: "Opening") -> None:
    fm = o.first_mix
    need("first_mix", "feature", fm.feature, ids_by_kind(o)["feature"])
    lanes = {c.id: c.lane for c in o.cards}
    if len(fm.cards) < 2 or len(set(fm.cards)) != len(fm.cards):
        fail("first_mix", "needs two or more different cards: a split needs two things to divide")
    for card in fm.cards:
        need("first_mix", "card", card, list(lanes))
        if lanes[card] != HANDS:
            fail("first_mix", f"card {card} is not a hands card, so it cannot be mixed")
