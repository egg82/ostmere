"""Journal entry `crow`: a crow standing, side on, facing left. Run: bash render.sh entry_crow -> entry_crow_ink.png

Measured off a photo of a carrion crow side on (Commons, "Common Carrion Crow Side Profile"), as fractions of the
total length L, bill tip to tail tip (here 400): bill ~0.135 L, about the head's length, slimmer than a raven's
(depth at the base ~0.35 of its length) and only slightly hooked; head height ~0.13 L; body axis tilted ~30 degrees,
head high; tail ~0.36 L, square-ended (a raven's is a wedge); folded wing tips reach two thirds down the tail;
tarsus ~0.2 L; standing height ~0.75 L. The throat is smooth (no raven's shaggy hackles). Feathers, not fur: the
raven's method (sparse hatching along the feathers, a second layer for black, layered coverts and open blades).
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 23))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_crow", text_scale=1.3)
A = lambda *p: np.array(p, float)

GROUND = 500
BODY, HEAD = (A(244, 330), 90, 52, 32), (A(184, 226), 26, 25, -10)
GESTURE = [(100, 238), (184, 222), (226, 262), (300, 340), (400, 400), (500, 428)]
LEG_N = [A(258, 396), A(252, 424), A(222, 494)]
LEG_F = [A(284, 400), A(286, 428), A(276, 488)]

body = mk("body", [ell_poly(*BODY), ell_poly(*HEAD), tube([(194, 236), (208, 268), (228, 298)], [52, 62, 72]),
                   tube([(300, 380), (340, 396)], [44, 30]), ell_poly(A(268, 384), 22, 16, 20)],
          16, z=3, tone=0.5, hatch_angle=30, hatch_spacing=4.0)
beak = Part("beak", [(176, 210), (150, 212), (126, 220), (104, 234), (100, 239), (116, 237), (140, 234), (176, 238)],
            z=2.9, n=6, tone=0.3, lw=1.8)
wing = mk("wing", [ell_poly(A(282, 336), 86, 36, 30), tube([(330, 366), (404, 396), (446, 408)], [50, 26, 6])], 6,
          z=4, tone=0.45, hatch_angle=32, hatch_spacing=4.6)
tail = Part("tail", [(340, 384), (400, 402), (462, 418), (500, 424), (498, 440), (458, 438), (398, 424), (338, 400)],
            z=2, n=6, tone=0.55)
tail.hatch_angle, tail.hatch_spacing = 18, 4.0
leg_n = mk("leg_n", [tube(LEG_N, [12, 6, 5]), tube([LEG_N[2], (196, 498)], [4, 3]),
                     tube([LEG_N[2], (208, 502)], [4, 3]), tube([LEG_N[2], (238, 500)], [4, 3])], 2, z=2.8, tone=0.1,
           lw=1.4)
leg_f = mk("leg_f", [tube(LEG_F, [10, 5, 4]), tube([LEG_F[2], (254, 494)], [3.5, 3]),
                     tube([LEG_F[2], (290, 492)], [3.5, 3])], 2, z=1, tone=0.4, lw=1.2)
parts = [ground_shadow(186, 330, 496, 8), leg_f, tail, body, wing, leg_n, beak]

with L.figure(pen, (300, 360)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(170, GROUND + 2), (380, GROUND - 3)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (BODY, HEAD):
            hand_ellipse(pen, c, rx, ry, rot)
        pen.line([(160, 212), (100, 238), (158, 238)], w=0.4, wobble=0.5, overshoot=6)
        hand_ellipse(pen, A(282, 336), 86, 36, 30, w=0.4)
        bones(pen, LEG_N); bones(pen, LEG_F)
    ink_figure(pen, parts, SEED, hatch_t=0.55, form_parts=("body",),
               part_t={"beak": 0.6, "body": 0.36, "wing": 0.34, "tail": 0.34, "leg_n": 0.5},
               cross={"body": (0.8, -60), "wing": (0.85, -50), "tail": (0.8, 75)})
    feather_row(pen, (226, 300), (318, 340), 7, 12, 14, angle_off=60, w=0.9)
    feather_row(pen, (244, 318), (338, 358), 6, 16, 18, angle_off=55, w=0.9)
    for k in range(6):                                   # secondaries along the trailing edge
        b = A(276 + k * 14, 340 + k * 6)
        feather_blade(pen, b, b + (34, 24 - k), 12, w=1.0)
    for k in range(5):                                   # primaries stacking to the tip, tips staggered
        b = A(332 + k * 8, 360 + k * 5)
        feather_blade(pen, b, b + (100 - k * 12, 46 - k * 6), 11, w=1.1, round_tip=False, shaft=k == 0)
    for k, dy in enumerate((-6, -2, 2, 6)):              # tail feathers, square-ended: tips level
        b = A(390, 404 + dy * 1.6)
        feather_blade(pen, b, A(496 - abs(k - 1.5) * 2, 424 + dy * 1.4), 13, w=0.75)
    # head: smooth crown, eye, gape line, nasal bristles; leg scutes, claws
    pen.fill(catmull([(172, 216), (179, 214), (181, 220), (174, 222)], True, 5))
    pen.ellipse((176, 218), 6, 5.5, w=0.6, turns=1.0, wobble=0.2)
    pen.line([(164, 228), (130, 230), (104, 237)], w=0.9)
    for k in range(9):                                   # nasal bristles lying forward over the bill's base
        q = A(160 + k * 2.6, 211 + k * 1.4)
        pen.stroke(np.array([q, q + (-14, 2.5)]), 0.6, taper=(0.1, 0.7), wobble=0.2)
    for t in np.linspace(0.1, 0.9, 7):
        q = LEG_N[1] * (1 - t) + LEG_N[2] * t
        pen.stroke(np.array([q + (-4, -1), q + (4, 1)]), 0.6, taper=(0.2, 0.2))
    for x, y in [(196, 498), (208, 502), (238, 500)]:
        pen.stroke(np.array([(x, y), (x - 4, y + 3)]), 1.1, taper=(0.1, 0.8))


def s_foot(pen):
    fx, fy = 500, 70
    for tip in [(452, 104), (476, 112), (506, 110)]:
        pen.line([(fx, fy), ((fx + tip[0]) / 2, (fy + tip[1]) / 2 + 4), tip], w=1.2, passes=2, spread=0.6)
        pen.stroke(np.array([tip, A(*tip) + (-6, 6)]), 1.4, taper=(0.1, 0.8))
    pen.line([(fx, fy), (536, 86)], w=1.2, passes=2); pen.stroke(np.array([(536, 86), (544, 94)]), 1.4, taper=(0.1, 0.8))
    pen.line([(fx - 4, fy), (fx - 2, 30)], w=1.0); pen.line([(fx + 6, fy - 2), (fx + 6, 30)], w=1.0)
    for y in range(34, 68, 6):
        pen.stroke(np.array([(fx - 3, y), (fx + 6, y + 1)]), 0.6, taper=(0.2, 0.2))


CROW_SIL = [(-17, 11), (-15, 6), (-9, -4), (-2, -11), (3, -15), (7, -17), (10, -15), (17, -13), (10, -11),
            (8, -8), (8, -1), (4, 3), (-4, 5), (-15, 13)]
"""A perched crow far off, facing right, feet at (0, 6): tail down and back, body tilted, head up, bill out."""


def s_row(pen):
    """Crows small on the ridge, seen from below: black shapes against the sky, the row running off past the
    edge."""
    ridge = [(0, 100), (30, 92), (70, 88), (110, 84), (150, 86), (176, 80)]
    pen.line(ridge, w=1.0, passes=2, spread=0.6)
    for k in range(14):                                  # a little ground under the skyline
        q = A(6 + k * 12, 102 - k * 1.3) + pen.rng.normal(0, 1.5, 2)
        pen.stroke(np.array([q, q + (6, 7)]), 0.45, taper=(0.2, 0.5))
    x = 14
    while x < 150:
        y = 93 - 0.07 * x + pen.rng.uniform(-1.5, 1.5)
        s = pen.rng.uniform(0.95, 1.15)
        f = 1 if pen.rng.random() < 0.65 else -1
        hunch = pen.rng.uniform(-0.15, 0.15)
        sil = [A(x + f * (px + hunch * py) * s, y - 6 + py * s) + pen.rng.normal(0, 0.35, 2) for px, py in CROW_SIL]
        pen.fill(catmull(sil, True, 4))
        pen.line(sil + [sil[0]], w=0.7, wobble=0.3)
        pen.stroke(np.array([(x - f * 1, y - 2), (x - f * 1, y + 1)]), 0.7, taper=(0.2, 0.2))
        x += pen.rng.uniform(24, 32)
    pen.line([(156, 72), (162, 66)], w=0.6); pen.line([(164, 76), (170, 70)], w=0.6)


def s_head(pen):
    pen.line([(60, 40), (34, 44), (8, 58), (2, 64), (12, 64), (34, 62), (62, 66)], w=1.3, passes=2, spread=0.5)
    pen.line([(60, 40), (84, 32), (104, 40), (112, 60), (100, 80), (72, 86), (62, 66)], w=1.1, passes=2, spread=0.6)
    pen.line([(62, 54), (34, 54), (8, 61)], w=0.8)
    hand_ellipse(pen, (78, 50), 5, 4.5, 0, w=0.7, passes=1)
    pen.fill(catmull([(76, 48), (80, 48), (80, 52), (76, 52)], True, 4))
    for k in range(7):
        pen.stroke(np.array([(58 + k * 2, 42 + k), (46 + k * 2, 45 + k)]), 0.5, taper=(0.1, 0.7))


def first_try(pen):
    hand_ellipse(pen, (70, 74), 34, 28, 0, w=0.9, passes=2)
    hand_ellipse(pen, (40, 50), 16, 15, 0, w=0.9, passes=1)
    pen.line([(26, 50), (14, 54), (26, 56)], w=0.8)
    pen.line([(100, 82), (124, 92)], w=0.8)
    pen.line([(66, 100), (66, 116)], w=0.7); pen.line([(80, 100), (80, 116)], w=0.7)


L.page(pen, {"foot": (s_foot, (440, 26, 548, 116)), "row": (s_row, (0, 44, 178, 112)),
             "head": (s_head, (0, 28, 114, 90))}, crossed_draw=(first_try, (10, 30, 130, 120)))
save(pen, os.environ.get("OUT", "entry_crow"))
