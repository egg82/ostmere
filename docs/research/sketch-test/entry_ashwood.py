"""Journal entry `ashwood` (places): a stand of standing dead trunks, one near, bracket fungus stepping up its side,
others thinning off behind. Run: bash render.sh entry_ashwood -> entry_ashwood_ink.png

A place, so the reference is the kind of thing rather than one drawing: a dead hardwood snag keeps its trunk taper
(about 1:14 width to height over the part drawn), loses its crown to a jagged break and its branches to short stubs,
and sheds bark in long strips that bare the grey wood. Hoof and shelf brackets (Fomes, Ganoderma) grow out of one
side in a loose column, each about 0.8 trunk-widths across, projecting about half that, and spaced about 1 to 1.5
of their own widths apart. The near trunk is about 46 wide at the root flare and 30 at the break, 360 tall; the far
trunks shrink with distance and stand on a ground line that rises behind.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 23))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_ashwood", text_scale=1.3)
A = lambda *p: np.array(p, float)
rng = np.random.default_rng(SEED)
BASE, TOP = 470, 112


def axis(y):
    """The near trunk's centre at height y: a slight lean and a kink where it once took the wind."""
    return 296 + 0.05 * (BASE - y) - 6 * np.sin((BASE - y) / 120)


def width(y):
    return np.interp(BASE - y, [0, 30, 120, 360], [58, 44, 38, 30])


def edge(y, side):
    return A(axis(y) + side * width(y) / 2, y)


ys = np.linspace(BASE, TOP, 30)
trunk_polys = [tube([(axis(y), y) for y in ys], [width(y) for y in ys])]
trunk_polys.append(tube([edge(BASE - 20, -1) + (8, 0), edge(BASE, -1) + (-12, 4)], [14, 6]))   # a root going in
x0, x1 = axis(TOP) - 15, axis(TOP) + 15
trunk_polys.append(np.array([(x0, TOP + 4), (x0 + 3, TOP - 22), (x0 + 9, TOP - 8), (x0 + 15, TOP - 40),
                             (x0 + 20, TOP - 14), (x1 - 2, TOP - 4), (x1, TOP + 4)]))   # the jagged break
trunk_polys.append(tube([edge(300, -1) + (4, 0), edge(300, -1) + (-26, -14)], [10, 6]))   # branch stubs
trunk_polys.append(tube([edge(196, 1) + (-4, 0), edge(196, 1) + (20, -16)], [9, 5]))
trunk = mk("trunk", trunk_polys, 4, z=3, tone=0.15, lw=1.9)


EYE = 380
"""The sketcher's eye height on the near trunk: shelves above it show their undersides, so their lips bow up."""


def bracket(name, y, side, proj, thick, wrap=70):
    """A shelf fungus round the trunk at height y, on one side (+1 right, -1 left): its lip an arc about the trunk's
    axis, from where it comes out from behind the trunk to wrap degrees past the trunk's edge across its front, proj
    out from the bark."""
    half = width(y) / 2
    rx = half + proj
    ry, c = rx * float(np.clip((y - EYE) / 260, -0.32, 0.32)), A(axis(y), y)
    te = np.degrees(np.arccos(half / rx))
    t = np.radians(np.linspace(-te, te + wrap, 18))
    if side < 0:
        t = np.pi - t
    top = np.column_stack([c[0] + rx * np.cos(t), c[1] + ry * np.sin(t)])
    u = np.linspace(0, 1, len(t))
    th = thick * np.minimum(1.0, np.minimum(u, 1 - u) * 5 + 0.35)
    lip = top + np.column_stack([np.zeros(len(t)), th])
    p = Part(name, np.vstack([top, lip[::-1]]), z=5, tone=0.25, lw=1.3, n=4)
    p.hatch_angle, p.hatch_spacing = 4, 3.2
    return p, top, lip


BR = [bracket("b0", 434, 1, 26, 13, 40), bracket("b1", 392, 1, 32, 15, 25), bracket("b2", 350, -1, 24, 12, 30),
      bracket("b3", 304, 1, 28, 12, 20), bracket("b4", 262, 1, 20, 10, 35), bracket("b5", 226, -1, 15, 8, 15)]


