"""Groups as authored (engine design/groups.txt, "GROUPS (pooled lanes)", "Content"): the checks on pooled lanes, groups, marks
and unmarked joins, and the unlocks a person's move into their group carries. Raises ValueError naming the entry
(refs.fail)."""
from typing import TYPE_CHECKING

from .entries import OutcomeEntry, UnlockEntry
from .refs import fail, need, outcomes

if TYPE_CHECKING:
    from .lane_entries import LaneEntry
    from .schema import Opening


def with_crews(lanes: "list[LaneEntry]") -> "list[LaneEntry]":
    """`lanes` with each lane that lists `crews` and has no group set to its smallest crew: the one with the most members
    among the lanes before it, a tie going to the first listed (docs/decisions/people.md, "Groups follow what people
    can do"). A lane is placed once, in the chapter that declares it."""
    pooled: set[str] = set()
    size: dict[str, int] = {}
    out: list[LaneEntry] = []
    for x in lanes:
        if x.pooled:
            pooled.add(x.id)
        if x.crews and x.group is None:
            unknown = [c for c in x.crews if c not in pooled]
            if unknown:
                fail(f"lane {x.id}", f"crews {', '.join(unknown)} are not pooled lanes declared before it")
            x = x.model_copy(update={"group": min(x.crews, key=lambda c: size.get(c, 0)), "crews": []})
        elif x.crews:
            fail(f"lane {x.id}", "sets both group and crews")
        if x.group is not None:
            size[x.group] = size.get(x.group, 0) + 1
        out.append(x)
    return out


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
    check_group_abilities(o)
    check_own_town_cards(o)


def check_own_town_cards(o: "Opening") -> None:
    """A town card's `own` lanes are on its `lanes`, and each has the hand-written card of the pattern's id."""
    cards = {c.id: c.lane for c in o.cards}
    for tc in o.town_cards:
        for lane in tc.own:
            card = tc.id.replace("{lane}", lane)
            if lane not in tc.lanes:
                fail(f"town card {tc.id}", f"own lane {lane} is not in its lanes")
            if cards.get(card) != lane:
                fail(f"town card {tc.id}", f"own lane {lane} has no hand-written card {card} on it")


def check_group_abilities(o: "Opening") -> None:
    """A group holds only work its members can do (docs/decisions/people.md, "The mark: who keeps their own split"): a
    town card fanned out to a group is fanned out to each member whose lane any town card names. A member no town card
    names has no list of their own, so the group's list is theirs."""
    able = {lane for tc in o.town_cards for lane in tc.lanes}
    members: dict[str, list[str]] = {}
    for x in o.lanes:
        if x.group is not None and x.id in able:
            members.setdefault(x.group, []).append(x.id)
    for tc in o.town_cards:
        for g in tc.lanes:
            missing = [m for m in members.get(g, []) if m not in tc.lanes]
            if missing:
                fail(f"town card {tc.id}", f"is on group {g}, and its members {', '.join(missing)} cannot do it")


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
