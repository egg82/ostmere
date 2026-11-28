"""Fixture content for the casting contract tests (api/contract/casting.txt, "CASTING"), built from that part and the
loader's and engine's public entry points that existed before it. A chapter is written as text, merged onto the opening
alone, and played through `to_rules`, `decide` and `advance`.

Four people t_a, t_b, t_c, t_m (declared in that order; t_m is in the group t_p), a pooled lane t_p and a station t_pot.
Every lane but the station has two town cards, `{lane}_chop` and `{lane}_haul`, of 10 s a completion. The people all join at
0 (t_c's join is written first, so the order they joined is not the order they are declared). The town mix holds the shares a
test names, and a cast lands at CAST_AT, which no completion is due at: a card at a share of s basis points has done
floor((CAST_AT * s) / 100000) completions then."""
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from ashfall_app.api.service import Game
from ashfall_app.engine import (
    AfterTime, CardId, CardShare, Mix, MixId, Order, Rules, Save, SaveMix, SetOrders, SwitchMix, Unlock, UnlockKind,
    advance, decide, new_save, view,
)
from ashfall_app.rules.schema import OPENING, Opening, load_opening, to_rules
from ashfall_app.saves.ruleset import ruleset

PEOPLE = ("t_a", "t_b", "t_c", "t_m")
CAST_AT = 205
TOWN = MixId("town:main")
LEAD = "{ role = \"lead\", label_key = \"t_role\", patterns = [\"{lane}_chop\"] }"


def kills(*rows: int) -> pytest.MarkDecorator:
    """Marks the test as one that must go red for these rows of MUTANTS.txt."""
    return pytest.mark.kills(*rows)


def feature(role: str, lane: str) -> Unlock:
    return Unlock(UnlockKind.FEATURE, f"{role}_{lane}")


def shares(**by_card: int) -> dict[str, int]:
    """Basis points by card id, e.g. shares(t_a_chop=1000)."""
    return dict(by_card)


def _card(pattern: str, label: str, store: str) -> str:
    lanes = ", ".join(f'"{x}"' for x in PEOPLE)
    return (f'[[town_cards]]\nid = "{pattern}"\nlanes = [{lanes}]\nkinds = ["t_work"]\npresentation = "action"\nlabel_key = "{label}"\n'
            f'upside_key = "t_up"\nwork_s = 10\nmakes = [{{ store = "{store}", items_per_hour = 1 }}]\n\n')


def _lane(lane: str, extra: str = "") -> str:
    return (f'[[lanes]]\nid = "{lane}"\nlabel_key = "t_l_{lane}"\nruled = true\n{extra}\n')


def _person(lane: str, extra: str = "") -> str:
    return _lane(lane, f'name_key = "t_n_{lane}"\ntold = "mention"\n{extra}')


def _join(lane: str, at: int, crew: bool = False) -> str:
    cards = f'{{ unlock_kind = "card", id = "{lane}_chop" }}, {{ unlock_kind = "card", id = "{lane}_haul" }}'
    if lane == "t_m":
        cards += ', { unlock_kind = "card", id = "t_p_chop" }, { unlock_kind = "card", id = "t_p_haul" }'
    return (f'[[triggers]]\nid = "t_join_{lane}"\nwhen = {{ test = "after_time", value = {at} }}\noutcome = {{ '
            f'unlocks = [{cards}], joins = [{{ lane = "{lane}", mix = "town:main", card = "{"t_p" if crew else lane}_chop", '
            f'own_split = {"false" if crew else "true"} }}] }}\n\n')


def _leave(lane: str, at: int) -> str:
    return (f'[[triggers]]\nid = "t_leave_{lane}"\nwhen = {{ test = "after_time", value = {at} }}\n'
            f'outcome = {{ leaves = [{{ lane = "{lane}" }}] }}\n\n')


