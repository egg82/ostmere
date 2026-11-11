"""Raven with the journal method. Run: python3 raven.py -> raven.svg (SEED, LAYOUT_SEED env vars)"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 21))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "raven")
A = lambda *p: np.array(p, float)

# Raven proportions: head ~0.4 of body length, bill ~ head length, tail wedge ~0.6 of body,
# tarsus ~0.35 of body length. Feathers, not fur: smooth form shading, sparse hatching along the
# feather direction, layered feather edges on wing and tail, lanceolate throat feathers.
GROUND = 470
BODY, HEAD = (A(305, 322), 92, 60, 26), (A(206, 246), 36, 32, -10)
GESTURE = [(116, 262), (206, 236), (262, 262), (330, 290), (420, 350), (486, 392)]
LEG_N = [A(296, 372), A(300, 404), A(296, 462)]
LEG_F = [A(322, 368), A(328, 400), A(326, 458)]

body = mk("body", [ell_poly(*BODY), ell_poly(*HEAD), tube([(214, 262), (240, 296), (268, 312)], [44, 54, 50])],
          16, z=3, tone=0.35, hatch_angle=26, hatch_spacing=4.4)
beak = Part("beak", [(184, 228), (152, 233), (126, 248), (110, 262), (122, 262), (150, 260), (186, 266)],
            z=7, n=6, tone=0.15, lw=2.0)
wing = mk("wing", [ell_poly(A(338, 314), 98, 40, 28), tube([(390, 340), (456, 382), (484, 396)], [50, 26, 6])], 6,
          z=4, tone=0.3, hatch_angle=30, hatch_spacing=4.6)
tail = Part("tail", [(392, 340), (440, 362), (476, 382), (494, 398), (474, 410), (436, 398), (396, 372)], z=2, n=6,
            tone=0.4)
tail.hatch_angle, tail.hatch_spacing = 28, 4.0
leg_n = mk("leg_n", [tube(LEG_N, [9, 6, 5]), tube([LEG_N[2], (266, 468)], [4, 3]), tube([LEG_N[2], (280, 472)], [4, 3]),
                     tube([LEG_N[2], (318, 470)], [4, 3])], 2, z=5, tone=0.1, lw=1.4)
leg_f = mk("leg_f", [tube(LEG_F, [8, 5, 4]), tube([LEG_F[2], (300, 464)], [3.5, 3]),
                     tube([LEG_F[2], (342, 464)], [3.5, 3])], 2, z=1, tone=0.4, lw=1.2)
parts = [ground_shadow(250, 380, 466, 8), leg_f, tail, body, wing, leg_n, beak]

with L.figure(pen, (300, 340)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(200, GROUND + 2), (430, GROUND - 3)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (BODY, HEAD):
            hand_ellipse(pen, c, rx, ry, rot)
        pen.line([(186, 230), (112, 262), (186, 266)], w=0.4, wobble=0.5, overshoot=6)
        hand_ellipse(pen, A(338, 314), 98, 40, 28, w=0.4)
        bones(pen, LEG_N); bones(pen, LEG_F)
    ink_figure(pen, parts, SEED, hatch_t=0.55, form_parts=("body",),
               part_t={"beak": 0.75, "body": 0.5, "wing": 0.45, "tail": 0.45},
               cross={"body": (0.95, -60), "wing": (1.05, -50), "tail": (1.0, 75)})
    # wing: covert rows (short layered edges), then secondaries and primaries as open blades
    feather_row(pen, (268, 286), (372, 318), 7, 12, 14, angle_off=60, w=0.9)
    feather_row(pen, (286, 302), (396, 334), 6, 16, 18, angle_off=55, w=0.9)
    for k in range(6):  # secondaries along the trailing edge
        b = A(318 + k * 16, 318 + k * 6)
        feather_blade(pen, b, b + (36, 26 - k), 13, w=1.0)
    for k in range(5):  # primaries stacking to the tip, tips staggered
        b = A(380 + k * 8, 338 + k * 6)
        feather_blade(pen, b, b + (100 - k * 12, 56 - k * 7), 12, w=1.1, round_tip=False, shaft=k == 0)
    for k, (dx, dy) in enumerate([(-6, -4), (0, 0), (6, 3), (10, 8)]):  # tail feathers, centre longest
        b = A(420 + dx, 362 + dy)
        feather_blade(pen, b, A(486 - abs(k - 1.5) * 8 + dx * 0.3, 396 + dy), 14, w=0.75)
    # throat: lanceolate feather tips, not fur
    for k in range(9):
        q = A(206 + k * 6.5, 270 + k * 5 + pen.rng.uniform(-2, 2))
        pen.line([q + (-3, -2), q + (1, 8 + pen.rng.uniform(0, 4)), q + (4, -1)], w=0.6, wobble=0.15)
    # head: smooth; eye, bill line, nostril bristles; leg scutes, claws
    pen.fill(catmull([(196, 238), (203, 236), (205, 242), (198, 244)], True, 5))
    pen.ellipse((200, 240), 6, 5.5, w=0.6, turns=1.0, wobble=0.2)
    pen.line([(186, 250), (150, 252), (118, 260)], w=0.9)
    for k in range(6):
        q = A(182 + k * 3, 232 + k)
        pen.stroke(np.array([q, q + (-8, 1.5)]), 0.5, taper=(0.1, 0.7), wobble=0.2)
    for y in range(408, 456, 6):
        pen.stroke(np.array([(294, y), (302, y + 1)]), 0.6, taper=(0.2, 0.2))
    for x, y in [(266, 468), (280, 472), (318, 470)]:
        pen.stroke(np.array([(x, y), (x - 3, y + 4)]), 1.1, taper=(0.1, 0.8))


# side studies, drawn at native coords; the layout fits them into free corners
def s_foot(pen):
    fx, fy = 500, 70
    for tip in [(452, 104), (476, 112), (506, 110)]:
        pen.line([(fx, fy), ((fx + tip[0]) / 2, (fy + tip[1]) / 2 + 4), tip], w=1.2, passes=2, spread=0.6)
        pen.stroke(np.array([tip, A(*tip) + (-6, 6)]), 1.4, taper=(0.1, 0.8))
    pen.line([(fx, fy), (536, 86)], w=1.2, passes=2); pen.stroke(np.array([(536, 86), (544, 94)]), 1.4, taper=(0.1, 0.8))
    pen.line([(fx - 4, fy), (fx - 2, 30)], w=1.0); pen.line([(fx + 6, fy - 2), (fx + 6, 30)], w=1.0)
    for y in range(34, 68, 6):
        pen.stroke(np.array([(fx - 3, y), (fx + 6, y + 1)]), 0.6, taper=(0.2, 0.2))


def s_feather(pen):
    pen.line([(40, 560), (110, 470)], w=1.0, passes=2, spread=0.4)
    for k in range(14):
        t = k / 13
        q = A(40, 560) * (1 - t) + A(110, 470) * t
        pen.stroke(np.array([q, q + (14 - 6 * t, 6 + 4 * t)]), 0.55, taper=(0.1, 0.4))
        pen.stroke(np.array([q, q + (-8 + 3 * t, -10 + 2 * t)]), 0.55, taper=(0.1, 0.4))


def s_head(pen):
    pen.line([(60, 40), (30, 46), (6, 62), (0, 70), (10, 70), (30, 66), (62, 70)], w=1.3, passes=2, spread=0.5)
    pen.line([(60, 40), (84, 34), (104, 46), (110, 66), (98, 84), (70, 88), (62, 70)], w=1.1, passes=2, spread=0.6)
    pen.line([(62, 56), (30, 58), (6, 66)], w=0.8)
    hand_ellipse(pen, (76, 52), 5, 4.5, 0, w=0.7, passes=1)
    pen.fill(catmull([(74, 50), (78, 50), (78, 54), (74, 54)], True, 4))
    for k in range(6):
        pen.stroke(np.array([(58 + k * 2, 44 + k), (48 + k * 2, 46 + k)]), 0.5, taper=(0.1, 0.7))


def first_try(pen):
    hand_ellipse(pen, (70, 74), 34, 28, 0, w=0.9, passes=2)
    hand_ellipse(pen, (40, 50), 16, 15, 0, w=0.9, passes=1)
    pen.line([(26, 50), (14, 54), (26, 56)], w=0.8)
    pen.line([(100, 82), (124, 92)], w=0.8)
    pen.line([(66, 100), (66, 116)], w=0.7); pen.line([(80, 100), (80, 116)], w=0.7)


L.page(pen, {"foot": (s_foot, (440, 26, 548, 116)), "feather": (s_feather, (28, 466, 128, 566)),
             "head": (s_head, (0, 30, 112, 90))}, crossed_draw=(first_try, (10, 30, 130, 120)))
save(pen, "raven")
