"""Journal entry `mourner`: a big cat stalking, the near fore lifted with its toes spread open like a hand. Run:
bash render.sh entry_mourner -> entry_mourner_ink.png

Body measured as a cougar's, side on, withers height H at the shoulder blade's top: body from chest to rump ~1.4 H,
chest depth ~0.45 H, the rump a little higher than the withers, head small (~0.3 H) with a short muzzle and round
ears, tail ~1.1 H carried low with its end turned up, legs long and the hind ones heavier. The fore toes are not a
cat's: borrowed from a hand, each ~0.15 H long in two joints, spread from a broad palm pad, with a short thumb set
higher on the inside, so the lifted foot reads as a hand reaching.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 23))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 41)), "entry_mourner", text_scale=1.3)
A = lambda *p: np.array(p, float)

GROUND, H = 500, 190
WITHERS = A(252, GROUND - H)
J = {k: A(*v) for k, v in dict(
    shoulder=(250, 360), elbow=(240, 410), wrist=(214, 442), palm=(192, 458),
    f_shoulder=(288, 364), f_elbow=(294, 420), f_wrist=(296, 472), f_paw=(292, 492),
    hip=(452, 344), stifle=(418, 410), hock=(482, 456), hpaw=(466, 494),
    f_hip=(474, 340), f_stifle=(462, 408), f_hock=(500, 450), f_hpaw=(490, 492)).items()}
CHEST, HAM = (A(262, 352), 70, 56, -6), (A(448, 340), 54, 50, 8)
SKULL = (A(166, 326), 33, 27, -4)
NOSE = A(122, 342)
TAIL = [(496, 322), (526, 362), (552, 398), (578, 414), (596, 402)]
GESTURE = [NOSE + (4, -6), (170, 306), WITHERS + (0, -4), (360, 318), (470, 304), (500, 318)] + TAIL[1:]

# The hand: palm pad, four long toes fanning down and forward, a short thumb on the inside. (base angle deg, length)
FINGERS = [(206, 46), (186, 56), (166, 54), (146, 42)]
THUMB = (112, 26)


def finger_chain(base, ang, length):
    a = np.radians(ang)
    d1 = np.array([np.cos(a), np.sin(a)])
    a2 = a + np.radians(16)                        # each toe curls down a little at its middle joint
    d2 = np.array([np.cos(a2), np.sin(a2)])
    mid = base + d1 * length * 0.55
    return [base, mid, mid + d2 * length * 0.45]


PALM = J["palm"]
finger_polys, finger_tips = [], []
for k, (ang, ln) in enumerate(FINGERS):
    base = PALM + np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))]) * 8
    ch = finger_chain(base, ang, ln)
    finger_polys += limb(ch, [9, 7, 4], knuckles=[(1, 4.4)])
    finger_tips.append((ch[-2], ch[-1]))
thumb_base = PALM + (6, 8)
thumb = finger_chain(thumb_base, *THUMB)
finger_polys += limb(thumb, [9, 7, 5])
finger_tips.append((thumb[-2], thumb[-1]))

trunk = mk("trunk", [ell_poly(*CHEST), ell_poly(*HAM),
                     tube([(300, 344), (370, 342), (430, 340)], [100, 70, 86]),                    # barrel, belly tucked
                     ell_poly(WITHERS + (6, 22), 34, 18, -8),                                      # shoulder blades
                     tube([WITHERS + (-6, 32), (204, 320), SKULL[0]], [88, 68, 50]),                # neck into skull
                     ell_poly(*SKULL),
                     tube([SKULL[0] + (-16, 8), (138, 338), NOSE + (2, 0)], [36, 30, 22]),          # muzzle, short
                     tube([(158, 350), (140, 354), (130, 352)], [16, 12, 9]),                       # chin
                     tube([WITHERS + (-4, 26), J["shoulder"], J["elbow"] + (0, -10)], [64, 54, 40]),   # shoulder
                     ell_poly(A(436, 372), 44, 50, 24)],                                          # the thigh, in the trunk
           18, z=3, lw=1.9,
           fur=[((230, 300, 320, 330), (0.4, -1.0), 0.6), ((260, 390, 430, 400), (0.0, 1.0), 0.6)])
near_fore = mk("near_fore", limb([J["shoulder"], J["elbow"], J["wrist"], PALM], [56, 42, 28, 28],
                                 knuckles=[(2, 13)]) + [ell_poly(PALM, 17, 13, 20)], 3, z=2.9)
fingers = mk("fingers", finger_polys, 1, z=3.6, lw=1.6)
far_fore = mk("far_fore", limb([J["f_shoulder"], J["f_elbow"], J["f_wrist"], J["f_paw"]], [44, 32, 20, 19],
                               knuckles=[(2, 11)]) + paw(J["f_paw"], (-1, 0.1), 19), 5, z=1, tone=0.3, lw=1.4)
near_hind = mk("near_hind", limb([J["stifle"] + (12, -20), J["stifle"], J["hock"], J["hpaw"]], [56, 42, 24, 20], knuckles=[(2, 12)]) +
               paw(J["hpaw"], (-1, 0.05), 21), 6, z=2.8, tone=-0.05)
far_hind = mk("far_hind", limb([J["f_hip"], J["f_stifle"], J["f_hock"], J["f_hpaw"]], [56, 38, 21, 18],
                               knuckles=[(2, 10)]) + paw(J["f_hpaw"], (-1, 0.05), 18), 5, z=1, tone=0.3, lw=1.4)
tail = mk("tail", [tube(TAIL, [20, 16, 13, 10, 7])], 4, z=2)
parts = [ground_shadow(170, 520, 496, 10), far_fore, far_hind, tail, trunk, near_hind, near_fore, fingers]

with L.figure(pen, (330, 390)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(140, GROUND + 2), (580, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (CHEST, HAM, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        for ch in (["shoulder", "elbow", "wrist", "palm"], ["f_shoulder", "f_elbow", "f_wrist", "f_paw"],
                   ["hip", "stifle", "hock", "hpaw"], ["f_hip", "f_stifle", "f_hock", "f_hpaw"]):
            bones(pen, [J[k] for k in ch])
        pen.line([WITHERS + (0, 4), (WITHERS[0], GROUND)], w=0.4, wobble=0.4, overshoot=6)   # H, measured off
    ink_figure(pen, parts, SEED, hatch_t=0.55, form_parts=("trunk",),
               part_t={"trunk": 0.36, "near_fore": 0.5, "fingers": 0.6, "near_hind": 0.42, "tail": 0.4},
               cross={"far_fore": (0.9, 20), "far_hind": (0.9, 20)})
    for a, b in finger_tips:                                                 # a short claw at each toe's end
        d = (b - a) / np.linalg.norm(b - a)
        pen.stroke(np.array([b, b + d * 6 + (d[1] * 2, -d[0] * 2)]), 1.0, taper=(0.2, 0.9), wobble=0.1)
    paw_details(pen, J["f_paw"], (-1, 0.1), 19)
    ear(pen, (172, 304), (192, 310), (190, 284), w=1.3, hatch=4)       # ears, short and rounded at the tip
    ear(pen, (150, 302), (164, 300), (154, 286), w=0.9, inner=False, hatch=0)
    eye = [A(143, 324), A(151, 320), A(159, 322), A(151, 326)]
    pen.line(eye + [eye[0]], w=0.9, wobble=0.2)
    pen.fill(catmull([A(150, 321), A(152, 321), A(152.5, 325), A(149.5, 325)], True, 5))   # the pupil a slit
    pen.line([(136, 318), (150, 313), (164, 318)], w=0.8)                    # brow
    pen.line([(132, 326), (128, 334), (126, 340)], w=0.7)                    # the bridge of the nose
    pen.fill(catmull([NOSE + (-4, -4), NOSE + (3, -5), NOSE + (5, 0), NOSE + (0, 3), NOSE + (-4, 1)], True, 6))
    pen.line([NOSE + (2, 4), NOSE + (6, 9), (146, 352)], w=0.8)              # mouth
    for k in range(3):                                                       # whisker pads, a few strokes
        q = NOSE + (10, 2 + k * 3)
        pen.stroke(np.array([q, q + (-18, -2 + k * 4)]), 0.5, taper=(0.1, 0.6), wobble=0.2)


def s_hand(pen):
    """The fore foot from below, opened: the palm pad, four long toes each in two joints, the thumb set back."""
    pad = [(42, 96), (60, 88), (82, 90), (96, 100), (92, 120), (72, 130), (50, 126), (38, 112), (42, 96)]
    pen.line(pad, w=1.3, passes=2, spread=0.6)
    for x0, ang, ln in ((46, 246, 40), (60, 260, 48), (76, 274, 46), (90, 288, 38)):
        a = np.radians(ang)
        d = np.array([np.cos(a), np.sin(a)])
        b = A(x0, 90)
        m = b + d * ln * 0.55
        t = m + np.array([np.cos(a - 0.12), np.sin(a - 0.12)]) * ln * 0.45
        out = tube([b, m, t], [9, 8, 6])
        pen.line(list(out[len(out) // 2 - 12:]) + list(out[:len(out) // 2 + 12]), w=1.0, wobble=0.3)
        nrm = np.array([-d[1], d[0]])
        pen.stroke(np.array([m - nrm * 3.5, m + nrm * 3.5]), 0.6, taper=(0.2, 0.2))   # the joint's crease
        pen.stroke(np.array([t, t + d * 7]), 1.0, taper=(0.2, 0.9))                    # the claw
    out = tube([(96, 110), (110, 100), (118, 88)], [9, 8, 6])                          # the thumb
    pen.line(list(out) + [out[0]], w=1.0, wobble=0.3)


def s_print(pen):
    """The fore print in soft ground: a broad pad, four long toe-marks well apart, the thumb's mark off to one side."""
    pen.line([(500, 540), (520, 530), (544, 534), (552, 552), (536, 566), (510, 566), (498, 554), (500, 540)],
             w=1.2, passes=2, spread=0.6)
    for x, y, rot in ((494, 506, 20), (512, 494, 8), (532, 492, -8), (550, 502, -20)):
        hand_ellipse(pen, (x, y), 5, 11, rot, w=0.9, passes=1)
    hand_ellipse(pen, (566, 540), 4, 7, -40, w=0.9, passes=1)


def first_try(pen):
    hand_ellipse(pen, (80, 74), 52, 26, 0, w=0.9, passes=2)
    hand_ellipse(pen, (26, 66), 15, 13, 0, w=0.8, passes=1)
    for x in (48, 62, 100, 116):
        pen.line([(x, 96), (x, 118)], w=0.8)
    pen.line([(132, 74), (146, 96), (154, 90)], w=0.8)


L.page(pen, {"hand": (s_hand, (30, 34, 126, 134)), "print": (s_print, (484, 478, 574, 572))},
       crossed_draw=(first_try, (6, 40, 160, 122)))
save(pen, os.environ.get("OUT", "entry_mourner"))
