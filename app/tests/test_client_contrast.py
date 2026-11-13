"""The client's colours keep WCAG contrast (tests/contrast.py reads them from game.css): text 4.5:1, large text, a
control's border and a mix hue 3:1. Testers called the scheme low-contrast; this holds the line for the controls, the
text and the bars."""
from tests.contrast import CSS, Pair, hue_pairs, pairs

def failing(found: list[Pair]) -> list[str]:
    return [f"{p.what}: {p.fg} on {p.bg} is {p.ratio:.2f}, needs {p.need}" for p in found
            if p.ratio < p.need]


def test_the_stylesheet_is_actually_read():
    found = pairs(CSS.read_text())
    assert len(found) > 80 and any(p.what.endswith("border") for p in found)


def test_text_and_control_borders_meet_wcag():
    assert failing(pairs(CSS.read_text())) == []


def test_the_check_fails_on_a_low_contrast_pair():
    """Control: a planted grey-on-grey rule and a dim hue label are both reported."""
    css = ":root { --bg: #121012; --raise: #19161a; }\n" \
          ".bad { color: #3a3a3a; }\n.hue-1 { --hue: #888888; }\n.ok { color: #ffffff; background: var(--hue); }\n" \
          ".big { color: #777777; font-size: 2rem; }\n"
    out = failing(pairs(css))
    assert any(".bad" in line for line in out) and any(".ok" in line for line in out)
    assert not any(".big" in line for line in out)   # 3.9:1 passes as large text


def test_every_mix_hue_stands_off_what_it_sits_on():
    found = hue_pairs(CSS.read_text())
    assert len(found) >= 18, "the six mix hues against three surfaces were not all read"
    assert failing(found) == []


def test_the_hue_check_fails_on_a_dim_hue():
    """Control: a hue too near the page is reported; a bright one is not."""
    css = ":root { --bg: #0f0f14; --track: #0b0b0f; --raise: #16161d; }\n.hue-0 { --hue: #3a3a44; }\n.hue-1 { --hue: #c9a35c; }\n"
    out = failing(hue_pairs(css))
    assert any("#3a3a44" in line for line in out) and not any("#c9a35c" in line for line in out)
