"""Journal note sketch `house_2`, drawn to its brief in content/team/week-five.md ("Journal sketches"). Run:
bash render.sh note_house_2 -> note_house_2_ink.png

A note's sketch, not an entry's: small, wider than tall, no layout furniture and no words, the weights twice an
entry's (as `note_gutter_knot`). It is a quick copy of marks seen on a wall, so it is drawn flat, as a diagram: no
form shading and no construction. The ring is the circles-round-a-circle shape of content/mysteries.md, Question 5:
a dark middle filled in and a ring of small circles round it, each drawn in its own stroke. Roads run
between the marks and off the edges, small squares sit along them, and one mark is a plain cross, no heavier than
the rest. The note's hand is the page's ink, so the marks stay ink.
"""
import os
from journal import *

SEED = int(os.environ.get("SEED", 11))
PAGE_W, PAGE_H = 300, 180
pen = JournalPen(SEED)
A = lambda *p: np.array(p, float)

MID, R_MID, R_RING = A(146, 90), 17, 42
RING = [MID + R_RING * np.array([np.cos(a), np.sin(a) * 0.86]) for a in np.radians(np.arange(8) * 45 + 12)]
CROSS = A(250, 136)

pen.fill(catmull([MID + (R_MID - 3 + pen.rng.normal(0, 0.8)) * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(0, 2 * np.pi, 9, endpoint=False)], True, 8))             # the dark middle
pen.ellipse(MID, R_MID, R_MID * 0.94, rot=0, w=1.8, turns=1.12, wobble=0.4)
for c in RING:                                                                    # the ring, each mark on its own
    pen.ellipse(c, 6, 5.6, rot=pen.rng.uniform(0, 90), w=1.7, turns=1.08, wobble=0.3)

ROADS = [[RING[0] + (8, 2), (220, 104), (262, 126), CROSS, (296, 150)],
         [RING[2] + (0, 8), (150, 162), (146, 180)],
         [RING[4] + (-8, -1), (60, 82), (4, 70)],
         [RING[6] + (2, -8), (156, 24), (176, 0)],
         [(220, 104), (246, 64), (292, 40)],
         [(60, 82), (40, 132), (18, 178)]]
for r in ROADS:
    pen.line([A(*p) for p in r], w=1.5, wobble=0.6, overshoot=2)
for c in ((231, 110), (238, 72), (272, 50), (49, 104), (30, 150), (76, 82), (149, 152)):   # houses along the roads
    x, y = c
    pen.line([(x - 4, y - 4), (x + 4, y - 4), (x + 4, y + 4), (x - 4, y + 4), (x - 4, y - 3)], w=1.4, wobble=0.25)
for d in ((-6, -6), (-6, 6)):                                                     # the one mark, a plain cross
    a = CROSS + d
    pen.line([a, CROSS - d], w=1.8, wobble=0.2)

name = os.environ.get("OUT", "note_house_2")
save(pen, name, PAGE_W, PAGE_H)
