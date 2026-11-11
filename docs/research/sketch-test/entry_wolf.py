"""Journal entry `wolf`: a lean wolf, walking, head low. Run: bash render.sh entry_wolf -> entry_wolf_ink.png

Measured off a photo of a lean grey wolf walking, side on (Commons, "Timber wolf walking in grass - DPLA"), with
withers height H: body length ~1.1 H, chest depth ~0.43 H (wolf3's heavier wolf had 0.55 H), tuck at the loin
~0.33 H, leg below the chest ~0.56 H, head length ~0.4 H. In a walk the near fore reaches forward with the pastern
sloped, the far fore is planted under the withers; the near hind is back with the hock behind the hip, the far
hind forward under the loin. Elbow behind the brisket; stifle forward of the hip, hock well behind it.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 11))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_wolf", text_scale=1.3)
A = lambda *p: np.array(p, float)
HD = A(4, 12)                       # the head carried low: every head coordinate is wolf3's moved by this
h = lambda x, y: A(x, y) + HD

GROUND, WITHERS = 504, A(232, 276)
J = {k: A(*v) for k, v in dict(
    shoulder=(210, 330), elbow=(224, 370), wrist=(204, 450), fpaw=(184, 494),
    f_shoulder=(228, 330), f_elbow=(250, 372), f_wrist=(262, 450), f_paw=(266, 494),
    hip=(418, 298), stifle=(392, 372), hock=(450, 436), hpaw=(442, 498),
    f_hip=(422, 296), f_stifle=(388, 366), f_hock=(414, 432), f_hpaw=(394, 494)).items()}
OCC, NOSE = h(150, 330), h(64, 382)
RIB, PEL, CRAN = (A(264, 322), 62, 50, -6), (A(414, 296), 34, 30, 8), (h(130, 342), 25, 22, -20)
GESTURE = [NOSE + (8, -14), OCC, WITHERS + (6, -2), (330, 282), (418, 274), (452, 300), (462, 360), (456, 418)]

trunk = mk("trunk", [ell_poly(*RIB), ell_poly(*PEL),
                     tube([WITHERS + (32, 30), (194, 314), OCC + (8, 8)], [64, 54, 40]),            # neck
                     tube([WITHERS + (4, 26), J["shoulder"], J["elbow"] + (2, -10)], [42, 34, 24]),  # shoulder
                     tube([(300, 310), (346, 298), (404, 290)], [76, 52, 56])],                     # lean loin
           18, z=3, fur=[((160, 320, 250, 392), (0.3, 1.0), 1.2), ((150, 262, 240, 318), (0.9, -0.2), 0.9)])
head = mk("head", [ell_poly(*CRAN), tube([h(118, 346), h(92, 362), NOSE + (4, 0)], [32, 24, 16]),
                   tube([h(124, 362), h(96, 378), h(74, 388)], [14, 10, 7])], 6, z=6, lw=1.9,
          fur=[((h(120, 355)[0], h(120, 355)[1], h(160, 385)[0], h(160, 385)[1]), (0.8, 0.6), 0.9)])
near_fore = mk("near_fore", limb([J["elbow"] + (1, -14), J["elbow"], J["wrist"], J["fpaw"]], [24, 18, 11, 10],
                                 knuckles=[(2, 8)]) + paw(J["fpaw"], (-1, 0.3), 14),
               4, z=2.5, fur=[((222, 370, 240, 410), (0.4, 1.0), 0.5)])
far_fore = mk("far_fore", limb([J["f_shoulder"], J["f_elbow"], J["f_wrist"], J["f_paw"]], [22, 17, 10, 9],
                               knuckles=[(2, 7)]) + paw(J["f_paw"], (-1, 0.25), 12), 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", [ell_poly(A(404, 332), 22, 38, 24)] +
               limb([J["hip"], J["stifle"], J["hock"], J["hpaw"]], [34, 22, 13, 12], knuckles=[(2, 7.5)]) +
               paw(J["hpaw"], (-1, 0.25), 13), 5, z=2.8, tone=-0.12, fur=[((410, 300, 446, 370), (0.4, 1.0), 0.6)])
far_hind = mk("far_hind", limb([J["f_hip"], J["f_stifle"], J["f_hock"], J["f_hpaw"]], [32, 20, 12, 10],
                               knuckles=[(2, 6.5)]) + paw(J["f_hpaw"], (-1, 0.25), 11), 4, z=1, tone=0.3, lw=1.3)
tail = mk("tail", [tube([(444, 284), (462, 306), (472, 342), (472, 384), (464, 420)], [10, 18, 21, 16, 5])], 4,
          z=4.5, fur=[((440, 280, 500, 430), (0.15, 1.0), 1.1)])
ear_far = Part("ear_far", [h(112, 330), h(116, 304), h(126, 324)], z=5.5, n=6, tone=0.25)
ear_near = Part("ear_near", [h(132, 326), h(146, 300), h(150, 332)], z=7, n=6)
parts = [ground_shadow(150, 480, 496), far_fore, far_hind, trunk, near_fore, near_hind, tail, head, ear_far,
         ear_near]

with L.figure(pen, (290, 385)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(130, GROUND + 2), (560, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (RIB, PEL, CRAN):
            hand_ellipse(pen, c, rx, ry, rot)
        for ch in (["shoulder", "elbow", "wrist", "fpaw"], ["f_shoulder", "f_elbow", "f_wrist", "f_paw"],
                   ["hip", "stifle", "hock", "hpaw"], ["f_hip", "f_stifle", "f_hock", "f_hpaw"]):
            bones(pen, [J[k] for k in ch])
        pen.line([WITHERS + (6, 0), J["shoulder"]], w=0.5, wobble=0.4, overshoot=6)
        pen.line([(390, 282), J["hip"], (444, 320)], w=0.5, wobble=0.4, overshoot=6)

    ink_figure(pen, parts, SEED, form_parts=("tail", "head"), part_t={"trunk": 0.7})
    for k, d, s in (("fpaw", (-1, 0.3), 14), ("hpaw", (-1, 0.25), 13)):
        paw_details(pen, J[k], d, s)

    # head details, wolf3's moved with the head
    eye = [h(104, 338), h(112, 333), h(121, 336), h(113, 341)]
    pen.line(eye + [eye[0]], w=1.0, wobble=0.2)
    pen.fill(catmull([h(110, 336), h(114, 336), h(113, 339), h(110, 339)], True, 5))
    pen.line([h(102, 341), h(94, 354)], w=0.5)
    pen.fill(catmull([NOSE + (-5, -6), NOSE + (4, -9), NOSE + (8, 0), NOSE + (1, 6), NOSE + (-6, 2)], True, 6))
    pen.line([NOSE + (6, 8), h(94, 386), h(118, 376)], w=1.0)
    pen.line([h(98, 330), h(110, 325), h(124, 328)], w=0.8)
    # ribs over the chest egg, the last ones fading into the flank; the hip point and spine under the skin
    c, rx, ry, _ = RIB
    for i in range(6):
        x = c[0] - 14 + i * 13
        top, bot = c[1] - ry * 0.55, c[1] + ry * (0.75 - 0.05 * i)
        pen.line([(x, top), (x + 7, (top + bot) / 2), (x + 3, bot)], w=0.75 - 0.06 * i, wobble=0.5)
    pen.line([(394, 282), (402, 276), (412, 280)], w=0.8, wobble=0.3)
    for x in (300, 322, 344, 366):
        pen.stroke(np.array([(x, 276), (x + 8, 274)]), 0.6, taper=(0.2, 0.5))
    tufts(pen, [A(180 + 44 * t, 316 + 50 * t * t + 8 * t) for t in np.linspace(0, 1, 12)], (0.5, 0.86))


def s_paw(pen):
    pen.line([(512, 418), (510, 446), (508, 470), (512, 482)], w=1.0, passes=2)
    pen.line([(530, 418), (532, 446), (538, 458)], w=1.0, passes=2)
    pen.line([(538, 458), (546, 456), (552, 462), (558, 464), (564, 472), (566, 480)], w=1.2, passes=2)
    pen.line([(512, 482), (526, 486), (540, 485), (552, 486), (564, 484)], w=1.4, passes=2)
    for (x, y) in [(552, 486), (564, 484)]:
        pen.line([(x, y - 2), (x + 6, y + 3), (x + 4, y + 5)], w=1.0)
    pen.line([(546, 456), (544, 470)], w=0.5); pen.line([(558, 464), (556, 476)], w=0.5)
    pen.line([(510, 452), (502, 458), (506, 466)], w=0.7)
    for k in range(9):
        x = 510 + k * 2.6
        pen.stroke(np.array([(x, 420), (x + 2, 410 + pen.rng.uniform(-3, 3))]), 0.5, taper=(0.1, 0.6))
    for (dx, dy, r) in [(-9, -12, 3.1), (-3, -17, 3.3), (4, -17, 3.3), (10, -12, 3.1)]:
        pen.ellipse((498 + dx * 1.3, 528 + dy * 1.3), r * 0.85, r * 1.15, w=0.7, turns=1.1, wobble=0.25)
    pen.line([(491, 532), (494, 524), (500, 522), (506, 524), (509, 532), (500, 536), (491, 532)], w=0.8)


def s_track(pen):
    """A walking line of prints, longer than wide: two middle toes forward of the outer two, a claw mark ahead
    of each toe, the heel pad lobed behind; drawn quickly, not as stamps."""
    for i in range(4):
        c = A(30 + i * 50, 112 - i * 24) + (0, 8 if i % 2 else -8)
        for dx, dy, r in ((-6.5, -7, 2.4), (-2.2, -13, 2.6), (2.6, -13, 2.6), (7, -7, 2.4)):
            q = c + (dx, dy)
            pen.line([q + (0, -r * 1.4), q + (r, 0), q + (0, r * 1.2), q + (-r, 0), q + (0, -r * 1.4)], w=0.7,
                     wobble=0.35)
            pen.stroke(np.array([q + (dx * 0.12, -r * 2.0), q + (dx * 0.2, -r * 2.9)]), 0.8, taper=(0.2, 0.6))
        pen.line([c + (-6, 2), c + (-3, -2), c + (0, -1), c + (3, -2), c + (6, 2), c + (4, 7), c + (0, 6),
                  c + (-4, 7), c + (-6, 2)], w=0.8, wobble=0.35)
    pen.line([(12, 134), (70, 104), (130, 70), (196, 26)], w=0.4, wobble=0.6, overshoot=8)


def first_try(pen):
    fa_body = [(40, 70), (70, 64), (110, 66), (132, 74), (130, 92), (100, 96), (60, 96), (42, 90)]
    pen.line(fa_body + [fa_body[0]], w=0.8, wobble=0.6, passes=2)
    pen.line([(44, 72), (36, 52), (30, 40), (20, 42), (12, 50), (22, 56), (30, 60)], w=0.8, passes=2)
    pen.line([(30, 40), (32, 30), (36, 41)], w=0.7)
    for x in (50, 62, 112, 124):
        pen.line([(x, 94), (x + 1, 116), (x + 4, 120)], w=0.7, passes=2)
    pen.line([(132, 76), (148, 88), (152, 104)], w=0.7)


L.page(pen, {"paw": (s_paw, (486, 404, 570, 540)), "track": (s_track, (10, 14, 200, 136))},
       crossed_draw=(first_try, (8, 26, 156, 124)))
save(pen, os.environ.get("OUT", "entry_wolf"))
