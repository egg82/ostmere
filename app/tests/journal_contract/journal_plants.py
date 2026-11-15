"""The planted wrong implementations of MUTANTS.txt, as exact edits to the composer's source (paths under
`ashfall_app/saves/`). A row with several variants ("2a", "2b") plants each of its alternatives on its own; `E1` and
`E2` are the equivalents, expected to survive. `plant_mutants.py` applies them one at a time to a copy of the tree."""

type Edit = tuple[str, str, str]
"""(file, old text, new text); the old text must occur exactly once."""

J, H, L, N = "journal.py", "journal_composer/history.py", "journal_composer/ledger.py", "journal_composer/numbers.py"
B, T, O = "journal_composer/bag.py", "journal_composer/telling.py", "journal_composer/owed.py"
W, D = "journal_composer/own.py", "journal_composer/day.py"
MK, P = "journal_composer/marks.py", "journal_composer/page.py"

KEY = 'sha256(f"{save_id}|journal|{day}|{subject}|{purpose}"'
CATCH_UP = "    for t in catchups(composed, history, subjects):\n        page.write(t)\n"
AWAY_DAY = '    if away(history, subjects, day):\n        page.gap = "away"\n        return page.done()\n'
AWAY_MOMENT = '        if s.away_days > 0:\n            page.gap = "away"\n            return False\n'
BUSY = "        if len(page.shown) > page.habits.busy_ratio * room:"
BUSY_BLOCK = BUSY + '\n            page.gap = "busy"\n            return False\n'
ROOM = "    room, diligent = budget(settled, habits), diligence(settled, habits)"
ROOMLEFT = "len(page.notes) < room"
TOLD = "s, page.told(s.id), history, page.habits, m.change)"
MOMENT_SORT = "key=lambda p: p[0].at)"
END_FIXES = ("    if page.notes or fixes:\n"
             "        for t in lates(page.save_id, page.composed, list(page.subjects.values()), page.habits):\n"
             "            page.write(t)\n    for t in fixes:\n        page.write(t)\n")
MARK_ROLL = 'roll(save_id, day, kind, "mark")'
LATE_ROLL = 'roll(save_id, yesterday.day, s.id, "late") < habits.late_rate'
WROTE = 'if n.slot not in ("late", "correction")}'
CARE_W = "    return faded(fade, 0 if change else told)"
EARLIER = "if d < day for k in keys}"
AWAY_RANGE = "range(day - s.away_days + 1, day)"
SORT_FIRST = "    for sid in sorted(first_at, key=lambda i: (first_at[i], i)):"
FIRST_AT = "            first_at.setdefault(s.id, history.first_at(s.id, d))\n"
BUDGET = "    return math.floor(habits.lines_floor + span * 0.5 ** (settled / habits.lines_halflife) + 0.5)"
BUDGET_RAW = "habits.lines_floor + span * 0.5 ** (settled / habits.lines_halflife)"
WRITTEN = "    written = sum(1 for r in composed if r.notes)"
MISREMEMBER_IF = '    if slot == "first" and s.misremember and s.correction:'
BAND = "    reached = [b for b in subject.mention if b.at_least <= count]"

