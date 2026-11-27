"""Row 41 of MUTANTS.txt: link lines folded."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/api/service.py',
     'lines=[self.log_line(ln) for ln in played.lines],',
     'lines=list({ln.key: self.log_line(ln) for ln in played.lines}.values()),'),
]
