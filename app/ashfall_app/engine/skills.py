"""Levels from XP, read off the pacing curve passed in as data."""
from .rules import PacingCurve


def level_for(curve: PacingCurve, xp: int) -> int:
    """1 + the number of thresholds <= xp. Monotone in xp; 1 at xp 0; len(thresholds) + 1 at the XP cap."""
    return 1 + sum(1 for th in curve.thresholds if th <= xp)


def xp_for(curve: PacingCurve, level: int) -> int:
    """The XP at which `level` is reached (0 for level 1). ValueError outside 1..len(thresholds) + 1."""
    if not 1 <= level <= len(curve.thresholds) + 1:
        raise ValueError(f"level {level} is outside 1..{len(curve.thresholds) + 1}")
    return 0 if level == 1 else curve.thresholds[level - 2]