def far_trunk(name, x, base, h, w, lean, z=1):
    """A trunk further off: thinner, shorter, a broken top and maybe a stub."""
    top = base - h
    c = [(x + lean * (base - y) / h, y) for y in np.linspace(base, top, 12)]
    polys = [tube(c, [w * 1.5, w * 1.05, w * 0.95, w * 0.7]), ell_poly(A(x, base - 2), w * 0.95, w * 0.28)]
    xt = c[-1][0]
    polys.append(np.array([(xt - w * 0.4, top + 3), (xt - w * 0.2, top - h * 0.08), (xt + w * 0.1, top - 2),
                           (xt + w * 0.3, top - h * 0.05), (xt + w * 0.4, top + 3)]))
    if rng.random() < 0.6:
        yb = base - h * rng.uniform(0.45, 0.7)
        sgn = rng.choice([-1, 1])
        xb = x + lean * (base - yb) / h
        polys.append(tube([(xb, yb), (xb + sgn * w * 1.2, yb - w * 0.7)], [w * 0.35, w * 0.2]))
    return mk(name, polys, 3, z=z, tone=0.3, lw=1.3)


FAR = [far_trunk("f0", 168, 414, 230, 22, -8, z=2), far_trunk("f1", 430, 408, 220, 24, 9, z=2),
       far_trunk("f2", 96, 384, 150, 13, 4), far_trunk("f3", 520, 380, 140, 12, -3),
       far_trunk("f4", 232, 376, 120, 10, 6)]


with L.figure(pen, (300, 300)):
    with pen.construction():
        pen.line([(axis(y), y) for y in np.linspace(BASE + 10, TOP - 30, 12)], w=0.45, wobble=0.6, overshoot=8)
        pen.line([(20, BASE + 4), (580, BASE - 2)], w=0.45, wobble=0.7, overshoot=6)
        pen.line([(30, 384), (580, 372)], w=0.4, wobble=0.8, overshoot=6)
        for y in (430, 386, 300):
            hand_ellipse(pen, (axis(y), y), width(y) / 2 + 20, (width(y) / 2 + 20) * 0.3, 0, w=0.4, passes=1)
    ink_figure(pen, FAR, SEED, hatch_t=0.64, contour_w=1.15)
    for x, w in ((60, 0.5), (392, 0.5), (560, 0.45), (482, 0.4)):   # trunks furthest off, clear of the near one
        h = rng.uniform(50, 90)
        pen.line([(x, 374), (x + rng.uniform(-3, 3), 374 - h)], w=w + 0.3, wobble=0.4)
        pen.line([(x + 3, 374), (x + 2, 374 - h * 0.8)], w=w, wobble=0.4)
    for f, x, b in ((FAR[0], 168, 414), (FAR[1], 430, 408), (FAR[2], 96, 384), (FAR[3], 520, 380), (FAR[4], 232, 376)):
        for k in range(5):                                # where each meets the ground
            q = A(x + rng.uniform(-22, 22), b + rng.uniform(-1, 4))
            pen.line([q, q + (rng.uniform(5, 10), 0)], w=0.5, wobble=0.3)
    for y, wd in ((304, 15), (272, 12), (330, 10)):           # small shelves on the far trunk to the right too
        e = A(430 + 9 * (408 - y) / 220 + 12, y)
        pen.line(catmull(np.array([e, e + (wd, -2), e + (wd + 3, 3), e + (wd * 0.5, 6), e + (1, 6)]), False, 6),
                 w=0.9, wobble=0.3)
    ink_figure(pen, [trunk, *[b[0] for b in BR]], SEED, hatch_t=0.56, part_t={"trunk": 0.48}, contour_w=1.9)
    for _, top, lip in BR:                                # growth bands round each lip, the shade under it
        for k in (0.35, 0.65):
            band = top + (lip - top) * k
            pen.line(band[3:-3], w=0.5, wobble=0.3)
        pen.line(lip[2:-2] + (0, 2.0), w=0.9, wobble=0.3)
    shelf = np.any([b[0].mask for b in BR], axis=0)

    def on_bark(pts):
        """Split a stroke where it would run over a shelf, which sits in front of the bark."""
        runs, cur = [], []
        for q in pts:
            i, j = (int(np.clip(v * S, 0, n - 1)) for v, n in ((q[1], shelf.shape[0]), (q[0], shelf.shape[1])))
            if shelf[i, j]:
                if len(cur) > 1:
                    runs.append(cur)
                cur = []
            else:
                cur.append(q)
        return runs + ([cur] if len(cur) > 1 else [])

    def across(y, f):
        return axis(y) + f * width(y) / 2

    rag = [(across(y, f), y) for f, y in zip(np.linspace(-1, 1, 7), 318 + np.array([0, 5, -3, 6, 9, 2, 4]))]
    pen.line(rag, w=0.9, wobble=0.4)                      # where the bark ends, ragged; bare wood above it
    for k in range(26):                                   # bark below: furrows, closer on the shaded right
        f = np.clip(rng.normal(0.25, 0.5), -0.9, 0.92)
        y0 = rng.uniform(326, BASE - 30)
        yy = np.linspace(y0, min(BASE - 4, y0 + rng.uniform(30, 90)), 8)
        for run in on_bark([A(across(y, f + rng.normal(0, 0.02)), y) for y in yy]):
            pen.line(run, w=rng.uniform(0.5, 0.85), wobble=0.4)
    for k in range(7):                                    # bare wood above: a few long checks along the grain
        f = rng.uniform(-0.6, 0.6)
        y0 = rng.uniform(TOP + 10, 280)
        yy = np.linspace(y0, min(314, y0 + rng.uniform(40, 110)), 8)
        for run in on_bark([A(across(y, f), y) for y in yy]):
            pen.line(run, w=0.5, wobble=0.3)
    for k in range(60):                                   # the grey ground: short flat strokes, thinner far off
        x, y = rng.uniform(30, 570), rng.uniform(372, 500)
        if abs(x - axis(BASE)) < 40 and y < BASE:
            continue
        w = 0.4 + 0.25 * (y - 372) / 128
        pen.line([(x, y), (x + rng.uniform(6, 14), y + rng.uniform(-0.5, 0.5))], w=w, wobble=0.3)
    for x, y in ((250, 482), (360, 478), (110, 418)):     # a few fallen bits on the ground
        pen.line([(x, y), (x + 22, y - 3)], w=0.9, wobble=0.4)