PLANTS: dict[str, list[Edit]] = {
    "1": [(J, f"digest = hashlib.{KEY}.encode()).digest()\n    return int.from_bytes(digest[:8], \"big\") / 2**64",
           'return (hash((save_id, "journal", day, subject, purpose)) % 2**61) / 2**61')],
    "2a": [(J, KEY, 'sha256(f"{save_id}|journal|{day}|{subject}"')],
    "2b": [(J, KEY, 'sha256(f"{save_id}|journal|0|{subject}|{purpose}"')],
    "2c": [(J, KEY, 'sha256(f"0|journal|{day}|{subject}|{purpose}"')],
    "3a": [(J, 'int.from_bytes(digest[:8], "big") / 2**64', 'int.from_bytes(digest[-8:], "little") / (2**64 - 1)')],
    "3b": [(J, KEY, 'sha256(f"{save_id}|{day}|{subject}|{purpose}"')],
    "3c": [(J, KEY, 'sha256(f"{save_id}:journal:{day}:{subject}:{purpose}"')],
    "4": [(D, "    for m in moments(lines, subjects, day):\n", "    for m in set(moments(lines, subjects, day)):\n")],
    "5": [(H, "for k in history.keys(subject, day))", "for k in history.keys(subject, day)[:1])")],
    "6": [(J, "import hashlib\n", "import hashlib\nimport itertools\n_COUNTER = itertools.count()\n"),
          (J, KEY, 'sha256(f"{save_id}|journal|{next(_COUNTER)}"')],
    "7": [(H, "line.at // DAY_S", "(line.at + 1) // DAY_S")],
    "8a": [(D, "    if any(line.at >= (day + 1) * DAY_S for line in lines):\n", "    if False:\n")],
    "8b": [(D, "    if [r.day for r in composed] != list(range(day)):\n", "    if False:\n")],
    "9": [(D, AWAY_DAY + CATCH_UP, CATCH_UP + AWAY_DAY)],
    "10": [(H, "    by_source = {s.source: s.id for s in subjects}",
            "    by_source = {s.source.id: s.id for s in subjects}"),
           (H, "by_source.get(line.source) if", "by_source.get(line.source.id) if")],
    "10b": [(D, "    crowds: list[Subject] = []\n",
             "    crowds: list[Subject] = []\n"
             "    page.shown.update(f'noise{i}' for i, x in enumerate(lines) if x.source is None and x.at // DAY_S == day)\n")],
    "11": [(D, BUSY, "        if sum(len(history.keys(i, page.day)) for i in page.shown) > page.habits.busy_ratio * room:")],
    "12": [(W, "    must = is_must(s, told)\n", "    must = False\n")],
    "13": [(T, 'return subject.kind == "routine" and told == 0 and bool(subject.first)',
            'return subject.kind == "routine" and bool(subject.first)')],
    "14": [(T, 'return "repeat" if subject.repeat else None', 'return "repeat" if subject.repeat else "first"')],
    "15": [(T, '        return "mention"\n', '        return "mention" if subject.repeat else None\n')],
    "16a": [(T, 'subject.kind in ("beat", "person")', 'subject.kind in ("beat", "person", "worry")')],
    "16b": [(T, 'subject.kind in ("beat", "person")', 'subject.kind in ("beat",)')],
    "17": [(T, "    if told == 0:\n", '    if told == 0 or subject.kind == "beat":\n')],
    "18": [(O, "    for d in gap_run(composed):", "    for d in gap_run(composed)[:0]:")],
    "19": [(O, FIRST_AT, FIRST_AT
            + "    pairs = [(d, s.id) for d in gap_run(composed) for s in showing(history, subjects, d)]\n"),
           (O, SORT_FIRST, "    for _, sid in sorted(pairs):")],
    "20": [(D, CATCH_UP, "    for t in (catchups(composed, history, subjects) if moments(lines, subjects, day) else []):\n"
                         "        page.write(t)\n")],
    "21": [(O, "        if t is not None and is_must(by_id[sid], tellings(composed, sid)):",
            "        if t is not None:")],
    "22": [(P, "n.subject == subject and n.slot in TELLINGS)", 'n.subject == subject and n.slot in TELLINGS and n.slot != "catchup")')],
    "23": [(D, "    for t in catchups(composed, history, subjects):\n",
            "    for t in catchups([ComposedDay(r.day, r.notes, compose(save_id, r.day, [x for x in lines if x.at < (r.day + 1) * DAY_S],"
            " composed[:r.day], subjects, habits, True).gap, r.marks) for r in composed], history, subjects):\n")],
    "24": [(W, CARE_W, "    return faded(fade, 0 if change else sum(1 for d in history.by_subject[s.id] if d < day))")],
    "25": [(L, '"misremember", "mention"})', '"misremember", "mention", "late", "correction"})')],
    "26a": [(W, CARE_W, "    return faded(fade, told)")],
    "26b": [(H, EARLIER, "if d <= day for k in keys}")],
    "26c": [(H, EARLIER, "if d == min(history.by_subject[subject]) < day for k in keys}")],
    "27a": [(H, "    while history.shows(subject, day - r):\n        r += 1\n    return r",
             "    return sum(1 for d in history.by_subject.get(subject, {}) if d <= day)")],
    "27b": [(N, "(days_in_a_row - 1)", "days_in_a_row")],
    "28": [(N, "    return min(1.0, press.base * (1 + press.press * (days_in_a_row - 1)))",
            "    return press.base * (1 + press.press * (days_in_a_row - 1))")],
    "29a": [(D, "diligence(settled, habits)", "diligence(float(day), habits)")],
    "29b": [(D, ROOM, "    room, diligent = budget(float(day), habits), diligence(settled, habits)")],
    "30a": [(L, WRITTEN, "    written = sum(len(r.notes) for r in composed)")],
    "30b": [(L, WRITTEN, "    written = sum(1 for r in composed if r.notes or r.gap)")],
    "30c": [(L, "    beat_notes = sum(1 for r in composed for n in r.notes if n.subject in beats)",
             "    beat_notes = sum(1 for r in composed if any(n.subject in beats for n in r.notes))")],
    "30d": [(L, "    return max(0.0, written - habits.beat_refresh * beat_notes)",
             "    return written - habits.beat_refresh * beat_notes")],
    "31a": [(N, BUDGET, f"    return round({BUDGET_RAW})")],
    "31b": [(N, BUDGET, f"    return math.floor({BUDGET_RAW})")],
    "31c": [(N, BUDGET, f"    return math.ceil({BUDGET_RAW})")],
    "33": [(D, ROOMLEFT, "len([n for n in page.notes if n.slot != 'catchup']) < room")],
    "34": [(D, ROOMLEFT, "len(page.notes) + len(lates(page.save_id, page.composed, list(page.subjects.values()), page.habits)) < room")],
    "36a": [(H, AWAY_RANGE, "range(day - s.away_days, day)")],
    "36b": [(H, AWAY_RANGE, "range(day - s.away_days + 2, day)")],
    "36c": [(H, AWAY_RANGE, "range(day - s.away_days + 1, day + 1)")],
    "37": [(D, "> page.habits.busy_ratio * room:", ">= page.habits.busy_ratio * room:")],
    "38": [(D, BUSY, "        if len(page.shown) + len(catchups(page.composed, history, list(page.subjects.values())))"
                     " > page.habits.busy_ratio * room:")],
    "39": [(D, AWAY_MOMENT + BUSY_BLOCK, BUSY_BLOCK + AWAY_MOMENT)],
    "39b": [(D, AWAY_MOMENT, AWAY_MOMENT.replace("            return False\n", ""))],
    "40": [(D, "> page.habits.busy_ratio * room:", "> page.habits.busy_ratio * page.habits.lines_start:")],
    "41": [(D, "    if page.notes or fixes:\n", "    if page.notes or fixes or lates(page.save_id, page.composed, list(page.subjects.values()), page.habits):\n")],
    "42": [(O, "    yesterday = composed[-1]",
            "    yesterday = next((r for r in reversed(composed) if r.notes), composed[-1])")],
    "43": [(O, LATE_ROLL, 'roll(save_id, yesterday.day + 1, s.id, "late") < habits.late_rate')],
    "44a": [(O, WROTE, 'if n.slot != "correction"}')],
    "44b": [(O, WROTE, 'if n.slot == "first"}')],
    "45": [(O, '        t = plain(s, "late")',
            '        t = plain(s, "late") or Telling(s.id, "late", s.first, "late")')],
    "46a": [(O, '        t = plain(by_id[sid], "catchup")',
             '        t = plain(by_id[sid], "misremember" if by_id[sid].correction else "catchup")')],
    "46b": [(W, MISREMEMBER_IF, '    if slot in ("first", "repeat") and s.misremember and s.correction:')],
    "46c": [(W, MISREMEMBER_IF, '    if slot == "first" and s.misremember:')],
    "47a": [(O, "wrong[-1] + wait > day:", "wrong[-1] + wait - 1 > day:")],
    "47b": [(O, "wrong[-1] + wait > day:", "wrong[-1] + wait != day:")],
    "47c": [(O, '    return not any(n.subject == subject and n.slot == "correction"',
             '    return True or not any(n.subject == subject and n.slot == "correction"')],
    "47d": [(D, "    for t in fixes:\n        page.write(t)\n", "    for t in (fixes if page.notes else []):\n        page.write(t)\n")],
    "48a": [(O, LATE_ROLL, 'roll(save_id, yesterday.day, s.id, "late") < 1 - habits.late_rate')],
    "48b": [(W, '"misremember") < habits.misremember_rate', '"misremember") > habits.misremember_rate')],
    "49a": [(O, SORT_FIRST, "    for sid in sorted(first_at):")],
    "49b": [(O, SORT_FIRST, "    for sid in sorted(first_at, key=lambda i: (-first_at[i], i)):")],
    "49c": [(O, FIRST_AT, "            first_at.setdefault(s.id, d)\n")],
    "50b": [(H, MOMENT_SORT, "key=lambda p: p[1].id)")],
    "50d": [(H, MOMENT_SORT, "key=lambda p: -p[0].at)")],
    "50e": [(H, "            days[day] = min(days.get(day, line.at), line.at)",
             "            days[day] = max(days.get(day, line.at), line.at)")],
    "50f": [(H, MOMENT_SORT, "key=lambda p: (p[0].at, p[1].id))")],
    "51a": [(D, CATCH_UP, ""), (D, "    if ended:\n", CATCH_UP + "    if ended:\n")],
    "51b": [(D, END_FIXES, "    due = bool(page.notes or fixes)\n    for t in fixes:\n        page.write(t)\n    if due:\n"
                           "        for t in lates(page.save_id, page.composed, list(page.subjects.values()), page.habits):\n"
                           "            page.write(t)\n")],
    "51c": [(O, '    for s in sorted(subjects, key=lambda x: x.id):\n        t = plain(s, "late")',
             '    for s in subjects:\n        t = plain(s, "late")')],
    "51d": [(O, '    for s in sorted(subjects, key=lambda x: x.id):\n        t = plain(s, "correction")',
             '    for s in subjects:\n        t = plain(s, "correction")')],
    "53": [(B, "    return min(unused, key=lambda k: _shuffle(save_id, subject, bag, round_no, k))",
            "    return min(keys, key=lambda k: _shuffle(save_id, subject, bag, len(stored), k))")],
    "54": [(B, "    stored = drawn(composed, t.subject, t.slot, t.keys)", "    stored: list[str] = []")],
    "55a": [(B, "    stored = drawn(composed, t.subject, t.slot, t.keys)",
             "    stored = [n.key for r in composed for n in r.notes if n.subject == t.subject]")],
    "55b": [(B, "    stored = drawn(composed, t.subject, t.slot, t.keys)",
             "    stored = [n.key for r in composed for n in r.notes if n.subject == t.subject and n.slot == t.slot]")],
    "56a": [(T, "    return max(reached, key=lambda b: b.at_least) if reached else None",
             "    return min(reached, key=lambda b: b.at_least) if reached else None")],
    "56b": [(T, BAND, "    reached = [b for b in subject.mention if b.at_least > count]"),
            (T, "    return max(reached, key=lambda b: b.at_least) if reached else None",
             "    return min(reached, key=lambda b: b.at_least) if reached else None")],
    "57": [(D, TOLD, "s, sum(1 for d in history.by_subject[s.id] if d < page.day)\n            + len([n for n in page.notes if n.subject == s.id]), history, page.habits, m.change)")],
    "58a": [(L, WRITTEN, "    written = sum(1 for r in composed"
                         " if any(n.subject in {s.id for s in subjects} for n in r.notes))")],
    "58b": [(P, "return tellings(self.composed, subject) + ",
             "return sum(1 for r in self.composed for n in r.notes if n.subject == subject and n.slot in TELLINGS"
             " and n.key in (*self.subjects[subject].first, *self.subjects[subject].repeat, *self.subjects[subject].catchup,"
             " *self.subjects[subject].misremember, *(k for b in self.subjects[subject].mention for k in b.keys))) + ")],
    "59a": [(MK, MARK_ROLL, 'roll(save_id, day, note.subject, "mark")')],
    "59b": [(MK, MARK_ROLL, 'roll(save_id, 0, kind, "mark")')],
    "59c": [(MK, MARK_ROLL, 'roll(0, day, kind, "mark")')],
    "59d": [(MK, MARK_ROLL, 'roll(save_id, day, kind, "write")')],
    "59e": [(MK, MARK_ROLL + " <", MARK_ROLL + " >")],
    "59f": [(MK, "< getattr(habits.marks, kind)", "< 1 - getattr(habits.marks, kind)")],
    "59g": [(MK, "getattr(habits.marks, kind)", "habits.marks.smudge")],
    "60a": [(MK, 'ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})', 'ABOUT_ANOTHER_DAY = frozenset()')],
    "60b": [(MK, 'ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})', 'ABOUT_ANOTHER_DAY = frozenset({"correction"})')],
    "60c": [(MK, 'ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})', 'ABOUT_ANOTHER_DAY = frozenset({"late"})')],
    "E4": [(MK, "if s is not None and s.mark is not None else []", 'if s is not None and s.mark is not None else [] if s is not None else ["smudge"]')],
    "61b": [(MK, "[s.mark] if s is not None and s.mark is not None else []", '[s.mark or "smudge"] if s is not None else []')],
    "62a": [(MK, 'return [*own, "smudge"] if note.slot == "catchup" else own', 'return [*own, "smudge"]')],
    "E3": [(MK, "< getattr(habits.marks, kind)", "<= getattr(habits.marks, kind)")],
    "62c": [(MK, 'return [*own, "smudge"] if note.slot == "catchup" else own', "return own")],
    "62d": [(MK, 'ABOUT_ANOTHER_DAY = frozenset({"late", "correction"})', 'ABOUT_ANOTHER_DAY = frozenset({"late", "correction", "catchup"})')],
    "63a": [(MK, "    for kind in held(note, subjects):\n", "    for kind in reversed(held(note, subjects)):\n")],
    "63b": [(P, "tuple(self.marks))", "tuple(sorted(self.marks, key=MARK_KINDS.index)))"),
            (P, "import ComposedDay, Gap, Habits, MarkKind, Note, Subject", "import MARK_KINDS, ComposedDay, Gap, Habits, MarkKind, Note, Subject")],
    "63c": [(MK, "if kind in have or kind in out or", "if kind in out or")],
    "64a": [(MK, "    for kind in held(note, subjects):\n", "    for kind in held(note, subjects)[:max(0, habits.marks_most - len(have))]:\n")],
    "64b": [(MK, "or len(have) + len(out) >= habits.marks_most:", "or False:")],
    "64c": [(MK, "len(have) + len(out) >= habits.marks_most", "len(have) + len(out) > habits.marks_most")],
    "64d": [(MK, "len(have) + len(out) >= habits.marks_most", "len(have) + len(out) >= habits.marks_most - 1")],
    "65a": [(D, '        page.gap = "away"\n        return page.done()\n',
             '        page.gap = "away"\n        page.marks += [k for k in ("smudge",) if roll(save_id, day, k, "mark") < getattr(habits.marks, k)]\n'
             "        return page.done()\n")],
    "66a": [(D, ROOMLEFT, "len(page.notes) + len(page.marks) < room")],
    "66b": [(P, "tuple(self.notes), self.gap", "tuple(self.notes[1:] + self.notes[:1] if self.marks else self.notes), self.gap")],
    "E1": [(D, "< care * diligent and", "<= care * diligent and")],
    "E2": [(B, "    return min(unused, key=lambda k:", "    return max(unused, key=lambda k:")],
}
