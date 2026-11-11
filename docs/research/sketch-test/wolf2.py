"""Wolf, construction-drawing version (Loomis/Hampton): gesture -> masses -> contour over them -> noise.
Page furniture (studies, labels) is reused verbatim from wolf.py. Run -> wolf2.svg"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from sketch import SketchPen, SketchScene, Part, catmull, resample, normals
import ink

SEED = int(os.environ.get("SEED", 7))
S = ink.S
W = ink.W


class FaintPen(SketchPen):
    """Construction marks go to a faint layer rendered at reduced opacity."""
    def __init__(self, seed):
        super().__init__(seed)
        self.faint = []

    def svg(self, path, size=600):
        n = super().svg(path, size)
        txt = open(path).read().replace("</g></svg>", "</g>")
        out = [f'<g fill="{ink.INK}" fill-opacity="0.42" stroke="none">']
        for P in self.faint:
            out.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in P) + 'Z"/>')
        out.append("</g></svg>")
        open(path, "w").write(txt + "\n".join(out))
        return n + len(self.faint)


pen = FaintPen(SEED)

# ---------------- 1. gesture + skeleton (canvas coords) ---------------------------------------
# proportions off the Gessner hound: body length ~1.15 x withers height; wolf chest ~50% of height.
GROUND = 500
WITHERS = np.array([228, 272])
H = GROUND - WITHERS[1]                       # withers height 228
J = dict(  # joints
    occ=(150, 332), nose=(58, 384),
    shoulder=(206, 338), elbow=(224, 388), wrist=(224, 452), fpaw=(210, 491), ftoe=(190, 498),
    f_shoulder=(222, 336), f_elbow=(250, 390), f_wrist=(258, 450), f_paw=(250, 488), f_toe=(232, 494),
    hip=(446, 304), stifle=(418, 382), hock=(470, 440), hpaw=(464, 494), htoe=(446, 499),
    f_hip=(452, 300), f_stifle=(440, 378), f_hock=(492, 432), f_hpaw=(490, 490), f_htoe=(474, 494),
)
J = {k: np.array(v, float) for k, v in J.items()}
RIB = dict(c=(262, 334), rx=64, ry=64, rot=-8)      # ribcage egg
PEL = dict(c=(444, 298), rx=36, ry=32, rot=10)      # pelvis
CRAN = dict(c=(128, 344), rx=27, ry=24, rot=-20)    # cranium
GESTURE = [J["nose"] + (8, -14), J["occ"], WITHERS + (6, -2), (340, 282), (445, 276), (482, 296), (500, 360),
           (494, 412)]


def ell_poly(c, rx, ry, rot, n=72):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    a = np.radians(rot)
    x, y = rx * np.cos(t), ry * np.sin(t)
    return np.column_stack([c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a)])


def tube(pts, widths, step=2.0):
    c = resample(np.asarray(pts, float), step)
    w = np.interp(np.linspace(0, 1, len(c)), np.linspace(0, 1, len(widths)), widths)
    nr = normals(c)
    return np.vstack([c + nr * w[:, None] / 2, (c - nr * w[:, None] / 2)[::-1]])


def to_mask(polys):
    im = Image.new("L", (W * S, W * S), 0)
    d = ImageDraw.Draw(im)
    for P in polys:
        d.polygon([(x * S, y * S) for x, y in P], fill=255)
    return np.array(im) > 127


def disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def contour_from(mask, close_r, smooth=2.0, step=5.0):
    """Contour drawn OVER the masses: closing makes the tangent bridges (back line, belly tuck)."""
    m = ndimage.binary_closing(np.pad(mask, 60), structure=disk(int(close_r * S)))[60:-60, 60:-60]
    m = ndimage.gaussian_filter(m.astype(float), smooth * S) > 0.5
    lab, n = ndimage.label(m)
    m = lab == (1 + np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
    ys, xs = np.nonzero(m)
    i = np.argmin(ys * 100000 + xs)
    start = (ys[i], xs[i])
    nb = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    pts, cur, d = [start], start, 6
    for _ in range(400000):
        for k in range(8):
            dd = (d + k) % 8
            y, x = cur[0] + nb[dd][0], cur[1] + nb[dd][1]
            if m[y, x]:
                cur, d = (y, x), (dd + 5) % 8
                break
        if cur == start:
            break
        pts.append(cur)
    P = np.array([(x / S, y / S) for y, x in pts])
    return resample(P, step)[:-1]


def leg(a, b, c, d, e, wa, wb, wc, wd):
    return [tube([a, b], [wa, wb]), tube([b, c], [wb, wc]), tube([c, d], [wc, wd]), tube([d, e], [wd, wd * 0.8])]


# ---------------- 2. masses -> part silhouettes ----------------------------------------------
trunk_polys = [ell_poly(**RIB), ell_poly(**PEL),
               tube([WITHERS + (34, 32), (190, 306), J["occ"] + (8, 8)], [70, 66, 44]),   # neck + ruff mass
               tube([WITHERS + (4, 28), J["shoulder"], J["elbow"] + (2, -8)], [44, 38, 26]),  # shoulder + upper arm (merged)
               tube([(290, 320), (360, 304), (432, 294)], [116, 64, 62])]                 # loin: back line + tuck
head_polys = [ell_poly(**CRAN), tube([(118, 346), (86, 364), J["nose"] + (4, 0)], [34, 24, 15]),
              tube([(126, 362), (90, 378), (66, 390)], [14, 10, 7])]                       # lower jaw
nf_polys = [tube([J["elbow"] + (1, -14), J["elbow"]], [26, 25]), tube([J["elbow"], J["wrist"]], [25, 13]),
            tube([J["wrist"], J["fpaw"]], [14, 13])] + \
    [tube([J["fpaw"] + (9, 1), J["ftoe"]], [15, 11])]
ff_polys = leg(J["f_shoulder"] + (0, -6), J["f_shoulder"], J["f_elbow"], J["f_wrist"], J["f_paw"], 26, 24, 14, 10) + \
    [tube([J["f_paw"] + (6, 0), J["f_toe"]], [10, 8])]
nh_polys = [ell_poly((440, 334), 34, 46, 20), tube([J["hip"], J["stifle"]], [40, 26]), tube([J["stifle"], J["hock"]], [26, 15]),
            tube([J["hock"], J["hpaw"]], [15, 12]), tube([J["hpaw"] + (8, 0), J["htoe"]], [12, 9])]
fh_polys = [tube([J["f_hip"], J["f_stifle"]], [40, 24]), tube([J["f_stifle"], J["f_hock"]], [22, 13]),
            tube([J["f_hock"], J["f_hpaw"]], [13, 10]), tube([J["f_hpaw"] + (6, 0), J["f_htoe"]], [10, 8])]
tail_polys = [tube([(470, 284), (490, 312), (502, 352), (504, 386), (494, 420)], [12, 22, 30, 24, 6])]


def fur_where(pts, box, flow, st):
    """Index ranges of contour points inside box -> fur spec."""
    x0, y0, x1, y1 = box
    inside = (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1)
    out, i, n = [], 0, len(pts)
    while i < n:
        if inside[i]:
            j = i
            while j < n and inside[j]:
                j += 1
            out.append((i, j, flow, st))
            i = j
        else:
            i += 1
    return out


def mk(name, polys, close_r, z, tone=0.0, lw=1.8, fur=()):
    c = contour_from(to_mask(polys), close_r)
    f = []
    for box, flow, st in fur:
        f += fur_where(c, box, flow, st)
    return Part(name, c, z=z, tone=tone, lw=lw, n=2, fur=f)


trunk = mk("trunk", trunk_polys, 22, z=3, fur=[((160, 330, 250, 400), (0.3, 1.0), 1.3),     # ruff underside
                                               ((150, 260, 240, 320), (0.9, -0.2), 0.9),     # scruff
                                               ((300, 360, 420, 400), (-0.1, 1.0), 0.8)])    # belly
head = mk("head", head_polys, 6, z=6, lw=1.9, fur=[((120, 355, 160, 385), (0.8, 0.6), 0.9),
                                                   ((138, 318, 175, 356), (0.9, 0.2), 1.1)])  # ruff over skull back
near_fore = mk("near_fore", nf_polys, 4, z=2.5, fur=[((222, 380, 245, 430), (0.4, 1.0), 0.6)])
far_fore = mk("far_fore", ff_polys, 4, z=1, tone=0.3, lw=1.3)
near_hind = mk("near_hind", nh_polys, 5, z=4, tone=-0.12, fur=[((440, 300, 480, 380), (0.4, 1.0), 0.8)])
far_hind = mk("far_hind", fh_polys, 4, z=1, tone=0.3, lw=1.3)
tail = mk("tail", tail_polys, 4, z=2, fur=[((470, 280, 520, 420), (0.1, 1.0), 1.1)])
ear_far = Part("ear_far", [(110, 330), (114, 298), (126, 324)], z=5.5, n=6, tone=0.25)
ear_near = Part("ear_near", [(130, 326), (150, 292), (152, 334)], z=7, n=6)
shadow = Part("shadow", [(160, 496), (300, 490), (440, 490), (520, 496), (500, 510), (330, 514), (180, 510)],
              z=0, tone=0.75, flat=1.0)
parts = [shadow, far_fore, far_hind, tail, trunk, near_hind, near_fore, head, ear_far, ear_near]

# ---------------- 3. construction layer (faint, drawn first, left visible) ---------------------
k0 = len(pen.polys)
pen.line(GESTURE, w=0.5, wobble=1.0, overshoot=10)
pen.line([(130, GROUND + 2), (560, GROUND - 4)], w=0.45, wobble=0.6)                   # ground plane
for e in (RIB, PEL, CRAN):
    pen.ellipse(e["c"], e["rx"], e["ry"], rot=e["rot"], w=0.5, turns=1.1, wobble=0.8)
# head box + muzzle wedge
pen.line([(104, 330), (148, 318), (156, 356), (112, 368), (104, 330)], w=0.4, wobble=0.5)
pen.line([(112, 336), J["nose"] + (0, -6), J["nose"] + (4, 8), (112, 368)], w=0.4, wobble=0.5)
# bones as lines, joints as small points
for chain in (["shoulder", "elbow", "wrist", "fpaw", "ftoe"], ["f_shoulder", "f_elbow", "f_wrist", "f_paw", "f_toe"],
              ["hip", "stifle", "hock", "hpaw", "htoe"], ["f_hip", "f_stifle", "f_hock", "f_hpaw", "f_htoe"]):
    pen.line([J[k] for k in chain], w=0.45, wobble=0.3)
    for k in chain[:-1]:
        pen.ellipse(J[k], 2.6, 2.6, w=0.45, turns=1.0, wobble=0.1)
pen.line([WITHERS + (6, 0), J["shoulder"]], w=0.5, wobble=0.4)                        # scapula
pen.line([(420, 284), J["hip"], (472, 322)], w=0.5, wobble=0.4)                        # ilium-ischium
pen.faint = pen.polys[k0:]
del pen.polys[k0:]

# ---------------- 4. contour over the masses, then hatching that follows the form --------------
sc = SketchScene(parts, pen, seed=SEED)
for p in parts:
    if p.name == "shadow":
        sc.quick_hatch(p, t=0.3, angle=-20, spacing=3.0, attn=0.0, w=0.45)
    else:
        sc.quick_hatch(p, t=0.62 if p.tone < 0.2 else 0.5, spacing=3.2, w=0.6)
for p in parts:
    if p.name in ("trunk", "tail", "head"):
        sc.hatch_form(p, t1=0.52, maxlen=16, w=0.6)
for p in parts:
    if p.name != "shadow":
        sc.search_contour(p, w=1.9, passes=(0.35, 0.5, 1.0))

# face + anatomy accents
eye = [(104, 338), (112, 333), (121, 336), (113, 341)]
pen.line(eye + [eye[0]], w=1.0, wobble=0.2)
pen.fill(catmull([(110, 336), (114, 336), (113, 339), (110, 339)], True, 5))
pen.line([(102, 341), (94, 354)], w=0.5)                                                # tear line
pen.fill(catmull([(53, 378), (62, 375), (66, 384), (59, 390), (52, 386)], True, 6))     # nose
pen.line([(64, 392), (90, 386), (118, 376)], w=1.0)                                    # mouth
pen.line([(98, 330), (110, 325), (124, 328)], w=0.8)                                   # brow
pen.line([(140, 322), (147, 304)], w=0.6)                                              # inner ear
for i in range(4):                                                                     # ribs, hinted
    x = 268 + i * 16
    pen.line([(x, 300), (x + 6, 330), (x + 3, 360)], w=0.45, wobble=0.6)
for i in range(14):                                                                    # ruff tufts
    t = i / 13
    q = np.array([176 + 46 * t, 318 + 52 * t * t + 10 * t])
    f = np.array([0.5, 0.86]) + pen.rng.normal(0, 0.12, 2)
    pen.stroke(np.array([q, q + f * pen.rng.uniform(6, 11)]), 0.7, taper=(0.1, 0.7), wobble=0.3)

# ---------------- page furniture, verbatim from wolf.py (arrow targets moved to this figure) ---
src = open(os.path.join(HERE, "wolf.py")).read()
furn = src[src.index("# ---------------- side studies"):src.index("n = pen.svg(")]
for old, new in [("pen.arrow((228, 134), (215, 225), bend=-18)", "pen.arrow((228, 134), (200, 292), bend=-18)"),
                 ("pen.arrow((52, 405), (80, 315), bend=8)", "pen.arrow((52, 405), (60, 396), bend=8)"),
                 ("pen.arrow((470, 556), (515, 400), bend=-15)", "pen.arrow((470, 556), (500, 418), bend=-15)")]:
    assert furn.count(old) == 1, old
    furn = furn.replace(old, new)
exec(furn)

n = pen.svg(os.path.join(HERE, "wolf2.svg"))
print("elements", n)
