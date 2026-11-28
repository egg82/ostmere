"""Lines whose he/she/him/her has no one in the same line to point at, by id. A line can show alone, with none of the
lines around it, so a pronoun reads only against someone the line itself names: a person's {slot}, a name, or a word
for a person ("the man"). Which one a pronoun means is the reader's call, so this flags and fails nothing. Ids and the
pronoun only (CLAUDE.md, "Never spoil the owner").

    python -m tests.rules.play.pronouns_readout     # from app/: print it
"""
import re
import sys

from ashfall_app.rules.schema import Opening, load_opening

NAMES = ("pronouns",)
PRONOUN = re.compile(r"\b(he|him|his|himself|she|her|hers|herself)\b", re.I)
SLOT = re.compile(r"\{(\w+)\}")
PERSON_WORDS = ("man", "woman", "women", "newcomer", "newcomers", "stranger", "figure", "child", "wife", "husband",
                "brother", "sister", "son", "mother", "bedesman", "someone", "one")
"""Words that stand for a person in a line before or without their name."""
NONE_FLAGGED = "every line's pronouns have someone in the line"


def unanchored(o: Opening) -> list[tuple[str, list[str]]]:
    """(line key, its pronouns) for each line with a pronoun and no person named or described in it."""
    names = {o.text[x.name_key].lower() for x in o.lanes if x.name_key and x.name_key in o.text}
    people = set(PERSON_WORDS) | names
    found: list[tuple[str, list[str]]] = []
    for key in sorted(o.line_kinds):
        text = o.text.get(key, "")
        said = PRONOUN.findall(text)
        if not said or SLOT.search(text):
            continue
        if people & set(re.findall(r"[a-z]+", text.lower())):
            continue
        found.append((key, sorted({p.lower() for p in said})))
    return found


def render(o: Opening) -> str:
    rows = unanchored(o)
    if not rows:
        return NONE_FLAGGED
    return "\n".join([f"{len(rows)} lines with a pronoun and no one in the line"] + [f"  {k}: {' '.join(p)}" for k, p in rows])


def readouts() -> dict[str, str]:
    return {"pronouns": render(load_opening())}


if __name__ == "__main__":
    print(readouts()["pronouns"])
    sys.exit(0)
