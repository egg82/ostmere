"""Journal entry `ash_bear`: a brown bear walking, head low, the hump over its shoulders. Run:
bash render.sh entry_ash_bear -> entry_ash_bear_ink.png

Measured off a photo of a brown bear walking, side on (Commons, "Brown bear walking on red clay"), with withers
height H at the hump's top: nose to rump ~1.9 H, shoulder point to rump ~1.3 H, chest depth ~0.58 H (leg below the
chest ~0.42 H), rump ~0.88 H, head length ~0.42 H carried below the back line, the face dished between brow and
muzzle, ears small and round. A plantigrade walk: the near fore reaches forward with the wrist bent and the long
claws showing, the far fore is back under the chest; the hind foot sets down flat, heel and all, the hock low.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 41))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 47)), "entry_ash_bear", text_scale=1.3)
A = lambda *p: np.array(p, float)

GROUND, H = 500, 200
HUMP = A(262, GROUND - H)
J = {k: A(*v) for k, v in dict(
    shoulder=(250, 362), elbow=(238, 424), wrist=(214, 474), fpaw=(198, 494),
    f_shoulder=(292, 366), f_elbow=(296, 426), f_wrist=(304, 476), f_paw=(306, 494),
    hip=(438, 356), stifle=(420, 420), hock=(446, 478), hpaw=(426, 496),
    f_hip=(458, 352), f_stifle=(462, 418), f_hock=(482, 474), f_hpaw=(468, 494)).items()}
CHEST, HAM = (A(272, 362), 82, 54, -4), (A(436, 380), 54, 42, 10)
SKULL, NOSE = (A(178, 352), 40, 33, -8), A(112, 386)
GESTURE = [NOSE + (6, -10), (176, 334), HUMP + (0, -4), (370, 320), (466, 334), (494, 370)]

trunk = mk("trunk", [ell_poly(*CHEST), ell_poly(*HAM), ell_poly(HUMP + (-8, 26), 56, 34, -10),      # hump
                     tube([(304, 370), (370, 382), (420, 380)], [96, 70, 76]),                      # barrel, falling to the rump
                     tube([HUMP + (-10, 34), (214, 344), SKULL[0]], [108, 88, 62]),                 # neck into skull
                     ell_poly(*SKULL),
                     tube([SKULL[0] + (-12, 8), (142, 374), NOSE + (4, 0)], [48, 38, 30]),          # muzzle, broad, dished
                     tube([(168, 384), (142, 394), (122, 396)], [22, 16, 12]),                      # lower jaw
                     tube([HUMP + (-6, 30), J["shoulder"], J["elbow"] + (0, -12)], [70, 62, 48])],  # shoulder
           18, z=3, lw=2.0,
           fur=[((200, 280, 330, 330), (0.5, -1.0), 1.3), ((230, 400, 440, 440), (0.1, 1.0), 0.9),
                ((150, 330, 240, 400), (0.7, 0.7), 0.8), ((470, 330, 500, 420), (0.6, 1.0), 1.0)])
near_fore = mk("near_fore", limb([J["elbow"] + (2, -18), J["elbow"], J["wrist"], J["fpaw"]], [54, 44, 34, 30],
                                 knuckles=[(2, 20)]) + paw(J["fpaw"], (-1, 0.15), 24),
               5, z=2.5, fur=[((220, 410, 262, 470), (0.2, 1.0), 0.9)])
far_fore = mk("far_fore", limb([J["f_shoulder"], J["f_elbow"], J["f_wrist"], J["f_paw"]], [48, 40, 30, 27],
                               knuckles=[(2, 17)]) + paw(J["f_paw"], (-1, 0.15), 21), 5, z=1, tone=0.3, lw=1.4)
near_hind = mk("near_hind",
               limb([J["hip"], J["stifle"], J["hock"], J["hpaw"]], [64, 46, 32, 28], knuckles=[(2, 18)]) +
               paw(J["hpaw"], (-1, 0.05), 26), 6, z=2.8, tone=-0.1, fur=[((404, 400, 470, 470), (0.3, 1.0), 0.8)])
far_hind = mk("far_hind", limb([J["f_hip"], J["f_stifle"], J["f_hock"], J["f_hpaw"]], [56, 40, 28, 25],
                               knuckles=[(2, 15)]) + paw(J["f_hpaw"], (-1, 0.05), 22), 5, z=1, tone=0.3, lw=1.4)
parts = [ground_shadow(150, 520, 496, 10), far_fore, far_hind, trunk, near_fore, near_hind]

with L.figure(pen, (300, 390)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(130, GROUND + 2), (560, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (CHEST, HAM, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        for ch in (["shoulder", "elbow", "wrist", "fpaw"], ["f_shoulder", "f_elbow", "f_wrist", "f_paw"],
                   ["hip", "stifle", "hock", "hpaw"], ["f_hip", "f_stifle", "f_hock", "f_hpaw"]):
            bones(pen, [J[k] for k in ch])
        pen.line([HUMP + (0, 4), (HUMP[0], GROUND)], w=0.4, wobble=0.4, overshoot=6)   # H, measured off
    ink_figure(pen, parts, SEED, hatch_t=0.5, form_parts=("trunk",), part_t={"trunk": 0.3, "near_fore": 0.42, "near_hind": 0.42},
               cross={"trunk": (0.72, 55), "far_fore": (0.9, 20), "far_hind": (0.9, 20)})
    for k, d, s in (("fpaw", (-1, 0.15), 24), ("f_paw", (-1, 0.15), 21)):
        paw_details(pen, J[k], d, s)
    for k in range(5):                                                      # the fore claws, long and pale
        q = J["fpaw"] + (-16 - k * 3.2, 10 + k * 1.2)
        pen.line([q, q + (-9, 3), q + (-12, 8)], w=0.9, wobble=0.2)
    for c, r, w in ((SKULL[0] + (14, -30), 8, 1.2), (SKULL[0] + (-2, -32), 6.5, 0.9)):   # ears, small and round
        pen.line([c + (-r, 6), c + (-r, -1), c + (-r * 0.4, -r), c + (r * 0.5, -r), c + (r, 0), c + (r, 6)],
                 w=w, wobble=0.3)
    eye = [A(158, 352), A(164, 349), A(170, 351), A(164, 354)]
    pen.line(eye + [eye[0]], w=0.9, wobble=0.2)
    pen.fill(catmull([A(162, 350), A(166, 350), A(166, 353), A(162, 353)], True, 5))
    pen.line([(150, 344), (162, 342), (174, 346)], w=0.8)                    # brow over the dish
    pen.fill(catmull([NOSE + (-5, -6), NOSE + (4, -8), NOSE + (7, 0), NOSE + (1, 5), NOSE + (-6, 1)], True, 6))
    pen.line([NOSE + (4, 8), (128, 394), (150, 390)], w=0.9)
    tufts(pen, [A(214 + 120 * t, 294 + 6 * t - 8 * np.sin(t * np.pi)) for t in np.linspace(0, 1, 16)],
          (0.4, -1.0), length=(4, 8), w=0.6)


def s_paw(pen):
    """A fore print: the broad pad, five toes in an arc, the claw marks well ahead of them."""
    pad = [(492, 520), (512, 512), (538, 514), (556, 524), (552, 544), (528, 552), (502, 548), (488, 534), (492, 520)]
    pen.line(pad, w=1.2, passes=2, spread=0.6)
    for i, (dx, dy) in enumerate(((-30, -8), (-16, -20), (2, -24), (20, -20), (34, -8))):
        c = A(522 + dx, 506 + dy)
        hand_ellipse(pen, c, 6, 7, 0, w=0.9, passes=1)
        pen.stroke(np.array([c + (dx * 0.05, -9), c + (dx * 0.12, -24)]), 1.0, taper=(0.2, 0.6))


def s_marks(pen):
    """Bark with four claw marks raked down it, the pale wood showing."""
    pen.line([(20, 20), (24, 80), (22, 140)], w=1.2, wobble=0.6, passes=2)
    pen.line([(90, 18), (92, 80), (96, 140)], w=1.2, wobble=0.6, passes=2)
    for k in range(4):
        x = 38 + k * 12
        pen.line([(x, 30 + k * 2), (x + 6, 70 + k * 3), (x + 8, 108 + k)], w=1.1, wobble=0.3, passes=2, spread=0.5)
        pen.line([(x + 3, 32 + k * 2), (x + 9, 72 + k * 3)], w=0.5, wobble=0.3)
    for y in (24, 52, 96, 128):
        pen.stroke(np.array([(26, y), (34, y + 2)]), 0.6, taper=(0.2, 0.5))


def first_try(pen):
    hand_ellipse(pen, (84, 72), 54, 30, 0, w=0.9, passes=2)
    hand_ellipse(pen, (26, 82), 18, 16, 0, w=0.8, passes=1)
    for x in (52, 68, 104, 120):
        pen.line([(x, 98), (x, 118)], w=0.8)


L.page(pen, {"paw": (s_paw, (482, 476, 562, 556)), "marks": (s_marks, (14, 14, 104, 146))},
       crossed_draw=(first_try, (6, 38, 140, 120)))
save(pen, os.environ.get("OUT", "entry_ash_bear"))
