"""Extract the Gessner hound's outer silhouette from ref 011.jpg as an ordered contour.
Writes hound_mask.png (for inspection) and hound_contour.npy (crop pixel coords)."""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
X0, Y0, X1, Y1 = 330, 1500, 1480, 2600  # figure crop in the full-res page
im = np.asarray(Image.open(SRC).convert("L").crop((X0, Y0, X1, Y1)), float)
bg = ndimage.gaussian_filter(im, 40)
ink = (im < bg - 45)
GROUND = int(os.environ.get("GROUND", 960))  # crop-y where paws meet grass
ink[GROUND:] = False
ink[GROUND - 2:GROUND] = True          # seal the paws along the ground line
ink = ndimage.binary_closing(ink, iterations=int(os.environ.get("CLOSE", 3)))
outside = ~ink
lab, n = ndimage.label(outside)
bg_lab = lab[0, 0]
m = lab != bg_lab                       # everything not reachable from the page corner
m = ndimage.binary_opening(m, iterations=3)
lab, n = ndimage.label(m)
sizes = ndimage.sum(m, lab, range(1, n + 1))
m = lab == (1 + int(np.argmax(sizes)))
Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(HERE, "hound_mask.png"))


def moore(mask):
    ys, xs = np.nonzero(mask)
    i = np.argmin(ys * 100000 + xs)
    start = (ys[i], xs[i])
    nb = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    pts = [start]
    cur, d = start, 6
    for _ in range(200000):
        for k in range(8):
            dd = (d + k) % 8
            y, x = cur[0] + nb[dd][0], cur[1] + nb[dd][1]
            if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1] and mask[y, x]:
                cur = (y, x)
                d = (dd + 5) % 8
                break
        if cur == start:
            break
        pts.append(cur)
    return np.array([(x, y) for y, x in pts], float)


c = moore(m)
np.save(os.path.join(HERE, "hound_contour.npy"), c)
print("contour points", len(c), "bbox", c.min(0), c.max(0))
