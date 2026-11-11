"""Journal entry `ashrat`: a large, fat grey rat with big digging fore claws, among roots, facing left.
Run: bash render.sh entry_ashrat -> entry_ashrat_ink.png

Invented, so measured off real analogues per part, as fractions of the head-and-body length HB (nose to tail
root, here 360):
- body, off a brown rat side on (Commons, "Rattus norvegicus (white background)"): head ~0.3 HB, back arched and
  highest over the loin, rump the heaviest mass, depth at the hip ~0.36 HB (fattened here to ~0.42), tail about HB,
  thick at the root and ringed; the hind foot long and flat (~0.2 HB); eye about halfway from nose to ear; small
  round ears close behind the eye; the nose rounded, overhanging the lower jaw.
- fore limbs, off a badger's paw (Commons, "Deceased Meles meles - side of paw"): a thick forearm, toes bunched
  into a pad, claws about as long as the toes, curved down like hooks and flattened side to side. Here the claws
  are ~0.08 HB, longer than a rat's would be, and the shoulder carries a digger's hump.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 41))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_ashrat", text_scale=1.3)
A = lambda *p: np.array(p, float)

GROUND = 470
CHEST, HAUNCH = (A(250, 384), 72, 50, -6), (A(392, 372), 80, 62, -4)
SKULL = (A(178, 386), 38, 28, 22)
NOSE = A(108, 420)
GESTURE = [NOSE + (4, -10), (170, 356), (240, 334), (330, 306), (420, 310), (466, 360), (540, 420), (520, 486)]
J = {k: A(*v) for k, v in dict(
    sh=(240, 384), el=(238, 432), wr=(222, 456), hand=(204, 462),
    f_sh=(262, 386), f_el=(266, 426), f_wr=(256, 454), f_hand=(242, 464),
    hip=(404, 384), kn=(366, 420), heel=(404, 452), toe=(346, 468),
    f_hip=(424, 378), f_kn=(392, 414), f_heel=(430, 448), f_toe=(380, 464)).items()}

body = mk("body", [ell_poly(*CHEST), ell_poly(*HAUNCH),
                   tube([(260, 372), (320, 362), (384, 356)], [84, 96, 104]),               # back and belly
                   tube([(296, 408), (366, 418)], [44, 40]),                                  # the belly sags
                   tube([(236, 362), (208, 372), SKULL[0]], [72, 64, 52]),                    # neck into skull
                   tube([(226, 386), (236, 420), (238, 436)], [42, 34, 28]),                  # upper arm, merged
                   ell_poly(*SKULL), tube([SKULL[0], (138, 408), NOSE], [48, 32, 21]),         # skull -> muzzle
                   tube([(170, 410), (140, 422), (122, 426)], [18, 12, 8])],                  # lower jaw
          16, z=3, tone=0.2, lw=1.9,
          fur=[((200, 296, 470, 340), (0.5, -0.9), 0.7), ((280, 420, 420, 450), (0.1, 1.0), 0.7),
               ((196, 350, 250, 420), (0.4, 0.9), 0.7)])
near_fore = mk("near_fore", limb([J["sh"], J["el"], J["wr"], J["hand"]], [46, 38, 26, 20], knuckles=[(2, 12)]) +
               [ell_poly(J["hand"] + (-4, 0), 13, 9, 10)], 5, z=2.8, tone=0.05,
               fur=[((206, 410, 262, 456), (-0.3, 1.0), 0.9)])
far_fore = mk("far_fore", limb([J["f_sh"], J["f_el"], J["f_wr"], J["f_hand"]], [40, 30, 20, 17], knuckles=[(2, 10)]) +
              [ell_poly(J["f_hand"] + (-5, 2), 13, 8, 20)], 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", limb([J["hip"], J["kn"], J["heel"], J["toe"]], [60, 34, 16, 10], knuckles=[(2, 7)]),
               5, z=2.8, tone=0.0)
far_hind = mk("far_hind", limb([J["f_hip"], J["f_kn"], J["f_heel"], J["f_toe"]], [54, 30, 14, 9]), 4, z=1, tone=0.3,
              lw=1.3)
TAIL = [(464, 380), (500, 404), (530, 430), (540, 458), (520, 480), (470, 488), (420, 486)]
tail = mk("tail", [tube(TAIL, [26, 20, 15, 11, 8, 5, 3])], 3, z=2, tone=0.15)
ROOTS = [([(20, 492), (70, 478), (120, 470), (170, 470), (214, 478)], 14),     # rising under the fore hand
         ([(236, 494), (280, 484), (330, 486), (380, 480)], 10),                 # under the belly
         ([(470, 496), (520, 490), (560, 470), (590, 452)], 12)]                 # behind the tail's end
"""Root centre lines and thickness, all clear of the figure (ink is not occluded by the figure's parts)."""
parts = [ground_shadow(170, 450, 466, 9), far_fore, far_hind, tail, near_hind, body, near_fore]

with L.figure(pen, (320, 380)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(60, GROUND + 2), (560, GROUND - 3)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (CHEST, HAUNCH, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        pen.line([(150, 352), NOSE + (-2, -6), NOSE + (6, 10), (164, 398)], w=0.4, wobble=0.6, overshoot=6)
        for ch in (["sh", "el", "wr", "hand"], ["f_sh", "f_el", "f_wr", "f_hand"], ["hip", "kn", "heel", "toe"],
                   ["f_hip", "f_kn", "f_heel", "f_toe"]):
            bones(pen, [J[k] for k in ch])
    # roots the creature stands among: drawn first so the figure's contours cross them
    for r, th in ROOTS:
        c = resample(np.asarray(r, float), 3.0)
        nr = normals(c)
        taper = np.linspace(1.0, 0.55, len(c))[:, None]
        for side in (-1, 1):
            pen.line(c + nr * side * th / 2 * taper, w=1.2 if side < 0 else 0.9, passes=2, spread=0.6, wobble=0.7)
        for i in range(2, len(c) - 2, 3):                 # bark: short strokes across, heavier on the shadow side
            q = c[i] + nr[i] * pen.rng.uniform(-0.1, 0.4) * th
            pen.stroke(np.array([q, q + nr[i] * th * 0.35 + pen.rng.normal(0, 1, 2)]), 0.5, taper=(0.2, 0.5))
    ink_figure(pen, parts, SEED, hatch_t=0.55, form_parts=("body",),
               part_t={"body": 0.48, "near_fore": 0.4, "tail": 0.9}, cross={"body": (0.95, 55)})

    # the claws: long, curved down like hooks, flattened; four on each fore hand
    for hand, sc, w, reach, bow in ((J["hand"] + (-4, 0), 1.15, 1.7, (-24, 30), (-12, -4)),     # hooked over the root
                                    (J["f_hand"] + (-5, 2), 0.85, 1.1, (-36, 12), (-3, -9))):  # flat on the ground
        for k in range(4):
            base = hand + (-12 * sc + k * 3 * sc, -5 * sc + k * 3.4 * sc)
            tip = base + (np.array(reach) + (k * 2, k * 1.5)) * sc
            mid = (base + tip) / 2 + np.array(bow) * sc
            pen.line([base, mid, tip], w=w * 1.3, passes=2, spread=0.4)
            pen.line([base + (0, 4 * sc), mid + (1, -3 * sc), tip], w=w * 0.6)
    # hind toes, short, clawed
    for toe, sc in ((J["toe"], 1.0), (J["f_toe"], 0.85)):
        for k in range(3):
            q = toe + (-4 + k * 2, -2 + k * 2.4)
            pen.stroke(np.array([q, q + np.array([-9, 3]) * sc]), 0.9, taper=(0.2, 0.8))
    # head: eye halfway nose to ear, round ear close behind it, nose pad, incisors, whiskers
    pen.fill(catmull([(152, 388), (158, 387), (159, 392), (153, 393)], True, 5))
    pen.ellipse((155, 390), 6.5, 5.5, rot=-15, w=0.6, turns=1.0, wobble=0.2)
    ear_pts = [(186, 370), (184, 354), (192, 344), (204, 344), (212, 354), (208, 368)]
    pen.line(ear_pts, w=1.4, passes=2, spread=0.4, wobble=0.3)
    pen.line([(190, 366), (192, 354), (200, 350), (206, 358)], w=0.6)
    pen.fill(catmull([NOSE + (-3, -6), NOSE + (4, -7), NOSE + (6, 0), NOSE + (0, 4), NOSE + (-4, 0)], True, 5))
    pen.line([NOSE + (8, 4), (128, 430), (152, 426)], w=0.9)
    pen.line([(120, 426), (119, 432), (123, 432)], w=0.7)
    for k in range(6):
        q = NOSE + (14 + k * 2, -2 + k * 2)
        ang = np.radians(-150 + k * 14)
        pen.stroke(np.array([q, q + np.array([np.cos(ang), np.sin(ang)]) * pen.rng.uniform(26, 40)]), 0.45,
                   taper=(0.2, 0.9), wobble=0.4)
    # tail rings
    for t in np.linspace(0.08, 0.92, 22):
        i = t * (len(TAIL) - 1)
        a, b = int(i), min(int(i) + 1, len(TAIL) - 1)
        q = A(*TAIL[a]) * (1 - (i - a)) + A(*TAIL[b]) * (i - a)
        d = A(*TAIL[b]) - A(*TAIL[a]); d /= np.linalg.norm(d) + 1e-9
        nv = np.array([-d[1], d[0]])
        wd = np.interp(t, np.linspace(0, 1, 7), [26, 20, 15, 11, 8, 5, 3]) / 2
        pen.stroke(np.array([q - nv * wd * 0.9, q + d * 1.5, q + nv * wd * 0.9]), 0.45, taper=(0.2, 0.2))
    # the digger's shoulder hump and the spine down the arched back
    tufts(pen, [A(206 + 250 * t, 338 - 30 * np.sin(t * np.pi) + 12 * t) for t in np.linspace(0, 1, 18)],
          (0.5, -0.8), length=(4, 8), w=0.6)


def s_claw(pen):
    """The fore hand from the side: thick wrist, toes bunched into a pad, hooked claws as long as the toes."""
    pen.line([(60, 10), (56, 40), (50, 62)], w=1.3, passes=2, spread=0.6)
    pen.line([(96, 10), (98, 40), (92, 62)], w=1.3, passes=2, spread=0.6)
    pen.line([(50, 62), (44, 74), (56, 84), (80, 86), (94, 76), (92, 62)], w=1.2, passes=2, spread=0.5)
    for k in range(4):
        base = A(48 + k * 4, 72 + k * 4)
        tip = base + (-46 + k * 4, 30 - k * 2)
        mid = (base + tip) / 2 + (-6, -10)
        pen.line([base, mid, tip], w=1.6, passes=2, spread=0.4)
        pen.line([base + (2, 5), mid + (2, -4), tip], w=0.7)
    for k in range(12):
        x = 58 + k * 3
        pen.stroke(np.array([(x, 12), (x + 1, 4 + pen.rng.uniform(-3, 3))]), 0.5, taper=(0.1, 0.6))
    pen.line([(-6, 108), (40, 112), (110, 106)], w=0.5, wobble=0.6)


def s_gouges(pen):
    """A root as it was found: bark torn in parallel grooves, four to a stroke."""
    pen.line([(0, 40), (60, 34), (130, 36), (200, 30)], w=1.4, passes=2, spread=0.7)
    pen.line([(0, 82), (70, 78), (140, 82), (200, 74)], w=1.4, passes=2, spread=0.7)
    pen.line([(200, 30), (206, 52), (200, 74)], w=0.9, passes=2)
    hand_ellipse(pen, (202, 52), 7, 20, 0, w=0.6, passes=1)
    for g in range(3):
        x0 = 30 + g * 52
        for k in range(4):
            x = x0 + k * 6
            pen.line([(x, 42), (x + 10, 58), (x + 18, 76)], w=0.9, wobble=0.4)
    for k in range(10):
        q = A(10 + k * 18, 46 + pen.rng.uniform(0, 26))
        pen.stroke(np.array([q, q + (12, 1)]), 0.4, taper=(0.2, 0.5))


def first_try(pen):
    hand_ellipse(pen, (70, 76), 40, 26, 0, w=0.9, passes=2)
    hand_ellipse(pen, (24, 66), 16, 14, 0, w=0.9, passes=1)
    hand_ellipse(pen, (30, 46), 10, 11, 0, w=0.8, passes=1)
    pen.line([(10, 70), (2, 72)], w=0.8)
    pen.line([(110, 80), (140, 70), (150, 50)], w=0.8)
    for x in (50, 92):
        pen.line([(x, 100), (x, 112)], w=0.7)


L.page(pen, {"claw": (s_claw, (-6, 0, 112, 120)), "gouges": (s_gouges, (0, 26, 210, 86))},
       crossed_draw=(first_try, (0, 30, 154, 116)))
save(pen, os.environ.get("OUT", "entry_ashrat"))
