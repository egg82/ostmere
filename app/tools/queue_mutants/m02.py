"""Row 02 of tests/writer/MUTANTS_queue.txt: the global budget is never checked."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/queue.py',
     '        if sum(self._spent.values()) >= self.budget.global_daily:\n',
     '        if False:\n'),
]
