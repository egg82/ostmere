"""Journal entry `ash_deer`: a stag standing, head up, antlers in a crown. Run:
bash render.sh entry_ash_deer -> entry_ash_deer_ink.png

Measured off Gessner's standing stag (Historia animalium, the Lapland woodcut; engravings/gessner/019.jpg, public
domain), with withers height H taken to the hind hooves: body length (brisket to buttock) ~0.95 H, chest depth
~0.36 H, leg below the belly ~0.62 H, head length ~0.37 H on a long upright neck, antlers ~0.5 H over the poll,
tail a short tuft. Stance: the near fore planted forward, the far fore back; the hock of the near hind well
behind the hip and the stifle forward of it, the far hind under the belly. Drawn in the reference's coordinates
and mapped by t() onto the page.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 23))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 5)), "entry_ash_deer", text_scale=1.3)
A = lambda *p: np.array(p, float)
S = 0.85
t = lambda x, y: A((x - 50) * S + 120, (y - 605) * S + 500)
GROUND = 500
wd = lambda *w: [x * S for x in w]
J = {k: t(*v) for k, v in dict(
    shoulder=(190, 335), elbow=(168, 410), knee=(152, 494), cannon=(151, 534), fet=(141, 568),
    f_shoulder=(205, 335), f_elbow=(205, 412), f_knee=(214, 494), f_cannon=(216, 534), f_fet=(212, 570),
    hip=(400, 346), stifle=(364, 432), hock=(452, 502), hfet=(436, 574),
    f_hip=(396, 344), f_stifle=(352, 428), f_hock=(340, 506), f_hfet=(338, 576)).items()}
WITHERS, NOSE = t(215, 302), t(50, 232)
CHEST, HAM = (t(250, 362), 108 * S, 72 * S, -3), (t(388, 382), 40 * S, 46 * S, 14)
SKULL = (t(120, 214), 44 * S, 30 * S, 18)
GESTURE = [NOSE + (6, -8), t(120, 205), t(175, 255), WITHERS, t(310, 308), t(420, 322), t(440, 350)]

trunk = mk("trunk", [ell_poly(*CHEST), ell_poly(*HAM),
                     tube([t(290, 350), t(340, 345), t(392, 340)], wd(112, 114, 118)),                # loin
                     tube([t(350, 334), t(400, 328), t(438, 340)], wd(80, 64, 48)),                   # croup, flat to the tail
                     tube([t(212, 332), t(190, 268), t(150, 212), SKULL[0]], wd(150, 118, 86, 62)),    # neck into skull
                     ell_poly(*SKULL),
                     tube([t(104, 219), t(76, 225), NOSE + (3, 0)], wd(46, 34, 24)),                  # muzzle
                     tube([t(100, 234), t(78, 243), t(60, 245)], wd(26, 18, 12)),                      # jaw
                     tube([t(212, 322), J["shoulder"] + (0, -4), J["elbow"] + (0, -12)] and
                          [t(212, 322), t(190, 345), t(172, 396)], wd(72, 62, 42))],                   # shoulder
           18, z=3, lw=2.0,
           fur=[((t(130, 240)[0], t(130, 240)[1], t(215, 330)[0], t(215, 330)[1]), (0.2, 1.0), 1.4),    # the mane under the throat
                ((t(380, 320)[0], t(380, 320)[1], t(440, 400)[0], t(440, 400)[1]), (0.5, 1.0), 0.8)])
near_fore = mk("near_fore", limb([J["elbow"] + (2, -14), J["elbow"], J["knee"], J["cannon"], J["fet"]],
                                 wd(54, 40, 22, 13, 15), knuckles=[(2, 10 * S), (4, 7 * S)]) + hoof(J["fet"], (-0.5, 1), 27 * S),
               4, z=2.5)
far_fore = mk("far_fore", limb([J["f_shoulder"], J["f_elbow"], J["f_knee"], J["f_cannon"], J["f_fet"]],
                               wd(48, 36, 20, 12, 14), knuckles=[(2, 9 * S), (4, 6 * S)]) + hoof(J["f_fet"], (-0.5, 1), 25 * S), 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", limb([J["hip"], J["stifle"], J["hock"], J["hfet"]], wd(104, 66, 32, 17),
                                 knuckles=[(2, 12 * S)]) + hoof(J["hfet"], (-0.5, 1), 27 * S),
               5, z=2.8, tone=-0.12)
far_hind = mk("far_hind", limb([J["f_hip"], J["f_stifle"], J["f_hock"], J["f_hfet"]], wd(80, 46, 22, 14),
                               knuckles=[(2, 11 * S)]) + hoof(J["f_hfet"], (-0.5, 1), 25 * S), 4, z=1, tone=0.3, lw=1.3)


def antler(name, dx, dy, z, tone, lw):
    def P(*pts):
        return [t(x + dx, y + dy) for x, y in pts]
    beam = tube(P((132, 196), (146, 164), (156, 128), (172, 96), (196, 70)), wd(12, 9, 7, 4))
    tines = [tube(P(*pts), wd(*w)) for pts, w in (
        (((138, 180), (120, 164), (98, 158)), (8, 6, 3)),                 # brow
        (((148, 160), (130, 140), (116, 112)), (8, 5.5, 3)),               # bez
        (((158, 124), (148, 98), (146, 66)), (8, 5.5, 3)),                 # trez
        (((174, 94), (172, 66), (178, 40)), (7, 5, 2.5)),                    # crown
        (((196, 70), (200, 48), (210, 30)), (7, 5, 2.5)),
        (((196, 70), (214, 62), (230, 66)), (7, 5, 2.5)))]
    return mk(name, [beam] + tines, 2, z=z, tone=tone, lw=lw)


antler_far = antler("antler_far", 26, 8, 5.2, 0.3, 1.3)
antler_near = antler("antler_near", 0, 0, 6.5, 0.0, 1.6)
parts = [ground_shadow(150, 480, 496, 10), far_fore, far_hind, trunk, near_fore, near_hind, antler_far, antler_near]

with L.figure(pen, (300, 300)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(110, GROUND + 2), (470, GROUND - 3)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (CHEST, HAM, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        for ch in (["shoulder", "elbow", "knee", "fet"], ["f_shoulder", "f_elbow", "f_knee", "f_fet"],
                   ["hip", "stifle", "hock", "hfet"], ["f_hip", "f_stifle", "f_hock", "f_hfet"]):
            bones(pen, [J[k] for k in ch])
        pen.line([WITHERS + (0, 0), (WITHERS[0], GROUND)], w=0.4, wobble=0.4, overshoot=6)

    ink_figure(pen, parts, SEED, hatch_t=0.55, part_t={"trunk": 0.6})
    ear(pen, t(134, 222), t(154, 208), t(214, 206), w=2.0, hatch=9)
    ear(pen, t(146, 206), t(160, 198), t(218, 184), w=1.3, hatch=0)
    eye = [t(94, 210), t(102, 205), t(110, 208), t(103, 213)]
    pen.line(eye + [eye[0]], w=0.9, wobble=0.2)
    pen.fill(catmull([t(99, 208), t(104, 208), t(104, 211), t(99, 211)], True, 5))
    pen.fill(catmull([NOSE + (-4, -5), NOSE + (3, -7), NOSE + (6, 0), NOSE + (0, 5), NOSE + (-5, 1)], True, 6))
    pen.line([NOSE + (5, 7), t(76, 237), t(98, 228)], w=0.9)
    pen.line([t(92, 202), t(104, 199), t(118, 204)], w=0.7)
    tufts(pen, [t(150 + 60 * u, 232 + 70 * u * u + 20 * u) for u in np.linspace(0, 1, 14)], (0.3, 1.0),
          length=(6, 13), w=0.6)
    flag = [t(434, 336), t(450, 344), t(454, 366), t(444, 378), t(436, 356)]
    pen.line(flag + [flag[0]], w=1.1, wobble=0.3, passes=2)
    for u in np.linspace(0.1, 0.9, 6):
        q = t(436 + 12 * u, 342 + 28 * u)
        pen.stroke(np.array([q, q + (1.5, 5)]), 0.5, taper=(0.1, 0.5), wobble=0.2)


def s_track(pen):
    """A line of prints walking: each a pair of long pointed halves with the dew claws behind."""
    for i in range(4):
        c = A(34 + i * 48, 116 - i * 24) + (0, 7 if i % 2 else -7)
        for s in (-1, 1):
            a = c + (s * 3.2, 0)
            pen.line([a + (0, -13), a + (s * 5.2, -2), a + (s * 4.4, 8), a + (s * 0.6, 9), a + (-s * 0.4, -1),
                      a + (0, -13)], w=0.8, wobble=0.3)
        for s in (-1, 1):
            pen.stroke(np.array([c + (s * 6, 15), c + (s * 7, 19)]), 0.8, taper=(0.2, 0.6))
    pen.line([(8, 138), (66, 108), (126, 72), (190, 28)], w=0.4, wobble=0.6, overshoot=8)


def s_hoof(pen):
    """Hoof from the front: two halves, the cleft between."""
    pen.line([(520, 420), (516, 450), (506, 482), (500, 506), (508, 514), (520, 512), (524, 470), (524, 436)],
             w=1.1, passes=2)
    pen.line([(524, 436), (527, 470), (530, 512), (542, 516), (552, 508), (544, 480), (538, 450), (536, 420)],
             w=1.1, passes=2)
    pen.line([(524, 470), (526, 500)], w=0.5)
    for k in range(7):
        x = 518 + k * 3.4
        pen.stroke(np.array([(x, 424), (x + 1, 413 + pen.rng.uniform(-3, 3))]), 0.5, taper=(0.1, 0.6))
    pen.line([(508, 520), (524, 524), (548, 520)], w=0.4, wobble=0.4)


def first_try(pen):
    body = [(40, 74), (74, 68), (112, 72), (130, 84), (126, 98), (96, 100), (60, 98), (42, 92)]
    pen.line(body + [body[0]], w=0.8, wobble=0.6, passes=2)
    pen.line([(46, 76), (34, 56), (26, 40), (14, 38), (8, 46), (20, 52)], w=0.8, passes=2)
    for x in (50, 62, 110, 122):
        pen.line([(x, 96), (x + 1, 120), (x + 3, 124)], w=0.7, passes=2)
    pen.line([(28, 40), (24, 22), (32, 14)], w=0.7)
    pen.line([(24, 40), (14, 24), (6, 22)], w=0.7)


L.page(pen, {"track": (s_track, (6, 14, 196, 142)), "hoof": (s_hoof, (496, 408, 556, 528))},
       crossed_draw=(first_try, (4, 12, 150, 128)))
save(pen, os.environ.get("OUT", "entry_ash_deer"))
