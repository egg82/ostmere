"""Journal entry `cellar` (places): looking down a flight of cut stone steps from above, the dug walls either side,
a doorway under a lintel at the foot, and the room's swept floor beyond it. Run: bash render.sh entry_cellar

A place, not a creature: the nearest precedent is warm_ground. Instead of guessing a perspective, the stair is built in
metres and put through a pinhole camera, so the steps close up and the walls deepen as a real stair does. Measured from
ordinary stone stairs: rise 0.2 m, going 0.28 m, a flight about a metre wide; a root cellar is about 3 m square and
1.8 m deep, its doorway under a lintel with a hand's depth of earth roof over it. The eye stands back from the top step
and a little right of the stair's middle, 2.4 m up, looking 48 degrees down. The top 0.35 m of each wall is the dug
ash, the rest coursed stone. The walls, the lintel and the doorway's shadow are Parts (the shadow hatched, never
outlined, and the lintel's edges drawn by hand); steps, courses, joints and ash are strokes.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 12))
pen = JournalPen(SEED)
L = Layout(int(os.environ.get("LAYOUT_SEED", SEED)), "entry_cellar", text_scale=1.3)
A = lambda *p: np.array(p, float)
rng = np.random.default_rng(SEED)

RISE, GOING, STEPS, HALF = 0.2, 0.28, 9, 0.5
Y0 = 0.0                                   # the top step's edge
FOOT = Y0 + STEPS * GOING                  # where the stair meets the room's near wall
FLOOR, ROOM, ASH, LINTEL = -STEPS * RISE, 3.0, -0.35, -0.4
EYE, PITCH, YAW = A(0.3, -1.5, 2.4), np.radians(48), np.radians(-5)
F_AX = A(np.sin(YAW) * np.cos(PITCH), np.cos(YAW) * np.cos(PITCH), -np.sin(PITCH))
R_AX = A(np.cos(YAW), -np.sin(YAW), 0)
U_AX = np.cross(R_AX, F_AX)


def raw(x, y, z):
    d = A(x, y, z) - EYE
    f = d @ F_AX
    return A(d @ R_AX / f, -(d @ U_AX) / f)


_box = np.array([raw(x, y, z) for x in (-HALF, HALF) for y, z in ((Y0, 0), (FOOT, 0), (FOOT, FLOOR))])
_lo, _hi = _box.min(0), _box.max(0)
SCALE = min(300 / (_hi[0] - _lo[0]), 360 / (_hi[1] - _lo[1]))
ORIGIN = A(300, 320) - SCALE * (_lo + _hi) / 2


def P(x, y, z):
    """A point in metres (x across, y away, z up) to page coordinates."""
    return ORIGIN + SCALE * raw(x, y, z)


def step_y(k):
    return Y0 + k * GOING


def wall_poly(x):
    """A side wall's face: top along the ground, bottom stepping down with the stair."""
    pts = [P(x, Y0, 0), P(x, FOOT, 0), P(x, FOOT, FLOOR)]
    for k in range(STEPS, 0, -1):
        pts += [P(x, step_y(k), -k * RISE), P(x, step_y(k - 1), -k * RISE)]
    return pts


ZB = LINTEL + 0.55 * (FLOOR - LINTEL)           # the daylight down the stair reaches this far up the doorway
left = Part("lwall", wall_poly(-HALF), z=1, tone=0.5, lw=1.6, n=2, smooth_contour=False)
right = Part("rwall", wall_poly(HALF), z=1, tone=0.1, lw=1.6, n=2, smooth_contour=False)
lintel = Part("lintel", [P(-HALF - 0.1, FOOT, LINTEL + 0.2), P(HALF + 0.1, FOOT, LINTEL + 0.2),
                        P(HALF + 0.1, FOOT, LINTEL), P(-HALF - 0.1, FOOT, LINTEL)],
              z=3, tone=0.3, lw=1.6, n=2, smooth_contour=False)
dark = Part("dark", [P(-HALF, FOOT, LINTEL), P(HALF, FOOT, LINTEL), P(HALF, FOOT, ZB), P(-HALF, FOOT, ZB)],
            z=2, tone=0.95, lw=1.2, n=2, smooth_contour=False)