def chapter(joins: Mapping[str, int] | None = None, casts: str | None = LEAD, leaves: Mapping[str, int] | None = None,
            cast_at: int = CAST_AT, cast_extra: str = "", extra: str = "", extra_text: str = "", extra_kinds: str = "",
            later: str = "", crew: bool = False, cast_id: str = "t_cast") -> str:
    """The chapter. `casts` is the body of the cast trigger's `casts = [ ... ]` (None: no cast trigger at all, the
    control), the trigger being `cast_id` at `cast_at`; `cast_extra` more fields of that outcome; `extra` more TOML;
    `extra_text` more `[text]` lines; `extra_kinds` more `[line_kinds]`; `later` the label t_a's lane takes once something
    is unlocked (a `later_labels` entry). People join at 0 unless `joins` says when (-1: never, by a trigger of their
    own); with `crew` t_m joins the crew of t_p (its group's cards, no split of its own)."""
    at = {**{p: 0 for p in PEOPLE}, **(joins or {})}
    out = ['version = 1\n\n[[stores]]\nid = "t_heap"\nlabel_key = "t_s_heap"\ncap_items = 20\n\n[[stores]]\nid = "t_load"\nlabel_key = "t_s_load"\ncap_items = 20\n\n']
    out.append(_lane("t_p", 'pooled = true\nkind = "t_work"\n'))
    out.append(_lane("t_pot", "station = true\n"))
    for p in PEOPLE:
        out.append(_person(p, ('group = "t_p"\n' if p == "t_m" else "") + (f"later_labels = [{later}]\n" if p == "t_a" and later else "")))
    out += [_card("{lane}_chop", "t_c_chop", "t_heap"), _card("{lane}_haul", "t_c_haul", "t_load")]
    for p in ("t_c", "t_a", "t_b", "t_m"):
        if at[p] >= 0:
            out.append(_join(p, at[p], crew and p == "t_m"))
    for p, t in (leaves or {}).items():
        out.append(_leave(p, t))
    line = 'line_keys = ["t_l_cast"], ' if casts is not None and "t_l_cast" in extra_text else ""
    if casts is not None:
        out.append(f'[[triggers]]\nid = "{cast_id}"\nwhen = {{ test = "after_time", value = {cast_at} }}\n'
                   f'outcome = {{ {line}casts = [{casts}]{cast_extra} }}\n\n')
    kinds = ""
    if "t_l_cast" in extra_text:
        kinds += 't_l_cast = "story"\n'
    names = "".join(f't_n_{p} = "{p[2:].upper()}name"\nt_l_{p} = "{p}"\n' for p in PEOPLE)
    out.append(PEOPLE_TOML)
    out.append(f'{extra}\n[line_kinds]\n{kinds}{extra_kinds}\n[text]\nt_up = "what it is for"\nt_s_heap = "Heap"\nt_s_load = "Load"\nt_l_t_p = "Crew"\n'
               f't_l_t_pot = "Pot"\nt_c_chop = "Chop"\nt_c_haul = "Haul"\nt_role = "Role"\n{names}{WORDS}{extra_text}\n')
    return "".join(out)


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "casting_chapter.toml"
    path.write_text(text)
    return path


def opening_of(tmp_path: Path, **kw: Any) -> Opening:
    return load_opening(OPENING, (write(tmp_path, chapter(**kw)),))


def rules_of(tmp_path: Path, **kw: Any) -> Rules:
    return to_rules(opening_of(tmp_path, **kw))


def refused(tmp_path: Path, entry: str, **kw: Any) -> None:
    """The plain chapter loads (the control), and this one raises ValueError with `entry` in its message."""
    rules_of(tmp_path)
    with pytest.raises(ValueError, match=entry):
        rules_of(tmp_path, **kw)


def scene(r: Rules, by_card: Mapping[str, int]) -> Save:
    """At 0, after the joins: the town mix holds `by_card`, and runs."""
    if not by_card and not any(m.id == TOWN for m in new_save(r).mixes):
        return new_save(r)
    mix = Mix(TOWN, tuple(CardShare(CardId(c), bp) for c, bp in by_card.items()))
    s = decide(new_save(r), r, 0, SaveMix(mix))
    return decide(s, r, 0, SetOrders((Order(AfterTime(0), SwitchMix(TOWN)),)))


def at(r: Rules, by_card: Mapping[str, int], t: int = CAST_AT + 5) -> Save:
    return advance(scene(r, by_card), r, t)


def held(s: Save, r: Rules, role: str = "lead") -> list[str]:
    """The lanes whose cast feature for `role` the view holds, in view order."""
    prefix = f"{role}_"
    return [u.id[len(prefix):] for u in view(s, r).unlocked if u.kind == UnlockKind.FEATURE and u.id.startswith(prefix)]


def completions(s: Save, r: Rules, card: str) -> int:
    return next(c.completions for c in (*view(s, r).cards, *view(s, r).completed) if c.card == card)


def game(tmp_path: Path, **kw: Any) -> Game:
    o = opening_of(tmp_path, **kw)
    return Game(o, ruleset(o, "test", 1))


def lead_of(tmp_path: Path, by_card: Mapping[str, int], t: int = CAST_AT + 5, **kw: Any) -> list[str]:
    """The lanes holding the lead's feature after the play, the cast being every `kw` says (default: lead by chops)."""
    r = rules_of(tmp_path, **kw)
    return held(at(r, by_card, t), r)


def counts(tmp_path: Path, by_card: Mapping[str, int], **kw: Any) -> dict[str, int]:
    """Every card's completions at the cast's instant on the control (no cast): the premise a test states its numbers on."""
    r = rules_of(tmp_path, **{**kw, "casts": None})
    s = at(r, by_card, CAST_AT)
    return {c.card: c.completions for c in (*view(s, r).cards, *view(s, r).completed)}


PEOPLE_TOML = (
    '[[people.came]]\nat_least = 1\nkeys = [' + ", ".join(f'"t_came_{n}"' for n in range(1, 7)) + ']\n\n'
    '[[people.went]]\nat_least = 1\nkeys = [' + ", ".join(f'"t_went_{n}"' for n in range(1, 7)) + ']\n\n')
WAYS = ("one", "two", "three", "four", "five", "six")
WORDS = "".join(f't_came_{n} = "One more, way {w}."\nt_went_{n} = "One fewer, way {w}."\n' for n, w in enumerate(WAYS, 1))


SLOT = re.compile(r"@[A-Z_]+@")
