"""Row 04 of tests/writer/MUTANTS_live.txt: the model is a literal."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/live.py',
     '        model = self.config.model(kind)\n',
     '        model = "claude-sonnet-5-5"\n'),
]
