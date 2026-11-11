"""The cards that are trips: the player leaves the scene while one runs (docs/design/banked-time-plan.md, item 6).

A trip is known by its card id, as every pose is (api/CONTRACT.txt, "BANKED TIME"): there is no flag on the card.
Add a chapter's trip cards here; the scene then hides the seated figure while one is tapped (`running:`) and for its
share of each cycle while the mix runs it (`mix:`, whose turns the page already gives out by share).
"""
from __future__ import annotations

TRIPS: tuple[str, ...] = ("field_track", "hunt_wolf", "hunt_bear")


def away(trips: tuple[str, ...]) -> list[str]:
    """Conditions, one per way a trip card can be running, for a pose's `until`."""
    return [f"{kind}:{card}" for card in trips for kind in ("running", "mix")]