for p, a, sp in ((left, -12, 3.6), (right, 8, 3.6), (lintel, -35, 3.0), (dark, -62, 2.6)):
    p.hatch_angle, p.hatch_spacing = a, sp


def course(x, z, y_a, y_b):
    """One mortar course along a wall, broken where the hand lifted."""
    y = y_a
    while y < y_b - 0.05:
        span = rng.uniform(0.35, 0.8)
        pen.line([P(x, y, z), P(x, min(y + span, y_b), z)], w=1.0, wobble=0.5)
        y += span + rng.uniform(0.04, 0.12)


def joints(x, z_top, z_bot, y_a, y_b):
    """Upright joints between the blocks of one course, staggered."""
    y = y_a + rng.uniform(0.1, 0.4)
    while y < y_b - 0.1:
        pen.line([P(x, y, z_top), P(x, y, z_bot)], w=1.0, wobble=0.3)
        y += rng.uniform(0.4, 0.7)


def scrape(a, b):
    """A short stroke in the dug ash, from a to b in metres."""
    pen.line([P(*a), P(*b)], w=0.5, wobble=0.3)


with L.figure(pen, (300, 320)):
    with pen.construction():
        for x in (-HALF, HALF):
            pen.line([P(x, Y0, 0), P(x, FOOT, FLOOR)], w=0.4, wobble=0.6, overshoot=14)
            pen.line([P(x, Y0 - 0.5, 0), P(x, FOOT + 0.8, 0)], w=0.4, wobble=0.6)
        pen.line([P(-1.3, Y0, 0), P(1.3, Y0, 0)], w=0.4, wobble=0.6, overshoot=8)
    sc = SketchScene([left, right, lintel, dark], pen, seed=SEED)
    for p, t in ((left, 0.74), (right, 0.85), (dark, 0.2)):
        sc.quick_hatch(p, t=t, w=0.6)
    sc.quick_hatch(lintel, t=0.5, w=0.6, ext=0.5)
    sc.quick_hatch(dark, t=0.35, angle=25, spacing=3.0, w=0.5)
    for p in (left, right):                                # the dark has no outline: it is shadow, not an edge
        sc.search_contour(p, w=1.9, passes=(0.35, 0.5, 1.0))
    c = lintel.ctrl                                        # the lintel by hand: a contour search rounds its ends
    for a, b, w in ((0, 1, 1.3), (3, 2, 2.0), (0, 3, 1.2), (1, 2, 1.4)):
        pen.line([c[a], c[b]], w=w, wobble=0.6, overshoot=3)
    for x in (-HALF, HALF):                                # coursed stone below the ash, ash above
        z, k = ASH, 0
        while z - 0.26 > FLOOR + 0.05:
            zn = z - rng.uniform(0.24, 0.3)
            first = max(0, int(np.floor(-zn / RISE)))      # the courses start where the stair has gone below them
            ya = step_y(min(first, STEPS))
            course(x, zn, ya, FOOT)
            joints(x, z, zn, ya, FOOT)
            z = zn
        course(x, ASH, step_y(1), FOOT)
        for _ in range(22):
            y, zz = rng.uniform(step_y(1), FOOT - 0.05), rng.uniform(ASH + 0.05, -0.03)
            scrape((x, y, zz), (x, y + rng.uniform(-0.03, 0.03), zz - rng.uniform(0.06, 0.12)))
    for _ in range(14):                                    # the end face over the lintel: dug ash
        xx, zz = rng.uniform(-HALF + 0.05, HALF - 0.05), rng.uniform(LINTEL + 0.28, -0.03)
        scrape((xx, FOOT, zz), (xx + rng.uniform(-0.02, 0.02), FOOT, zz - 0.07))
    for k in range(STEPS):                                 # step edges; the riser's shadow just beyond each
        y, z = step_y(k), -k * RISE
        pen.line([P(-HALF, y, z), P(HALF, y, z)], w=1.5 - 0.05 * k, wobble=0.5, overshoot=2)
        pen.line([P(-HALF, y + 0.025, z - RISE), P(HALF * 0.6, y + 0.025, z - RISE)], w=0.55, wobble=0.4)
        if k % 3 == 1:                                     # worn hollows in the treads
            m = P(rng.uniform(-0.1, 0.1), y + GOING * 0.55, z - RISE)
            pen.line([m + (-10, 0), m + (0, 1.6), m + (10, 0)], w=0.45, wobble=0.5)
    pen.line([P(-HALF * 0.9, FOOT + ROOM, FLOOR), P(HALF * 0.9, FOOT + ROOM, FLOOR)], w=0.7, wobble=0.4)
    for f in (0.3, 0.6):                                   # the floor through the doorway, swept bare
        y = FOOT + ROOM * f
        pen.line([P(-HALF * 0.7, y, FLOOR), P(HALF * 0.5, y, FLOOR)], w=0.4, wobble=0.4)
    for x, s in ((-HALF, -1), (HALF, 1)):                  # the cut edge of the ash either side
        pen.line([P(x + s * 0.03, Y0, 0), P(x + s * 0.06, FOOT * 0.5, 0), P(x, FOOT, 0)], w=1.3, wobble=0.7)
    pen.line([P(-HALF, FOOT, 0), P(HALF, FOOT, 0)], w=1.2, wobble=0.7)
    for _ in range(90):                                    # ash on the ground, thickest at the cut's edge
        x = (HALF + 0.06 + rng.exponential(0.25)) * rng.choice((-1, 1))
        y = rng.uniform(-0.3, FOOT + 0.3)
        if abs(x) < 1.4:
            q = P(x, y, 0)
            pen.line([q, q + (rng.uniform(3, 7), rng.uniform(-0.8, 0.8))], w=0.5, wobble=0.3)


