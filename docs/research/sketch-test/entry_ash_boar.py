"""Journal entry `ash_boar`: a wild boar standing, head low, its coat caked in clots. Run:
bash render.sh entry_ash_boar -> entry_ash_boar_ink.png

Built on `boar.py`, whose ratios came off a wild boar side on: forequarters ~1.4x the ham, shoulder height ~0.55 of
body length, head ~0.4 of body length carried low, legs short. Here the forequarters are heavier still (chest egg
taller, the crest higher over the shoulders) and the coat is caked: clots hang along the belly and the backs of the
legs, and the hatching on the trunk goes a second layer darker.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 31))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 34)), "entry_ash_boar", text_scale=1.3)
A = lambda *p: np.array(p, float)

GROUND = 480
CHEST, HAM = (A(238, 314), 90, 110, -5), (A(424, 346), 56, 64, 0)
SKULL, SNOUT = (A(158, 326), 46, 32, 22), (A(74, 362), 8, 16, -20)
GESTURE = [(80, 356), (150, 300), (220, 218), (330, 246), (430, 276), (480, 312)]
J = {k: A(*v) for k, v in dict(
    sh=(222, 380), el=(216, 412), wr=(214, 444), hf=(208, 466),
    f_sh=(258, 384), f_el=(258, 414), f_wr=(262, 442), f_hf=(260, 462),
    hip=(430, 360), st=(420, 404), ho=(442, 436), hh=(438, 466),
    f_hip=(456, 362), f_st=(454, 404), f_ho=(470, 432), f_hh=(468, 460)).items()}

body = mk("body", [ell_poly(*CHEST), ell_poly(*HAM), tube([(262, 326), (340, 340), (412, 346)], [180, 140, 120]),
                   tube([(222, 318), (190, 324), SKULL[0]], [120, 88, 62]),                  # neck bridges into skull
                   ell_poly(*SKULL), tube([SKULL[0], (116, 344), (80, 360)], [56, 40, 30]),  # skull -> snout
                   ell_poly(*SNOUT), tube([(170, 350), (120, 368), (90, 372)], [28, 16, 11])],  # lower jaw
          14, z=3, lw=1.9, fur=[((150, 210, 460, 300), (0.4, -1.0), 1.0), ((170, 370, 420, 425), (0.0, 1.0), 1.1),
                                ((150, 340, 210, 390), (0.5, 0.8), 0.9)])
legs = []
for name, ch, wd, z, tone in (("nf", ["sh", "el", "wr", "hf"], [46, 38, 23, 19], 2.5, 0.0),
                              ("ff", ["f_sh", "f_el", "f_wr", "f_hf"], [40, 31, 20, 16], 1, 0.3),
                              ("nh", ["hip", "st", "ho", "hh"], [54, 37, 23, 19], 2.5, 0.0),
                              ("fh", ["f_hip", "f_st", "f_ho", "f_hh"], [44, 30, 19, 16], 1, 0.3)):
    pts = [J[k] for k in ch]
    legs.append(mk(name, limb(pts, wd, knuckles=[(2, wd[2] * 0.6)]) + hoof(pts[-1], (-0.6, 1), wd[3]), 4, z=z,
                   tone=tone, lw=1.6 if tone == 0 else 1.3))
tail = mk("tail", [tube([(474, 300), (490, 326), (488, 350)], [8, 6, 5])], 2, z=2, fur=[((470, 330, 500, 360), (0, 1), 1.2)])
parts = [ground_shadow(170, 500, 474, 9)] + legs + [tail, body]


def lock(pen, base, length, lean=(-0.25, 1.0)):
    """A caked lock hanging off the coat: four or five hairs stuck together, drawn in to one point."""
    tip = A(*base) + np.asarray(lean) * length + pen.rng.normal(0, 1.2, 2)
    for dx in np.linspace(-5, 5, int(pen.rng.integers(4, 6))):
        q = A(*base) + (dx, pen.rng.normal(0, 1.5))
        pen.stroke(np.array([q, (q + tip) / 2 + (dx * 0.25, 0), tip]), 0.9, taper=(0.3, 0.9), wobble=0.3)


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
    ink_figure(pen, parts, SEED, hatch_t=0.5, form_parts=("body",), part_t={"body": 0.26},
               cross={"body": (0.62, 60), "nf": (0.8, 30), "nh": (0.8, 30), "ff": (0.9, 20), "fh": (0.9, 20)})
    ear(pen, (172, 302), (192, 308), (190, 266), w=1.4)               # ear rising out of the skull
    crest = [A(176 + 264 * t, 244 - 44 * np.sin((t + 0.15) * np.pi * 0.8) + 34 * t) for t in np.linspace(0, 1, 50)]
    tufts(pen, crest, (0.35, -1.0), length=(9, 19), w=0.8)
    for x in np.linspace(196, 410, 14):                               # locks along the belly, caked together
        y = 420 - 14 * (x - 196) / 214 + pen.rng.normal(0, 2)
        lock(pen, (x + pen.rng.normal(0, 3), y), pen.rng.uniform(10, 18))
    for (x, y), lean in (((232, 330), (-0.2, 1)), ((182, 360), (-0.3, 1)), ((420, 330), (0.1, 1))):  # under jaw, chest, ham
        lock(pen, (x, y), pen.rng.uniform(9, 13), lean)
    pen.ellipse((74, 362), 7, 15, rot=-20, w=0.9, turns=1.05, wobble=0.3)
    pen.fill(catmull([(72, 356), (75, 355), (75, 360), (72, 360)], True, 4))
    pen.fill(catmull([(74, 367), (77, 366), (77, 371), (74, 371)], True, 4))
    pen.line([(132, 320), (142, 314), (154, 318)], w=0.9)              # brow
    pen.fill(catmull([(140, 320), (145, 319), (145, 323), (140, 323)], True, 4))
    for base, tip in (((100, 368), (88, 334)), ((114, 366), (108, 344))):
        pen.line([base, (base[0] - 9, (base[1] + tip[1]) / 2 + 3), tip], w=2.0, wobble=0.2, passes=2, spread=0.4)
    for k in ("hf", "f_hf", "hh", "f_hh"):
        q = J[k] + (-4, 10)
        pen.stroke(np.array([q, q + (-2, 8)]), 0.8, taper=(0.1, 0.3))


def s_lock(pen):
    """One lock pulled off a carcass, close: free hairs at the root, stuck into a lump, a few split ends below."""
    for k in range(9):                                                # the hairs, free at the root
        x = 30 + k * 5 + pen.rng.normal(0, 1)
        pen.line([(x, 14), (x + (50 - x) * 0.3, 44), (50 + (x - 50) * 0.15, 62)], w=0.8, wobble=0.4)
    lump = [(34, 58), (50, 52), (66, 60), (70, 80), (62, 98), (52, 104), (40, 98), (32, 80), (34, 58)]
    pen.line(lump, w=1.4, wobble=0.5, passes=2, spread=0.8)
    for k in range(26):                                               # the lump: hairs showing through the cake
        x0, y0 = 38 + pen.rng.uniform(0, 26), 60 + pen.rng.uniform(0, 34)
        pen.stroke(np.array([(x0, y0), (x0 + pen.rng.normal(0, 1.5), y0 + pen.rng.uniform(4, 9))]), 0.6,
                   taper=(0.2, 0.5), wobble=0.3)
    pen.line([(40, 92), (48, 100), (60, 96), (66, 82)], w=1.0, wobble=0.4)   # its shaded underside
    for dx in (-8, -2, 4, 10):                                        # split ends below it
        pen.line([(50 + dx * 0.6, 102), (50 + dx, 120), (50 + dx * 1.4, 132)], w=0.8, wobble=0.4)


def s_print(pen):
    """A cloven print, the two dewclaws behind it."""
    for side in (-1, 1):
        pen.line([(500 + side * 4, 508), (500 + side * 18, 528), (500 + side * 15, 560), (500 + side * 4, 566)],
                 w=1.3, passes=2, spread=0.6)
    for x in (480, 520):
        hand_ellipse(pen, (x, 578), 4, 3, 0, w=0.9, passes=1)


def first_try(pen):
    hand_ellipse(pen, (74, 72), 50, 30, 0, w=0.9, passes=2)
    hand_ellipse(pen, (24, 64), 14, 13, 0, w=0.8, passes=1)
    for x in (44, 56, 92, 104):
        pen.line([(x, 98), (x, 116)], w=0.8)
    pen.line([(124, 66), (134, 58), (130, 52), (126, 60)], w=0.7)


L.page(pen, {"lock": (s_lock, (14, 10, 86, 136)), "print": (s_print, (474, 504, 526, 584))},
       crossed_draw=(first_try, (8, 38, 140, 120)))
save(pen, os.environ.get("OUT", "entry_ash_boar"))
