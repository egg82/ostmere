"""Compose an Ashfall test camp from owned Time Fantasy packs and grade it three ways."""
import random, os
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

TF = os.path.expanduser("~/src/time-fantasy")
OUT = os.path.dirname(os.path.abspath(__file__))
T = 32                      # tile size at 2x
COLS, ROWS = 12, 9
rng = random.Random(7)

def load(p): return Image.open(os.path.join(TF, p)).convert("RGBA")
A5 = load("tf_ashlands/2x_RMVX/tf_A5_ashlands_2.png")
B = load("tf_ashlands/2x_RMVX/tf_B_ashlands_2.png")
FORT = load("tf_farmandfort/rpgmaker_VXa/tileB_fortA.png")
NPC = load("timefantasy_characters/timefantasy_characters/sheets/npc1.png")
NPC3 = load("timefantasy_characters/timefantasy_characters/sheets/npc3.png")
MIL = load("timefantasy_characters/timefantasy_characters/sheets/military1.png")

def tile(sheet, c, r, w=1, h=1):
    return sheet.crop((c * T, r * T, (c + w) * T, (r + h) * T))

def up(img): return img.resize((img.width * 2, img.height * 2), Image.NEAREST)

def curated(name): return up(load(f"curated/buildings/{name}.png"))

GRIME = os.environ.get("GRIME") == "1"

