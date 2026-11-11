"""Row 19 of MUTANTS_spent.txt: the Pause's resume level is ignored, so any refill of the store lifts it (both where the
resume event is scheduled and where it is applied)."""
EDITS: list[tuple[str, str, str]] = [
    ("ashfall_app/engine/handlers.py", "store_value(save, pause.store) < pause.resume_at:\n        return save\n",
     "store_value(save, pause.store) < 1:\n        return save\n"),
    ("ashfall_app/engine/schedule.py", "seg.start_value >= p.resume_at else reach_time(seg, p.resume_at)",
     "seg.start_value >= 1 else reach_time(seg, 1)"),
]
