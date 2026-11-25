"""Journal entry `greycoat`, drawn to its brief in content/team/week-three.md. Run:
bash render.sh entry_greycoat -> entry_greycoat_ink.png

Body measured off a side-on photo of a grey wolf sitting (Commons, "Howlsnow.jpg" by Retron, released to the public
domain), with withers height H taken to the ground: back from tail root to withers ~1.1 H at ~53 degrees, the
haunch a round mass ~0.45 H across whose top is ~0.48 H up, forechest ~0.25 H ahead of the forelegs, foreleg from
elbow to ground ~0.43 H and plumb, tail root to fore toes ~1.13 H, the hind foot flat on the ground under the haunch
with the hock touching behind. The reference howls, so the head is entry_wolf's (from wolf3) turned level on an
upright neck, occiput ~0.38 H over the withers. Fore toes ~1.5x a wolf's, per the brief. Drawn in the reference's (mirrored)
coordinates and mapped by t() onto the page; the head by g() from wolf3's.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 7))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 19)), "entry_greycoat", text_scale=1.3)
A = lambda *p: np.array(p, float)
K = 0.47
t = lambda x, y: A(560 - K * x, K * y + 90.4)          # photo (facing right) -> page (facing left)
GROUND = 504
TURN = np.radians(12)
ROT = np.array([[np.cos(TURN), -np.sin(TURN)], [np.sin(TURN), np.cos(TURN)]])
OCC, HS = A(216, 200), 1.15
g = lambda x, y: ROT @ (A(x, y) - (150, 330)) * HS + OCC    # wolf3's head, turned level, set on the neck

WITHERS, ROOT = t(610, 410), t(300, 828)
NOSE = g(68, 380)
J = {k: t(*v) for k, v in dict(
    elbow=(735, 690), wrist=(772, 820), fpaw=(778, 846),
    f_elbow=(700, 690), f_wrist=(720, 822), f_paw=(724, 848),
    hock=(345, 862), hpaw=(560, 884)).items()}
RIB = (A(258, 344), 80, 40, 53)
PEL = (A(398, 446), 42, 36, 30)
THIGH = (t(446, 738), 56, 42, -26)
CRAN = (g(130, 342), 25 * HS, 22 * HS, -20 + 12)
GESTURE = [NOSE + (6, -10), OCC, WITHERS + (4, -4), (330, 360), (400, 440), ROOT, (480, 496), (548, 500)]


def _toe(a, d, size, k):
    """Base, raised knuckle and claw end of toe k (-1 far, 0 middle, 1 near), each ~1.5x a wolf's in length."""
    b = a + d * size * 0.3 + (0, k * size * 0.15)
    reach = (1.3, 1.5, 1.4)[k + 1]
    return b, b + d * size * reach * 0.5 + (0, -size * 0.2), b + d * size * reach + (0, size * 0.3)


def long_paw(pastern_end, toe_dir, size):
    """A forefoot whose toes run out long and knuckled, off a small pad mass."""
    d = np.asarray(toe_dir, float); d /= np.linalg.norm(d)
    a = np.asarray(pastern_end, float)
    polys = [ell_poly(a + d * size * 0.2 + (0, size * 0.1), size * 0.5, size * 0.42)]
    for k in (-1, 0, 1):
        polys.append(tube(_toe(a, d, size, k), [size * 0.34, size * 0.26, size * 0.14]))
    return polys


def long_toes(pen, pastern_end, toe_dir, size, w=0.8):
    """Each toe's knuckle line, and the claw hooked down off its end."""
    d = np.asarray(toe_dir, float); d /= np.linalg.norm(d)
    a = np.asarray(pastern_end, float)
    for k in (-1, 0, 1):
        b, kn, tip = _toe(a, d, size, k)
        pen.line([b + (0, -size * 0.12), kn + (0, -size * 0.12), tip + (0, -size * 0.06)], w=w * 0.8, wobble=0.2)
        pen.stroke(np.array([tip, tip + d * size * 0.28 + (0, size * 0.14)]), w * 1.3, taper=(0.1, 0.8), wobble=0.1)


trunk = mk("trunk", [ell_poly(*RIB), ell_poly(*PEL),
                     tube([(294, 350), (348, 406), ROOT + (-6, -12)], [78, 84, 50]),                      # flank, haunch to ribs
                     tube([WITHERS + (0, 24), (234, 252), OCC + (8, 30)], [64, 54, 42]),                     # upright neck, maned
                     tube([WITHERS + (-4, 44), (206, 356), J["elbow"] + (2, -8)], [50, 46, 32]),             # shoulder to elbow
                     tube([(184, 296), (174, 336), (188, 380)], [34, 38, 26]),                               # forechest
                     tube([g(130, 374), (198, 266), (184, 300)], [26, 40, 36]),                              # throat into the chest
                     tube([OCC + (14, 34), WITHERS + (-6, 10), (296, 318), (342, 380), ROOT + (-10, -16)], [30, 44, 46, 40, 30]),  # spine ridge
                     tube([OCC + (-6, 20), OCC + (-14, 34)], [28, 30])],                                     # nape under the skull
           16, z=3, lw=1.9,
           fur=[((150, 220, 250, 330), (0.25, 1.0), 1.4),                     # the ruff down the throat
                ((236, 230, 330, 340), (0.7, 0.7), 1.0),                       # mane over the withers
                ((290, 330, 430, 470), (0.6, 0.8), 0.8)])                      # rough back
