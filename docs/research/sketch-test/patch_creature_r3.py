"""Round-3 revision of creature.py: reverse ankles, sagging asymmetric torso, side ribs only,
hooked fang and split-flap face study instead of stitched ovals."""
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


cut('torso = Part("torso"', '# legs: hip', '''torso = Part("torso", [(252, 214), (256, 172), (276, 140), (306, 126), (340, 140), (366, 132), (410, 150),
                       (440, 178), (452, 210), (436, 238), (404, 250), (372, 276), (346, 302), (326, 288), (300, 268),
                       (272, 256), (256, 240)], z=5, lw=1.9)
''')
cut('legs = [', 'parts = [torso]', '''legs = [
    ("leg_fb", [(408, 214), (452, 120), (470, 58), (482, 170), (512, 300), (490, 400), (494, 488)], W_F, 1, 0.3),
    ("leg_ff", [(300, 214), (272, 130), (255, 62), (244, 180), (206, 310), (226, 400), (214, 484)], W_F, 2, 0.3),
    ("leg_nb", [(425, 225), (470, 120), (500, 40), (518, 150), (566, 296), (546, 410), (560, 506)], W_N, 6, 0.0),
    ("leg_nf", [(282, 228), (236, 120), (205, 38), (186, 150), (140, 296), (170, 404), (150, 504)], W_N, 7, 0.0),
]
''')
cut('# ribs pressing through the hide', '# the face: no eyes', '''# ribs pressing through the hide: short arcs on the flank only, raked back
for i in range(6):
    x = 306 + i * 19
    pen.line([(x, 176 + i * 2), (x + 12, 200 + i), (x + 14, 224 - i)], w=0.9, wobble=0.5, passes=2, spread=0.6)
pen.line([(300, 262), (330, 272), (350, 290)], w=0.6, wobble=0.6)  # sag fold
pen.line([(312, 252), (346, 262), (370, 262)], w=0.5, wobble=0.6)
pen.line([(275, 150), (320, 134), (366, 140), (420, 156)], w=0.7, wobble=0.6)  # spine ridge
for i in range(9):  # spine knobs as ticks
    x = 286 + i * 17
    y = 137 + 6 * abs(np.sin(i / 3.0))
    pen.stroke(np.array([(x, y), (x + 3, y - 7)]), 1.3, taper=(0.2, 0.5))
''')
cut('# tooth (top-left)', 'pen.write("tooth, from the ford."', '''# tooth (top-left): hooked fang, forked root
fang = [(40, 30), (54, 28), (60, 50), (62, 78), (58, 104), (48, 124), (36, 132), (42, 114), (46, 92), (44, 66), (38, 52)]
pen.line(fang + [fang[0]], w=1.2, passes=2, spread=0.6)
pen.line([(40, 30), (34, 14), (38, 10)], w=1.0); pen.line([(54, 28), (58, 12), (62, 14)], w=1.0)  # roots
pen.line([(38, 52), (48, 50), (60, 50)], w=0.7)  # gum line
for k in range(9):
    y = 58 + k * 7
    pen.stroke(np.array([(52 - k * 0.5, y), (60 - k * 0.9, y + 4)]), 0.55, taper=(0.1, 0.4))
''')
cut('# face opening study', 'pen.write("the face OPENS."', '''# face opening study (left-middle): the head split, two flaps peeled outward, teeth on the inner edges
cx = 62
for side in (-1, 1):
    outer = [(cx + side * 3, 196), (cx + side * 24, 214), (cx + side * 40, 246), (cx + side * 34, 280), (cx + side * 12, 302)]
    inner = [(cx + side * 3, 196), (cx + side * 9, 222), (cx + side * 14, 250), (cx + side * 10, 280), (cx + side * 12, 302)]
    pen.line(outer, w=1.4, passes=2, spread=0.7)
    pen.line(inner, w=1.0, passes=1)
    for k in range(7):
        t = (k + 0.5) / 7
        y = 204 + t * 92
        x0 = cx + side * (4 + 10 * np.sin(t * np.pi))
        pen.stroke(np.array([(x0, y), (x0 - side * 7, y + 3)]), 1.1, taper=(0.1, 0.7))
for k in range(16):  # dark throat between the flaps
    y = 210 + k * 5.5
    w = 3 + 6 * np.sin((y - 200) / 100 * np.pi)
    pen.stroke(np.array([(cx - w, y), (cx + w, y + 3)]), 0.7, taper=(0.1, 0.1))
''')
open(p, 'w').write(s)
t = open(p).read()
assert "hooked fang" in t and "split, two flaps" in t and "(566, 296)" in t
print("written")