def s_bracket(pen):
    """One shelf side on, cut through: the ridged top, the pore face under it, the trunk behind."""
    pen.line([(30, 0), (34, 130)], w=1.4, wobble=0.5, overshoot=5)
    pen.line([(20, 4), (22, 128)], w=0.7, wobble=0.5)
    prof = np.array([(34, 34), (70, 42), (102, 52), (120, 63), (119, 73), (98, 77), (64, 79), (34, 98)])
    pen.line(catmull(prof, False, 8), w=1.5, wobble=0.4)
    for k, (x, y) in enumerate(((62, 41), (84, 47), (102, 53))):   # the yearly ridges, each a step down the top
        pen.line([(x, y), (x + 5, y + 9 + k * 2), (x + 3, y + 22 - k * 3)], w=0.6, wobble=0.3)
    for x in range(42, 114, 5):                           # pore face, close strokes
        pen.line([(x, 77 + (114 - x) * 0.04), (x + 1, 81 + (114 - x) * 0.06)], w=0.45, wobble=0.2)


def s_break(pen):
    """The top of a trunk where it snapped: splinters standing, the heart gone soft."""
    pen.line([(40, 130), (42, 50), (48, 24), (54, 44), (62, 10), (70, 38), (78, 30), (82, 52), (84, 130)],
             w=1.4, wobble=0.5)
    for x in (50, 60, 70):
        pen.line([(x, 60), (x + 1, 128)], w=0.55, wobble=0.4)
    hand_ellipse(pen, (63, 56), 10, 4, 0, w=0.6, passes=1)


def first_try(pen):
    pen.line([(70, 120), (70, 60)], w=1.2)
    hand_ellipse(pen, (70, 46), 32, 26, 0, w=0.9, passes=2)


L.page(pen, {"bracket": (s_bracket, (0, 0, 130, 130)), "break": (s_break, (30, 0, 95, 130))},
       crossed_draw=(first_try, (30, 15, 110, 122)))
save(pen, os.environ.get("OUT", "entry_ashwood"))
