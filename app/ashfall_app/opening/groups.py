"""Groups as authored (engine DESIGN.txt, "GROUPS (pooled lanes)", "Content"): the checks on pooled lanes, groups, marks
and unmarked joins, and the unlocks a person's move into their group carries. Raises ValueError naming the entry
(refs.fail)."""
from typing import TYPE_CHECKING

from .entries import OutcomeEntry, UnlockEntry
from .refs import fail, need, outcomes

if TYPE_CHECKING:
    from .schema import Opening


def check_groups(o: "Opening") -> None:
    """A pooled lane is ruled, has no name, group or `told`; a group names a pooled lane; `tied` is on a pooled lane only and
    names a ruled person; marks only in a trigger's or an
    answer's outcome, each of a ruled person's lane; an unmarked join or an unmarking needs a group on the lane."""
    pooled = {x.id for x in o.lanes if x.pooled}
    people = {x.id: x for x in o.lanes if x.ruled and not x.pooled and not x.station}
    cards = {c.id: c for c in o.cards}
    for x in o.lanes:
        if x.pooled and (not x.ruled or x.name_key is not None or x.group is not None or x.told is not None):
            fail(f"lane {x.id}", "a pooled lane is ruled and has no name_key, group or told")
        if x.group is not None and x.group not in pooled:
            fail(f"lane {x.id}", f"group {x.group} is not a pooled lane")
        if x.tied is not None and not x.pooled:
            fail(f"lane {x.id}", "tied is only on a pooled lane")
        if x.tied is not None and x.tied not in people:
            fail(f"lane {x.id}", f"tied {x.tied} is not a ruled person's lane")
    once = {f"trigger {t.id}" for t in o.triggers} | {f"answer {a.id}" for x in o.offers for a in x.answers}
    for where, out in outcomes(o):
        for j in out.joins:
            if not j.own_split and people.get(j.lane) is not None and people[j.lane].group is None:
                fail(where, f"joins {j.lane} without its own split, and the lane has no group")
            group = people[j.lane].group if j.lane in people else None
            if not j.own_split and j.card is not None and (j.card not in cards or cards[j.card].lane != group
                                                           or cards[j.card].cap is not None):
                fail(where, f"joins {j.lane} without its own split, and card {j.card} is not an uncapped card on its group")
        if out.marks and where not in once:
            fail(where, "only a trigger's or an answer's outcome marks a person")
        for m in out.marks:
            need(where, "person's lane", m.lane, list(people))
            if not m.own_split and people[m.lane].group is None:
                fail(where, f"unmarks {m.lane}, which has no group")


TOWN_MANAGED_MAX = 6
"""Owner, 2026-11-25: "five-ish 'things' to manage at the town at once", a thing being a person who keeps their own split
or a group with a member; the ceiling sits one above the target of five."""


def town_managed(o: "Opening") -> tuple[list[str], list[str]]:
    """The people holding their own split and the groups with a member, at the end of `o`'s content: a person's mark is
    their last mark's, else their joins'; a left person is in neither."""
    people = {x.id: x for x in o.lanes if x.ruled and not x.pooled and not x.station}
    joined: dict[str, bool] = {}
    marked: dict[str, bool] = {}
    left: set[str] = set()
    for _, out in outcomes(o):
        for j in out.joins:
            joined[j.lane] = joined.get(j.lane, False) or j.own_split
        for m in out.marks:
            marked[m.lane] = m.own_split
        left |= {x.lane for x in out.leaves}
    here = [x for x in sorted(people) if x in joined and x not in left]
    own = [x for x in here if marked.get(x, joined[x])]
    groups = sorted({g for x in here if x not in own and (g := people[x].group) is not None})
    return own, groups


def check_town_managed(o: "Opening") -> None:
    """At the end of every chapter (the merge checks each prefix), people keeping their own split plus groups with a member
    come to at most TOWN_MANAGED_MAX: what the Town view asks the player to tune."""
    own, groups = town_managed(o)
    if len(own) + len(groups) > TOWN_MANAGED_MAX:
        fail("the town", f"{len(own) + len(groups)} things to manage, above the ceiling of {TOWN_MANAGED_MAX}: people keeping "
                         f"their own split ({', '.join(own)}) and groups with a member ({', '.join(groups)}); fold someone "
                         f"into a group, or send the newcomer to one that exists")


def with_group_unlocks(o: "Opening") -> "Opening":
    """`o` with each outcome that hands a person to their group (an unmarked join, an unmarking) also unlocking the
    group's cards: unlocks only grow, so a second member's copy is a no-op. A group card some outcome unlocks by name is
    left to that outcome: a later chapter's job reaches the group with the hands' card, not at a join before it."""
    group_of = {x.id: x.group for x in o.lanes if x.group is not None}
    if not group_of:
        return o
    named = {u.id for _, out in outcomes(o) for u in out.unlocks if u.unlock_kind == "card"}

    def out(x: OutcomeEntry) -> OutcomeEntry:
        lanes = [j.lane for j in x.joins if not j.own_split] + [m.lane for m in x.marks if not m.own_split]
        added = [UnlockEntry(unlock_kind="card", id=c.id)
                 for g in dict.fromkeys(group_of[lane] for lane in lanes if lane in group_of)
                 for c in o.cards if c.lane == g and c.id not in named]
        return x.model_copy(update={"unlocks": [*x.unlocks, *added]}) if added else x

    return o.model_copy(update={
        "triggers": [t.model_copy(update={"outcome": out(t.outcome)}) for t in o.triggers],
        "offers": [x.model_copy(update={"answers": [a.model_copy(update={"outcome": out(a.outcome)}) for a in x.answers]})
                   for x in o.offers],
    })
