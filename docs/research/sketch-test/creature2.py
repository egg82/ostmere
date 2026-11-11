"""Second invented creature ("the dragger"), same hand as the stilt thing. Run -> creature2.svg"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 41))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "creature2")
A = lambda *p: np.array(p, float)

# Design: a bloated hairless sack hauled along on two long arms whose elbows rise above the head
# (kin to the stilt thing's high knees); vestigial back stubs; a heavy blunt head hung from a short
# thick neck (one silhouette with the body), six small eyes, a wide lipless mouth.
GROUND = 480
SACK, HUMP, SKULL = (A(366, 392), 112, 68, 8), (A(252, 340), 56, 50, -10), (A(148, 388), 50, 38, 6)
GESTURE = [(104, 400), (150, 390), (250, 312), (360, 326), (460, 380), (520, 450)]
ARM_N = [A(244, 330), A(206, 214), A(124, 432), A(104, 470)]
ARM_F = [A(272, 326), A(258, 206), A(202, 440), A(190, 470)]

body = mk("body", [ell_poly(*SACK), ell_poly(*HUMP), tube([(440, 410), (500, 444), (520, 462)], [80, 40, 14]),
                   tube([(244, 352), (200, 372), SKULL[0]], [74, 64, 52]),          # neck bridges into skull
                   ell_poly(*SKULL), tube([SKULL[0], (112, 396), (96, 400)], [68, 62, 56])],  # blunt face
          14, z=3, lw=1.9)


def hand(wrist, spread, length, wid):
    polys = [ell_poly(wrist + (0, 6), wid * 1.1, wid * 0.7, 0)]
    for a in spread:
        r = np.radians(a)
        tip = wrist + np.array([np.cos(r), np.sin(r)]) * length
        mid = (wrist + tip) / 2 + (0, -3)
        polys += [tube([wrist, mid], [wid * 0.55, wid * 0.42]), tube([mid, tip], [wid * 0.42, wid * 0.25]),
                  ell_poly(mid, wid * 0.32, wid * 0.3)]
    return polys


SPREAD_N, SPREAD_F = (148, 166, 184, 202), (156, 176, 196)
arm_n = mk("arm_n", limb(ARM_N, [22, 15, 10, 9], knuckles=[(1, 11), (2, 8)]) + hand(ARM_N[3], SPREAD_N, 46, 15), 3,
           z=6)                                   # near arm crosses IN FRONT of the face
arm_f = mk("arm_f", limb(ARM_F, [18, 13, 9, 8], knuckles=[(1, 9), (2, 7)]) + hand(ARM_F[3], SPREAD_F, 38, 12), 3,
           z=1, tone=0.3, lw=1.3)                 # far arm behind body and head
stub = mk("stub", limb([A(430, 440), A(446, 462), A(440, 476)], [20, 12, 10]) + hand(A(440, 476), (170, 10), 14, 8),
          3, z=4)
parts = [ground_shadow(110, 540, 476, 10), arm_f, body, stub, arm_n]

with L.figure(pen, (300, 350)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(70, GROUND + 2), (560, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (SACK, HUMP, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        bones(pen, ARM_N); bones(pen, ARM_F)
    ink_figure(pen, parts, SEED, hatch_t=0.5, form_parts=("body",), part_t={"body": 0.45, "arm_n": 0.72},
               cross={"body": (0.95, 65), "arm_f": (0.85, 20)})
    for k in range(4):                                       # sag folds
        x0 = 300 + k * 40
        pen.line([(x0, 440 - k * 2), (x0 + 22, 452), (x0 + 46, 446 + k * 2)], w=0.7, wobble=0.6)
    for i in range(11):                                      # spine knuckles
        t = i / 10
        q = A(232 + 260 * t, 300 - 10 * np.sin(t * np.pi) + 120 * t ** 2.2)
        pen.stroke(np.array([q, q + (2, -7)]), 1.3, taper=(0.2, 0.5))
    for i in range(4):                                       # ribs on the hump
        x = 236 + i * 14
        pen.line([(x, 312), (x + 8, 336), (x + 4, 362)], w=0.8, wobble=0.5, passes=2, spread=0.5)
    pen.line([(196, 366), (186, 384), (190, 404)], w=0.6, wobble=0.5)   # neck fold into the skull
    # mouth wraps the lower face; small teeth; six eyes in a shallow arc above
    pen.line([(94, 412), (124, 420), (160, 420), (186, 408)], w=1.6, passes=2, spread=0.4)
    for k in range(13):
        x = 98 + k * 7
        y = 415 + 4 * np.sin((k / 12) * np.pi)
        pen.stroke(np.array([(x, y - 1), (x + 1, y + 5)]), 1.1, taper=(0.1, 0.8))
    for k in range(6):
        c = A(102 + k * 14, 380 - 6 * np.sin(k / 5 * np.pi))
        r = 3.8 - 0.3 * abs(k - 2.5)
        hand_ellipse(pen, c, r * 1.3, r, 0, w=0.7, passes=1)
        if k != 4:
            pen.fill(catmull([c + (-1.3, -1.1), c + (1.3, -1.1), c + (1.3, 1.1), c + (-1.3, 1.1)], True, 4))
    for q, angs, Ln in ((ARM_N[3], SPREAD_N, 46), (ARM_F[3], SPREAD_F, 38)):   # nails
        for a in angs:
            r = np.radians(a)
            tip = q + np.array([np.cos(r), np.sin(r)]) * Ln
            pen.stroke(np.array([tip, tip + np.array([np.cos(r), np.sin(r)]) * 6]), 1.2, taper=(0.1, 0.8))


def s_hand(pen):
    w0 = A(500, 44)
    hand_ellipse(pen, w0 + (0, 8), 26, 17, 0, w=1.1, passes=2)
    pen.line([w0 + (-14, -4), w0 + (-12, -30)], w=1.1, passes=2); pen.line([w0 + (14, -4), w0 + (12, -30)], w=1.1, passes=2)
    for a, Ln in ((112, 70), (96, 80), (80, 76), (64, 62)):
        r = np.radians(a)
        dv = np.array([np.cos(r), np.sin(r)]); nv = np.array([-dv[1], dv[0]])
        base = w0 + dv * 14
        for sd in (-1, 1):
            pen.line([base + nv * 4.5 * sd, base + dv * Ln * 0.5 + nv * 5.5 * sd, base + dv * Ln + nv * 2.5 * sd],
                     w=1.0, wobble=0.4)
        pen.stroke(np.array([base + dv * Ln * 0.5 - nv * 6, base + dv * Ln * 0.5 + nv * 6]), 0.8, taper=(0.3, 0.3))
        tip = base + dv * Ln
        pen.stroke(np.array([tip, tip + dv * 10 + nv * 2]), 1.8, taper=(0.1, 0.8))


def s_eyes(pen):
    for k in range(6):
        c = A(440 + k * 22, 528 + 3 * np.sin(k))
        hand_ellipse(pen, c, 7, 5 - (k % 3), 0, w=0.9, passes=1)
        if k != 4:
            pen.fill(catmull([c + (-2, -2), c + (2, -2), c + (2, 2), c + (-2, 2)], True, 4))
        else:
            pen.line([c + (-7, 0), c + (7, 0)], w=1.0)


def s_tracks(pen):
    pen.line([(10, 60), (60, 58), (120, 62), (160, 60)], w=0.8, wobble=1.0, passes=2, spread=2.0)
    pen.line([(10, 76), (70, 78), (160, 74)], w=0.8, wobble=1.0, passes=2, spread=2.0)
    for x in (30, 100):
        for k in range(4):
            a = np.radians(200 + k * 20)
            pen.line([(x, 40), (x + np.cos(a) * 16, 40 + np.sin(a) * 16)], w=0.9)


def first_try(pen):
    hand_ellipse(pen, (74, 70), 46, 28, 0, w=0.9, passes=2)
    hand_ellipse(pen, (26, 58), 16, 14, 0, w=0.8, passes=1)
    for x in (46, 60, 94, 108):
        pen.line([(x, 94), (x + 1, 114)], w=0.8)


L.page(pen, {"hand": (s_hand, (470, 6, 540, 130)), "eyes": (s_eyes, (430, 520, 560, 536)),
             "tracks": (s_tracks, (6, 22, 164, 82))}, crossed_draw=(first_try, (8, 40, 122, 116)))
save(pen, "creature2")
