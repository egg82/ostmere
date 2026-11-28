"""Journal entry `hush_moth`: a big moth seen from above, wings open, settled. Run:
bash render.sh entry_hush_moth -> entry_hush_moth_ink.png

Measured off a large silk moth seen from above (the shape of a polyphemus or emperor moth), body length B from head
to abdomen's tip: wingspan ~3.6 B, forewing from base to apex ~1.6 B with its leading edge nearly straight and the
outer margin bowed, the hindwing round and ~0.75 of the forewing's length, thorax ~0.3 B and furred, abdomen ~0.6 B
tapering, antennae ~0.45 B and feathered (a comb along each side of the shaft). One cross-line runs through both
wings, a small mark in the middle of each forewing, and the margins carry a fringe. The left and right halves are
mirrored and then set a degree or two apart, so the page is not a pinned plate.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 17))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", 41)), "entry_hush_moth", text_scale=1.3)
A = lambda *p: np.array(p, float)

CX = 300
B = 150
HEAD = A(CX, 236)
THORAX = (A(CX, 266), 17, 26, 0)
ABDOMEN = [(CX, 290), (CX, 330), (CX, 362), (CX + 1, 384)]
FORE = [(292, 252), (250, 230), (190, 212), (126, 200), (90, 206), (84, 228), (96, 262), (122, 296), (160, 318),
        (214, 316), (266, 300), (292, 278)]
HIND = [(294, 286), (250, 296), (196, 318), (158, 350), (150, 392), (172, 424), (214, 432), (254, 410), (282, 368),
        (294, 320)]
CROSS = [(152, 210), (160, 246), (180, 282), (206, 306)]
"""The forewing's cross-line, outer side, run on into the hindwing as HIND_CROSS."""
HIND_CROSS = [(238, 316), (216, 346), (208, 382), (222, 410)]
TURN = {-1: np.radians(-1.5), 1: np.radians(2.0)}


def side(pts, s):
    """A left-side point list turned into side s (-1 left, +1 right), rotated a little about the thorax."""
    P = np.asarray(pts, float)
    if s == 1:
        P = np.column_stack([2 * CX - P[:, 0], P[:, 1]])
    c, a = THORAX[0], TURN[s]
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return (P - c) @ R.T + c


def band(margin, depth):
    """The dark band along a wing's outer margin: the margin, and the same line pulled toward the wing base."""
    M = np.asarray(margin, float)
    inner = M + (THORAX[0] - M) * depth
    return np.vstack([M, inner[::-1]])


def flat(part, flatness):
    part.flat = flatness
    return part


parts = []
for s in (-1, 1):
    parts.append(flat(mk(f"hind{s}", [catmull(side(HIND, s), True, 10)], 2, z=1, tone=-0.05, lw=1.6,
                         hatch_angle=60 * s, hatch_spacing=4.2), 0.85))
    parts.append(flat(mk(f"fore{s}", [catmull(side(FORE, s), True, 10)], 2, z=2, tone=-0.1, lw=1.7,
                         hatch_angle=40 * s, hatch_spacing=4.4), 0.85))
    parts.append(flat(mk(f"hband{s}", [side(band(HIND[2:8], 0.16), s)], 1, z=1.5, tone=0.75, lw=0.01,
                         hatch_angle=70 * s, hatch_spacing=3.6), 1.0))
    parts.append(flat(mk(f"fband{s}", [side(band(FORE[3:9], 0.13), s)], 1, z=2.5, tone=0.75, lw=0.01,
                         hatch_angle=50 * s, hatch_spacing=3.6), 1.0))
body = mk("body", [ell_poly(THORAX[0], 21, 28, 0), tube(ABDOMEN, [38, 34, 24, 10]), ell_poly(HEAD, 13, 11)], 5, z=3,
          tone=0.45, fur=[((270, 236, 330, 300), (0.0, -1.0), 1.6), ((268, 296, 332, 390), (1.0, 0.3), 1.2)])
parts.append(body)


def inside(q, poly):
    """Ray-cast point-in-polygon."""
    x, y, n, hit = q[0], q[1], len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def antenna(pen, s):
    """A feathered antenna: the shaft curving out, short comb teeth along both sides, longest near the middle."""
    shaft = side([(296, 228), (284, 208), (268, 190), (250, 178)], s)
    c = catmull(shaft, False, 8)
    pen.line(c, w=1.0, wobble=0.2)
    nr = normals(c)
    for i in range(2, len(c) - 1, 2):
        u = i / (len(c) - 1)
        ln = 3 + 7 * np.sin(np.pi * u)
        for k in (-1, 1):
            q = c[i]
            pen.stroke(np.array([q, q + nr[i] * k * ln + (c[i] - c[i - 1]) * 0.8]), 0.5, taper=(0.1, 0.5), wobble=0.1)


