"""Row 01 of tests/writer/MUTANTS_live.txt: an API error answers the stand-in from inside the client."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '            self._fail("api_error", {**fields, "status": e.status_code}, t0, e)\n',
     '            return stand_in\n'),
]
