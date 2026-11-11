#!/usr/bin/env python3
"""Flag lines for the voice-pass reader: the lines briefs' must-not words, and phrases repeated across nearby lines.

Usage: linecheck.py [chapter.toml ...]   (default: every shipped and in-writing chapter)
A flag is a lead for a reader, never a verdict: word matches misfire ("stove" holds no "tove"), and a repeat can be
deliberate. Exit status is always 0. Lines are the `l_` keys of a chapter's [text] table, in file order (the order the
chapter was written in, not player order); the unwritten marker is skipped. The must-not terms are the briefs' (day two's
and day three's), as words; the briefs' rules about what a line may imply are for the reader.
"""
import re
import sys
import tomllib
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"
sys.path.insert(0, str(APP))
from ashfall_app.opening.schema import CHAPTERS, IN_WRITING, UNWRITTEN  # noqa: E402

MUST_NOT = {
    "again": r"\bagain\b",
    "warm/glow": r"\b(warm\w*|glow\w*)\b",
    "hands and heat": r"\bhands?\b.*\b(heat\w*|hot|warm\w*)\b|\b(heat\w*|hot|warm\w*)\b.*\bhands?\b",
    "animal": r"\b(wolf|wolves|howl\w*|deer|dog|dogs|animal\w*|hare|rabbit|fox|bird|birds|crow|crows)\b",
    "cart": r"\bcart\b",
    "stool": r"\bstool\b",
    "banned noun": r"\b(chequer|keels?|holders?|magic|faith|burn)\b",
}
ECHO_WORDS = 3
NEARBY = 8


def lines_of(path: Path) -> dict[str, str]:
    text = tomllib.loads(path.read_text())["text"]
    return {k: v for k, v in text.items() if k.startswith("l_") and UNWRITTEN not in v}


def proper_nouns(line: str) -> list[str]:
    """Capitalised words not at a sentence start (lines are lowercase, so any is a name or slot to look at)."""
    words = re.findall(r"(?<=[a-z,;] )[A-Z][a-z]+", line)
    return [w for w in words if w != "Lucy"]


def grams(line: str) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z']+", line.lower())
    return {tuple(w[i:i + ECHO_WORDS]) for i in range(len(w) - ECHO_WORDS + 1)}


def must_not_flags(lines: dict[str, str]) -> list[str]:
    out = []
    for key, line in lines.items():
        hits = [name for name, rx in MUST_NOT.items() if re.search(rx, line, re.I)]
        hits += [f"proper noun {w}" for w in proper_nouns(line)]
        if hits:
            out.append(f"  {key}: {', '.join(hits)}: {line}")
    return out


def echo_flags(lines: dict[str, str]) -> list[str]:
    keys = list(lines)
    seen = {k: grams(v) for k, v in lines.items()}
    out = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:i + 1 + NEARBY]:
            shared = seen[a] & seen[b]
            if shared:
                phrase = " ".join(sorted(shared)[0])
                out.append(f"  {a} / {b}: \"{phrase}\"" + (f" (+{len(shared) - 1})" if len(shared) > 1 else ""))
    return out


def main(paths: list[Path]) -> None:
    for path in paths:
        lines = lines_of(path)
        print(f"{path.name}: {len(lines)} lines")
        for title, flags in (("must-not words", must_not_flags(lines)), ("echoes", echo_flags(lines))):
            print(f" {title}: {len(flags)}")
            print("\n".join(flags))


if __name__ == "__main__":
    main([Path(a) for a in sys.argv[1:]] or [*CHAPTERS, *IN_WRITING])
    sys.exit(0)