with L.figure(pen, (300, 316)):
    with pen.construction():
        pen.line([(CX, 200), (CX, 400)], w=0.45, wobble=0.6, overshoot=8)       # the body's axis
        pen.line(side([(80, 214), (300, 230)], -1).tolist() + side([(300, 230), (80, 214)], 1).tolist(),
                 w=0.4, wobble=0.6)                                            # the leading edges' line
        hand_ellipse(pen, *THORAX)
        for s in (-1, 1):
            hand_ellipse(pen, side([(206, 362)], s)[0], 64, 58, 0)
            hand_ellipse(pen, side([(176, 262)], s)[0], 106, 50, -12 * s)
    ink_figure(pen, parts, SEED, hatch_t=0.62, part_t={"body": 0.3})
    for s in (-1, 1):
        pen.line(catmull(side(CROSS, s), False, 8), w=1.1, wobble=0.5, passes=2, spread=0.8)   # the cross-line
        pen.line(catmull(side(HIND_CROSS, s), False, 8), w=1.1, wobble=0.5, passes=2, spread=0.8)
        for a, b in (((290, 258), (110, 210)), ((288, 266), (104, 246)), ((286, 274), (132, 296)),
                     ((290, 298), (166, 360)), ((292, 312), (196, 420))):     # veins, faint, from the wing base
            pen.line(catmull(side([a, (np.add(a, b) / 2) + (0, -4), b], s), False, 6), w=0.45, wobble=0.4)
        m = side([(198, 260)], s)[0]                                           # the small mark mid-wing
        hand_ellipse(pen, m, 7, 5, 10 * s, w=0.9, passes=1)
        for P, n in ((FORE[3:9], 30), (HIND[2:8], 26)):                        # the fringe along the margins
            c = catmull(side(P, s), False, 6)
            idx = np.linspace(0, len(c) - 2, n).astype(int)
            nr = normals(c)
            out = np.sign(np.dot(nr[len(nr) // 2], c[len(c) // 2] - THORAX[0]))
            for i in idx:
                pen.stroke(np.array([c[i], c[i] + nr[i] * out * pen.rng.uniform(2.5, 4.5)]), 0.5,
                           taper=(0.1, 0.5), wobble=0.1)
        antenna(pen, s)
    wings = [side(P, s) for P in (FORE, HIND) for s in (-1, 1)]
    for k in range(110):                                                       # the dust, on the wings only
        q = A(pen.rng.uniform(90, 510), pen.rng.uniform(200, 430))
        if any(inside(q, w) for w in wings):
            pen.fill(ell_poly(q, 0.7, 0.6, 0, n=6))
    for t in np.linspace(0, 2 * np.pi, 46, endpoint=False):                   # the fur standing off the thorax
        q = THORAX[0] + (21 * np.cos(t), 28 * np.sin(t))
        f = np.array([np.cos(t), np.sin(t) * 0.8]) + pen.rng.normal(0, 0.15, 2)
        pen.stroke(np.array([q - f * 3, q + f * pen.rng.uniform(4, 8)]), 0.6, taper=(0.1, 0.7), wobble=0.3)
    for y in np.linspace(300, 376, 20):                                        # and off the abdomen's sides
        hw = np.interp(y, [290, 330, 362, 384], [19, 17, 12, 5])
        for k in (-1, 1):
            q = A(CX + k * hw, y)
            pen.stroke(np.array([q - (k * 2, 0), q + (k * pen.rng.uniform(3, 6), pen.rng.uniform(1, 3))]), 0.55,
                       taper=(0.1, 0.7), wobble=0.3)
    for y in (316, 334, 350, 364):                                             # its segments, faint
        hw = np.interp(y, [290, 330, 362, 384], [19, 17, 12, 5])
        pen.line([(CX - hw * 0.8, y - 1), (CX, y + 2), (CX + hw * 0.8, y - 1)], w=0.5, wobble=0.3)
    pen.fill(ell_poly(HEAD + (-5, -4), 2.2, 2.0, 0, n=8))                      # the eyes
    pen.fill(ell_poly(HEAD + (5, -4), 2.2, 2.0, 0, n=8))


def s_antenna(pen):
    """One antenna, close: the shaft and its two combs, each tooth a fine hair."""
    shaft = catmull(np.array([(20, 130), (34, 96), (50, 64), (70, 34)], float), False, 10)
    pen.line(shaft, w=1.2, wobble=0.2)
    nr = normals(shaft)
    for i in range(1, len(shaft) - 1):
        u = i / (len(shaft) - 1)
        ln = 6 + 16 * np.sin(np.pi * u)
        for k in (-1, 1):
            pen.stroke(np.array([shaft[i], shaft[i] + nr[i] * k * ln + (shaft[i] - shaft[i - 1]) * 1.2]), 0.6,
                       taper=(0.1, 0.5), wobble=0.15)


def s_scales(pen):
    """Wing scales under a glass: rows of small rounded tiles laid over each other like a roof."""
    for r in range(5):
        for c in range(6 - (r % 2)):
            x, y = 500 + c * 14 + (r % 2) * 7, 470 + r * 12
            pen.line([(x - 6, y - 4), (x - 6, y + 4), (x - 3, y + 8), (x + 3, y + 8), (x + 6, y + 4), (x + 6, y - 4)],
                     w=0.8, wobble=0.25)
    hand_ellipse(pen, (540, 500), 52, 44, 0, w=1.0, passes=2)


def first_try(pen):
    pen.line([(20, 60), (60, 40), (90, 64), (60, 86), (20, 60)], w=0.9)
    pen.line([(150, 60), (110, 40), (90, 64), (110, 86), (150, 60)], w=0.9)
    pen.line([(90, 40), (90, 100)], w=1.2)


L.page(pen, {"antenna": (s_antenna, (8, 24, 92, 140)), "scales": (s_scales, (486, 454, 594, 546))},
       crossed_draw=(first_try, (12, 32, 160, 108)))
save(pen, os.environ.get("OUT", "entry_hush_moth"))
