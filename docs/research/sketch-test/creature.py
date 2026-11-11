"""Unknown (1), "the stilt thing", redrawn by following process.md as written.
Run: python3 creature.py -> creature.svg (SEED, LAYOUT_SEED env vars)"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 11))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "creature")
A = lambda *p: np.array(p, float)

# Step 1, measurements. Invented: measured off the v1 page; real analogues are harvestman legs and a
# heron's hanging neck. Body length B ~210; torso depth ~0.6B; knee height ~2.2B above ground;
# femur ~0.9B, tibia ~1.2B, metatarsus ~1.0B (reverse-bent ankle); neck ~0.65B, head ~0.5B, hanging.
GROUND = 500
TORSO, SAG, SKULL = (A(302, 182), 56, 54, -15), (A(338, 254), 50, 30, 6), (A(246, 386), 26, 36, -4)
REAR = (A(414, 192), 54, 46, 10)  # hunched shoulders + smaller rear: one egg reads as a bun
GESTURE = [(232, 452), (242, 360), (262, 222), (300, 160), (400, 160), (460, 196)]
W_N = [9, 6, 10, 5, 8, 4, 6]
W_F = [7, 4.5, 8, 4, 6.5, 3.5, 5]
LEGS = [("leg_fb", [(408, 214), (452, 120), (470, 58), (482, 170), (512, 300), (490, 400), (494, 488)], W_F, 1, 0.3),
        ("leg_ff", [(300, 214), (272, 130), (255, 62), (244, 180), (206, 310), (226, 400), (214, 484)], W_F, 1.5, 0.3),
        ("leg_nb", [(425, 225), (470, 120), (500, 40), (518, 150), (566, 296), (546, 410), (560, 506)], W_N, 2.5, 0.0),
        ("leg_nf", [(282, 228), (236, 120), (205, 38), (186, 150), (140, 296), (170, 404), (150, 504)], W_N, 2.6, 0.0)]

# Step 4: head built from the neck, in the same mk as the torso.
body = mk("body", [ell_poly(*TORSO), ell_poly(*SAG), ell_poly(*REAR),
                   tube([(262, 170), (330, 132), (400, 146), (452, 176)], [40, 34, 30, 22]),       # spine ridge
                   tube([(266, 212), (246, 262), (238, 310), (244, 350)], [40, 22, 17, 20]),       # hanging neck
                   ell_poly(*SKULL), tube([(246, 400), (240, 436), (234, 464)], [40, 30, 16]),
                   tube([(232, 362), (262, 360)], [12, 10])],    # long face, brow ridge
          10, z=3, lw=1.9)
# Step 5: near legs' hip ends would show as caps, so they go behind the trunk (z just under it).
legs = [mk(n, limb([A(*p) for p in c], w, knuckles=[(2, w[2] * 0.75), (4, w[4] * 0.7)]), 2, z=z, tone=t,
           lw=1.6 if t == 0 else 1.3) for n, c, w, z, t in LEGS]
parts = [ground_shadow(120, 590, 500, 8)] + legs + [body]

with L.figure(pen, (330, 280)):
    # Steps 2-3: gesture, masses, bones; faint
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(110, GROUND + 2), (590, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (TORSO, SAG, SKULL, REAR):
            hand_ellipse(pen, c, rx, ry, rot)
        for _, c, _, _, _ in LEGS:
            bones(pen, [A(*p) for p in c])
    # Step 6: ink. Bare skin: form hatching only.
    ink_figure(pen, parts, SEED, hatch_t=0.5, form_parts=("body",), part_t={"body": 0.38}, cross={"body": (0.9, 60)})
    # Step 7: details. Ribs, spine knuckles, sag folds, the face seam with teeth.
    for i in range(6):
        x = 306 + i * 19
        pen.line([(x, 160 + i * 2), (x + 12, 192 + i), (x + 14, 220 - i)], w=0.9, wobble=0.5, passes=2, spread=0.6)
    for i in range(10):
        x = 270 + i * 18
        y = 146 - 8 * np.sin(i / 9 * np.pi)
        pen.stroke(np.array([(x, y), (x + 3, y - 7)]), 1.3, taper=(0.2, 0.5))
    pen.line([(300, 262), (330, 276), (356, 280)], w=0.6, wobble=0.6)
    pen.line([(246, 366), (243, 400), (240, 432), (235, 458)], w=1.9, passes=2, spread=0.4)
    for k in range(8):
        y = 376 + k * 9.5
        pen.stroke(np.array([(242, y), (238, y + 3)]), 0.9, taper=(0.1, 0.6))
        pen.stroke(np.array([(245, y + 4), (249, y + 7)]), 0.9, taper=(0.1, 0.6))
    pen.line([(228, 360), (250, 354), (266, 362)], w=1.6, passes=2, spread=0.5)        # brow
    for k in range(7):                                                                  # neck vertebrae
        t = k / 6
        q = A(268 - 26 * t, 222 + 120 * t) + (12 - 4 * t, 0)
        pen.stroke(np.array([q, q + (5, 2)]), 1.4, taper=(0.2, 0.5))
    pen.line([(258, 372), (260, 410), (250, 446)], w=0.6, wobble=0.5)                    # cheek plane


def s_tooth(pen):
    fang = [(40, 30), (54, 28), (60, 50), (62, 78), (58, 104), (48, 124), (36, 132), (42, 114), (46, 92), (44, 66), (38, 52)]
    pen.line(fang + [fang[0]], w=1.2, passes=2, spread=0.6)
    pen.line([(40, 30), (34, 14), (38, 10)], w=1.0); pen.line([(54, 28), (58, 12), (62, 14)], w=1.0)
    for k in range(9):
        y = 58 + k * 7
        pen.stroke(np.array([(52 - k * 0.5, y), (60 - k * 0.9, y + 4)]), 0.55, taper=(0.1, 0.4))


def s_face(pen):
    cx = 62
    for side in (-1, 1):
        pen.line([(cx + side * 3, 196), (cx + side * 24, 214), (cx + side * 40, 246), (cx + side * 34, 280),
                  (cx + side * 12, 302)], w=1.4, passes=2, spread=0.7)
        pen.line([(cx + side * 3, 196), (cx + side * 9, 222), (cx + side * 14, 250), (cx + side * 10, 280),
                  (cx + side * 12, 302)], w=1.0)
        for k in range(7):
            t = (k + 0.5) / 7
            y = 204 + t * 92
            x0 = cx + side * (4 + 10 * np.sin(t * np.pi))
            pen.stroke(np.array([(x0, y), (x0 - side * 7, y + 3)]), 1.1, taper=(0.1, 0.7))


def s_knee(pen):
    pen.line([(20, 120), (60, 50)], w=1.3, passes=2, spread=0.6)
    pen.line([(36, 126), (70, 60)], w=1.1, passes=2, spread=0.6)
    pen.line([(60, 50), (110, 110)], w=1.3, passes=2, spread=0.6)
    pen.line([(70, 60), (100, 120)], w=1.1, passes=2, spread=0.6)
    hand_ellipse(pen, (66, 56), 14, 11, 20, w=1.1, passes=2)
    for k in range(6):
        pen.stroke(np.array([(58 + k * 3, 64), (62 + k * 3, 72)]), 0.6, taper=(0.1, 0.5))


def first_try(pen):
    fa = [(30, 540), (48, 528), (80, 526), (98, 538), (86, 550), (50, 552)]
    pen.line(fa + [fa[0]], w=0.9, passes=2)
    for x in (40, 52, 76, 88):
        pen.line([(x, 550), (x - 6, 532), (x - 2, 572)], w=0.8)
    pen.line([(32, 542), (22, 560), (24, 574)], w=0.8)


# Step 8: page from data and a seed
L.page(pen, {"tooth": (s_tooth, (30, 8, 66, 134)), "face": (s_face, (18, 194, 106, 304)),
             "knee": (s_knee, (14, 36, 116, 130))}, crossed_draw=(first_try, (16, 520, 104, 580)))
save(pen, "creature")
