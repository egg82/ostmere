"""The makers readout: for each store over a played route through day twelve, how much of it came from which card, by
band of game days, and how often the store stood at its cap. A choice between routes into one store (two cards making
the same thing) shows here as the split between them; the ladder's share view reads cards' shares of the running mixes
and misses a tapped card, which runs a few seconds. A card paying a lump per completion is counted by its completions;
a flow by each sampled instant's rate held for the step. The store's cap is not applied, so a figure is what the makers
could add, and "at cap" says when it went to waste. Taste, so it reports and fails nothing (docs/design/
sim-invariants.md). Stores and card ids and counts only (CLAUDE.md, "Never spoil the owner").

    python -m tests.makers.readout                  # from app/: the push routes through day twelve, seed 0
    python -m tests.makers.readout typical smoked   # the named routes, then only the named stores
"""
import sys
from fractions import Fraction

from ashfall_app.engine import Save, advance
from ashfall_app.engine.counts import completions
from ashfall_app.engine.gates import store_cap
from ashfall_app.engine.ids import CardId
from ashfall_app.engine.index import index
from ashfall_app.engine.lumps import has_lump, lump_amount, lump_lines
from ashfall_app.engine.modifiers import FlowKind, RateRef
from ashfall_app.engine.rates import exact_contribution, running, store_value
from ashfall_app.engine.sides import makes
from ashfall_app.engine.units import QUANTITY_SCALE
from tests.daytwo.player import DayTwoPlayer
from tests.ladder.readout import STEP_H, played_saves, sampled
from tests.ladder.sources import BANDS, band_label
from tests.ladder.ticks import at_time
from tests.makers.tally import Band, Made, at_cap_share, band_spans, made_by_band, merged
from tests.weektwo.routes import TWELVE_PUSH_ROUTES, twelve

NAMES = tuple(f"makers-{name}" for name in TWELVE_PUSH_ROUTES)
HOUR_S = 3600


def made_at(p: DayTwoPlayer, save: Save) -> Made:
    """Items per hour into each store from each running runner that makes it as a flow, at `save`'s instant; a card's
    outcome stores are counted by its completions (lumps_made), which a tap's few seconds of running would miss."""
    rules, now = p.rules, running(save, p.rules)
    out: dict[str, dict[str, float]] = {}
    for runner, share in now.shares.items():
        for store in makes(rules, runner):
            card = index(rules).cards.get(CardId(runner))
            if card is not None and has_lump(card, RateRef(runner, FlowKind.MAKE, store)):
                continue
            per_s: Fraction = exact_contribution(save, rules, runner, store, share, now.runs[runner])
            if per_s > 0:
                out.setdefault(str(store), {})[str(runner)] = float(per_s * HOUR_S / QUANTITY_SCALE)
    return out


def lumps_made(p: DayTwoPlayer) -> dict[str, dict[Band, dict[str, float]]]:
    """Items each card's outcome stores gained per band: its completions in the band times what a completion pays at
    the band's end (a modifier that changed inside the band is read at its end)."""
    rules, saves = p.rules, played_saves(p)
    save_at = at_time(saves, lambda s, t: advance(s, rules, t))
    out: dict[str, dict[Band, dict[str, float]]] = {}
    for band, t0, t1 in band_spans(saves[-1].time):
        a, b = save_at(t0), save_at(t1)
        for store in (d.id for d in rules.stores):
            for card, ref in lump_lines(rules, store):
                if ref.kind is not FlowKind.MAKE:
                    continue
                n = completions(b, rules, card.id) - completions(a, rules, card.id)
                if n > 0:
                    out.setdefault(str(store), {}).setdefault(band, {})[str(card.id)] = (
                        n * lump_amount(b, rules, card, ref) / QUANTITY_SCALE)
    return out


def full_at(p: DayTwoPlayer, save: Save) -> dict[str, bool]:
    return {str(d.id): store_value(save, d.id) >= store_cap(save, p.rules, d.id) for d in p.rules.stores}


def route_text(name: str, p: DayTwoPlayer, only: tuple[str, ...] = ()) -> str:
    """A route's readout: each store's makers by band, in percent of the items made, with the store's items made and the
    percent of samples at its cap."""
    at = sampled(p, STEP_H)
    made = merged(made_by_band([(t, made_at(p, s)) for t, s in at], STEP_H), lumps_made(p))
    full = at_cap_share([(t, full_at(p, s)) for t, s in at])
    assert made, "no store was made in over the route"
    out = [f"== {name}: items made per store by maker, percent (sampled every {STEP_H} game hours; made = items the "
           f"makers could add, cap not applied)"]
    for store in sorted(made):
        if only and store not in only:
            continue
        out.append(f"  {store}")
        for band in BANDS:
            got = made[store].get(band)
            if got:
                total = sum(got.values())
                cells = sorted(((m, 100 * v / total) for m, v in got.items()), key=lambda mv: (-mv[1], mv[0]))
                rest = sum(v for _, v in cells if v < 1)
                shown = [f"{m} {v:.0f}" for m, v in cells if v >= 1] + ([f"other {rest:.0f}"] if rest >= 0.5 else [])
                out.append(f"    d{band_label(band):5s} made {total:7.0f}  at cap {full[store][band]:3.0f}%  "
                           + ", ".join(shown))
    return "\n".join(out) + "\n"


def readouts() -> dict[str, str]:
    return {f"makers-{name}": route_text(name, twelve(name)) for name in TWELVE_PUSH_ROUTES}


def main(argv: list[str]) -> int:
    names = [a for a in argv if a in TWELVE_PUSH_ROUTES] or list(TWELVE_PUSH_ROUTES)
    only = tuple(a for a in argv if a not in TWELVE_PUSH_ROUTES)
    for name in names:
        sys.stdout.write(route_text(name, twelve(name), only))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