head = mk("head", [ell_poly(*CRAN), tube([g(118, 346), g(92, 362), NOSE + (4, 0)], [37, 28, 18]),
                   tube([g(124, 362), g(98, 376), g(80, 384)], [16, 12, 8])], 6, z=6, lw=1.9,
          fur=[((g(122, 352)[0], g(122, 352)[1], g(162, 384)[0], g(162, 384)[1]), (0.6, 0.8), 1.0)])
near_fore = mk("near_fore", limb([J["elbow"] + (0, -16), J["elbow"], J["wrist"], J["fpaw"]], [34, 26, 16, 14],
                                 knuckles=[(2, 8)]) + long_paw(J["fpaw"], (-1, 0.12), 25),
               4, z=2.5, fur=[((200, 400, 230, 440), (-0.3, 1.0), 0.6)])
far_fore = mk("far_fore", limb([J["f_elbow"] + (0, -16), J["f_elbow"], J["f_wrist"], J["f_paw"]], [30, 22, 13, 12],
                               knuckles=[(2, 7)]) + long_paw(J["f_paw"], (-1, 0.15), 19), 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", [ell_poly(*THIGH)] +
               limb([THIGH[0] + (20, 30), J["hock"], J["hpaw"] + (14, -6)], [40, 16, 12]) +
               paw(J["hpaw"] + (12, -6), (-1, 0.2), 13), 6, z=3.5, tone=-0.1,
               fur=[((310, 400, 400, 470), (0.5, 1.0), 0.6)])
tail = mk("tail", [tube([ROOT + (-4, -6), ROOT + (24, 2), ROOT + (60, 10), ROOT + (98, 18), ROOT + (126, 12)],
                        [20, 26, 26, 20, 8])], 4, z=2.8, fur=[((410, 470, 560, 510), (1.0, 0.1), 1.5)])
ear_far = Part("ear_far", [g(112, 330), g(116, 304), g(126, 324)], z=5.5, n=6, tone=0.25)
ear_near = Part("ear_near", [g(132, 326), g(146, 300), g(150, 332)], z=7, n=6)
parts = [ground_shadow(150, 470, 498, 9), far_fore, trunk, tail, near_fore, near_hind, head, ear_far, ear_near]

