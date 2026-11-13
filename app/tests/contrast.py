"""WCAG contrast of the client's text and control colours, read from game.css (the :root tokens and the rules that pair
a colour with a background). A helper for test_client_contrast.py; no dependencies."""
import re
from dataclasses import dataclass
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "client" / "src" / "game.css"
RGB = tuple[float, float, float]
_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)|var\(\s*--[\w-]+\s*(?:,[^)]*)?\)|\btransparent\b")


@dataclass(frozen=True)
class Rule:
    selector: str
    decls: dict[str, str]


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def rules(css: str) -> list[Rule]:
    """Every style rule, @media bodies flattened in (a query narrows where a rule applies, never what it says)."""
    out: list[Rule] = []

    def walk(text: str) -> None:
        i = 0
        while True:
            open_ = text.find("{", i)
            if open_ < 0:
                return
            head, depth, j = text[i:open_].strip(), 1, open_ + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(text[j], 0)
                j += 1
            body = text[open_ + 1:j - 1]
            if head.startswith("@media"):
                walk(body)
            elif not head.startswith("@"):
                out.append(Rule(head, _decls(body)))
            i = j

    walk(strip_comments(css))
    return out


def _decls(body: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for part in re.split(r";(?![^(]*\))", body):
        name, _, value = part.partition(":")
        if value.strip():
            found[name.strip()] = value.replace("!important", "").strip()
    return found


def tokens(rs: list[Rule]) -> dict[str, str]:
    return {k: v for r in rs if r.selector == ":root" for k, v in r.decls.items() if k.startswith("--")}


def parse_color(value: str, tok: dict[str, str]) -> tuple[RGB, float] | None:
    """(rgb 0-255, alpha) of one colour term, following var(); None when it is not a plain colour."""
    value = value.strip()
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,(.*))?\)", value)
    if m:
        inner = tok.get(m[1], m[2] or "")
        return parse_color(inner, tok) if inner else None
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value)
    if m:
        h = m[1] if len(m[1]) == 6 else "".join(c * 2 for c in m[1])
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), 1.0
    m = re.fullmatch(r"rgba?\(([^)]*)\)", value)
    if m:
        n = [float(x) for x in re.split(r"[,\s/]+", m[1].strip()) if x]
        return (n[0], n[1], n[2]), (n[3] if len(n) > 3 else 1.0)
    return None


def over(top: tuple[RGB, float], under: RGB) -> RGB:
    (r, g, b), a = top
    return (r * a + under[0] * (1 - a), g * a + under[1] * (1 - a), b * a + under[2] * (1 - a))


def luminance(c: RGB) -> float:
    def lin(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2])


def ratio(a: RGB, b: RGB) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _without_gradients(value: str) -> str:
    while (m := re.search(r"(?:linear|radial|conic)-gradient\(", value)):
        depth, j = 1, m.end()
        while depth:
            depth += {"(": 1, ")": -1}.get(value[j], 0)
            j += 1
        value = value[:m.start()] + value[j:]
    return value


def background_of(r: Rule, tok: dict[str, str]) -> tuple[RGB, float] | None:
    """The solid colour a rule paints behind its content: the last colour in `background`, gradients aside."""
    value = r.decls.get("background-color") or r.decls.get("background")
    if not value:
        return None
    terms = _COLOR.findall(_without_gradients(value))
    return parse_color(terms[-1], tok) if terms else None


def font_rem(r: Rule) -> tuple[float | None, bool]:
    """(font size in rem, bold) when the rule sets them in rem."""
    size = r.decls.get("font-size", "")
    weight = r.decls.get("font-weight", "")
    short = re.match(r"(?:(\d{3}|bold)\s+)?([\d.]+)rem\b", r.decls.get("font", ""))
    if short:
        size, weight = size or short[2] + "rem", weight or (short[1] or "")
    m = re.fullmatch(r"([\d.]+)rem", size)
    return (float(m[1]) if m else None), weight in ("bold", "700", "800", "900")


def variants(rs: list[Rule]) -> dict[str, list[str]]:
    """Custom properties set outside :root (a card's --hue per .hue-N): each value is a case a rule using it must pass."""
    out: dict[str, list[str]] = {}
    for r in rs:
        if r.selector != ":root":
            for k, v in r.decls.items():
                if k.startswith("--") and v not in out.setdefault(k, []):
                    out[k].append(v)
    return out


def border_of(r: Rule, tok: dict[str, str]) -> tuple[RGB, float] | None:
    """The colour a rule draws its border (or underline) in, if it draws one."""
    for key, value in r.decls.items():
        if key.startswith("border") and not key.endswith(("radius", "width", "style", "image")):
            terms = _COLOR.findall(value)
            if terms and (c := parse_color(terms[-1], tok)):
                return c
    return None


TEXT_MIN = 4.5
"""WCAG AA for body text."""
LARGE_MIN = 3.0
"""WCAG AA for large text (24px, or 18.66px bold) and for the border of a control."""
LARGE_REM, LARGE_BOLD_REM = 1.5, 1.17
"""Large text in rem at the 16px root (the root only grows from there)."""


@dataclass(frozen=True)
class Pair:
    what: str   # the rule, and the case (a hue) when it has several
    fg: str
    bg: str
    ratio: float
    need: float


def _hex(c: RGB) -> str:
    return "#%02x%02x%02x" % tuple(round(v) for v in c)


def _cases(r: Rule, tok: dict[str, str], var: dict[str, list[str]]) -> list[tuple[str, dict[str, str]]]:
    """The rule once per value of each custom property it uses that only other rules set (a card's --hue)."""
    used = set(re.findall(r"var\(\s*(--[\w-]+)", " ".join(r.decls.values())))
    cases: list[tuple[str, dict[str, str]]] = [("", tok)]
    for name in sorted(used - tok.keys()):
        cases = [(f"{label} {name}={v}".strip(), {**t, name: v}) for label, t in cases for v in var.get(name, [])]
    return cases


def pairs(css: str) -> list[Pair]:
    """Every text colour against the surface it sits on (the rule's own background, else the page or a raised surface, whichever
    is worse), and every control's border against the same. Controls are the rules that set `cursor: pointer`."""
    rs = rules(css)
    tok, var = tokens(rs), variants(rs)
    page = parse_color(tok["--bg"], tok)
    raised = parse_color(tok["--raise"], tok)
    assert page and raised
    found: list[Pair] = []
    for r in rs:
        for label, t in _cases(r, tok, var):
            own = background_of(r, t)
            surfaces = [over(own, page[0])] if own and own[1] > 0 else [page[0], raised[0]]
            name = f"{r.selector} {label}".strip()
            fg = parse_color(r.decls["color"], t) if "color" in r.decls else None
            if fg:
                size, bold = font_rem(r)
                large = size is not None and (size >= LARGE_REM or (bold and size >= LARGE_BOLD_REM))
                text = fg
                worst = min(surfaces, key=lambda s: ratio(over(text, s), s))
                found.append(Pair(name, _hex(over(fg, worst)), _hex(worst), ratio(over(fg, worst), worst), LARGE_MIN if large else TEXT_MIN))
            edge = border_of(r, t)
            if edge and r.decls.get("cursor") == "pointer":
                line = edge
                worst = min(surfaces, key=lambda s: ratio(over(line, s), s))
                found.append(Pair(f"{name} border", _hex(over(edge, worst)), _hex(worst), ratio(over(edge, worst), worst), LARGE_MIN))
    return found
