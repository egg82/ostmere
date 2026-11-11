"""Turn a scanned public-domain engraving into journal ink: crop, drop the paper, recolour the ink.
Usage: python3 -I ink_engraving.py <scan> <x0,y0,x1,y1> <out.png>"""
import sys
from PIL import Image, ImageOps, ImageFilter

src, box, out = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(",")), sys.argv[3]
g = ImageOps.grayscale(Image.open(src).crop(box))
g = ImageOps.autocontrast(g, cutoff=1)
# paper -> transparent, ink -> opaque, with a soft ramp so hatching keeps its weight
alpha = g.point(lambda v: 0 if v > 170 else 255 if v < 90 else int((170 - v) * 255 / 80))
alpha = alpha.filter(ImageFilter.GaussianBlur(0.4))
ink = Image.new("RGBA", g.size, (43, 36, 28, 255))
ink.putalpha(alpha)
ink.save(out)
print("wrote", out, ink.size)
