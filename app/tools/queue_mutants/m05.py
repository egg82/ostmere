"""Row 05 of tests/writer/MUTANTS_queue.txt: an abandoned world's job is queued."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/queue.py',
     '        if job.save_id not in self._visits:\n',
     '        if False:\n'),
]
