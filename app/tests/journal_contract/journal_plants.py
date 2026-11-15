"""The planted wrong implementations of MUTANTS.txt, as exact edits to the composer's source (paths under
`ashfall_app/saves/`). A row with several variants ("2a", "2b") plants each of its alternatives on its own; `E1` and
`E2` are the equivalents, expected to survive. `plant_mutants.py` applies them one at a time to a copy of the tree."""

type Edit = tuple[str, str, str]
"""(file, old text, new text); the old text must occur exactly once."""

J, H, L, N = "journal.py", "journal_composer/history.py", "journal_composer/ledger.py", "journal_composer/numbers.py"
B, T, O = "journal_composer/bag.py", "journal_composer/telling.py", "journal_composer/owed.py"
W, D = "journal_composer/own.py", "journal_composer/day.py"

KEY = 'sha256(f"{save_id}|journal|{day}|{subject}|{purpose}"'
HEAD = "    head = [*caught, *(c.telling for c in written)]"
KEEP = "    kept = sorted(passing, key=lambda c: (-c.care, c.order, c.telling.subject))[:left]"
LEFT = "    left = max(0, room - len(caught) - len(musts) - len(fixes))"
AT = "history.first_at(c.telling.subject, day)"
BY = "    written = sorted([*musts, *kept], key=lambda c: "
OWN_SORT = f"{BY}({AT}, c.telling.subject))"
CAUGHT = "    caught = catchups(composed, history, subjects)\n"
TOLD = "        told = tellings(composed, s.id) + (s.id in caught)"
LATE_ROLL = 'roll(save_id, yesterday.day, s.id, "late") < habits.late_rate'
WROTE = 'if n.slot not in ("late", "correction")}'
CARE_W = "    return faded(fade, 0 if changed(history, s.id, day) else told)"
EARLIER = "if d < day for k in keys}"
AWAY_RANGE = "range(day - s.away_days + 1, day + 1)"
BUSY = "    if len(showing(history, subjects, day)) > habits.busy_ratio * room:"
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
    "4": [(D, OWN_SORT, "    both = [*musts, *kept]\n"
                        "    written = [c for i in {c.telling.subject for c in both} for c in both"
                        " if c.telling.subject == i]")],
    "5": [(H, "for k in history.keys(subject, day))", "for k in history.keys(subject, day)[:1])")],
    "6": [(J, "import hashlib\n", "import hashlib\nimport itertools\n_COUNTER = itertools.count()\n"),
          (J, KEY, 'sha256(f"{save_id}|journal|{next(_COUNTER)}"')],
    "7": [(H, "line.at // DAY_S", "(line.at + 1) // DAY_S")],
    "8a": [(D, "    if any(line.at >= (day + 1) * DAY_S for line in lines):\n", "    if False:\n")],
    "8b": [(D, "    if [r.day for r in composed] != list(range(day)):\n", "    if False:\n")],
    "9": [(D, "    if gap is not None:\n        return ComposedDay(day, (), gap)\n", ""),
          (D, "        return ComposedDay(day, (), None)", "        return ComposedDay(day, (), gap)"),
          (D, "for t in told), None)", "for t in told), gap)")],
    "10": [(H, "    by_source = {s.source: s.id for s in subjects}",
            "    by_source = {s.source.id: s.id for s in subjects}"),
           (H, "by_source.get(line.source) if", "by_source.get(line.source.id) if")],
    "10b": [(D, BUSY, "    if len(showing(history, subjects, day)) + noise > habits.busy_ratio * room:"),
            (D, "room: int, habits: Habits) -> Gap | None:",
             "room: int, habits: Habits, noise: int = 0) -> Gap | None:"),
            (D, "    gap = _gap(history, subjects, day, room, habits)",
             "    gap = _gap(history, subjects, day, room, habits,"
             " sum(1 for x in lines if x.source is None and x.at // DAY_S == day))")],
    "11": [(D, BUSY, "    if sum(len(history.keys(s.id, day)) for s in subjects) > habits.busy_ratio * room:")],
    "12": [(W, "        must = is_must(s, told)", "        must = False")],
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
    "20": [(D, CAUGHT, "    caught = catchups(composed, history, subjects)"
                       " if showing(history, subjects, day) else []\n")],
    "21": [(O, "        if t is not None and is_must(by_id[sid], tellings(composed, sid)):",
            "        if t is not None:")],
    "22": [(D, "{t.subject for t in caught})", "set())")],
    "23": [(D, CAUGHT, "    caught = catchups([ComposedDay(r.day, r.notes,"
                       " _gap(history, subjects, r.day, room, habits))"
                       " for r in composed], history, subjects)\n")],
    "24": [(W, CARE_W, "    return faded(fade, 0 if changed(history, s.id, day) else"
                       " len([d for d in history.by_subject[s.id] if d < day]))")],
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
    "29b": [(D, "    room = budget(settled, habits)", "    room = budget(float(day), habits)")],
    "30a": [(L, WRITTEN, "    written = sum(len(r.notes) for r in composed)")],
    "30b": [(L, WRITTEN, "    written = sum(1 for r in composed if r.notes or r.gap)")],
    "30c": [(L, "    beat_notes = sum(1 for r in composed for n in r.notes if n.subject in beats)",
             "    beat_notes = sum(1 for r in composed if any(n.subject in beats for n in r.notes))")],
    "30d": [(L, "    return max(0.0, written - habits.beat_refresh * beat_notes)",
             "    return written - habits.beat_refresh * beat_notes")],
    "31a": [(N, BUDGET, f"    return round({BUDGET_RAW})")],
    "31b": [(N, BUDGET, f"    return math.floor({BUDGET_RAW})")],
    "31c": [(N, BUDGET, f"    return math.ceil({BUDGET_RAW})")],
    "32": [(D, LEFT, "    left = room - len(caught) - len(musts) - len(fixes)")],
    "33": [(D, LEFT, "    left = max(0, room - len(musts))")],
    "34": [(D, LEFT, "    left = max(0, room - len(caught) - len(musts) - len(fixes)"
                     " - len(lates(save_id, composed, subjects, habits)))")],
    "35a": [(D, KEEP, "    kept = sorted(passing, key=lambda c: c.telling.subject)[:left]")],
    "35b": [(D, KEEP, "    kept = sorted(passing, key=lambda c: (c.care, c.order, c.telling.subject))[:left]")],
    "35c": [(D, KEEP, "    kept = sorted(passing, key=lambda c: (-c.care, -c.order, c.telling.subject))[:left]")],
    "35d": [(D, KEEP, "    kept = sorted(passing, key=lambda c: (c.order, c.telling.subject))[:left]")],
    "36a": [(H, AWAY_RANGE, "range(day - s.away_days, day + 1)")],
    "36b": [(H, AWAY_RANGE, "range(day - s.away_days + 2, day + 1)")],
    "36c": [(H, AWAY_RANGE, "range(day - s.away_days, day)")],
    "37": [(D, "> habits.busy_ratio * room:", ">= habits.busy_ratio * room:")],
    "38": [(D, BUSY, "    if len(showing(history, subjects, day)) + owed > habits.busy_ratio * room:"),
           (D, "room: int, habits: Habits) -> Gap | None:", "room: int, habits: Habits, owed: int = 0) -> Gap | None:"),
           (D, "    gap = _gap(history, subjects, day, room, habits)",
            "    gap = _gap(history, subjects, day, room, habits, len(catchups(composed, history, subjects)))")],
    "39": [(D, f'    if away(history, subjects, day):\n        return "away"\n{BUSY}\n        return "busy"',
            f'{BUSY}\n        return "busy"\n    if away(history, subjects, day):\n        return "away"')],
    "40": [(D, "> habits.busy_ratio * room:", "> habits.busy_ratio * habits.lines_start:")],
    "41": [(D, "    if not head and not fixes:",
            "    if not head and not fixes and not lates(save_id, composed, subjects, habits):")],
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
    "47d": [(D, "    if not head and not fixes:", "    if not head:")],
    "48a": [(O, LATE_ROLL, 'roll(save_id, yesterday.day, s.id, "late") < 1 - habits.late_rate')],
    "48b": [(W, '"misremember") < habits.misremember_rate', '"misremember") > habits.misremember_rate')],
    "49a": [(O, SORT_FIRST, "    for sid in sorted(first_at):")],
    "49b": [(O, SORT_FIRST, "    for sid in sorted(first_at, key=lambda i: (-first_at[i], i)):")],
    "49c": [(O, FIRST_AT, "            first_at.setdefault(s.id, d)\n")],
    "50a": [(D, OWN_SORT, f"{BY}(c.order, c.telling.subject))")],
    "50b": [(D, OWN_SORT, f"{BY}c.telling.subject)")],
    "50c": [(D, OWN_SORT, f"{BY}(not c.must, {AT}, c.telling.subject))")],
    "50d": [(D, OWN_SORT, f"{BY}(-{AT}, c.telling.subject))")],
    "50e": [(H, "            days[day] = min(days.get(day, line.at), line.at)",
             "            days[day] = max(days.get(day, line.at), line.at)")],
    "50f": [(D, OWN_SORT, f"{BY}{AT})")],
    "51a": [(D, HEAD, "    head = [*(c.telling for c in written), *caught]")],
    "51b": [(D, "    told = [*head, *lates(save_id, composed, subjects, habits), *fixes]",
             "    told = [*head, *fixes, *lates(save_id, composed, subjects, habits)]")],
    "51c": [(O, '    for s in sorted(subjects, key=lambda x: x.id):\n        t = plain(s, "late")',
             '    for s in subjects:\n        t = plain(s, "late")')],
    "51d": [(O, '    for s in sorted(subjects, key=lambda x: x.id):\n        t = plain(s, "correction")',
             '    for s in subjects:\n        t = plain(s, "correction")')],
    "52": [(D, OWN_SORT, f"{BY}(-c.care, {AT}, c.telling.subject))")],
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
    "57": [(W, TOLD, "        told = sum(1 for d in history.by_subject[s.id] if d < day) + (s.id in caught)")],
    "58a": [(L, WRITTEN, "    written = sum(1 for r in composed"
                         " if any(n.subject in {s.id for s in subjects} for n in r.notes))")],
    "58b": [(W, TOLD, "        told = sum(1 for r in composed for n in r.notes if n.subject == s.id"
                      ' and n.slot in ("first", "repeat", "catchup", "misremember", "mention") and n.key in'
                      " (*s.first, *s.repeat, *s.catchup, *s.misremember, *(k for b in s.mention for k in b.keys)))"
                      " + (s.id in caught)")],
    "E1": [(D, '"write") < c.care * diligent]', '"write") <= c.care * diligent]')],
    "E2": [(B, "    return min(unused, key=lambda k:", "    return max(unused, key=lambda k:")],
}
