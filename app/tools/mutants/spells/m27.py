"""Row 27 of MUTANTS.txt: runner unchecked."""
EDITS: list[tuple[str, str, str]] = [
    ('ashfall_app/engine/validate/chaincheck.py',
     '    _require(runner is not None and runner.fight is not None,\n             f"{where}: chain names {chain.runner}, which is not a standing fight")\n    assert runner is not None and runner.fight is not None\n',
     '    if runner is None or runner.fight is None:\n        return\n'),
]
