"""Days eight and nine's built things, warm because the camp made them: the palisade in four states and its gate, the
stakes stacked for it, the fire laid at the gap, the heap of ash off the roofs, her ash-dark ground and the fourth snare.
Pieces are Time Fantasy's: the palisade, its gate and the stakes are Farm and Fort's pointed-log fort wall (the stakes
its logs laid down), the gap fire the watch fire's stones and flames, the ash heap and the ground the pack's soil mounds.
Nothing is drawn.
Story spoilers (content/team/week-two.md, Art): never shown to the owner."""
from __future__ import annotations

from PIL import Image, ImageChops

import daythree_fire as fire
import dayfour_made as d4made
import dayone
import kit
from daytwo import cut
from kit import FORT
from place import WATCH, canvas, put

FACE = (32, 12, 128, 52)
"""The fort wall's plain upper face: pointed logs, cut above its loopholes, a little shorter than a person."""
LOW = (144, 96, 176, 128)
"""Its low stretch of pointed logs, which the gate's leaf is cut from."""
POST = (128, 12, 144, 58)
"""A wall end seen edge-on: the gate's posts."""
LOG = (153, 12, 161, 46)
"""The top of one log of the face, point and all: a stake."""
STRETCHES = {3: [(392, 450, 146)], 6: [(450, 488, 145), (488, 628, 147)],
             9: [(250, 278, 149), (304, 330, 147), (628, 768, 147)]}
"""The palisade's states by the stage that finishes each: runs of (left x, right x, feet y). The rim past the wall stub
first, then the rest of it out to the art's right edge, then the gap's two sides; stage 12 is the gate between them."""
GATE = (278, 304, 149)
STAKES = (712, 338)
"""The stakes' stack: its bottom-left, on open ground at the camp's far right edge."""
GAP_AT = (340, 405)
"""The gap fire's centre: open ground at the camp's lower middle, far from the hearth and the watch fire, clear of every
build and figure shown from the fire's stage on."""
GAP_FIRE = (round(GAP_AT[0] - WATCH[0]), round(GAP_AT[1] - WATCH[1]))
"""The gap fire from the watch fire's spot, which its art is drawn at."""
ASH_HEAP = (620, 430)
"""The ash off the roofs: its bottom-left, on open ground at the camp's far right, below the turned ground."""
ASHED = kit.Grade(sat=0.25, mul=(0.94, 0.94, 0.98), bright=0.55, contrast=1.05)
"""Her ground with the ash worked in: the turned soil gone grey-black."""
ASH_PALE = kit.Grade(sat=0.05, mul=(1.0, 1.0, 1.02), bright=1.7, contrast=0.8)
SNARE_4 = (243, 86)
"""The fourth snare from the first: on open ground at the camp's right edge, between the turned ground and the stakes."""
FLAPS = [(48, 250), (68, 341)]
"""Each flap's top-left, over the dark of a bay's open side: the first bay's (open to the right), then the second's."""
FLAP = (18, 32)


def _run(left: int, right: int, feet: int) -> Image.Image:
    face = kit.load(FORT).crop(FACE)
    out = canvas()
    x = left
    while x < right:
        piece = face.crop((0, 0, min(face.width, right - x), face.height))
        put(out, piece, x, feet - piece.height)
        x += piece.width
    return out


def palisade(stage: int) -> Image.Image:
    """The runs that stage `stage` finishes (3, 6 or 9), or the gate at 12."""
    if stage == 12:
        return gate()
    out = canvas()
    for left, right, feet in STRETCHES[stage]:
        out.alpha_composite(_run(left, right, feet))
    return out


def gate() -> Image.Image:
    """A leaf of the low pointed logs hung between two posts, the ring's last gap closed."""
    left, right, feet = GATE
    leaf = kit.load(FORT).crop(LOW)
    leaf = leaf.crop((0, 0, right - left, leaf.height))
    post = cut(FORT, POST)
    out = canvas()
    put(out, leaf, left, feet - leaf.height)
    put(out, post, left - post.width // 2, feet - post.height)
    put(out, post, right - post.width // 2, feet - post.height)
    return out


def stakes(size: int) -> Image.Image:
    """Logs laid one on another, points to the right, a little staggered: three, or six for the second size."""
    log = cut(FORT, LOG).transpose(Image.Transpose.ROTATE_270)
    out = canvas()
    x0, y = STAKES
    for i in range(3 if size == 1 else 6):
        put(out, log, x0 + (i % 2) * 3, y - (i + 1) * (log.height - 3))
    return out


def _moved(img: Image.Image, dx: int, dy: int) -> Image.Image:
    box = img.getchannel("A").getbbox()
    assert box is not None
    out = canvas()
    put(out, img.crop(box), box[0] + dx, box[1] + dy)
    return out


def gap_ring() -> Image.Image:
    return _moved(fire.watch_ring(), *GAP_FIRE)


def gap_laid() -> Image.Image:
    return _moved(fire.watch_laid(), *GAP_FIRE)


def gap_lit() -> Image.Image:
    return _moved(fire.watch_lit(), *GAP_FIRE)


def gap_light() -> Image.Image:
    return _moved(fire.watch_light(), *GAP_FIRE)


def ash_heap() -> Image.Image:
    """Two of the soil mounds, pale with ash."""
    a, b = (kit.grade(cut(d4made.FARM, box), **ASH_PALE) for box in d4made.MOUNDS[:2])
    out = canvas()
    put(out, a, ASH_HEAP[0], ASH_HEAP[1] - a.height)
    put(out, b, ASH_HEAP[0] + 14, ASH_HEAP[1] - b.height + 2)
    return out


def ashed(row: int) -> Image.Image:
    """Row `row` of the turned ground, ash-dark."""
    return kit.grade(d4made.turned(row), **ASHED)


def snare_4() -> Image.Image:
    return _moved(dayone.snare(0), *SNARE_4)



def hide_flap(n: int, bay: Image.Image) -> Image.Image:
    """The nth hide hung over a bay's open side (the hide off the kit's stretched-hide frame), cut to `bay`'s own
    drawing so it hangs inside the frame."""
    out = canvas()
    put(out, kit.resize(d4made.hide(), FLAP), *FLAPS[n - 1])
    out.putalpha(ImageChops.multiply(out.getchannel("A"), bay.getchannel("A")))
    return out
