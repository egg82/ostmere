"""Row 06 of tests/writer/MUTANTS_live.txt: the success line carries the key."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '        fields: dict[str, object] = {"kind": kind.name, "model": model}\n',
     '        fields: dict[str, object] = {"kind": kind.name, "model": model, "key": self.sdk.api_key}\n'),
]
