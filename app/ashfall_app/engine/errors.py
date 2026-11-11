"""Every error the engine raises. All are EngineError, so a caller can catch the engine's failures in one place."""
from .ids import IdKind


class EngineError(Exception):
    """Base of every engine error."""


class InvalidRulesError(EngineError):
    """validate_rules() found rules the engine cannot run (duplicate or unknown ids, bad curve, bad cap, ...)."""


class InvalidVerbError(EngineError):
    """decide() was given a verb that does not fit this save and rules; the save is unchanged (nothing is returned)."""


class TimeOrderError(EngineError):
    """A call asked for a time before save.time. Engine time only moves forward."""




class StateFormatError(EngineError):
    """codec.decode() was given text encode() did not produce under these rules: bad shape, another format, or a save
    made under other rules (a rules change between requests)."""


class RebaseError(EngineError):
    """rebase() met an id the save's manifest declares that the new rules, after the renames, do not (or a cycle of
    renames): `kind` and `id` name it as the save had it. Nothing is dropped instead (DESIGN.txt, "Rebase")."""

    def __init__(self, kind: IdKind, id: str) -> None:
        super().__init__(f"{kind.value} {id} is not in the new rules and no rename maps it")
        self.kind = kind
        self.id = id