def s_plan(pen):
    """The plan: the square room, the stair coming in on one side."""
    sq = [(20, 20), (120, 22), (118, 120), (22, 118)]
    for k in range(4):
        pen.line([sq[k], sq[(k + 1) % 4]], w=1.3, wobble=0.6, overshoot=4)
    for x in (60, 82):
        pen.line([(x, 120), (x, 178)], w=1.0, wobble=0.5)
    for k in range(7):
        y = 126 + k * 7.5
        pen.line([(60, y), (82, y)], w=0.6, wobble=0.3)
    pen.arrow(A(71, 172), A(71, 132), bend=0, w=0.8, head=5)
    pen.line([(20, 8), (120, 8)], w=0.6, wobble=0.4)
    for x in (20, 120):
        pen.line([(x, 3), (x, 13)], w=0.6)


def s_section(pen):
    """Side on: the ash, the stair cut down through it, the room under."""
    pen.line([(0, 30), (52, 30)], w=1.1, wobble=0.6, overshoot=4)
    pen.line([(112, 30), (200, 30)], w=1.1, wobble=0.6, overshoot=4)
    prof = [(52, 30)]
    for k in range(6):
        x, y = 52 + k * 10, 30 + k * 9
        prof += [(x, y + 9), (x + 10, y + 9)]
    pen.line(prof, w=1.0, wobble=0.3)
    pen.line([(112, 44), (112, 30)], w=0.9, wobble=0.3)
    for a, b in (((112, 40), (112, 84)), ((112, 84), (190, 84)), ((190, 84), (190, 40)), ((190, 40), (112, 40))):
        pen.line([a, b], w=1.2, wobble=0.5, overshoot=3)
    for _ in range(14):
        x = pen.rng.uniform(4, 196)
        if not 50 < x < 112:
            pen.line([(x, 22 + pen.rng.uniform(0, 4)), (x + 4, 22 + pen.rng.uniform(0, 4))], w=0.45)


def first_try(pen):
    pen.line([(20, 90), (60, 40), (100, 40), (140, 90)], w=0.9, wobble=0.6)
    for k in range(4):
        y = 50 + k * 10
        pen.line([(52 - k * 8, y), (108 + k * 8, y)], w=0.7, wobble=0.5)


L.page(pen, {"plan": (s_plan, (10, 0, 130, 182)), "section": (s_section, (0, 18, 200, 90))},
       crossed_draw=(first_try, (10, 34, 150, 96)))
save(pen, os.environ.get("OUT", "entry_cellar"))
