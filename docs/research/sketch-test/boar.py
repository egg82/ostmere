"""Wild boar with the journal method. Run: python3 boar.py -> boar.svg (SEED, LAYOUT_SEED env vars)"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 31))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "boar")
A = lambda *p: np.array(p, float)

# Boar: forequarters ~1.4x the ham, shoulder height ~0.55 of body length, head ~0.4 of body
# length carried low, legs short. Head built FROM the neck: one silhouette with the trunk.
GROUND = 480
CHEST, HAM = (A(238, 318), 86, 104, -5), (A(424, 346), 56, 64, 0)
SKULL, SNOUT = (A(158, 326), 46, 32, 22), (A(74, 362), 8, 16, -20)
GESTURE = [(80, 356), (150, 300), (220, 226), (330, 250), (430, 276), (480, 312)]
J = {k: A(*v) for k, v in dict(
    sh=(222, 380), el=(216, 412), wr=(214, 444), hf=(208, 466),
    f_sh=(258, 384), f_el=(258, 414), f_wr=(262, 442), f_hf=(260, 462),
    hip=(430, 360), st=(420, 404), ho=(442, 436), hh=(438, 466),
    f_hip=(456, 362), f_st=(454, 404), f_ho=(470, 432), f_hh=(468, 460)).items()}

body = mk("body", [ell_poly(*CHEST), ell_poly(*HAM), tube([(262, 326), (340, 340), (412, 346)], [180, 140, 120]),
                   tube([(222, 318), (190, 324), SKULL[0]], [120, 88, 62]),                  # neck bridges into skull
                   ell_poly(*SKULL), tube([SKULL[0], (116, 344), (80, 360)], [56, 40, 30]),  # skull -> snout
                   ell_poly(*SNOUT), tube([(170, 350), (120, 368), (90, 372)], [28, 16, 11])],  # lower jaw
          14, z=3, lw=1.9, fur=[((150, 220, 460, 300), (0.4, -1.0), 1.0), ((170, 370, 300, 420), (0.0, 1.0), 0.8),
                                ((150, 340, 210, 390), (0.5, 0.8), 0.9)])
legs = []
for name, ch, wd, z, tone in (("nf", ["sh", "el", "wr", "hf"], [44, 36, 22, 19], 2.5, 0.0),
                              ("ff", ["f_sh", "f_el", "f_wr", "f_hf"], [38, 30, 19, 16], 1, 0.3),
                              ("nh", ["hip", "st", "ho", "hh"], [52, 36, 22, 19], 2.5, 0.0),
                              ("fh", ["f_hip", "f_st", "f_ho", "f_hh"], [44, 30, 19, 16], 1, 0.3)):
    pts = [J[k] for k in ch]
    legs.append(mk(name, limb(pts, wd, knuckles=[(2, wd[2] * 0.6)]) + hoof(pts[-1], (-0.6, 1), wd[3]), 4, z=z,
                   tone=tone, lw=1.6 if tone == 0 else 1.3))
tail = mk("tail", [tube([(474, 300), (490, 326), (488, 350)], [8, 6, 5])], 2, z=2, fur=[((470, 330, 500, 360), (0, 1), 1.2)])
parts = [ground_shadow(170, 500, 474, 9)] + legs + [tail, body]

with L.figure(pen, (290, 350)):
    with pen.construction():
        pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
        pen.line([(150, GROUND + 2), (520, GROUND - 4)], w=0.45, wobble=0.6)
        for c, rx, ry, rot in (CHEST, HAM, SKULL):
            hand_ellipse(pen, c, rx, ry, rot)
        pen.line([(190, 296), (84, 340), (88, 372), (186, 346)], w=0.4, wobble=0.6, overshoot=6)
        for ch in (["sh", "el", "wr", "hf"], ["f_sh", "f_el", "f_wr", "f_hf"], ["hip", "st", "ho", "hh"],
                   ["f_hip", "f_st", "f_ho", "f_hh"]):
            bones(pen, [J[k] for k in ch])
    ink_figure(pen, parts, SEED, hatch_t=0.5, form_parts=("body",), part_t={"body": 0.3},
               cross={"body": (0.8, 60), "ff": (0.9, 20), "fh": (0.9, 20)})
    ear(pen, (172, 302), (192, 308), (190, 266), w=1.4)               # ear rising out of the skull
    crest = [A(176 + 264 * t, 252 - 40 * np.sin((t + 0.15) * np.pi * 0.8) + 30 * t) for t in np.linspace(0, 1, 46)]
    tufts(pen, crest, (0.35, -1.0), length=(8, 17), w=0.75)
    pen.ellipse((74, 362), 7, 15, rot=-20, w=0.9, turns=1.05, wobble=0.3)
    pen.fill(catmull([(72, 356), (75, 355), (75, 360), (72, 360)], True, 4))
    pen.fill(catmull([(74, 367), (77, 366), (77, 371), (74, 371)], True, 4))
    pen.line([(132, 320), (142, 314), (154, 318)], w=0.9)              # brow
    pen.fill(catmull([(140, 320), (145, 319), (145, 323), (140, 323)], True, 4))
    for base, tip in (((100, 368), (88, 334)), ((114, 366), (108, 344))):
        pen.line([base, (base[0] - 10, (base[1] + tip[1]) / 2 + 2), tip], w=2.4, wobble=0.2, passes=2, spread=0.5)
    for k in ("hf", "f_hf", "hh", "f_hh"):
        q = J[k] + (-4, 10)
        pen.stroke(np.array([q, q + (-2, 8)]), 0.8, taper=(0.1, 0.3))


def s_tusk(pen):
    pen.line([(470, 120), (482, 92), (506, 64), (540, 50), (552, 54)], w=1.4, passes=2, spread=0.6)
    pen.line([(486, 124), (494, 98), (514, 76), (542, 60), (552, 54)], w=1.1, passes=2, spread=0.6)
    pen.line([(470, 120), (486, 124)], w=0.8)
    for k in range(8):
        t = k / 7
        q = A(482, 108) * (1 - t) + A(532, 60) * t
        pen.stroke(np.array([q, q + (6, 5)]), 0.5, taper=(0.1, 0.4))


def s_print(pen):
    for side in (-1, 1):
        pen.line([(500 + side * 4, 508), (500 + side * 18, 528), (500 + side * 15, 560), (500 + side * 4, 566)],
                 w=1.3, passes=2, spread=0.6)
    for x in (480, 520):
        hand_ellipse(pen, (x, 578), 4, 3, 0, w=0.9, passes=1)


def s_bristle(pen):
    for k in range(5):
        x = 20 + k * 9
        pen.line([(x, 120), (x + 2, 60), (x + 4, 40)], w=0.9, wobble=0.4)
        for dx in (-4, 0, 4):
            pen.stroke(np.array([(x + 4, 40), (x + 4 + dx, 30)]), 0.6, taper=(0.1, 0.7))


def first_try(pen):
    hand_ellipse(pen, (74, 72), 50, 30, 0, w=0.9, passes=2)
    hand_ellipse(pen, (24, 64), 14, 13, 0, w=0.8, passes=1)
    for x in (44, 56, 92, 104):
        pen.line([(x, 98), (x, 116)], w=0.8)
    pen.line([(124, 66), (134, 58), (130, 52), (126, 60)], w=0.7)


L.page(pen, {"tusk": (s_tusk, (466, 48, 556, 126)), "print": (s_print, (474, 504, 526, 584)),
             "bristle": (s_bristle, (12, 26, 72, 124))}, crossed_draw=(first_try, (8, 38, 140, 120)))
save(pen, "boar")
