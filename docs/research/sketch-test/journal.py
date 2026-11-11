"""Field-journal construction drawing: the library each subject script uses.

Order of work (see process.md): gesture -> hand-drawn masses (faint) -> silhouettes built from masses
-> contour over them (closing = tangent bridges) -> partial hatching -> details -> page furniture.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from contextlib import contextmanager
from PIL import Image, ImageDraw
from scipy import ndimage
import ink
from ink import catmull, resample, normals
from sketch import SketchPen, SketchScene, Part

S, W = ink.S, ink.W


# ---------------------------------------------------------------- pen with a faint layer
class JournalPen(SketchPen):
    def __init__(self, seed):
        super().__init__(seed)
        self.faint = []

    @contextmanager
    def construction(self):
        """Everything drawn inside goes to the faint (42% opacity) construction layer."""
        k = len(self.polys)
        yield self
        self.faint += self.polys[k:]
        del self.polys[k:]

    def svg(self, path, size=600, height=None):
        n = super().svg(path, size, height)
        txt = open(path).read().replace("</g></svg>", "</g>")
        out = [f'<g fill="{ink.INK}" fill-opacity="0.42" stroke="none">']
        for P in self.faint:
            out.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in P) + 'Z"/>')
        out.append("</g></svg>")
        open(path, "w").write(txt + "\n".join(out))
        return n + len(self.faint)


# ---------------------------------------------------------------- hand-drawn construction marks
def hand_ellipse(pen, c, rx, ry, rot=0.0, w=0.5, passes=None):
    """An ellipse as a hurried hand draws it: flattened, tilted, egg-ish, not closed or overshooting,
    sometimes two quick passes that do not coincide."""
    r = pen.rng
    passes = passes or (2 if r.random() < 0.45 else 1)
    for k in range(passes):
        fl = r.uniform(0.86, 1.0)
        a = np.radians(rot + r.normal(0, 5))
        t0 = r.uniform(0, 2 * np.pi)
        sweep = 2 * np.pi * r.uniform(0.82, 1.12)
        n = int(50 * sweep / np.pi)
        t = t0 + np.linspace(0, sweep, n)
        egg = 1 + r.uniform(0.03, 0.09) * np.cos(t - r.uniform(0, 2 * np.pi))
        rr = egg * (1 + pen.noise(n, 14, 0.035))
        x, y = rx * rr * np.cos(t), ry * fl * rr * np.sin(t)
        cx, cy = c[0] + r.normal(0, 1.2), c[1] + r.normal(0, 1.2)
        P = np.column_stack([cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a)])
        pen.stroke(P, w * (1 if k == 0 else 0.8), taper=(0.12, 0.25), wobble=0.9, wvar=0.4)


def joint(pen, p, r=2.6, w=0.45):
    hand_ellipse(pen, p, r, r * 0.9, w=w, passes=1)


def bones(pen, pts, w=0.45):
    """Bone chain as quick separate strokes that overshoot each joint a little."""
    for a, b in zip(pts[:-1], pts[1:]):
        pen.line([a, b], w=w, wobble=0.4, overshoot=4)
    for q in pts[:-1]:
        joint(pen, q)


# ---------------------------------------------------------------- mass geometry -> silhouettes
def ell_poly(c, rx, ry, rot=0.0, n=72):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    a = np.radians(rot)
    x, y = rx * np.cos(t), ry * np.sin(t)
    return np.column_stack([c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a)])


def tube(pts, widths, step=2.0):
    c = resample(np.asarray(pts, float), step)
    w = np.interp(np.linspace(0, 1, len(c)), np.linspace(0, 1, len(widths)), widths)
    nr = normals(c)
    return np.vstack([c + nr * w[:, None] / 2, (c - nr * w[:, None] / 2)[::-1]])


def limb(chain, widths, knuckles=()):
    """Bone chain -> tube segments plus small knuckle masses at the named joint indices
    (wrist/hock/elbow bumps, so the contour does not run straight past a joint)."""
    polys = []
    for i, (a, b) in enumerate(zip(chain[:-1], chain[1:])):
        polys.append(tube([a, b], [widths[i], widths[i + 1]]))
    for i, rr in knuckles:
        polys.append(ell_poly(chain[i], rr, rr * 0.85))
    return polys


def paw(pastern_end, toe_dir, size):
    """Canine paw: a flattened oval mass tipped toward toe_dir, plus toe bumps along its front."""
    d = np.asarray(toe_dir, float); d /= np.linalg.norm(d)
    c = np.asarray(pastern_end, float) + d * size * 0.45
    rot = np.degrees(np.arctan2(d[1], d[0]))
    polys = [ell_poly(c, size * 0.95, size * 0.48, rot)]
    for k in (-1, 0, 1):
        polys.append(ell_poly(c + d * size * 0.65 + np.array([0, -1]) * k * size * 0.12 + np.array([0, 2]),
                              size * 0.32, size * 0.3))
    return polys


def paw_details(pen, pastern_end, toe_dir, size, w=0.7):
    d = np.asarray(toe_dir, float); d /= np.linalg.norm(d)
    c = np.asarray(pastern_end, float) + d * size * 0.45
    tip = c + d * size * 0.95
    for k in (-0.5, 0.5):  # toe splits
        a = tip + np.array([-d[0], -d[1]]) * size * 0.35 + np.array([0, -1]) * k * size * 0.25
        pen.stroke(np.array([a + (0, -size * 0.25), a + (0, size * 0.22)]), w, taper=(0.2, 0.4), wobble=0.2)
    for k in (-1, 0, 1):  # claws
        q = tip + np.array([0, size * 0.2 + k * size * 0.12])
        pen.stroke(np.array([q, q + d * size * 0.3 + (0, size * 0.12)]), w * 1.2, taper=(0.1, 0.8), wobble=0.1)


def hoof(pastern_end, toe_dir, size):
    d = np.asarray(toe_dir, float); d /= np.linalg.norm(d)
    a = np.asarray(pastern_end, float)
    return [tube([a, a + d * size + (0, size * 0.4)], [size * 0.8, size * 0.95])]


def to_mask(polys):
    im = Image.new("L", (W * S, W * S), 0)
    dr = ImageDraw.Draw(im)
    for P in polys:
        dr.polygon([(x * S, y * S) for x, y in P], fill=255)
    return np.array(im) > 127


def _disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def contour_from(mask, close_r, smooth=2.0, step=5.0):
    """Contour drawn OVER the masses: morphological closing makes the tangent bridges
    (back line, belly tuck) a draughtsman draws between masses."""
    pad = int(close_r * S) + 10
    m = ndimage.binary_closing(np.pad(mask, pad), structure=_disk(max(1, int(close_r * S))))[pad:-pad, pad:-pad]
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


def fur_where(pts, box, flow, st):
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


def mk(name, polys, close_r, z, tone=0.0, lw=1.8, fur=(), hatch_angle=None, hatch_spacing=None):
    """Masses -> one Part whose outline is the contour over them. fur: [(box, flow, strength)]."""
    c = contour_from(to_mask(polys), close_r)
    f = []
    for box, flow, st in fur:
        f += fur_where(c, box, flow, st)
    p = Part(name, c, z=z, tone=tone, lw=lw, n=2, fur=f)
    p.hatch_angle, p.hatch_spacing = hatch_angle, hatch_spacing
    return p


def ground_shadow(x0, x1, y, h=10):
    return Part("shadow", [(x0, y - 2), ((x0 + x1) / 2, y - h * 0.6), (x1, y - 2), (x1 - 20, y + h),
                           ((x0 + x1) / 2, y + h * 1.3), (x0 + 15, y + h)], z=0, tone=0.75, flat=1.0)


# ---------------------------------------------------------------- the inking pass
def ink_figure(pen, parts, seed, hatch_t=0.6, form_parts=(), contour_w=1.9, part_t=None, cross=None):
    """cross: {part: (threshold, angle)} second hatch layer for dark-coloured subjects (a raven is black)."""
    sc = SketchScene(parts, pen, seed=seed)
    for p in parts:
        if p.name == "shadow":
            sc.quick_hatch(p, t=0.3, angle=-18, spacing=3.0, attn=0.0, w=0.45)
        else:
            t = (part_t or {}).get(p.name, hatch_t if p.tone < 0.2 else hatch_t - 0.12)
            sc.quick_hatch(p, t=t, w=0.6)
    for p in parts:
        if p.name in (cross or {}):
            t2, a2 = cross[p.name]
            sc.quick_hatch(p, t=t2, angle=a2, spacing=3.0, w=0.5)
    for p in parts:
        if p.name in form_parts:
            sc.hatch_form(p, t1=0.52, maxlen=16, w=0.6)
    for p in parts:
        if p.name != "shadow":
            sc.search_contour(p, w=contour_w, passes=(0.35, 0.5, 1.0))
    return sc


def tufts(pen, base_pts, flow, length=(6, 11), w=0.7):
    for q in base_pts:
        f = np.asarray(flow, float) + pen.rng.normal(0, 0.12, 2)
        pen.stroke(np.array([q, q + f * pen.rng.uniform(*length)]), w, taper=(0.1, 0.7), wobble=0.3)


# ---------------------------------------------------------------- page furniture
def note(pen, lines, x, y, size=17, rot=-2, lead=17):
    for i, ln in enumerate(lines):
        pen.write(ln, x + (i % 2) * 4, y + i * lead, size=size, rot=rot)


def crossed_out(pen, draw, box, lines, note_xy, size=17):
    """A quick wrong first attempt (draw(pen) makes it), struck through, with a note."""
    draw(pen)
    pen.scribble_out(box, w=1.0)
    note(pen, lines, *note_xy, size=size, rot=-4)


def title(pen, text, y=594):
    pen.write(text, 110, y, size=19, rot=-1, op=0.95)


def save(pen, name, W=600, H=600):
    n = pen.svg(os.path.join(HERE, name + ".svg"), W, H)
    print("elements", n)


# ---------------------------------------------------------------- ears grow from the skull
def ear(pen, base_a, base_b, tip, w=1.3, inner=True, hatch=6):
    """Ear as two edges rising from inside the skull outline to the tip. No base line is drawn,
    so the ear reads as growing out of the head rather than a shape pasted on top."""
    a, b, t = (np.asarray(v, float) for v in (base_a, base_b, tip))
    for s0, wf in ((a, 1.0), (b, 0.8)):
        mid = (s0 + t) / 2 + (t - s0)[::-1] * np.array([1, -1]) * 0.08
        pen.line([s0, mid, t], w=w * wf, wobble=0.35, overshoot=3, taper=(0.35, 0.1))
    if inner:
        m = (a + b) / 2
        pen.line([m + (b - a) * 0.15, (m + t) / 2 + (b - a) * 0.1, t + (m - t) * 0.12], w=w * 0.45, wobble=0.3)
    for k in range(hatch):
        u = (k + 1) / (hatch + 1)
        q = a * (1 - u) + t * u
        pen.stroke(np.array([q, q + (b - a) * 0.3 * (1 - u)]), 0.5, taper=(0.1, 0.5), wobble=0.15)


# ---------------------------------------------------------------- feathers (not fur)
def feather_blade(pen, base, tip, width, w=0.8, round_tip=True, shaft=False):
    """One feather as a hand draws it in a layered wing/tail: two edges converging on the tip,
    open at the base (it tucks under the feather above), optional shaft."""
    base, tip = np.asarray(base, float), np.asarray(tip, float)
    d = tip - base; L = np.linalg.norm(d); d /= L
    nv = np.array([-d[1], d[0]])
    for sd in (-1, 1):
        mid = base + d * L * 0.55 + nv * width * 0.5 * sd
        end = tip - d * (width * 0.35 if round_tip else 0) + nv * width * 0.15 * sd
        pts = [base + nv * width * 0.35 * sd, mid, end, tip] if sd == 1 else [base + nv * width * 0.35 * sd, mid, end]
        pen.line(pts, w=w * (1.0 if sd == 1 else 0.7), wobble=0.35, taper=(0.4, 0.15))
    if shaft:
        pen.line([base, base + d * L * 0.85], w=w * 0.45, wobble=0.2, taper=(0.3, 0.4))


def feather_row(pen, start, end, n, length, width, angle_off=0.0, w=0.7, skip=0.12):
    """A row of overlapping feather edges (coverts): short open arcs, sizes and gaps varied."""
    start, end = np.asarray(start, float), np.asarray(end, float)
    d = end - start; d /= np.linalg.norm(d)
    rot = np.radians(angle_off)
    fd = np.array([d[0] * np.cos(rot) - d[1] * np.sin(rot), d[0] * np.sin(rot) + d[1] * np.cos(rot)])
    fn = np.array([-fd[1], fd[0]])
    for i in range(n):
        if pen.rng.random() < skip:
            continue
        t = (i + pen.rng.uniform(-0.25, 0.25)) / max(n - 1, 1)
        q = start * (1 - t) + end * t
        L = length * pen.rng.uniform(0.75, 1.15)
        a = np.linspace(-1, 1, 9)
        pts = q[None, :] + fn[None, :] * (a * width * 0.5)[:, None] + fd[None, :] * (L * (1 - a ** 2) * 0.35)[:, None]
        pen.stroke(pts, w * pen.rng.uniform(0.7, 1.2), taper=(0.25, 0.25), wobble=0.25)


# ---------------------------------------------------------------- seeded page layout + notes as data
import json


class Layout:
    """Per-page layout chosen from a seed: figure scale/position, optional crossed-out try, 0-3 side
    studies in free corners, caption top or bottom, a slight tilt for all writing. All text comes from
    notes/<subject>.json; the drawing code authors none of it."""
    SLOTS = {"TL": (95, 85), "TR": (505, 85), "BL": (95, 515), "BR": (505, 515), "ML": (78, 300), "MR": (522, 300)}

    def __init__(self, seed, subject, W=600, H=600, text_scale=1.0, fig_scale=1.0):
        """W, H: the page box the game gives (viewport-derived). text_scale/fig_scale enlarge writing and
        figure when the page has room (e.g. a tall phone page). Positions are authored for 600x600 and scaled."""
        self.W, self.H, self.ts = W, H, text_scale
        self.SLOTS = {k: (x * W / 600, y * H / 600) for k, (x, y) in Layout.SLOTS.items()}
        self.gx, self.gy = int(np.ceil(W / 15)), int(np.ceil(H / 15))
        self.r = r = np.random.default_rng(seed)
        self.notes = json.load(open(os.path.join(HERE, "notes", subject + ".json")))
        self.scale = r.uniform(0.74, 1.0) * fig_scale
        self.rot = r.uniform(-4.0, 2.0)
        self.cap_top = r.random() < 0.35
        self.crossed = r.random() < 0.55
        self.n_studies = int(r.integers(0, 4))
        self.center = np.array([W / 2 + r.uniform(-45, 45) * W / 600,
                                (330 if self.cap_top else 295) * H / 600 + r.uniform(-25, 25) * H / 600])
        self.boxes = []

    # figure: draw in native coords, then scale/translate everything drawn
    @contextmanager
    def figure(self, pen, native_center):
        self.nc = np.asarray(native_center, float)
        k = (len(pen.polys), len(pen.faint), len(pen.fills))
        yield
        for lst, k0 in ((pen.polys, k[0]), (pen.faint, k[1]), (pen.fills, k[2])):
            for i in range(k0, len(lst)):
                lst[i] = self.T(lst[i])
        pts = np.vstack([P for P in pen.polys[k[0]:]] + [P for P in pen.faint[k[1]:]])
        self.occ = np.zeros((self.gy, self.gx), bool)
        ij = (pts // 15).astype(int)
        ij[:, 0] = np.clip(ij[:, 0], 0, self.gx - 1); ij[:, 1] = np.clip(ij[:, 1], 0, self.gy - 1)
        self.occ[ij[:, 1], ij[:, 0]] = True
        self.occ = ndimage.binary_dilation(self.occ, iterations=1)

    def T(self, P):
        return (np.asarray(P, float) - self.nc) * self.scale + self.center

    def _cost(self, box):
        x0, y0, x1, y1 = box
        c = 0.0
        if x0 < 6 or y0 < 6 or x1 > self.W - 6 or y1 > self.H - 6:
            c += 1000
        i0, i1 = max(0, int(x0 // 15)), min(self.gx - 1, int(x1 // 15))
        j0, j1 = max(0, int(y0 // 15)), min(self.gy - 1, int(y1 // 15))
        c += self.occ[j0:j1 + 1, i0:i1 + 1].sum() * 3
        for b in self.boxes:
            ox = max(0, min(x1, b[2]) - max(x0, b[0])); oy = max(0, min(y1, b[3]) - max(y0, b[1]))
            c += ox * oy * 0.2
        return c

    @staticmethod
    def _chars(lines):
        """A line is a string or {"t": str, "struck": bool, "later": bool}; width in chars (later = indented)."""
        return max(len(l) if isinstance(l, str) else len(l["t"]) + (4 if l.get("later") else 0) for l in lines)

    def text(self, pen, lines, x, y, size=16):
        for i, ln in enumerate(lines):
            d = {"t": ln} if isinstance(ln, str) else ln
            lx = x + (i % 2) * 3 + (size * 1.6 if d.get("later") else 0)   # added later: indented ...
            rot = self.rot + self.r.normal(0, 0.8) + (self.r.choice([-1, 1]) * 3.5 if d.get("later") else 0)  # ... other angle
            ly = y + i * size * 1.05
            pen.write(d["t"], lx, ly, size=size, rot=rot)
            if d.get("struck"):                                              # one pen line through it
                wpx = len(d["t"]) * size * 0.4
                a = np.radians(rot)
                p0 = np.array([lx - 2, ly - size * 0.3]); p1 = p0 + np.array([np.cos(a), np.sin(a)]) * (wpx + 4)
                pen.stroke(np.array([p0, (p0 + p1) / 2 + (0, self.r.normal(0, 0.8)), p1]), 1.1, taper=(0.05, 0.2), wobble=0.5)
        w = self._chars(lines) * size * 0.42
        self.boxes.append((x, y - size, x + w, y + size * 1.05 * (len(lines) - 1) + 4))
        return self.boxes[-1]

    def _tbox(self, lines, x, y, size):
        w = self._chars(lines) * size * 0.42
        return (x, y - size, x + w, y + size * 1.05 * (len(lines) - 1) + 4)

    def place(self, pen, draw, bbox, slot, size=(140, 110)):
        """Draw a study/crossed-out at native coords, then fit it into a slot (random size)."""
        k = (len(pen.polys), len(pen.fills))
        draw(pen)
        x0, y0, x1, y1 = bbox
        f = min(size[0] * self.ts / (x1 - x0), size[1] * self.ts / (y1 - y0)) * self.r.uniform(0.7, 1.0)
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        tgt = np.array(self.SLOTS[slot]) + self.r.normal(0, 8, 2)
        hw, hh = (x1 - x0) * f / 2, (y1 - y0) * f / 2                       # keep the study on the page
        tgt = np.array([np.clip(tgt[0], 6 + hw, self.W - 6 - hw), np.clip(tgt[1], 6 + hh, self.H - 6 - hh)])
        for lst, k0 in ((pen.polys, k[0]), (pen.fills, k[1])):
            for i in range(k0, len(lst)):
                lst[i] = (lst[i] - c) * f + tgt
        b = (tgt[0] - (x1 - x0) * f / 2, tgt[1] - (y1 - y0) * f / 2, tgt[0] + (x1 - x0) * f / 2, tgt[1] + (y1 - y0) * f / 2)
        self.boxes.append(b)
        return b

    def free_slots(self):
        sc = {s: self._cost((x - 60, y - 50, x + 60, y + 50)) for s, (x, y) in self.SLOTS.items()}
        return sorted(sc, key=lambda s: sc[s] + self.r.uniform(0, 4))

    def page(self, pen, studies, crossed_draw=None):
        """studies: {id: (draw_fn, native_bbox)}. Places crossed-out + studies, labels, caption."""
        notes = self.notes
        slots = self.free_slots()
        items = []
        req = {n.get("id", n["kind"]) for n in notes if n.get("required")}   # "required": always shown
        if crossed_draw is not None and (self.crossed or "crossed" in req):
            items.append(("crossed", crossed_draw))
        ids = list(studies)
        self.r.shuffle(ids)
        ids = [i for i in ids if i in req] + [i for i in ids if i not in req]
        items += [(i, studies[i]) for i in ids[:max(self.n_studies, sum(i in req for i in ids))]]
        for (kind, spec), slot in zip(items, slots):
            if kind == "crossed":
                draw, bbox = spec
                b = self.place(pen, lambda p: (draw(p)), bbox, slot, size=(130, 95))
                pen.scribble_out(b, w=1.0)
                text = next((n["text"] for n in notes if n["kind"] == "crossed"), None)
            else:
                draw, bbox = spec
                b = self.place(pen, draw, bbox, slot)
                text = next((n["text"] for n in notes if n["kind"] == "study" and n.get("id") == kind), None)
            if text:
                below = b[3] + 18 * self.ts if b[3] < self.H - 60 else b[1] - 8 - 16 * self.ts * len(text)
                x = min(max(8, b[0]), self.W - 6 - self._chars(text) * 16 * self.ts * 0.42)
                self.text(pen, text, x, below, size=15 * self.ts)
        for n in notes:
            if n["kind"] != "label":
                continue
            a = self.T(n["anchor"])
            best = None
            for ang in np.linspace(0, 2 * np.pi, 16, endpoint=False):
                for dist in (60 * self.ts, 90 * self.ts, 120 * self.ts):   # bigger writing sits farther out
                    x = a[0] + np.cos(ang) * dist; y = a[1] + np.sin(ang) * dist
                    w = self._chars(n["text"]) * 16 * self.ts * 0.42
                    x -= w / 2 * (1 - np.cos(ang))
                    bx = self._tbox(n["text"], x, y, 16 * self.ts)
                    c = self._cost(bx) + dist * 0.05
                    if best is None or c < best[0]:
                        best = (c, x, y, bx)
            _, x, y, bx = best
            self.text(pen, n["text"], x, y, size=16 * self.ts)
            s = np.array([np.clip(a[0], bx[0], bx[2]), np.clip(a[1], bx[1], bx[3])])
            s = s + (a - s) / (np.linalg.norm(a - s) + 1e-9) * 6
            e = a - (a - s) / (np.linalg.norm(a - s) + 1e-9) * 5
            if np.linalg.norm(e - s) > 15:
                pen.arrow(s, e, bend=self.r.uniform(-14, 14))
        cap = next((n["text"] for n in notes if n["kind"] == "caption"), None)
        if cap:
            y = 30 * self.H / 600 if self.cap_top else self.H - 10
            pen.write(cap[0], self.r.uniform(14, 150) * self.W / 600, y, size=19 * self.ts, rot=self.rot * 0.5, op=0.95)
