"""Journal entry `old_road` (places): from the ridge, a straight dent in the ash running away over the next low hill,
a stake or two marking it. Run: bash render.sh entry_old_road -> entry_old_road_ink.png

A place, not a creature, so no reference to measure; the frame is a road seen down its length from a little above.
A cart is about 1.6 m across and the dent is a little over that, about 2 m. Standing on the ridge with the eye about
2 m over the near ground, the near edge of the drawing is some 4 m out, so the dent there is half the page wide; the
near slope's lines run to one vanishing point (VP_NEAR) and the far hill's, which climb towards us, to a higher one
(VP_FAR). Between them is the dead ground behind the brow, where the road drops out of sight. Where the road tops the
far hill it notches the skyline. The dent's walls are hachures, the surveyor's mark for a cutting (heavier on the left
wall, which faces away from the light); the ash, the land and the stakes are strokes only.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 16))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_old_road", text_scale=1.3)
A = lambda *p: np.array(p, float)
rng = np.random.default_rng(SEED)

VP_NEAR, VP_FAR = A(330, 200), A(330, 120)
NEAR_Y, BROW_Y, FOOT_Y, CREST_Y = 540, 352, 322, 222
WALL = 0.16
"""How much of the dent's half width each sloping wall takes."""


def edge(vp, half_at, y_at, y, side, inset=0.0):
    """The x of a road edge at height y, on lines to vp; half_at is the half width at y_at."""
    half = half_at * (vp[1] - y) / (vp[1] - y_at)
    return vp[0] + side * half * (1 - inset)


NEAR_HALF, FAR_HALF = 150, 44            # half widths at NEAR_Y and at FOOT_Y
crest = lambda x: CREST_Y + 0.00042 * (x - 330) ** 2 + 4 * np.sin(x / 47)   # the far hill's skyline


def notch(x):
    """The skyline, cut down where the dent tops the hill."""
    hw = edge(VP_FAR, FAR_HALF, FOOT_Y, CREST_Y, 1) - 330
    d = abs(x - 330)
    return crest(x) + (8.0 * (1 - (d / hw) ** 2) if d < hw else 0.0)


SPANS = {"lnear": (VP_NEAR, NEAR_HALF, NEAR_Y, NEAR_Y, BROW_Y, -1), "rnear": (VP_NEAR, NEAR_HALF, NEAR_Y, NEAR_Y, BROW_Y, 1),
         "lfar": (VP_FAR, FAR_HALF, FOOT_Y, FOOT_Y, CREST_Y + 4, -1), "rfar": (VP_FAR, FAR_HALF, FOOT_Y, FOOT_Y, CREST_Y + 4, 1)}


def lip(pen, name, w):
    """A dent's edge as the hand pulls it: two or three runs, the gaps where the ash lip softens."""
    vp, half, ya, y0, y1, side = SPANS[name]
    cuts = np.sort(rng.uniform(0.15, 0.85, 2))
    for a, b in ((0, cuts[0]), (cuts[0] + 0.04, cuts[1]), (cuts[1] + 0.04, 1)):
        ys = y0 + (y1 - y0) * np.linspace(a, b, 6)
        pen.line([(edge(vp, half, ya, y, side), y) for y in ys], w=w, wobble=0.5, overshoot=3)


def hachures(pen, name, w, every, keep):
    """The wall as a surveyor marks a cutting: short strokes from the lip down into the dent, heavy at the lip,
    spaced and shortened with distance, some left out where the hand hurried."""
    vp, half, ya, y0, y1, side = SPANS[name]
    y = y0
    while y > y1 + 2:
        k = (vp[1] - y) / (vp[1] - ya)                     # perspective scale at this depth
        if rng.random() < keep:
            x = edge(vp, half, ya, y, side)
            ln = half * k * WALL * rng.choice([rng.uniform(0.5, 0.9), rng.uniform(0.9, 1.7)], p=[0.35, 0.65])
            q = np.array([x - side * ln, y + ln * rng.uniform(0.15, 0.55)])
            pen.stroke(np.array([(x, y), (np.array([x, y]) + q) / 2, q]), w * max(k, 0.45),
                       taper=(0.05, 0.6), wobble=0.3)
        y -= every * max(k, 0.25) * rng.uniform(0.55, 1.6)


