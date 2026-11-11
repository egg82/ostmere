"""Journal note sketch `gutter_knot`: a snare's running knot, drawn small in the old hand's pencil by a page's gutter,
with no words. Run: bash render.sh note_gutter_knot -> note_gutter_knot_ink.png

A note's sketch, not an entry's: the game sets it beside the note's words at up to 40% of the column and 8rem high
(game.css, `.journal-note-sketch`), so the page is small and wider than tall, and carries no layout furniture. The
knot is the one a snare's noose is tied with: a loop of cord whose end is passed through a small eye on the standing
part, so the loop runs closed when pulled; the standing part trails away to the stake, the tag end short. Drawn
quickly: the loop gone round twice, the eye's turns as three short crossing strokes, the run of the cord in one
line, the weights twice an entry's since the note's sketch shows at under half an entry's size. Pencil: the ink's marks recoloured to the page's pencil (#645d52, game.css `--hand-pencil`).
"""
import os
from journal import *
from ink import INK

SEED = int(os.environ.get("SEED", 7))
PAGE_W, PAGE_H = 300, 180
PENCIL = "#645d52"
pen = JournalPen(SEED)
A = lambda *p: np.array(p, float)

EYE = A(176, 96)
"""Where the end passes through the eye: the knot itself."""
LOOP = (A(110, 104), 58, 40, -8)

with pen.construction():
    hand_ellipse(pen, *LOOP, w=0.4)
loop = [EYE + (-4, -6), (150, 66), (110, 62), (68, 78), (54, 106), (66, 132), (104, 146), (146, 138), EYE + (-6, 8)]
pen.line(loop, w=2.4, wobble=0.5, passes=2, spread=1.2)
pen.line([(c[0] + 1.5, c[1] + 2.5) for c in loop[2:7]], w=1.0, wobble=0.4)        # the cord's lower edge, once
for k in range(3):                                                                # the eye's turns
    x = EYE[0] - 6 + k * 6
    pen.line([(x, EYE[1] - 9), (x + 5, EYE[1] + 1), (x + 2, EYE[1] + 9)], w=2.0, wobble=0.3)
pen.line([EYE + (8, -2), (212, 92), (246, 102), (282, 96)], w=2.2, wobble=0.6, overshoot=4)   # standing part
pen.line([EYE + (4, 8), (188, 116), (192, 128)], w=1.8, wobble=0.4)                            # tag end
for x, y in ((214, 84), (232, 108), (258, 92)):                                                # twist of the cord
    pen.stroke(np.array([(x, y), (x + 5, y + 5)]), 1.0, taper=(0.2, 0.4))

name = os.environ.get("OUT", "note_gutter_knot")
save(pen, name, PAGE_W, PAGE_H)
svg = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".svg")
text = open(svg).read()
assert INK in text, "no ink colour in the svg to turn to pencil"
open(svg, "w").write(text.replace(INK, PENCIL))
