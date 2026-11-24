"""Wire models of a card in the view (View.cards, View.completed) and how its share runs; the conventions in models.py
hold here, which re-exports them."""
from enum import StrEnum

from pydantic import BaseModel

from .decision_models import Segment
from .need_models import Blocker, Need
from .spent_models import SpentShare


class RunKind(StrEnum):
    FULL = "full"
    PAUSED = "paused"
    YIELDED = "yielded"
    WAITING = "waiting"
    """A mix card whose requirement does not hold yet."""
    GREYED = "greyed"
    """A card of the running mix while the mix is greyed."""
    SPENT = "spent"
    """Its share runs nothing and its store will not refill by itself; the rest of its mix runs the share."""


class RunBy(StrEnum):
    """Who runs a card now: never both on the hands, since a tap yields the mix."""

    TAP = "tap"
    MIX = "mix"


class Card(BaseModel):
    """An unlocked card that is not completed: one entry of the card panel, the same whether tapped, mixed or idle.
    Tappable iff blocker is null and its lane's LaneBar has no running_card or cuts_in is true."""

    card: str
    completions: int
    cap: int | None
    """Completions allowed, raised caps included; null: no cap. Draw "completions of cap"."""
    bar: Segment
    """The card's one bar, whoever runs it: sample it and draw the remainder modulo bar_total."""
    bar_total: int
    by: RunBy | None
    """Who moves its work now: tap, or mix while its share runs; null: nobody (paused,
    waiting, greyed or yielded), the bar holds still."""
    completes_at: int | None
    """When a tap's bar next fills; null: not tapped (a share claims no landing: a rule may take the hands from the
    mix), or it will not by itself."""
    share_bp: int
    """Its share in the running mix (flattened) as the player set it; 0 when the running mix does not hold it. It runs
    at share_bp plus the sum of gained."""
    run: RunKind | None
    """How its mix share runs, whoever runs the card (yielded while it or another card is tapped); the longest-lasting
    of greyed, spent, paused, waiting, yielded when several apply; null when the running mix does not hold it."""
    blocker: Blocker | None
    """null means a tap now is ready; otherwise what a tap now fails on (a failed tap: CONTRACT.txt)."""
    tap_s: int | None
    """Seconds a tap started now takes; null when its speed is 0. Draw this, not
    CardInfo.work_s, which is the time at full speed."""
    needs: list[Need]
    """The stores a tap needs, inputs in CardInfo order then requirements."""
    cuts_in: bool
    """A tap now starts it although its lane is busy: a glowing step not yet done, while the hands run a task the queue
    or a rule starts again once it lands, or a cure for a chip shown now, while the hands run a task that is not one
    (CONTRACT.txt, "Cut-in")."""
    speed: int
    """Work units per second a tap started now runs at: bar_total / speed is one whole completion's time, whatever the
    bar holds (tap_s is the rest of the current one); 0 when tap_s is null."""
    spent_store: str | None
    """The store a spent card is stopped on; null unless run is spent."""
    gained: list[SpentShare]
    """What each spent card of its mix on its lane gives it now, in mix order; empty when none (CONTRACT.txt, "SPENT")."""
    crew: int | None
    """A group card's free members now (CONTRACT.txt, "GROUPS"); null on a card of no pooled lane. While above 0,
    share_bp and gained are the totals over those members; 0 with no free member."""
    full_store: str | None
    """The store a full pause stopped the card on: every store it fills is full, so it keeps its inputs until one has
    room (CONTRACT.txt, "FULL OUTPUT"); null on any other card. Its run is paused."""


class CompletedCard(BaseModel):
    """An unlocked card at its cap: the Completed tab. It returns to View.cards if a cap is raised."""

    card: str
    completions: int
