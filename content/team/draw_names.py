#!/usr/bin/env python3
"""Draw a given name for each light-tier person the content names, by world.md's rule ("How names are made").

Source: Talan Gwynek, "Late 16C English Given Names", every name listed with its count in the frequency tables
(men: https://heraldry.sca.org/names/eng16/eng16mfreq.html, women: .../eng16ffreq.html, fetched 2026-10-28).
Weighted by count; virtue and common-noun names, and names the cast already holds, rejected before drawing; no two
people drawn the same name. The same seed always draws the same names, so a reviewer can check the draw.

Usage: draw_names.py  (prints "person<TAB>name" per person; the names go in each lane's name_key text)
"""
import random

SEED = 20261028
MEN = {
    "John": 1215, "Thomas": 805, "William": 786, "Richard": 534, "Robert": 372, "Henry": 204, "George": 172,
    "Edward": 169, "Nicholas": 129, "James": 114, "Francis": 86, "Christopher": 80, "Edmund": 72, "Roger": 70,
    "Peter": 58, "Anthony": 54, "Ralph": 51, "Walter": 47, "Barnard": 46, "Hugh": 46, "Humphrey": 42, "Stephen": 37,
    "Phillip": 34, "Simon": 31, "Matthew": 29, "Lawrence": 26, "David": 25, "Giles": 23, "Andrew": 20, "Leonard": 19,
    "Roland": 19, "Michael": 19, "Arthur": 18, "Charles": 15, "Alexander": 15, "Gilbert": 13, "Daniel": 12,
    "Bartholomew": 12, "Geoffrey": 11, "Godfrey": 11, "Jerome": 11, "Martin": 10, "Oliver": 10, "Morgan": 10,
    "Reginald": 10, "Samuel": 10, "Gregory": 9, "Alan": 9, "Lewis": 9, "Gabriel": 9, "Griffin": 9, "Cornelius": 9,
    "Maurice": 8, "Ambrose": 8, "Owen": 8, "Paul": 8, "Brian": 8, "Augustine": 8, "Vincent": 8, "Miles": 7,
}
WOMEN = {
    "Elizabeth": 90, "Anne": 72, "Joan": 60, "Margaret": 58, "Alice": 57, "Mary": 43, "Agnes": 40, "Catherine": 26,
    "Jane": 16, "Dorothy": 15, "Margery": 10, "Isabella": 10, "Joyce": 9, "Helen": 9, "Susanna": 8, "Eleanor": 7,
    "Christiana": 6, "Edith": 6, "Sybil": 6, "Ellen": 6, "Marian": 5, "Frances": 4, "Lucy": 4, "Grace": 4,
    "Thomasina": 4, "Barbara": 4, "Magdalen": 3, "Etheldreda": 3, "Blanche": 3, "Francisca": 3, "Emma": 3,
    "Ursula": 3, "Dionise": 3, "Martha": 3, "Judith": 3,
}
REJECTED = {"Grace"}
"""Virtue and common-noun names."""
CAST = {"Lucy", "Margaret", "Sorrel"}
"""Given names the cast already holds (content/cast.md)."""
PEOPLE = (("n2", MEN), ("n3", WOMEN), ("n4", MEN), ("n5", WOMEN), ("n6", MEN), ("n7", MEN))
"""Each light-tier person with a name_key, in the order they join, and the table their name comes from."""


def draw() -> list[tuple[str, str]]:
    rng = random.Random(SEED)
    taken = set(REJECTED | CAST)
    out = []
    for person, table in PEOPLE:
        pool = [(n, c) for n, c in table.items() if n not in taken]
        name = rng.choices([n for n, _ in pool], weights=[c for _, c in pool])[0]
        taken.add(name)
        out.append((person, name))
    return out


if __name__ == "__main__":
    for person, name in draw():
        print("%s\t%s" % (person, name))
