"""Loose field-sketch layer on top of ink.py: searching multi-pass contours, construction
marks, partial overshooting hatching, arrows, scribble-outs, handwritten labels as glyph paths."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import numpy as np
from scipy import ndimage
import ink
from ink import catmull, resample, normals, Part, Scene, Pen, INK, W, S

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONTS = {}


def font(name):
    if name not in FONTS:
        FONTS[name] = TTFont(os.path.join(HERE, "fonts", name))
    return FONTS[name]


class SketchPen(Pen):
    def __init__(self, seed=1):
        super().__init__(seed)
        self.raw = []  # (d, opacity)

    def svg(self, path, size=600, height=None):
        h = height or size
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {h}" width="{size}" height="{h}">',
               f'<g fill="{INK}" stroke="none">']
        for P in self.fills + self.polys:
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in P) + "Z"
            out.append(f'<path d="{d}"/>')
        for d, op in self.raw:
            out.append(f'<path d="{d}" fill-opacity="{op:.2f}"/>')
        out.append("</g></svg>")
        open(path, "w").write("\n".join(out))
        return len(self.polys) + len(self.fills) + len(self.raw)

    # ---- handwriting -------------------------------------------------------------------
    def write(self, s, x, y, size=16, rot=-2, fname="ReenieBeanie.ttf", op=0.92, jitter=1.0):
        f = font(fname)
        gs = f.getGlyphSet()
        cmap = f.getBestCmap()
        upm = f["head"].unitsPerEm
        sc = size / upm
        cx = 0.0
        a = np.radians(rot)
        ca, sa = np.cos(a), np.sin(a)
        for ch in s:
            gname = cmap.get(ord(ch))
            if gname is None:
                cx += size * 0.3
                continue
            g = gs[gname]
            r = np.radians(rot + self.rng.normal(0, 2.5 * jitter))
            k = sc * (1 + self.rng.normal(0, 0.05 * jitter))
            dy = self.rng.normal(0, 0.6 * jitter)
            px = x + cx * ca
            py = y + cx * sa + dy
            cr, sr = np.cos(r), np.sin(r)
            # font y up -> svg y down
            tr = (k * cr, k * sr, k * sr, -k * cr, px, py)
            sp = SVGPathPen(gs)
            g.draw(TransformPen(sp, tr))
            d = sp.getCommands()
            if d:
                self.raw.append((d, op))
            cx += g.width * sc * (1 + self.rng.normal(0, 0.03))

    # ---- marks ------------------------------------------------------------------------
    def line(self, pts, w=1.0, wobble=0.5, overshoot=0.0, taper=(0.15, 0.3), passes=1, spread=1.2):
        P = catmull(np.asarray(pts, float), closed=False, n=8) if len(pts) > 2 else resample(pts, 1.0)
        for i in range(passes):
            Q = P.copy()
            if overshoot:
                t0 = Q[0] - Q[min(3, len(Q) - 1)]
                t1 = Q[-1] - Q[max(-4, -len(Q))]
                t0 /= np.linalg.norm(t0) + 1e-9
                t1 /= np.linalg.norm(t1) + 1e-9
                Q = np.vstack([Q[0] + t0 * self.rng.uniform(0, overshoot), Q,
                               Q[-1] + t1 * self.rng.uniform(0, overshoot)])
            if i > 0:
                Q = Q + self.rng.normal(0, spread, 2) + normals(resample(Q, 1.0))[0] * 0
                Q = Q + self.noise(len(Q), 30, spread)[:, None] * normals(Q)
            self.stroke(Q, w * (1 if i == passes - 1 else 0.6), taper=taper, wobble=wobble)

    def ellipse(self, c, rx, ry, rot=0, w=0.45, turns=1.15, wobble=0.9):
        t = np.linspace(0, 2 * np.pi * turns, int(60 * turns)) + self.rng.uniform(0, 6.28)
        rr = 1 + self.noise(len(t), 15, 0.05)
        x, y = rx * rr * np.cos(t), ry * rr * np.sin(t)
        a = np.radians(rot)
        P = np.column_stack([c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a)])
        self.stroke(P, w, taper=(0.1, 0.2), wobble=wobble)

    def arrow(self, a, b, bend=20, w=0.9, head=7):
        a, b = np.asarray(a, float), np.asarray(b, float)
        m = (a + b) / 2
        d = b - a
        nv = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        mid = m + nv * bend
        P = catmull([a, mid, b], closed=False, n=16)
        self.stroke(P, w, taper=(0.1, 0.15), wobble=0.5)
        t = P[-1] - P[-5]
        t /= np.linalg.norm(t)
        for s in (1, -1):
            ang = np.radians(150 * s + self.rng.normal(0, 6))
            r = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]]) @ t
            self.stroke(np.array([b + r * head * self.rng.uniform(0.8, 1.2), b]), w, taper=(0.2, 0.1), wobble=0.2)

    def scribble_out(self, box, w=0.9, density=10):
        x0, y0, x1, y1 = box
        # two hard X strokes plus a fast zigzag
        self.stroke(np.array([[x0, y0], [(x0 + x1) / 2 + 3, (y0 + y1) / 2], [x1, y1]]), w * 1.3, taper=(0.05, 0.2), wobble=1.2)
        self.stroke(np.array([[x1, y0 + 4], [x0 + 2, y1 - 3]]), w * 1.2, taper=(0.05, 0.2), wobble=1.2)

    def zigzag(self, pts_pairs, w=0.55):
        """pts_pairs: list of (start,end) roughly parallel strokes -> one continuous zigzag line"""
        P = []
        for i, (a, b) in enumerate(pts_pairs):
            P.extend([a, b] if i % 2 == 0 else [b, a])
        if len(P) > 3:
            self.stroke(resample(np.array(P), 1.0), w, taper=(0.05, 0.1), wobble=0.3)


class SketchScene(Scene):
    def __init__(self, parts, pen, seed=3):
        self.parts = sorted(parts, key=lambda p: p.z)
        self.pen = pen
        front = np.zeros((W * S, W * S), bool)
        for p in reversed(self.parts):
            p.front = front.copy()
            p.vis = p.mask & ~front
            front |= p.mask
        self.union = front
        behind = np.zeros((W * S, W * S), bool)
        for p in self.parts:
            p.behind = behind.copy()
            if p.name != "shadow":  # a cast shadow is not an overlapping form
                behind |= p.mask
        for p in self.parts:
            p.fields()
            if p.front.any():
                df = ndimage.distance_transform_edt(~p.front) / S
                p.dark = p.dark + 0.35 * np.exp(-df / 6.0)
        # low-frequency "attention" field: where the hand bothered to hatch
        r = np.random.default_rng(seed)
        a = r.normal(0, 1, (12, 12))
        a = ndimage.zoom(a, W * S / 12, order=3)
        self.attn = (a - a.mean()) / (a.std() + 1e-9)

    def search_contour(self, p, w=1.25, passes=(0.45, 1.0), seg=(18, 55), over=5):
        pen = self.pen
        dense = resample(p.dense, 1.0)
        n = len(dense)
        nr = normals(dense)
        test = dense + nr * 1.5
        if np.mean([self._at(p.mask, q) for q in test]) > 0.5:
            nr = -nr
        facing = nr @ ink.L2
        hidden = np.array([self._at(p.front, q) for q in dense])
        ovl = np.array([self._at(p.behind, q + o * 3.0) for q, o in zip(dense, nr)]).astype(float)
        ovl = ndimage.gaussian_filter1d(ovl, 4, mode="wrap")
        fur = np.zeros(n); flow = np.zeros((n, 2))
        m = len(p.ctrl)
        for (i0, i1, fl, st) in p.fur:
            a, b = int(i0 / m * n), int(i1 / m * n)
            idx = np.arange(a, b) % n
            fur[idx] = st; flow[idx] = fl
        for pi, wf in enumerate(passes):
            last = pi == len(passes) - 1
            k = int(pen.rng.integers(0, n))
            done = 0
            while done < n:
                L = int(pen.rng.uniform(*seg) * (1.6 if not last else 1.0))
                idx = (k + np.arange(L)) % n
                k = (k + L - int(pen.rng.integers(-3, 6))) % n
                done += L
                vis = ~hidden[idx]
                if last:
                    vis &= fur[idx] < 0.5
                if vis.sum() < 4:
                    continue
                # keep longest visible run
                runs = np.split(idx, np.where(np.diff(vis.astype(int)) != 0)[0] + 1)
                for rn in runs:
                    if len(rn) < 4 or hidden[rn[0]] or (last and fur[rn[0]] >= 0.5):
                        continue
                    pts = dense[rn].copy()
                    off = pen.rng.normal(0, 1.4 if not last else 0.5)
                    pts = pts + nr[rn] * off
                    # overshoot along tangent at both ends
                    if len(pts) > 6:
                        t0 = pts[0] - pts[4]; t0 /= np.linalg.norm(t0) + 1e-9
                        t1 = pts[-1] - pts[-5]; t1 /= np.linalg.norm(t1) + 1e-9
                        pts = np.vstack([pts[0] + t0 * pen.rng.uniform(0, over), pts,
                                         pts[-1] + t1 * pen.rng.uniform(0, over)])
                    fw = np.concatenate([[facing[rn[0]]], facing[rn], [facing[rn[-1]]]])
                    ov = np.concatenate([[ovl[rn[0]]], ovl[rn], [ovl[rn[-1]]]])
                    ww = p.lw / 1.7 * w * wf * (1.0 - 0.5 * fw) * (1.0 + 0.45 * ov)
                    # lost edges on the lit side for the final pass
                    if last and fw.mean() > 0.55 and pen.rng.random() < 0.45:
                        continue
                    pen.stroke(pts, ww, taper=(0.18, 0.3), wobble=0.7 if not last else 0.45, wvar=0.35)
        # fur tufts
        k = 0
        while k < n:
            if fur[k] > 0 and not hidden[k]:
                q = dense[k]; o = nr[k]
                f = flow[k] / (np.linalg.norm(flow[k]) + 1e-9)
                Lt = pen.rng.uniform(3, 8) * fur[k]
                a = q - o * pen.rng.uniform(1.0, 4.0) - f * 2
                e = q + o * Lt * 0.4 + f * Lt
                pts = catmull([a, q + o * Lt * 0.25 + f * Lt * 0.4, e], closed=False, n=6)
                pen.stroke(pts, 0.85 * (1 - 0.4 * facing[k]), taper=(0.1, 0.75), wobble=0.2)
                k += int(pen.rng.integers(2, 5))
            else:
                k += 1

    def quick_hatch(self, p, t=0.5, angle=None, spacing=None, w=0.55, attn=0.3, ext=3.0, zig=0.35,
                    maxrun=60):
        """Diagonal, fast, right-handed hatching; partial (attention field), overshooting edges."""
        pen = self.pen
        ys, xs = np.nonzero(p.vis)
        if len(xs) == 0:
            return
        if angle is None:
            angle = getattr(p, "hatch_angle", None)
        if angle is None:  # auto: near-axial strokes on elongated forms (rings read as pipes), a hand's diagonal on round ones
            P0 = np.column_stack([xs, ys]).astype(float)
            ev, evec = np.linalg.eigh(np.cov((P0 - P0.mean(0)).T))
            ax = np.degrees(np.arctan2(evec[1, 1], evec[0, 1]))
            angle = (ax + 18) if np.sqrt(ev[1] / max(ev[0], 1e-6)) > 1.8 else -58 + pen.rng.normal(0, 10)
        if spacing is None:
            spacing = getattr(p, "hatch_spacing", None) or 3.4
        spacing = spacing * (1.15 - 0.35 * float(np.clip(p.dark[p.vis].mean(), 0, 1)))
        ang = np.radians(angle)
        d = np.array([np.cos(ang), np.sin(ang)])
        nv = np.array([-d[1], d[0]])
        pts = np.column_stack([xs, ys]) / S
        pn, pdd = pts @ nv, pts @ d
        groups = []
        for o in np.arange(pn.min(), pn.max(), spacing):
            o2 = o + pen.rng.normal(0, 0.45)
            ts = np.arange(pdd.min() - 2, pdd.max() + 2, 0.8)
            line = o2 * nv[None, :] + ts[:, None] * d[None, :]
            ok = np.array([self._at(p.vis, q) and
                           (self._at(p.dark, q) + attn * self._at(self.attn, q) * 0.5) > t for q in line])
            runs = []
            i = 0
            while i < len(ok):
                if ok[i]:
                    j = i
                    while j < len(ok) and ok[j]:
                        j += 1
                    if j - i > 3:
                        j2 = min(j, i + int(maxrun / 0.8))
                        a = line[i] - d * pen.rng.uniform(0, ext * 0.4)
                        b = line[j2 - 1] + d * pen.rng.uniform(-1, ext)
                        runs.append((a, b))
                    i = j
                else:
                    i += 1
            groups.append(runs)
        # draw: some as zigzag clusters, others as separate flicks with hooks
        for gi, runs in enumerate(groups):
            for (a, b) in runs:
                if pen.rng.random() < 0.06:
                    continue  # skipped stroke
                L = np.linalg.norm(b - a)
                hook = nv * pen.rng.normal(0, 0.12) * L
                pts = catmull([a, (a + b) / 2 + hook, b], closed=False, n=max(4, int(L / 2)))
                pen.stroke(pts, w * pen.rng.uniform(0.7, 1.25), taper=(0.08, 0.5), wobble=0.3, wvar=0.3)
