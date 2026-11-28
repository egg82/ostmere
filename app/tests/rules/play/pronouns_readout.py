"""Text that can show alone whose he/she/him/her has no one in the same text to point at, by key: the lines, the aims
(the goal line), the cards' upsides, every `pays_key` and the standing actions' labels. Each shows with nothing around
it, so a pronoun reads only against someone the text itself names: a person's {slot}, a name, or a word for a person
("the man"). Which one a pronoun means is the reader's call, so this flags and fails nothing. Keys and the pronoun
only (CLAUDE.md, "Never spoil the owner").

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
"""Words that stand for a person before or without their name."""
NONE_FLAGGED = "every pronoun has someone in its own text"


PAYS_KEY = re.compile(r'"pays_key":"([^"]+)"')
"""Every `pays_key` field in the opening's entries, read off their JSON."""


def alone_keys(o: Opening) -> set[str]:
    """The keys of text that can show alone."""
    upsides = {c.upside_key for c in o.cards if c.upside_key is not None}
    return (set(o.line_kinds) | {a.text_key for a in o.aims} | upsides | {a.label_key for a in o.standing}
            | {lb.label_key for a in o.standing for lb in a.later_labels}
            | set(PAYS_KEY.findall(o.model_dump_json())))


def unanchored(o: Opening) -> list[tuple[str, list[str]]]:
    """(key, its pronouns) for each text that can show alone with a pronoun and no person named or described in it."""
    persons = {x.id for x in o.lanes if x.name_key}
    names = {o.text[x.name_key].lower() for x in o.lanes if x.name_key and x.name_key in o.text}
    people = set(PERSON_WORDS) | names
    found: list[tuple[str, list[str]]] = []
    for key in sorted(alone_keys(o)):
        text = o.text.get(key, "")
        said = PRONOUN.findall(text)
        if not said or persons & set(SLOT.findall(text)):
            continue
        if people & set(re.findall(r"[a-z]+", text.lower())):
            continue
        found.append((key, sorted({p.lower() for p in said})))
    return found


def render(o: Opening) -> str:
    rows = unanchored(o)
    if not rows:
        return NONE_FLAGGED
    return "\n".join([f"{len(rows)} texts with a pronoun and no one in the text"] + [f"  {k}: {' '.join(p)}" for k, p in rows])


def readouts() -> dict[str, str]:
    return {"pronouns": render(load_opening())}


if __name__ == "__main__":
    print(readouts()["pronouns"])
    sys.exit(0)
