"""Wolf (third pass) with the journal method. Run: python3 wolf3.py -> wolf3.svg"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 7))
pen = JournalPen(SEED)
# page box from the caller (the game passes the viewport's page box); 600x600 by default
PW, PH = int(os.environ.get("PAGE_W", 600)), int(os.environ.get("PAGE_H", 600))
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "wolf", W=PW, H=PH,
           text_scale=float(os.environ.get("TEXT_SCALE", 1.0)), fig_scale=float(os.environ.get("FIG_SCALE", 1.0)))
A = lambda *p: np.array(p, float)

# 1. gesture + skeleton. Proportions off the Gessner hound, adjusted to wolf:
#    body length ~1.15 x withers height H, chest depth ~0.5 H, head length ~0.37 H.
GROUND, WITHERS = 500, A(228, 272)
J = {k: A(*v) for k, v in dict(
    occ=(150, 332), nose=(58, 384),
    shoulder=(206, 338), elbow=(220, 388), wrist=(230, 448), fpaw=(216, 486),
    f_shoulder=(222, 336), f_elbow=(246, 390), f_wrist=(262, 446), f_paw=(254, 483),
    hip=(446, 304), stifle=(418, 382), hock=(470, 438), hpaw=(462, 486),
    f_hip=(452, 300), f_stifle=(440, 378), f_hock=(494, 430), f_hpaw=(490, 482)).items()}
RIB, PEL, CRAN = (A(262, 334), 64, 64, -8), (A(444, 298), 36, 32, 10), (A(128, 344), 27, 24, -20)
GESTURE = [J["nose"] + (8, -14), J["occ"], WITHERS + (6, -2), (340, 282), (445, 276), (484, 296), (504, 350),
           (500, 404)]

# 2. masses -> silhouettes
trunk = mk("trunk", [ell_poly(*RIB), ell_poly(*PEL),
                     tube([WITHERS + (34, 32), (190, 306), J["occ"] + (8, 8)], [70, 66, 44]),          # neck + ruff
                     tube([WITHERS + (4, 28), J["shoulder"], J["elbow"] + (2, -8)], [44, 38, 26]),     # shoulder, upper arm
                     tube([(290, 320), (360, 304), (432, 294)], [116, 64, 62])],                      # loin
           22, z=3, fur=[((160, 330, 250, 400), (0.3, 1.0), 1.3), ((150, 260, 240, 320), (0.9, -0.2), 0.9),
                         ((300, 360, 420, 400), (-0.1, 1.0), 0.8)])
head = mk("head", [ell_poly(*CRAN), tube([(118, 346), (86, 364), J["nose"] + (4, 0)], [34, 24, 15]),
                   tube([(126, 362), (90, 378), (66, 390)], [14, 10, 7])], 6, z=6, lw=1.9,
          fur=[((120, 355, 160, 385), (0.8, 0.6), 0.9), ((138, 318, 175, 356), (0.9, 0.2), 1.1)])
near_fore = mk("near_fore", limb([J["elbow"] + (1, -14), J["elbow"], J["wrist"], J["fpaw"]], [26, 25, 15, 13],
                                 knuckles=[(2, 8.5)]) + paw(J["fpaw"], (-1, 0.25), 15),
               4, z=2.5, fur=[((222, 380, 245, 430), (0.4, 1.0), 0.6)])
far_fore = mk("far_fore", limb([J["f_shoulder"], J["f_elbow"], J["f_wrist"], J["f_paw"]], [24, 22, 13, 12],
                               knuckles=[(2, 7.5)]) + paw(J["f_paw"], (-1, 0.25), 13), 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", [ell_poly(A(440, 334), 34, 46, 20)] +
               limb([J["hip"], J["stifle"], J["hock"], J["hpaw"]], [40, 26, 15, 13], knuckles=[(2, 8.5)]) +
               paw(J["hpaw"], (-1, 0.25), 14), 5, z=4, tone=-0.12, fur=[((440, 300, 480, 380), (0.4, 1.0), 0.8)])
far_hind = mk("far_hind", limb([J["f_hip"], J["f_stifle"], J["f_hock"], J["f_hpaw"]], [40, 22, 13, 11],
                               knuckles=[(2, 7)]) + paw(J["f_hpaw"], (-1, 0.25), 12), 4, z=1, tone=0.3, lw=1.3)
tail = mk("tail", [tube([(472, 284), (494, 306), (510, 344), (512, 380), (500, 408)], [12, 22, 28, 22, 6])], 4,
          z=4.5, fur=[((470, 280, 530, 420), (0.15, 1.0), 1.1)])
ear_far = Part("ear_far", [(110, 330), (114, 298), (126, 324)], z=5.5, n=6, tone=0.25)
ear_near = Part("ear_near", [(130, 326), (150, 292), (152, 334)], z=7, n=6)
parts = [ground_shadow(160, 520, 492), far_fore, far_hind, trunk, near_fore, near_hind, tail, head, ear_far,
         ear_near]

with L.figure(pen, (290, 385)):
    # 3. construction, faint and hand-drawn
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(130, GROUND + 2), (560, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (RIB, PEL, CRAN):
            hand_ellipse(pen, c, rx, ry, rot)
        pen.line([(104, 330), (148, 318), (156, 356), (112, 368), (104, 330)], w=0.4, wobble=0.6)   # head box
        pen.line([(112, 336), J["nose"] + (0, -6), J["nose"] + (4, 8), (112, 368)], w=0.4, wobble=0.6)
        for ch in (["shoulder", "elbow", "wrist", "fpaw"], ["f_shoulder", "f_elbow", "f_wrist", "f_paw"],
                   ["hip", "stifle", "hock", "hpaw"], ["f_hip", "f_stifle", "f_hock", "f_hpaw"]):
            bones(pen, [J[k] for k in ch])
        pen.line([WITHERS + (6, 0), J["shoulder"]], w=0.5, wobble=0.4, overshoot=6)
        pen.line([(420, 284), J["hip"], (472, 322)], w=0.5, wobble=0.4, overshoot=6)

    # 4. ink
    ink_figure(pen, parts, SEED, form_parts=("tail", "head"), part_t={"trunk": 0.68})
    for k, d, s in (("fpaw", (-1, 0.25), 15), ("hpaw", (-1, 0.25), 14)):
        paw_details(pen, J[k], d, s)

    # 5. details
    eye = [(104, 338), (112, 333), (121, 336), (113, 341)]
    pen.line(eye + [eye[0]], w=1.0, wobble=0.2)
    pen.fill(catmull([(110, 336), (114, 336), (113, 339), (110, 339)], True, 5))
    pen.line([(102, 341), (94, 354)], w=0.5)
    pen.fill(catmull([(53, 378), (62, 375), (66, 384), (59, 390), (52, 386)], True, 6))
    pen.line([(64, 392), (90, 386), (118, 376)], w=1.0)
    pen.line([(98, 330), (110, 325), (124, 328)], w=0.8)
    pen.line([(140, 322), (147, 304)], w=0.6)
    for i in range(4):
        x = 268 + i * 16
        pen.line([(x, 300), (x + 6, 330), (x + 3, 360)], w=0.45, wobble=0.6)
    tufts(pen, [A(176 + 46 * t, 318 + 52 * t * t + 10 * t) for t in np.linspace(0, 1, 14)], (0.5, 0.86))


# 6. page: studies at native coords; text comes from notes/wolf.json
def s_eye(pen):
    ec = np.array([508, 70])
    up = [(468, 76), (486, 60), (510, 55), (534, 60), (552, 54)]
    lo = [(468, 76), (488, 84), (512, 85), (536, 74), (552, 54)]
    pen.line(up, w=1.6, passes=3, spread=0.8)
    pen.line(lo, w=1.9, passes=2, spread=0.6)
    pen.line([(468, 76), (462, 92), (458, 112)], w=0.8, passes=2)  # tear streak
    pen.fill(catmull([(504, 66), (511, 65), (512, 72), (505, 73)], True, 5))  # small round pupil
    pen.ellipse((509, 69), 21, 18, w=0.6, turns=1.0, wobble=0.3)
    pen.ellipse((505, 64), 2.2, 2.0, w=0.5, turns=1.0, wobble=0.05)
    for i in range(30):
        t = i / 29
        base = np.array(up[0]) * (1 - t) + np.array(up[-1]) * t + [0, -12 - 6 * np.sin(t * np.pi)]
        f = np.array([0.9, -0.15]) + pen.rng.normal(0, 0.1, 2)
        pen.stroke(np.array([base, base + f * pen.rng.uniform(6, 12)]), 0.55, taper=(0.1, 0.7), wobble=0.2)
    for i in range(18):
        t = i / 17
        base = np.array([476, 92]) * (1 - t) + np.array([548, 80]) * t + [0, pen.rng.uniform(0, 6)]
        f = np.array([0.8, 0.5]) + pen.rng.normal(0, 0.1, 2)
        pen.stroke(np.array([base, base + f * pen.rng.uniform(5, 10)]), 0.5, taper=(0.1, 0.7), wobble=0.2)


def s_paw(pen):
    pen.line([(512, 418), (510, 446), (508, 470), (512, 482)], w=1.0, passes=2)          # back of pastern
    pen.line([(530, 418), (532, 446), (538, 458)], w=1.0, passes=2)                      # front of pastern
    pen.line([(538, 458), (546, 456), (552, 462), (558, 464), (564, 472), (566, 480)], w=1.2, passes=2)  # knuckles
    pen.line([(512, 482), (526, 486), (540, 485), (552, 486), (564, 484)], w=1.4, passes=2)  # pads
    for (x, y) in [(552, 486), (564, 484)]:
        pen.line([(x, y - 2), (x + 6, y + 3), (x + 4, y + 5)], w=1.0)                    # claws
    pen.line([(546, 456), (544, 470)], w=0.5); pen.line([(558, 464), (556, 476)], w=0.5)  # toe splits
    pen.line([(510, 452), (502, 458), (506, 466)], w=0.7)                                # dewclaw
    for k in range(9):                                                                    # torn-off top: fur
        x = 510 + k * 2.6
        pen.stroke(np.array([(x, 420), (x + 2, 410 + pen.rng.uniform(-3, 3))]), 0.5, taper=(0.1, 0.6))
    for k in range(7):
        y = 428 + k * 6
        pen.stroke(np.array([(514, y), (524, y + 5)]), 0.45, taper=(0.1, 0.4))
    for (dx, dy, r) in [(-9, -12, 3.1), (-3, -17, 3.3), (4, -17, 3.3), (10, -12, 3.1)]:
        pen.ellipse((498 + dx * 1.3, 528 + dy * 1.3), r * 0.85, r * 1.15, w=0.7, turns=1.1, wobble=0.25)
    pen.line([(491, 532), (494, 524), (500, 522), (506, 524), (509, 532), (500, 536), (491, 532)], w=0.8)


def first_try(pen):
    fa_body = [(40, 70), (70, 64), (110, 66), (132, 74), (130, 92), (100, 96), (60, 96), (42, 90)]
    pen.line(fa_body + [fa_body[0]], w=0.8, wobble=0.6, passes=2)
    pen.line([(44, 72), (36, 52), (30, 40), (20, 42), (12, 50), (22, 56), (30, 60)], w=0.8, passes=2)  # head up
    pen.line([(30, 40), (32, 30), (36, 41)], w=0.7)
    for x in (50, 62, 112, 124):
        pen.line([(x, 94), (x + 1, 116), (x + 4, 120)], w=0.7, passes=2)
    pen.line([(132, 76), (148, 88), (152, 104)], w=0.7)


L.page(pen, {"eye": (s_eye, (455, 40, 562, 116)), "paw": (s_paw, (486, 404, 570, 540))},
       crossed_draw=(first_try, (8, 26, 156, 124)))
save(pen, os.environ.get("OUT", "wolf"), PW, PH)
