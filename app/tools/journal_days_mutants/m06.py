"""Row 06 of tests/saves/MUTANTS_journal_days.txt: a stored line under a key renamed since feeds nothing."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/saves/journal_write.py',
     'if (key := rs.line_renames.get(old, old)) not in rs.retired_lines',
     'if (key := old) not in rs.retired_lines'),
]
