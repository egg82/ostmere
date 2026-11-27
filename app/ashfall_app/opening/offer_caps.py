"""The cap a store has for certain when something is offered: its own cap with the cap modifiers of every outcome that
must already have happened (the chain of what unlocks it, what each outcome waits on, and the camp levels a certain
card lifts). A rule offered then may let go above the store's first cap, never above this."""
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING

from .condition_convert import levels
from .convert import amount
from .refs import outcomes

if TYPE_CHECKING:
    from .entries import ConditionEntry, ModifierEntry, UnlockEntry
    from .schema import Opening


def offer_cap(o: "Opening", store: str, after: "UnlockEntry | None", chain: "Chain | None" = None) -> float:
    """The cap `store` has for certain once `after` is unlocked, in items. Several ways to `after`: the least of them.
    `chain` is Chain(o), passed when many caps of one Opening are asked for."""
    base = float(next(s.cap_items for s in o.stores if s.id == store))
    if after is None:
        return base
    chain = chain or Chain(o)
    ways = [_with(base, store, chain.cap_modifiers(chain.before[where])) for where in chain.unlockers(after.unlock_kind, after.id)]
    return min(ways, default=base)


class Chain:
    """What must have happened before each outcome (`before`, by `refs.outcomes`' place string): the outcome itself, and
    for each condition it waits on the outcomes common to every way of meeting it. A fixpoint from everything down, so a
    cycle is never its own prerequisite."""

    def __init__(self, o: "Opening") -> None:
        self.o = o
        self.out = dict(outcomes(o))
        self.makers: dict[str, list[str]] = {}
        for w, out in self.out.items():
            for a in out.stores:
                self.makers.setdefault(a.store, []).append(w)
        self.made_by_flow = {f.store for x in (*o.cards, *o.standing) for f in x.makes}
        self.triggers = {f"trigger {t.id}": t for t in o.triggers}
        self.cards = {w: c for c in o.cards for w in (f"card {c.id}", f"card {c.id} finished")}
        self.answers = {f"answer {a.id}": x for x in o.offers for a in x.answers}
        self.unlocked_by: dict[tuple[str, str], list[str]] = {}
        for w, out in self.out.items():
            for u in out.unlocks:
                self.unlocked_by.setdefault((u.unlock_kind, u.id), []).append(w)
        self.waits = {w: self._wait_ways(w) for w in self.out}
        self.before = self._solve()

    def _solve(self) -> "Before":
        """A worklist: an outcome is solved again only when an outcome its conditions read has shrunk. Each set only
        shrinks from everything, so this reaches the same greatest fixpoint as sweeping until nothing changes. The
        sets are held as bit masks over the outcomes while solving."""
        names = list(self.out)
        bit = {w: 1 << i for i, w in enumerate(names)}
        everything = (1 << len(names)) - 1
        before = dict.fromkeys(names, everything)
        conds = {w: [ways for ways in c if ways] for w, c in self.waits.items()}
        readers: dict[str, set[str]] = {}
        for w, c in self.waits.items():
            for ways in c:
                for x in ways:
                    readers.setdefault(x, set()).add(w)
        todo, queued = list(self.waits), set(self.waits)
        while todo:
            w = todo.pop()
            queued.discard(w)
            new = bit[w]
            for ways in conds[w]:
                common = everything
                for x in ways:
                    common &= before[x]
                new |= common
            if new != before[w]:
                before[w] = new
                for r in readers.get(w, ()):
                    if r not in queued:
                        todo.append(r)
                        queued.add(r)
        return Before(before, names)

    def unlockers(self, unlock_kind: str, id_: str) -> list[str]:
        return self.unlocked_by.get((unlock_kind, id_), [])

    def _wait_ways(self, where: str) -> list[list[str]]:
        """For each condition `where` waits on, the outcomes that could meet it (one of them did)."""
        if where in self.triggers:
            t = self.triggers[where]
            return [w for c in (t.when, *t.requires) for w in self._ways(c)]
        if where in self.cards:
            c = self.cards[where]
            return [*(w for x in c.requires for w in self._ways(x)), self.unlockers("card", c.id)]
        if where in self.answers:
            x = self.answers[where]
            return [w for c in (x.gate, *x.requires) for w in self._ways(c)]
        return []

    def _ways(self, c: "ConditionEntry") -> list[list[str]]:
        """The ways of meeting `c`, as alternatives: none when met from the start or in a way not followed; a store
        only outcomes make, whose every item is needed to reach the level, has each of its makers as a condition."""
        if c.test != "at_least" or c.value < 1:
            return []
        if c.subject_kind == "unlocked" and c.unlock_kind is not None and c.id is not None:
            if any(u.unlock_kind == c.unlock_kind and u.id == c.id for u in self.o.start):
                return []
            return [self.unlockers(c.unlock_kind, c.id)]
        if c.subject_kind == "card_count":
            return [[f"card {c.id} finished"]] if f"card {c.id} finished" in self.out else []
        if c.subject_kind == "store" and c.id is not None and c.id not in self.made_by_flow:
            makers = self.makers.get(c.id, [])
            total = sum(amount(a).quantity for w in makers for a in self.out[w].stores if a.store == c.id)
            return [[w] for w in makers] if total <= levels(c)[0] else [makers]
        return []

    def cap_modifiers(self, done: frozenset[str]) -> "list[ModifierEntry]":
        """The modifiers of the outcomes done and of the camp levels landed. The camp's levels land in order (engine
        design/camp.txt, "THE CAMP"), and a held level lands when its lifting card finishes, the bar waiting just under it:
        so once the highest lifted level a certain card lifts has landed, every level below has, each lifting card
        finished, and what that needed (the chain of those cards) was done too."""
        camp = self.o.camp
        landed = [i for i, lv in enumerate(camp.levels if camp else [])
                  if lv.held and lv.lifted_by and all(f"card {c} finished" in done for c in lv.lifted_by)]
        mods: list[ModifierEntry] = []
        if camp is not None and landed:
            for lv in camp.levels[:max(landed) + 1]:
                mods.extend(lv.modifiers)
                if lv.held and lv.lifted_by:
                    done = done | _common(self.before, [f"card {c} finished" for c in lv.lifted_by])
        return [*(m for w in sorted(done) for m in self.out[w].modifiers), *mods]


class Before(Mapping[str, frozenset[str]]):
    """Chain.before: each outcome's solved mask, read out as names only when asked for (most never are)."""

    def __init__(self, masks: dict[str, int], names: list[str]) -> None:
        self._masks, self._names, self._read = masks, names, dict[str, frozenset[str]]()

    def __getitem__(self, where: str) -> frozenset[str]:
        if where not in self._read:
            self._read[where] = _names(self._masks[where], self._names)
        return self._read[where]

    def __iter__(self) -> Iterator[str]:
        return iter(self._masks)

    def __len__(self) -> int:
        return len(self._masks)


def _names(mask: int, names: list[str]) -> frozenset[str]:
    """The outcomes whose bits are set in `mask`, bit i being names[i]."""
    out: list[str] = []
    while mask:
        low = mask & -mask
        out.append(names[low.bit_length() - 1])
        mask ^= low
    return frozenset(out)


def _common(before: Before, ways: list[str]) -> frozenset[str]:
    """What every one of `ways` has behind it."""
    sets = [before[w] for w in ways]
    return sets[0].intersection(*sets[1:])


def _with(base: float, store: str, mods: "list[ModifierEntry]") -> float:
    for m in mods:
        if m.target == "cap" and m.id == store:
            base = base * m.amount_bp / 10_000 if m.kind == "mul_bp" else base + m.amount_bp / 10_000
    return base
