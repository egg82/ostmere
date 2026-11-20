"""Every error the engine raises. All are EngineError, so a caller can catch the engine's failures in one place."""


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
