"""Map look test: Widman 2.1 PNG stamps (CC0, kmalexander.com) composed on a dark ground, ink recoloured warm.
Usage: python3 -I compose_map.py <widman png pack dir> <out.png>"""
import glob, random, sys
from PIL import Image, ImageDraw, ImageFilter

PACK, OUT = sys.argv[1], sys.argv[2]
W, H = 780, 880
INK = (196, 178, 146)
rng = random.Random(3)

def stamps(sub):
    return sorted(f for f in glob.glob(PACK + "/" + sub + "/*.png"))

def ink(path, scale=1.0, colour=INK):
    im = Image.open(path).convert("RGBA")
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    a = im.split()[3]
    solid = Image.new("RGBA", im.size, colour + (255,))
    solid.putalpha(a)
    return solid

bg = Image.new("RGBA", (W, H), (29, 25, 19, 255))
noise = Image.effect_noise((W, H), 18).convert("L").filter(ImageFilter.GaussianBlur(1.2))
bg = Image.composite(Image.new("RGBA", (W, H), (36, 31, 24, 255)), bg, noise.point(lambda v: 90 if v > 128 else 0))

placed = []  # boxes already inked, so stamps never overlap

def fits(x, y, w, h, pad=4):
    return all(x + w + pad <= a or a + c + pad <= x or y + h + pad <= b or b + d + pad <= y for a, b, c, d in placed)

def put(path, x, y, scale=1.0, colour=INK, force=False):
    s = ink(path, scale, colour)
    left, top = int(x - s.width / 2), int(y - s.height / 2)
    if not force and not fits(left, top, s.width, s.height):
        return False
    placed.append((left, top, s.width, s.height))
    bg.alpha_composite(s, (left, top))
    return True

def scatter(paths, n, box, tries=400):
    """Place n stamps in box without overlaps, never the same stamp twice in a row (a shuffle bag)."""
    bag = []
    for _ in range(tries):
        if n == 0:
            return
        if not bag:
            bag = list(paths); rng.shuffle(bag)
        if put(bag[-1], rng.randint(box[0], box[2]), rng.randint(box[1], box[3]), rng.uniform(0.85, 1.1)):
            bag.pop(); n -= 1

ranges, mtns = stamps("Landforms/Mountain Range"), stamps("Landforms/Mountains")
forests, trees = stamps("Trees/Forest"), stamps("Trees/Individual Trees")
villages, forts = stamps("Settlements/Villages"), stamps("Settlements/Forts")

put(rng.choice(villages), 340, 600, 1.2, (232, 200, 150), force=True)
put(rng.choice(forts), 540, 400, 1.2, force=True)
for x, y in [(130, 230), (400, 170), (640, 220)]:
    put(rng.choice(ranges), x, y, 1.1)
scatter(mtns, 8, (60, 110, 720, 300))
scatter(forests, 4, (60, 660, 720, 830))
scatter(forests, 1, (520, 470, 620, 540))
scatter(trees, 12, (40, 620, 740, 850))

d = ImageDraw.Draw(bg)
def smooth(pts, n=16):
    """Catmull-Rom through the points, with a little hand wobble."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) + rng.uniform(-0.8, 0.8) for j in (0, 1)))
    return out

river = smooth([(-10, 600), (120, 586), (220, 640), (330, 618), (460, 566), (600, 604), (790, 648)])
RIVER = (150, 160, 158, 255)
d.line(river, fill=RIVER, width=3, joint="curve")
d.line([(x, y + 7) for x, y in river], fill=RIVER, width=1, joint="curve")
route = smooth([(352, 584), (400, 520), (470, 470), (528, 418)], 30)
for i in range(0, len(route) - 4, 8):
    d.line(route[i:i + 4], fill=(200, 116, 58, 255), width=3)

fog = Image.new("L", (W, H), 0)
fd = ImageDraw.Draw(fog)
for i in range(60):
    r = 640 - i * 6
    fd.ellipse((350 - r, 560 - r * 0.9, 350 + r, 560 + r * 0.9), fill=min(255, 30 + i * 8))
fog = fog.filter(ImageFilter.GaussianBlur(30))
dark = Image.new("RGBA", (W, H), (15, 13, 11, 255))
out = Image.composite(bg, dark, fog)
out.convert("RGB").save(OUT)
print("wrote", OUT, out.size)