with L.figure(pen, (320, 340)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(120, GROUND + 2), (570, GROUND - 3)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (RIB, PEL, THIGH, CRAN):
            hand_ellipse(pen, c, rx, ry, rot)
        for ch in (["elbow", "wrist", "fpaw"], ["f_elbow", "f_wrist", "f_paw"]):
            bones(pen, [J[k] for k in ch])
        bones(pen, [THIGH[0], J["hock"], J["hpaw"]])
        pen.line([WITHERS, (WITHERS[0], GROUND)], w=0.4, wobble=0.4, overshoot=6)

    ink_figure(pen, parts, SEED, hatch_t=0.55, form_parts=("tail", "head"), part_t={"trunk": 0.5, "near_hind": 0.52})
    long_toes(pen, J["fpaw"], (-1, 0.12), 25)
    pen.line([WITHERS + (-10, 26), (226, 300), (196, 338)], w=0.7, wobble=0.5, overshoot=4)       # shoulder blade
    pen.line([J["elbow"] + (8, -22), J["elbow"] + (12, -6), J["elbow"] + (4, 6)], w=1.0, wobble=0.3)   # elbow
    pen.line([(302, 404), (296, 424), (300, 446)], w=0.8, wobble=0.4)                                  # stifle fold
    long_toes(pen, J["f_paw"], (-1, 0.15), 19, w=0.6)

    eye = [g(104, 338), g(112, 333), g(121, 336), g(113, 341)]
    pen.line(eye + [eye[0]], w=1.0, wobble=0.2)
    pen.fill(catmull([g(110, 336), g(114, 336), g(113, 339), g(110, 339)], True, 5))
    pen.line([g(102, 341), g(94, 354)], w=0.5)
    pen.fill(catmull([NOSE + (-5, -4), NOSE + (3, -8), NOSE + (8, -1), NOSE + (2, 5), NOSE + (-5, 3)], True, 6))
    pen.line([NOSE + (5, 8), g(94, 386), g(118, 376)], w=1.0)
    pen.line([g(98, 330), g(110, 325), g(124, 328)], w=0.8)
    tufts(pen, [A(176 + 30 * u, 236 + 120 * u - 20 * u * u) for u in np.linspace(0, 1, 14)], (-0.4, 0.9),
          length=(6, 12), w=0.6)
    tufts(pen, [A(250 + 120 * u, 270 + 150 * u) for u in np.linspace(0, 1, 12)], (0.8, 0.5), length=(5, 9), w=0.6)


def s_foot(pen):
    """The forefoot side on, three toes laid out long and knuckled with a claw hooked off each, and its print below:
    four long toe pads well out from the heel pad, claw marks ahead."""
    pen.line([(512, 396), (511, 426), (509, 446), (512, 458)], w=1.0, passes=2)
    pen.line([(530, 396), (532, 428), (536, 442)], w=1.0, passes=2)
    for k, (reach, dy) in enumerate(((52, -6), (66, 0), (58, 6))):
        b0 = A(530, 446 + dy)
        kn, tip = b0 + (reach * 0.5, -9), b0 + (reach, 12)
        pen.line([b0, kn, tip], w=1.2 if k == 2 else 0.8, wobble=0.25, passes=2 if k == 2 else 1)
        pen.line([tip, tip + (7, 4), tip + (5, 7)], w=1.0)
    pen.line([(512, 458), (536, 466), (566, 468), (588, 466)], w=1.4, passes=2)
    for k in range(9):
        x = 510 + k * 2.6
        pen.stroke(np.array([(x, 398), (x + 2, 388 + pen.rng.uniform(-3, 3))]), 0.5, taper=(0.1, 0.6))
    c = A(552, 536)
    pen.line([c + (-9, 8), c + (-4, 3), c + (0, 4), c + (4, 3), c + (9, 8), c + (6, 14), c + (0, 13), c + (-6, 14),
              c + (-9, 8)], w=0.8, wobble=0.3)
    for dx, dy in ((-13, -14), (-5, -26), (5, -26), (13, -14)):
        q = c + (dx, dy)
        pen.line([q + (0, -10), q + (2.6, -2), q + (0, 7), q + (-2.6, -2), q + (0, -10)], w=0.7, wobble=0.3)
        pen.stroke(np.array([q + (dx * 0.1, -12), q + (dx * 0.18, -17)]), 0.8, taper=(0.2, 0.6))


def s_sitting(pen):
    """Three sat in a row, from behind: a head and ears over a pear of a body bulged at the haunches, tails laid out
    on the ground."""
    for x, s in ((40, 1.0), (92, 0.9), (138, 1.05)):
        y = 120
        body = [(x - 7 * s, y - 40 * s), (x - 12 * s, y - 24 * s), (x - 18 * s, y - 10 * s), (x - 17 * s, y),
                (x + 17 * s, y), (x + 18 * s, y - 10 * s), (x + 12 * s, y - 24 * s), (x + 7 * s, y - 40 * s)]
        pen.line(body, w=0.9, wobble=0.5, passes=2)
        pen.line([(x, y - 30 * s), (x, y - 4 * s)], w=0.5, wobble=0.4)
        pen.ellipse((x, y - 47 * s), 8 * s, 7 * s, w=0.8, turns=1.05, wobble=0.3)
        for e in (-1, 1):
            pen.line([(x + e * 4 * s, y - 51 * s), (x + e * 7 * s, y - 62 * s), (x + e * 8.5 * s, y - 49 * s)], w=0.8)
        pen.line([(x + 8 * s, y + 1), (x + 20 * s, y + 4), (x + 28 * s, y + 2)], w=1.0, wobble=0.4)
    pen.line([(16, 122), (170, 120)], w=0.4, wobble=0.5)


def first_try(pen):
    body = [(60, 120), (54, 96), (58, 70), (70, 52), (84, 60), (92, 90), (96, 120)]
    pen.line(body, w=0.8, wobble=0.6, passes=2)
    pen.ellipse((70, 42), 14, 11, w=0.8, turns=1.1)
    pen.line([(58, 44), (40, 48), (44, 54), (60, 52)], w=0.8)
    pen.line([(64, 34), (66, 20), (74, 32)], w=0.7)
    for x in (62, 70):
        pen.line([(x, 70), (x - 2, 120)], w=0.7, passes=2)
    pen.line([(96, 120), (130, 122)], w=0.7)


L.page(pen, {"foot": (s_foot, (500, 382, 600, 556)), "sitting": (s_sitting, (12, 50, 176, 128))},
       crossed_draw=(first_try, (30, 16, 136, 126)))
save(pen, os.environ.get("OUT", "entry_greycoat"))
