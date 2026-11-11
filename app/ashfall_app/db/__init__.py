"""Postgres, the only place SQL lives (docs/engineering.md, "Postgres from the first table"): the tables
(`tables.py`), the engine the app reads and writes through (`engine.py`), the schema's migrations (`migrate.py`,
run as `python -m ashfall_app.db migrate`), and the typed records each table is read and written as (`accounts.py`,
`saves.py`, `tries.py`), always in the caller's transaction."""
