"""The loader's expansions of authored fields into ordinary entries, in the order they run. The one pipeline the loader
and a test's own merge (tests/opening/edited.py) both call, so an expansion added here reaches both."""
from typing import TYPE_CHECKING

from .casts import with_cast_picks
from .clocks import with_moment_clocks
from .echoes import with_answer_echoes
from .groups import with_group_unlocks
from .people import with_mentions

if TYPE_CHECKING:
    from .schema import Opening


def with_expansions(o: "Opening") -> "Opening":
    """The merged content with every expansion applied."""
    return with_moment_clocks(with_answer_echoes(with_group_unlocks(with_cast_picks(with_mentions(o)))))
