"""Procedural pen-and-ink helper: authored part outlines -> inflated-form shading ->
form-following hatch strokes + variable-width tapered contours, emitted as SVG polygons."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

S = 2          # mask supersampling
W = 600
INK = "#2b241c"
LIGHT = np.array([-0.45, -0.75, 0.55]); LIGHT /= np.linalg.norm(LIGHT)
L2 = np.array([-0.5, -0.86])  # 2D direction the light comes from


def catmull(pts, closed=True, n=10):
    P = np.asarray(pts, float)
    if closed:
        P = np.vstack([P[-1], P, P[0], P[1]])
    else:
        P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out = np.vstack(out)
    if not closed:
        out = np.vstack([out, P[-2]])
    return out


def resample(pts, step=1.0):
    pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    if s[-1] < step:
        return pts
    n = max(2, int(s[-1] / step) + 1)
    u = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])])


def normals(pts):
    t = np.gradient(pts, axis=0)
    t /= (np.linalg.norm(t, axis=1, keepdims=True) + 1e-9)
    return np.column_stack([-t[:, 1], t[:, 0]])


class Pen:
    def __init__(self, seed=1):
        self.rng = np.random.default_rng(seed)
        self.polys = []
        self.fills = []

    def noise(self, n, period, amp):
        k = max(3, int(n / max(period, 1e-3)) + 3)
        v = self.rng.normal(0, 1, k)
        x = np.linspace(0, k - 3, n)
        return amp * np.interp(x, np.arange(k), v)

    def stroke(self, pts, w, taper=(0.2, 0.35), wobble=0.35, wvar=0.25, min_w=0.22, step=1.0):
        pts = resample(pts, step)
        n = len(pts)
        if n < 3:
            return
        nr = normals(pts)
        pts = pts + nr * self.noise(n, 22, wobble)[:, None]
        nr = normals(pts)
        s = np.linspace(0, 1, n)
        prof = np.ones(n)
        a, b = taper
        if a > 0:
            prof *= np.clip(s / a, 0.08, 1) ** 0.7
        if b > 0:
            prof *= np.clip((1 - s) / b, 0.08, 1) ** 0.7
        w = np.asarray(w, float)
        if w.ndim and len(w) != n:
            w = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(w)), w)
        w = np.broadcast_to(w, (n,))
        wid = np.maximum(min_w, w * prof * (1 + self.noise(n, 28, wvar)))
        Lp = pts + nr * wid[:, None] / 2
        Rp = pts - nr * wid[:, None] / 2
        self.polys.append(np.vstack([Lp, Rp[::-1]]))

    def fill(self, pts):
        self.fills.append(np.asarray(pts, float))

    def svg(self, path, size=600):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
               f'<g fill="{INK}" stroke="none">']
        for P in self.fills + self.polys:
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in P) + "Z"
            out.append(f'<path d="{d}"/>')
        out.append("</g></svg>")
        open(path, "w").write("\n".join(out))
        return len(self.polys) + len(self.fills)


def raster(poly):
    im = Image.new("L", (W * S, W * S), 0)
    ImageDraw.Draw(im).polygon([(x * S, y * S) for x, y in poly], fill=255)
    return np.array(im) > 127


class Part:
    def __init__(self, name, pts, z, tone=0.0, lw=1.7, spacing=2.6, cross=35, fur=(), n=10,
                 hatch=True, smooth_contour=True, flat=0.0):
        self.name, self.z, self.tone, self.lw, self.spacing, self.cross = name, z, tone, lw, spacing, cross
        self.ctrl = np.asarray(pts, float)
        self.n = n
        self.dense = catmull(self.ctrl, True, n)
        self.fur = fur  # list of (i0, i1, flow(dx,dy), strength) on control-point indices
        self.hatch = hatch
        self.flat = flat
        self.mask = raster(self.dense)

    def fields(self):
        m = self.mask
        d = ndimage.distance_transform_edt(m) / S
        R = ndimage.maximum_filter(d, size=int(max(8, d.max() * 2.2) * S))
        R = ndimage.gaussian_filter(R, 4 * S)
        r = np.clip(d / (R + 1e-6), 0, 1)
        h = R * np.sqrt(np.clip(1 - (1 - r) ** 2, 0, 1)) * (1 - self.flat)
        h = ndimage.gaussian_filter(h, 1.5 * S)
        hy, hx = np.gradient(h)
        hx *= S; hy *= S
        nz = np.ones_like(h)
        nrm = np.sqrt(hx ** 2 + hy ** 2 + 1)
        lam = (-hx * LIGHT[0] - hy * LIGHT[1] + nz * LIGHT[2]) / nrm
        self.dark = np.clip(1 - (0.1 + 1.0 * np.clip(lam, 0, 1)), 0, 1) + self.tone
        ds = ndimage.gaussian_filter(d, 2 * S)
        gy, gx = np.gradient(ds)
        g = np.sqrt(gx ** 2 + gy ** 2) + 1e-9
        self.gx, self.gy = gx / g, gy / g


class Scene:
    def __init__(self, parts, seed=3):
        self.parts = sorted(parts, key=lambda p: p.z)
        self.pen = Pen(seed)
        front = np.zeros((W * S, W * S), bool)
        for p in reversed(self.parts):
            p.front = front.copy()
            p.vis = p.mask & ~front
            front |= p.mask
        self.union = front
        for p in self.parts:
            p.fields()
            # occlusion shadow: darker near a front part's edge
            if p.front.any():
                df = ndimage.distance_transform_edt(~p.front) / S
                p.dark = p.dark + 0.45 * np.exp(-df / 7.0)
            p.extra = np.zeros_like(p.dark)

    def add_shadow(self, name, poly, amt, blur=6):
        """Paint extra darkness into a part (cast shadows etc)."""
        m = raster(catmull(poly, True, 8)).astype(float)
        m = ndimage.gaussian_filter(m, blur * S)
        for p in self.parts:
            if p.name == name:
                p.dark = p.dark + amt * m

    def _at(self, arr, q):
        x, y = int(q[0] * S), int(q[1] * S)
        if 0 <= x < W * S and 0 <= y < W * S:
            return arr[y, x]
        return 0

    def hatch_form(self, p, t1=0.38, maxlen=40, w=0.62):
        pen = self.pen
        b = resample(p.dense, p.spacing)
        b = b + self.pen.rng.normal(0, 0.35, b.shape)
        for s in b:
            # find inward direction
            q = s.copy()
            gx, gy = self._at(p.gx, q), self._at(p.gy, q)
            q = q + np.array([gx, gy]) * 0.8
            if not self._at(p.vis, q):
                continue
            thr = t1 + pen.rng.normal(0, 0.05)
            line = [q.copy()]
            dirv = np.array([gx, gy])
            bend = pen.rng.normal(0, 0.012)
            for _ in range(int(maxlen * (0.8 + 0.4 * pen.rng.random()))):
                if self._at(p.dark, q) < thr or not self._at(p.vis, q):
                    break
                g = np.array([self._at(p.gx, q), self._at(p.gy, q)])
                dirv = 0.82 * dirv + 0.18 * g
                dirv = dirv + bend * np.array([-dirv[1], dirv[0]])
                dirv /= np.linalg.norm(dirv) + 1e-9
                q = q + dirv
                line.append(q.copy())
            if len(line) > 3:
                dk = self._at(p.dark, line[0])
                pen.stroke(np.array(line), w * (0.7 + 0.5 * min(dk, 1.2)), taper=(0.12, 0.55), wobble=0.25)

    def hatch_cross(self, p, t2=0.66, angle=None, spacing=None, w=0.5, curve=0.0):
        pen = self.pen
        ang = np.radians(p.cross if angle is None else angle)
        sp = (p.spacing * 1.25) if spacing is None else spacing
        d = np.array([np.cos(ang), np.sin(ang)])
        nv = np.array([-d[1], d[0]])
        ys, xs = np.nonzero(p.vis)
        if len(xs) == 0:
            return
        pts = np.column_stack([xs, ys]) / S
        proj_n = pts @ nv
        proj_d = pts @ d
        for o in np.arange(proj_n.min(), proj_n.max(), sp):
            o2 = o + pen.rng.normal(0, 0.3)
            ts = np.arange(proj_d.min() - 2, proj_d.max() + 2, 0.8)
            line = o2 * nv[None, :] + ts[:, None] * d[None, :]
            line = line + nv[None, :] * (curve * ((ts - ts.mean()) / 50.0) ** 2)[:, None]
            thr = t2 + pen.noise(len(ts), 30, 0.05)
            ok = np.array([self._at(p.vis, q) and self._at(p.dark, q) > th for q, th in zip(line, thr)])
            # runs
            i = 0
            while i < len(ok):
                if ok[i]:
                    j = i
                    while j < len(ok) and ok[j]:
                        j += 1
                    if j - i > 3:
                        pen.stroke(line[i:j], w, taper=(0.3, 0.3), wobble=0.3)
                    i = j
                else:
                    i += 1

    def contour(self, p, seglen=(35, 90), gap_lit=0.55):
        pen = self.pen
        dense = resample(p.dense, 1.0)
        n = len(dense)
        nr = normals(dense)
        # make normals outward
        test = dense + nr * 1.5
        inside = np.array([self._at(p.mask, q) for q in test])
        if inside.mean() > 0.5:
            nr = -nr
        facing = nr @ L2  # >0 lit
        hidden = np.array([self._at(p.front, q) for q in dense])
        # fur map
        fur = np.zeros(n)
        flow = np.zeros((n, 2))
        perim_ctrl = len(p.ctrl)
        for (i0, i1, fl, st) in p.fur:
            a, b = int(i0 / perim_ctrl * n), int(i1 / perim_ctrl * n)
            idx = np.arange(a, b) % n
            fur[idx] = st
            flow[idx] = fl
        width = p.lw * (1.0 - 0.45 * facing)
        # segmentation into pen strokes
        i = 0
        start = int(pen.rng.integers(0, n))
        order = (np.arange(n) + start) % n
        cur = []
        target = pen.rng.uniform(*seglen)
        def flush(cur):
            if len(cur) > 4:
                idx = np.array(cur)
                pts = dense[idx]
                pen.stroke(pts, width[idx], taper=(0.12, 0.2), wobble=0.4)
        for k in order:
            lost = facing[k] > gap_lit and pen.rng.random() < 0.0  # handled below
            if hidden[k] or fur[k] > 0.5:
                flush(cur); cur = []
                continue
            cur.append(k)
            if len(cur) > target:
                flush(cur); cur = [k] if pen.rng.random() < 0.6 else []
                target = pen.rng.uniform(*seglen)
        flush(cur)
        # lit-edge lost lines: overdraw nothing; fur tufts
        k = 0
        while k < n:
            if fur[k] > 0 and not hidden[k]:
                q = dense[k]
                o = nr[k]
                f = flow[k] / (np.linalg.norm(flow[k]) + 1e-9)
                L = pen.rng.uniform(3, 7) * fur[k]
                a = q - o * pen.rng.uniform(1.0, 3.0)
                mid = q + o * L * 0.35 + f * L * 0.5
                e = q + o * L * 0.5 + f * L
                pts = catmull([a, mid, e], closed=False, n=6)
                pen.stroke(pts, width[k] * 0.75, taper=(0.15, 0.7), wobble=0.15)
                k += int(pen.rng.integers(2, 4))
            else:
                k += 1

    def render(self, form=True, cross=True, deep=True, t1=0.38, t2=0.66, t3=0.86):
        for p in self.parts:
            if p.hatch:
                if form:
                    self.hatch_form(p, t1=t1)
                if cross:
                    self.hatch_cross(p, t2=t2)
                if deep:
                    self.hatch_cross(p, t2=t3, angle=p.cross + 75, spacing=p.spacing * 1.1, w=0.45)
            self.contour(p)