def ash(pen, x, y, k):
    """A short level mark for loose ash; k shrinks it with distance."""
    L_ = rng.uniform(4, 9) * k
    pen.stroke(np.array([(x - L_ / 2, y), (x + L_ / 2, y + rng.normal(0, 0.4))]), 0.5, taper=(0.2, 0.3), wobble=0.3)


def stalk(pen, x, y, h):
    """A dead stalk poking up through the ash."""
    pen.line([(x, y), (x + rng.normal(0, h * 0.15), y - h)], w=0.55, wobble=0.3)


with L.figure(pen, (300, 360)):
    with pen.construction():
        pen.line([(40, 200), (580, 200)], w=0.4, wobble=0.6, overshoot=8)          # eye level
        for side in (-1, 1):                                                         # the dent run back to its point
            pen.line([(edge(VP_NEAR, NEAR_HALF, NEAR_Y, NEAR_Y + 20, side), NEAR_Y + 20), tuple(VP_NEAR)], w=0.4,
                     wobble=0.5)
            pen.line([(edge(VP_FAR, FAR_HALF, FOOT_Y, FOOT_Y, side), FOOT_Y), tuple(VP_FAR)], w=0.4, wobble=0.5)
        hand_ellipse(pen, VP_FAR, 5, 5, 0, w=0.45, passes=1)
    xs = np.linspace(30, 575, 40)
    sky = [(x, notch(x) + rng.normal(0, 0.5)) for x in xs]
    pen.line(sky[:19], w=1.4, wobble=0.6, overshoot=4)
    pen.line(sky[18:], w=1.2, wobble=0.6, overshoot=4)
    for x0, x1, y0 in ((440, 590, 206),):                                            # a farther rise behind
        pen.line([(x, y0 - 6 * np.sin((x - x0) / (x1 - x0) * np.pi)) for x in np.linspace(x0, x1, 8)], w=0.6,
                 wobble=0.6)
    brow = lambda x: BROW_Y + 0.00018 * (x - 300) ** 2
    for x0, x1 in ((15, edge(VP_NEAR, NEAR_HALF, NEAR_Y, BROW_Y, -1) + 6),
                   (edge(VP_NEAR, NEAR_HALF, NEAR_Y, BROW_Y, 1) - 6, 590)):
        pen.line([(x, brow(x)) for x in np.linspace(x0, x1, 9)], w=1.3, wobble=0.6, overshoot=3)
    xl, xr = edge(VP_NEAR, NEAR_HALF, NEAR_Y, BROW_Y, -1), edge(VP_NEAR, NEAR_HALF, NEAR_Y, BROW_Y, 1)
    dip = [(x, brow(x) + 14 * max(0.0, np.sin(np.pi * (x - xl) / (xr - xl))) ** 0.35) for x in np.linspace(xl - 4, xr + 4, 12)]
    pen.line(dip, w=1.0, wobble=0.6)                                                 # the brow sags where the dent crosses it
    for name, w, every, keep in (("lnear", 1.0, 7, 0.9), ("rnear", 0.7, 10, 0.55), ("lfar", 1.0, 7, 0.9),
                                 ("rfar", 0.7, 10, 0.5)):
        hachures(pen, name, w, every, keep)
    for name, w in (("lnear", 1.8), ("rnear", 1.2), ("lfar", 1.3), ("rfar", 0.9)):
        lip(pen, name, w)
    SX = 452                                                                         # the near stake, cut square
    pen.line([(SX, 494), (SX - 4, 398)], w=2.1, wobble=0.4, passes=2)
    pen.line([(SX + 10, 492), (SX + 6, 395)], w=1.3, wobble=0.4)
    pen.line([(SX - 5, 400), (SX + 1, 393), (SX + 7, 397)], w=1.1, wobble=0.3)
    for k in range(13):
        y = 404 + k * 6.8 + rng.uniform(-1.5, 1.5)
        x = SX - 3.5 - (y - 400) * 0.042
        pen.line([(x, y), (x + rng.uniform(4, 7), y + 7)], w=0.55, wobble=0.2)
    for k in range(260):                                                             # loose ash, finer with distance
        y = rng.uniform(CREST_Y + 6, NEAR_Y + 10)
        x = rng.uniform(15, 590)
        far = y < BROW_Y - 2
        if far and (y < notch(x) + 4 or y > FOOT_Y + 0.0001 * (x - 330) ** 2 - 3):
            continue
        vp, half, ya = (VP_FAR, FAR_HALF, FOOT_Y) if far else (VP_NEAR, NEAR_HALF, NEAR_Y)
        inside = abs(x - 330) < abs(edge(vp, half, ya, y, 1) - 330) + 4
        if inside and rng.random() < 0.85:                                           # the dent's floor is smoother
            continue
        if not inside and rng.random() < 0.08:
            stalk(pen, x, y, 4 + 10 * (y - CREST_Y) / (NEAR_Y - CREST_Y))
        else:
            ash(pen, x, y, 0.35 + 0.65 * (y - CREST_Y) / (NEAR_Y - CREST_Y))
    for x, y, h in ((281, 300, 18), (316, 238, 7)):                                  # the stakes farther on
        pen.line([(x, y), (x - 0.6, y - h)], w=1.7 if h > 8 else 1.2, wobble=0.3)
        pen.line([(x - 3, y + 0.5), (x + 3, y)], w=0.5, wobble=0.3)
    pen.line([(SX - 18, 495), (SX + 4, 489), (SX + 24, 494)], w=0.8, wobble=0.6)     # ash heaped round its foot
    pen.line([(SX + 10, 494), (SX + 38, 500)], w=0.5, wobble=0.4)                    # its shadow


