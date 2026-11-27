"""Fixed-point units and the one integer division every event time uses.

Time is integer seconds since the save began. A rate is fixed-point per hour: RATE_SCALE units are one whole item per
hour. A quantity is fixed-point with QUANTITY_SCALE = RATE_SCALE * 3600 units per whole item, chosen so a rate of r
moves a quantity by exactly r units per second: value(t) = v0 + r * (t - t0) has no division, so splitting a span
anywhere cannot round differently. The same integer is a store's rate per hour (rate units) and per second (quantity
units).
"""

SECONDS_PER_HOUR = 3600
RATE_SCALE = 1000
QUANTITY_SCALE = RATE_SCALE * SECONDS_PER_HOUR
BP = 10_000
"""Basis points: shares, additive modifiers and multipliers are in BP (10_000 = 100%, or a factor of 1)."""


def units(whole: int) -> int:
    """`whole` items as a quantity: whole * QUANTITY_SCALE. For authoring caps, initial values and thresholds."""
    return whole * QUANTITY_SCALE


def per_hour(whole: int) -> int:
    """`whole` items per hour as a rate: whole * RATE_SCALE."""
    return whole * RATE_SCALE


def ceil_div(a: int, b: int) -> int:
    """Exact integer ceiling of a / b for b > 0 (any sign of a); raises ValueError for b <= 0. No floats anywhere."""
    if b <= 0:
        raise ValueError(f"ceil_div needs a positive divisor, got {b}")
    return -((-a) // b)
