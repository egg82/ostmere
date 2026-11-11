"""Round-2 revision of creature.py (high knees, lumpy torso, skull head, relaid studies)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'creature.py')
s = open(p).read()


def rep(old, new, label):
    global s
    n = s.count(old)
    assert n == 1, (label, n)
    s = s.replace(old, new)


def cut(a_mark, b_mark, new):
    global s
    a = s.index(a_mark); b = s.index(b_mark)
    s = s[:a] + new + s[b:]


cut('torso = Part("torso"', 'parts = [torso]', '''torso = Part("torso", [(252, 214), (258, 176), (284, 146), (318, 138), (346, 150), (372, 136), (412, 140),
                       (446, 162), (460, 196), (448, 232), (414, 252), (378, 270), (342, 284), (306, 274), (276, 258),
                       (258, 240)], z=5, lw=1.9)
# legs: hip -> knee (far above the back) -> ankle -> foot; widths knob at joints
W_N = [8, 5, 9, 4.5, 7.5, 3.5, 5]
W_F = [6, 4, 7, 3.5, 6, 3, 4]
legs = [
    ("leg_fb", [(408, 214), (452, 120), (470, 58), (480, 170), (486, 318), (490, 410), (494, 488)], W_F, 1, 0.3),
    ("leg_ff", [(300, 214), (272, 130), (255, 62), (244, 180), (230, 330), (220, 410), (214, 484)], W_F, 2, 0.3),
    ("leg_nb", [(425, 225), (470, 120), (500, 40), (515, 150), (535, 300), (548, 420), (560, 506)], W_N, 6, 0.0),
    ("leg_nf", [(282, 228), (236, 120), (205, 38), (190, 150), (172, 300), (160, 420), (150, 504)], W_N, 7, 0.0),
]
''')
rep('neck = Part("neck", limb([(262, 214), (232, 246), (214, 296), (212, 346)], [16, 11, 9, 10])',
    'neck = Part("neck", limb([(262, 222), (238, 262), (232, 300), (244, 330), (240, 360)], [15, 10, 8, 8, 9])', "neck")
rep('''head = Part("head", [(200, 342), (226, 344), (232, 380), (226, 420), (212, 452), (200, 462), (190, 450), (186, 412),
                     (188, 376)]''', '''head = Part("head", [(228, 352), (252, 350), (258, 366), (250, 378), (247, 410), (240, 440), (234, 452),
                     (226, 446), (224, 412), (220, 378), (222, 362)]''', "head")
rep("# ribs pressing through the hide", '''for name, c, w, z, tone in legs:
    for j in (2, 4):
        q = np.array(c[j], float)
        for k in range(2):
            pen.stroke(np.array([q + (-w[j] - 2, pen.rng.normal(0, 1.5)), q + (w[j] + 2, pen.rng.normal(0, 1.5))]),
                       1.1, taper=(0.3, 0.3), wobble=0.4)
# ribs pressing through the hide''', "knobs")
cut('# the face: no eyes', '# ground', '''# the face: no eyes; a vertical seam down the front with teeth at the edges; nostril slits
pen.line([(232, 366), (230, 400), (229, 430), (230, 450)], w=1.5, passes=2, spread=0.4)
for k in range(8):
    y = 374 + k * 9.5
    pen.stroke(np.array([(229, y), (225, y + 3)]), 0.9, taper=(0.1, 0.6))
    pen.stroke(np.array([(232, y + 4), (236, y + 7)]), 0.9, taper=(0.1, 0.6))
pen.line([(226, 358), (246, 356), (254, 364)], w=1.1)  # brow ridge, smooth skin under it
pen.line([(238, 444), (236, 452)], w=0.8); pen.line([(232, 446), (232, 453)], w=0.8)
''')
cut('# face opening study', '# crossed-out first attempt', '''# face opening study (left-middle): the seam parted like a pod
cx = 62
for side in (-1, 1):
    pen.line([(cx, 196), (cx + side * 16, 210), (cx + side * 24, 240), (cx + side * 20, 270), (cx + side * 6, 296),
              (cx, 300)], w=1.3, passes=2, spread=0.7)
    for k in range(8):
        y = 208 + k * 11
        x0 = cx + side * (5 + 9 * np.sin((y - 196) / 104 * np.pi))
        pen.stroke(np.array([(x0, y), (x0 - side * 6, y + 2)]), 1.1, taper=(0.1, 0.7))
for k in range(12):
    y = 204 + k * 7.5
    pen.stroke(np.array([(cx - 1, y), (cx + 1, y + 5)]), 0.8, taper=(0.2, 0.2))
pen.write("the face OPENS.", 12, 322, size=17, rot=-2)
pen.write("sideways.", 22, 339, size=17, rot=-2)
pen.write("no eyes - but it", 12, 362, size=16, rot=-2)
pen.write("turned to the lamp", 12, 378, size=16, rot=-2)
pen.arrow((110, 350), (214, 400), bend=-10)

''')
cut('# foot study', '# labels on the main figure', '')
cut('# labels on the main figure', 'pen.write("Unnamed', '''# labels on the main figure
pen.write("knees ABOVE the back.", 290, 20, size=17, rot=-2)
pen.write("clicked when it moved", 296, 38, size=17, rot=-2)
pen.arrow((436, 30), (490, 42), bend=-8)
pen.arrow((292, 28), (216, 36), bend=8)
pen.write("ribs through the hide", 330, 308, size=17, rot=-2)
pen.arrow((380, 298), (370, 262), bend=-8)
''')
rep('pen.write("much longer. knees", 118, 562, size=17, rot=-3)\npen.write("ABOVE the back", 124, 579, size=17, rot=-3)',
    'pen.write("much longer.", 118, 562, size=17, rot=-3)', "fa label")
open(p, 'w').write(s)
print("written")
assert "knees ABOVE the back." in open(p).read()