def chara(sheet, idx, facing=0):
    """idx 0-7 across a 4x2 sheet; facing row 0 down, 1 left, 2 right, 3 up; middle (standing) frame."""
    cx, cy = (idx % 4) * 78, (idx // 4) * 144
    im = sheet.crop((cx + 26, cy + facing * 36, cx + 52, cy + facing * 36 + 36))
    if GRIME:   # drained, darker, a little browner: worn clothes, no bright dyes
        a = im.getchannel("A"); rgb = im.convert("RGB")
        rgb = ImageEnhance.Color(rgb).enhance(0.35)
        rgb = ImageEnhance.Brightness(rgb).enhance(0.78)
        r, g, b = rgb.split()
        rgb = Image.merge("RGB", (r.point(lambda v: v * 1.06), g, b.point(lambda v: v * 0.88)))
        im = rgb.convert("RGBA"); im.putalpha(a)
    return up(im)

W, H = COLS * T, ROWS * T
scene = Image.new("RGBA", (W, H))
ground = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
for r in range(ROWS):
    for c in range(COLS):
        scene.alpha_composite(tile(A5, *rng.choice(ground)), (c * T, r * T))
for c, r in [(4, 4), (5, 4), (6, 4), (7, 4), (4, 5), (5, 5), (6, 5), (7, 5), (5, 6), (6, 6), (5, 3), (6, 3)]:
    scene.alpha_composite(tile(A5, rng.choice([1, 2, 3]), 2), (c * T, r * T))   # trodden dirt around the fire

def put(img, x, y): scene.alpha_composite(img, (int(x), int(y)))

# palisade along the top
for c0 in (0, 6):
    put(tile(FORT, 1, 0, 6, 2), c0 * T, -8)
# dead trees and wasteland litter
put(tile(B, 5, 6, 3, 6), -20, 2.6 * T)
put(tile(B, 2, 7, 2, 5), 9.6 * T, 3.2 * T)
put(tile(B, 2, 4, 2, 2), 10.4 * T, 7.2 * T)
for c, r, x, y in [(5, 1, 2.2, 7.5), (6, 1, 8.6, 7.8), (1, 1, 3.5, 2.4), (13, 0, 8.8, 2.5)]:
    put(tile(B, c, r), x * T, y * T)
for c, r, x, y in [(1, 12, 4.0, 7.6), (3, 12, 7.4, 2.6), (4, 12, 0.6, 7.6), (5, 12, 1.4, 7.9)]:
    put(tile(B, c, r), x * T, y * T)
# skull pikes by the gap in the wall
put(tile(FORT, 11, 1, 1, 3), 5.2 * T, 0.9 * T)
put(tile(FORT, 12, 1, 1, 3), 6.4 * T, 1.0 * T)
# camp
put(tile(FORT, 0, 5, 3, 5), 1.2 * T, 2.4 * T)       # wooden shelters
put(tile(FORT, 0, 5, 3, 5), 8.4 * T, 2.8 * T)
put(curated("camp_logs_stack_a"), 3.6 * T, 6.2 * T)
put(curated("camp_cooking_tripod"), 6.9 * T, 4.6 * T)
fire = curated("camp_campfire_lit")
FIRE = (5.0 * T + fire.width / 2, 4.5 * T + fire.height / 2)
put(fire, 5.0 * T, 4.5 * T)
# people around the fire: the desperate, and one guard with a spear
for sheet, idx, facing, x, y in [(NPC, 1, 2, 3.7, 4.4), (NPC, 6, 1, 7.0, 5.4), (NPC3, 2, 3, 5.2, 6.0),
                                 (NPC3, 5, 0, 4.4, 3.4), (MIL, 0, 0, 5.8, 1.9)]:
    put(chara(sheet, idx, facing), x * T, y * T)

SUF = "_grime" if GRIME else ""
scene.save(os.path.join(OUT, f"a_raw{SUF}.png"))

def grade(img, sat, tint, bright, contrast):
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(sat)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    r, g, b = rgb.split()
    r = r.point(lambda v: v * tint[0]); g = g.point(lambda v: v * tint[1]); b = b.point(lambda v: v * tint[2])
    return Image.merge("RGB", (r, g, b))

def radial(size, centre, radius, inner, outer):
    """Mask: `inner` at the centre falling to `outer` at radius (0-255)."""
    m = Image.new("L", size, outer); d = ImageDraw.Draw(m)
    steps = 40
    for i in range(steps, 0, -1):
        f = i / steps; rr = radius * f
        v = int(inner + (outer - inner) * f)
        d.ellipse((centre[0] - rr, centre[1] - rr, centre[0] + rr, centre[1] + rr), fill=v)
    return m.filter(ImageFilter.GaussianBlur(radius / 10))

def ash(img, n, colour):
    d = ImageDraw.Draw(img)
    r = random.Random(11)
    for _ in range(n):
        x, y = r.randrange(img.width), r.randrange(img.height)
        d.point((x, y), fill=colour)
        if r.random() < .3: d.point((x + 1, y), fill=colour)
    return img

def vignette(img, strength):
    mask = radial(img.size, (img.width / 2, img.height / 2), max(img.size) * 0.75, 0, strength)
    dark = Image.new("RGB", img.size, (8, 8, 12))
    return Image.composite(dark, img, mask)

# dusk: drained, cold, ash in the air
dusk = grade(scene, sat=0.55, tint=(0.95, 0.95, 1.05), bright=0.82, contrast=1.08)
dusk = vignette(dusk, 150)
dusk = ash(dusk, 260, (200, 196, 190))
dusk.save(os.path.join(OUT, f"b_dusk{SUF}.png"))

# night: near-dark, one warm pool of firelight
base = grade(scene, sat=0.5, tint=(0.8, 0.85, 1.05), bright=0.32, contrast=1.1)
lit = grade(scene, sat=0.85, tint=(1.15, 0.95, 0.75), bright=1.0, contrast=1.05)
light = radial(scene.size, FIRE, 3.4 * T, 255, 0)
night = Image.composite(lit, base, light)
night = vignette(night, 170)
night = ash(night, 160, (150, 140, 130))
night.save(os.path.join(OUT, f"c_night{SUF}.png"))

for n in (f"a_raw{SUF}", f"b_dusk{SUF}", f"c_night{SUF}"):
    im = Image.open(os.path.join(OUT, n + ".png"))
    up(im).save(os.path.join(OUT, n + "@2x.png"))
print("ok", W, H)
