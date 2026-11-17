"""The writer's daily budget (docs/decisions/writer.md, layer 4): the numbers, and a world's allowance from them."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    """Calls, not tokens: one job is one call. The values are the starting estimate, tuned with the model test."""

    global_daily: int = 400
    """Calls across every world in a day."""
    per_save_daily: int = 12
    """Calls one world may take in a day, whatever its share."""
    weight_cap: int = 8
    """A world weighs 1 + its returning days, up to this."""


DEFAULT = Budget()


def weight(budget: Budget, returning_days: int) -> int:
    return min(budget.weight_cap, 1 + max(0, returning_days))


def allowance(budget: Budget, own_weight: int, weights_today: list[int]) -> int:
    """Calls this world may make today: its weighted share of the global budget among the worlds played today
    (`weights_today` includes `own_weight`), at most the per-save cap."""
    total = sum(weights_today)
    if total <= 0:
        return 0
    return min(budget.per_save_daily, budget.global_daily * own_weight // total)