def s_section(pen):
    """Across the dent: the ash surface sagging, and where the bed might lie under it."""
    surf = [(0, 60), (40, 60), (58, 63), (70, 72), (130, 72), (142, 63), (160, 60), (200, 60)]
    pen.line(surf, w=1.1, wobble=0.6, overshoot=4)
    bed = np.linspace(58, 142, 14)
    for a, b in zip(bed[::2], bed[1::2]):
        pen.line([(a, 104), (b, 104)], w=0.8, wobble=0.3)
    pen.arrow(A(100, 76), A(100, 100), bend=0, w=0.7, head=5)
    pen.arrow(A(70, 48), A(130, 48), bend=0, w=0.8, head=6)
    pen.arrow(A(130, 48), A(70, 48), bend=0, w=0.8, head=6)


def s_stake(pen):
    """The near stake close to, the ash heaped round its foot."""
    st = mk("s", [tube([A(40, 100), A(36, 20)], [8, 6])], 2, z=1, tone=0.4)
    sc = SketchScene([st], pen, seed=SEED)
    sc.quick_hatch(st, t=0.4, angle=80, w=0.55)
    sc.search_contour(st, w=1.5, passes=(0.4, 1.0))
    pen.line([(0, 102), (24, 100), (38, 95), (52, 99), (90, 102)], w=0.9, wobble=0.6, overshoot=5)
    pen.line([(33, 30), (40, 34)], w=0.7)


def first_try(pen):
    pen.line([(0, 80), (60, 50), (140, 60)], w=0.9, wobble=0.6)
    pen.line([(40, 92), (68, 52)], w=0.8); pen.line([(100, 92), (74, 52)], w=0.8)


L.page(pen, {"section": (s_section, (0, 40, 200, 110)), "stake": (s_stake, (0, 15, 90, 105))},
       crossed_draw=(first_try, (0, 45, 140, 95)))
save(pen, os.environ.get("OUT", "entry_old_road"))
