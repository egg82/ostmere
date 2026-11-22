"""What makes a parsed Opening valid beyond its shape: unique ids, every reference known, every `*_key` in `text`,
every fraction exact. Raises ValueError naming the entry. Imports the schema for types only (schema.py calls this)."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from ..engine import HANDS, TOWN_PREFIX
from .aims import check_aims
from .ask_checks import check_asks
from .band_checks import check_bands
from .camp_checks import check_camp
from .chip_checks import check_chips
from .choice_checks import check_choices
from .player_checks import check_player_only
from .face_checks import check_clocks
from .convert import build_rules
from .fight_checks import check_fight_content
from .journal_checks import check_journal
from .map_checks import check_places
from .keep_checks import check_kept_needs
from .fight_refs import check_fights, fights
from .kind_checks import check_kinds
from .line_kinds import check_line_kinds
from .find_checks import check_finds
from .name_checks import check_names, without_slots
from .phase_pays import check_phase_pays
from .prestige import check_phase_spans
from .order_checks import check_order_cards
from .refs import check_refs, fail, ids_by_kind, need, outcomes
from .groups import check_groups
from .leave_checks import check_leaves
from .line_only_checks import check_line_only
from .people_checks import check_people
from .replace_checks import check_replacements
from .retire_checks import check_retired_chores
from .season_checks import check_season_turns
from .slot_checks import check_slots
from .stake_checks import check_stakes, check_stakes_hold
from .subject_checks import check_subjects
from .tally_checks import check_tallies
from .ui_keys import UI_KEYS

if TYPE_CHECKING:
    from .entries import CardEntry, OutcomeEntry
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
    check_asks(o)
    check_fights(o)
    check_tallies(o)
    check_stakes(o)
    check_clocks(o)
    check_season_turns(o)
    check_line_only(o)
    check_retired_chores(o)
    check_replacements(o)
    check_choices(o)
    check_player_only(o)
    check_leaves(o)
    check_groups(o)
    check_people(o)
    check_aims(o)
    check_journal(o)
    check_places(o)
    check_subjects(o)
    check_bands(o)
    check_kept_needs(o)
    check_phase_pays(o)


def check_content(o: "Opening") -> None:
    """The costly checks, which hold of a line or a fight on its own and need no prefix: the text's rules (a digit, a
    slot, a fixed key), a prestige phase outlasting an ordinary absence (prestige.check_phase_spans), and every fight's
    cure reachable (fight_checks.py, which builds the Rules); and every side stake held on a fought side, which a later
    chapter may add (stake_checks.py). The merge runs them once, on the last state."""
    _check_text(o)
    check_stakes_hold(o)
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
    check_order_cards(o, ids)
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
    """A join names a ruled lane, a town mix id and, when it names a card, an uncapped card on that lane (on its group
    when the join is unmarked: groups.py); only a trigger's or an answer's outcome joins (engine DESIGN.txt, "THE TOWN'S MIX", "Join")."""
    if out.joins and not installs:
        fail(where, "only a trigger's or an answer's outcome joins a person")
    for j in out.joins:
        need(where, "ruled lane", j.lane, list(ruled))
        if not j.mix.startswith(TOWN_PREFIX):
            fail(where, f"a join's mix {j.mix} does not begin {TOWN_PREFIX!r}")
        if j.card is not None:
            need(where, "card", j.card, list(cards))
            if j.own_split and (cards[j.card].lane != j.lane or cards[j.card].cap is not None):
                fail(where, f"a join's card {j.card} is not an uncapped card on lane {j.lane}")


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
    yield from (("town title", lb.label_key) for lb in o.town_later_labels)
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
    yield from ((f"place {p.id}", p.label_key) for p in o.places if p.label_key is not None)
    for x in o.offers:
        yield from ((f"offer {x.id}", k) for k in (x.text_key, *x.line_keys, x.waiting_key, x.expiry_key, x.permanence_key)
                    if k is not None)
        yield from ((f"answer {a.id}", k) for a in x.answers for k in (a.label_key, a.cost_key))
    yield from ((f"offer kind {x.kind}", r.label_key) for x in o.offer_kinds for r in x.roles)
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
