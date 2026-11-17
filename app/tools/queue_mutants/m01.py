"""Row 01 of tests/writer/MUTANTS_queue.txt: a world's own allowance is never checked."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/writer/queue.py',
     '        if self._spent.get(job.save_id, 0) >= budgets.allowance(self.budget, own, weights):\n',
     '        if False:\n'),
]
