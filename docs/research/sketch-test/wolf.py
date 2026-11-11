"""Wolf field-sketch page. Run: python3 wolf.py -> wolf.svg"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from sketch import SketchPen, SketchScene, Part, catmull

SEED = int(os.environ.get("SEED", 7))
pen = SketchPen(SEED)

SC, OX, OY = 0.55, 85, -17  # main figure transform


def T(pts):
    return [(x * SC + OX, y * SC + OY) for x, y in pts]


# ---------------- main wolf ---------------------------------------------------------------
# Silhouette in the hound woodcut's crop coordinates (ref 011.jpg cropped at 330,1500).
# Points flagged 1 were read off the hound and get snapped to the nearest real ink pixel;
# flagged 0 are the wolf changes (lowered head, ruff, softer tuck, bushy tail).
from PIL import Image
from scipy import ndimage
REF = os.environ.get("WOLF_REF", "011.jpg")  # an engraving scan, not in the repo
_im = np.asarray(Image.open(REF).convert("L").crop((330, 1500, 1480, 2600)), float)
INKREF = _im < ndimage.gaussian_filter(_im, 40) - 45
_iy, _ix = np.nonzero(INKREF)
_ink_pts = np.column_stack([_ix, _iy]).astype(float)


def snap(pts, flags, r=14):
    out = []
    for (x, y), f in zip(pts, flags):
        if f:
            d = np.hypot(_ink_pts[:, 0] - x, _ink_pts[:, 1] - y)
            i = np.argmin(d)
            if d[i] < r:
                x, y = _ink_pts[i]
        out.append((x, y))
    return out


def TC(pts, flags=None):
    if flags is not None:
        pts = snap(pts, flags)
    return [(x * SC + OX, y * SC + OY) for x, y in pts]


SIL = [((-30, 540), 0), ((-15, 525), 0), ((25, 500), 0), ((75, 468), 0), ((135, 440), 0), ((190, 430), 0),
       ((225, 395), 0), ((270, 365), 0), ((315, 352), 1), ((360, 378), 1), ((420, 372), 1), ((480, 368), 1),
       ((540, 362), 1), ((600, 362), 1), ((650, 368), 1), ((685, 388), 1), ((705, 420), 1), ((712, 470), 1),
       ((690, 540), 1), ((650, 600), 1), ((615, 680), 1), ((590, 740), 1), ((572, 800), 1), ((556, 860), 1),
       ((544, 890), 1), ((528, 905), 1), ((468, 905), 1), ((455, 892), 1), ((475, 866), 1), ((498, 825), 1),
       ((520, 770), 1), ((540, 700), 1), ((538, 640), 1), ((525, 560), 1), ((522, 495), 0), ((470, 535), 0),
       ((400, 575), 0), ((330, 592), 0), ((262, 598), 1), ((205, 625), 0), ((172, 662), 1), ((156, 730), 1),
       ((150, 800), 1), ((150, 860), 1), ((155, 900), 1), ((150, 920), 1), ((98, 918), 1), ((100, 905), 1),
       ((112, 890), 1), ((118, 860), 1), ((112, 800), 1), ((105, 720), 1), ((95, 650), 1), ((96, 615), 0),
       ((112, 590), 0), ((122, 572), 0), ((124, 548), 0), ((85, 558), 0), ((45, 564), 0), ((5, 560), 0),
       ((-25, 556), 0)]
silp = TC([p for p, f in SIL], [f for p, f in SIL])
shadow = Part("shadow", TC([(60, 905), (300, 895), (560, 892), (780, 900), (740, 935), (400, 942), (90, 935)]),
              z=0, tone=0.75, flat=1.0)
far_hind = Part("far_hind", TC([(650, 600), (700, 620), (740, 700), (745, 760), (725, 830), (715, 880), (725, 905),
                                (660, 908), (668, 880), (690, 820), (695, 760), (670, 700), (640, 650)], [1] * 13),
                z=1, tone=0.3, lw=1.2)
far_fore = Part("far_fore", TC([(240, 600), (275, 600), (265, 660), (245, 730), (228, 800), (220, 870), (226, 905),
                                (222, 916), (168, 916), (172, 902), (185, 875), (188, 800), (195, 720), (210, 650)],
                               [1] * 14), z=2, tone=0.3, lw=1.2)
body = Part("body", silp, z=5, lw=1.8, n=6,
            fur=[(5, 8.5, (1.0, -0.1), 1.0), (53, 58, (0.25, 1.0), 1.4), (34, 38.5, (-0.1, 1.0), 0.9),
                 (17, 19.5, (0.3, 1.0), 0.9), (38.5, 40.5, (0.4, 1.0), 0.6)])
tail = Part("tail", TC([(690, 400), (716, 408), (746, 458), (772, 530), (792, 600), (796, 664), (780, 716),
                        (768, 692), (758, 630), (740, 560), (714, 490), (696, 446)]), z=6, tone=0.05,
            fur=[(1, 11, (0.1, 1.0), 1.2)])
ear_far = Part("ear_far", TC([(140, 448), (150, 405), (160, 442)]), z=4, n=6, tone=0.25)
ear_near = Part("ear_near", TC([(176, 440), (214, 398), (208, 448)]), z=9, n=6)

parts = [shadow, far_hind, far_fore, body, tail, ear_far, ear_near]
sc = SketchScene(parts, pen, seed=SEED)

for p in parts:
    if p.name == "shadow":
        sc.quick_hatch(p, t=0.3, angle=-20, spacing=3.0, attn=0.0, w=0.45)
    else:
        sc.quick_hatch(p, t=0.5 if p.tone < 0.2 else 0.42, spacing=3.0, w=0.7)
for p in parts:
    if p.name in ("body", "tail"):
        sc.hatch_form(p, t1=0.6, maxlen=14, w=0.55)
for p in parts:
    if p.name != "shadow":
        sc.search_contour(p, w=2.0, passes=(0.4, 0.55, 1.0))

# face + internal anatomy (crop coords)
eye = TC([(40, 496), (54, 488), (68, 492), (54, 499)])
pen.line(eye + [eye[0]], w=1.0, wobble=0.2)
pen.fill(catmull(TC([(51, 491), (58, 491), (57, 496), (51, 496)]), True, 5))
pen.line(TC([(38, 498), (24, 518)]), w=0.5)  # tear line
pen.fill(catmull(TC([(-40, 533), (-26, 530), (-22, 544), (-32, 552), (-42, 544)]), True, 6))  # nose
pen.line(TC([(-24, 556), (10, 558), (60, 548)]), w=1.0)  # mouth
pen.line(TC([(30, 486), (52, 476), (76, 480)]), w=0.8)  # brow ridge
pen.line(TC([(176, 438), (188, 412), (192, 402)]), w=0.6)  # inner ear
pen.line(TC(*zip(*[((330, 365), 1), ((300, 440), 1), ((262, 530), 1)])), w=0.7, wobble=0.8)  # shoulder (hound's)
pen.line(TC(*zip(*[((640, 400), 1), ((600, 470), 1), ((560, 540), 1)])), w=0.7, wobble=0.8)  # thigh (hound's)
for i in range(4):  # ribs, hinted
    x = 330 + i * 32
    pen.line(TC([(x, 420), (x + 10, 470), (x + 6, 520)]), w=0.45, wobble=0.6)
for i in range(16):  # ruff mane: tufts from behind the ear down to the chest
    t = i / 15
    q = np.array(TC([(215 + 70 * t, 420 + 120 * t * t + 30 * t)])[0])
    f = np.array([0.5, 0.86]) + pen.rng.normal(0, 0.12, 2)
    pen.stroke(np.array([q, q + f * pen.rng.uniform(6, 12)]), 0.7, taper=(0.1, 0.7), wobble=0.3)
pen.line(TC([(-20, 925), (200, 920), (330, 928)]), w=0.6, wobble=1.0)
pen.line(TC([(420, 918), (640, 915), (840, 922)]), w=0.6, wobble=1.0)

# ---------------- side studies -----------------------------------------------------------
# crossed-out first attempt (top-left): proportions wrong, head held high
fa_body = [(40, 70), (70, 64), (110, 66), (132, 74), (130, 92), (100, 96), (60, 96), (42, 90)]
pen.line(fa_body + [fa_body[0]], w=0.8, wobble=0.6, passes=2)
pen.line([(44, 72), (36, 52), (30, 40), (20, 42), (12, 50), (22, 56), (30, 60)], w=0.8, passes=2)  # head up
pen.line([(30, 40), (32, 30), (36, 41)], w=0.7)
for x in (50, 62, 112, 124):
    pen.line([(x, 94), (x + 1, 116), (x + 4, 120)], w=0.7, passes=2)
pen.line([(132, 76), (148, 88), (152, 104)], w=0.7)
pen.scribble_out((6, 22, 158, 128), w=1.0)
pen.write("no. too dog. head is LOW", 14, 146, size=17, rot=-4)

# eye study (top-right): almond, tilted, dark rims, tear streak, fur flow
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
pen.write("eyes held the lantern", 440, 128, size=16, rot=-3)
pen.write("light too long", 456, 144, size=16, rot=-3)

# paw study (bottom-right): fragment of fore paw, side view, toes arched
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
pen.write("fore paw", 528, 504, size=15, rot=2)
pen.write("print ~ my palm", 514, 552, size=15, rot=2)

# labels + arrows on the main figure
pen.write("ruff - thick, hides the neck", 190, 128, size=17, rot=-3)
pen.arrow((228, 134), (215, 225), bend=-18)
pen.write("head carried below", 10, 420, size=17, rot=-2)
pen.write("the shoulders. never", 10, 437, size=17, rot=-2)
pen.write("looked up at us", 10, 454, size=17, rot=-2)
pen.arrow((52, 405), (80, 315), bend=8)
pen.write("tail low - not afraid of us?", 340, 566, size=17, rot=-1)
pen.arrow((470, 556), (515, 400), bend=-15)
pen.write("Grey wolf, Ashen Marches - 3rd night", 120, 594, size=19, rot=-1, op=0.95)

n = pen.svg(os.path.join(HERE, "wolf.svg"))
print("elements", n)
