"""Row 02 of tests/writer/MUTANTS_live.txt: a timeout answers the stand-in from inside the client."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '            self._fail("timeout", fields, t0, e)\n',
     '            return stand_in\n'),
]
