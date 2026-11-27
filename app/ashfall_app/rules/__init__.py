"""The game's rules as authored data, and the loader that checks them and builds the engine's Rules.

`schema.py` loads `opening.toml` and the chapter files in `days/`; `entries/` holds the models each table is validated
against, `expand/` the passes that turn authored fields into ordinary entries and then into Rules, and `checks/` the
loader's refusals (`checks/run.py` runs them). The rest is shared lookups and per-subject readers."""
