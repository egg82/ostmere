"""Every text key the opening names is in its text: the fields that carry a key, and the check over them."""
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .refs import fail, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def key_fields(o: "Opening") -> Iterator[tuple[str, str]]:
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
        yield from ((f"chip {ch.id}", k) for k in (ch.label_key, ch.cost_key, ch.on_line_key, *ch.off_line_keys)
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
    yield from ((f"entry {e.id}", e.title_key) for e in o.entries)
    yield "hands", o.hands_label_key


def check_keys(o: "Opening") -> None:
    for where, key in key_fields(o):
        if key not in o.text:
            fail(where, f"key {key!r} is not in text")
