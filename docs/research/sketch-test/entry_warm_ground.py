"""Journal entry `warm_ground` (places): the hearth's ring and the ground round it, seen from a little above, the warm
patch paced out to four paces and the cold beyond it. Run: bash render.sh entry_warm_ground -> entry_warm_ground_ink.png

A place, not a creature, so no reference to measure: the ground is seen at about 25 degrees, so a circle on it draws
as an ellipse 0.4 as deep as it is wide. The ring is a camp hearth of fist-to-head-sized stones, about a stride across
(rx 58); a pace is about 0.75 m, so four paces out from the ring's edge put the warm patch's edge at rx 230. Stones are
Parts (contour and hatching from the method); the ground is strokes only, bare inside the paced line and hatched cold
outside it.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 31))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_warm_ground", text_scale=1.3)
A = lambda *p: np.array(p, float)
DEPTH = 0.4
"""How deep a circle on the ground draws, as a fraction of its width."""
HEARTH, RING, WARM = A(300, 330), 68, 236


def on_ground(c, r, t):
    """The point at angle t on a circle of radius r round c, laid on the ground."""
    return A(c[0] + r * np.cos(t), c[1] + r * DEPTH * np.sin(t))


rng = np.random.default_rng(SEED)
stones = []
for k, t in enumerate(np.linspace(0, 2 * np.pi, 14, endpoint=False) + 0.1):
    c = on_ground(HEARTH, RING, t)
    near = np.sin(t) > 0                                  # the front of the ring sits lower and nearer
    rx, ry = rng.uniform(10, 14) * (1.0 if near else 0.85), rng.uniform(6.5, 8.5) * (1.0 if near else 0.8)
    stones.append(mk(f"stone{k}", [ell_poly(c, rx, ry, rng.uniform(-15, 15))], 3, z=3 if near else 1,
                     tone=0.4, lw=1.5, hatch_angle=-30, hatch_spacing=3.4))
ash = Part("ash", [tuple(on_ground(HEARTH, RING - 14, t)) for t in np.linspace(0, 2 * np.pi, 28, endpoint=False)],
           z=2, n=6, tone=0.7, lw=0.9)
ash.hatch_angle, ash.hatch_spacing = 20, 2.6


def frost(pen, x, y):
    """A short cold mark: a dash with a tick, as a hand marks frost on a plan."""
    pen.stroke(np.array([(x - 5, y), (x + 5, y + 0.6)]), 0.55, taper=(0.2, 0.3), wobble=0.3)
    if pen.rng.random() < 0.45:
        pen.stroke(np.array([(x - 1, y - 3), (x + 1, y + 2)]), 0.45, taper=(0.2, 0.3), wobble=0.2)


with L.figure(pen, (300, 330)):
    with pen.construction():
        hand_ellipse(pen, HEARTH, RING, RING * DEPTH, 0, w=0.45)
        hand_ellipse(pen, HEARTH, WARM, WARM * DEPTH, 0, w=0.4)
        pen.line([HEARTH + (-WARM - 20, 0), HEARTH + (WARM + 20, 0)], w=0.4, wobble=0.6, overshoot=8)
    ink_figure(pen, [*stones, ash], SEED, hatch_t=0.5, part_t={"ash": 0.3}, cross={"ash": (0.5, -55)})
    for a, b in (((-34, -6), (10, 8)), ((-6, 9), (36, -3)), ((-20, 4), (24, -8))):   # half-burnt sticks across it
        pen.line([HEARTH + a, HEARTH + b], w=1.5, wobble=0.5)
    for k in range(5):                                    # the air moving over the coals
        x0 = HEARTH[0] - 26 + k * 13
        ys = np.linspace(HEARTH[1] - 16, HEARTH[1] - 70 - rng.uniform(0, 14), 14)
        pen.line([(x0 + 3.5 * np.sin(y / 7 + k), y) for y in ys], w=0.55, wobble=0.4)
    t = 0.0
    while t < 2 * np.pi:                                  # the paced line: dashes, the hand lifting between paces
        span = rng.uniform(0.09, 0.14)
        seg = [on_ground(HEARTH, WARM + rng.normal(0, 1.5), u) for u in np.linspace(t, t + span, 5)]
        pen.line(seg, w=1.1, wobble=0.5)
        t += span + rng.uniform(0.05, 0.08)
    edge = on_ground(HEARTH, RING + 14, 0)
    for k in range(1, 5):                                 # the four paces along the line out
        q = edge + ((WARM - RING - 14) * k / 4, 0)
        pen.line([q + (-4, -5), q + (4, 5)], w=0.9); pen.line([q + (-4, 5), q + (4, -5)], w=0.9)
    pen.line([edge, edge + (WARM - RING - 14, 0)], w=0.6, wobble=0.5)
    for k in range(70):                                   # cold ground: only past the paced line
        t, r = rng.uniform(0, 2 * np.pi), rng.uniform(WARM + 12, WARM + 70)
        q = on_ground(HEARTH, r, t)
        if 120 < q[1] < 520 and 20 < q[0] < 580:
            frost(pen, *q)


def s_stone(pen):
    """One stone of the ring, side on, the ground under it."""
    pen.line([(0, 80), (140, 82)], w=0.9, wobble=0.6, overshoot=6)
    st = mk("s", [ell_poly(A(70, 64), 46, 20, -4), ell_poly(A(52, 56), 22, 14, 10)], 8, z=1, tone=0.45)
    sc = SketchScene([st], pen, seed=SEED)
    sc.quick_hatch(st, t=0.42, w=0.55)
    sc.search_contour(st, w=1.6, passes=(0.4, 1.0))


def s_section(pen):
    """The ground side on: the ring at the middle, the paced line either side, frost past it."""
    pen.line([(0, 80), (70, 80), (84, 77), (116, 77), (130, 80), (200, 80)], w=1.1, wobble=0.6, overshoot=4)
    for x in (88, 100, 112):
        hand_ellipse(pen, (x, 72), 7, 5, 0, w=0.9, passes=1)
    for x in (24, 176):
        pen.line([(x, 60), (x, 92)], w=0.9)
    pen.arrow(A(104, 50), A(176, 50), bend=0, w=0.8, head=6)
    pen.arrow(A(96, 50), A(24, 50), bend=0, w=0.8, head=6)
    for k in range(10):
        frost(pen, 4 + (k % 2) * 186 + pen.rng.uniform(-3, 3), 86 + pen.rng.uniform(0, 10))


def first_try(pen):
    hand_ellipse(pen, (70, 60), 30, 12, 0, w=0.9, passes=2)
    hand_ellipse(pen, (70, 60), 70, 28, 0, w=0.8, passes=1)


L.page(pen, {"stone": (s_stone, (0, 30, 140, 90)), "section": (s_section, (0, 40, 200, 100))},
       crossed_draw=(first_try, (0, 28, 140, 92)))
save(pen, os.environ.get("OUT", "entry_warm_ground"))
