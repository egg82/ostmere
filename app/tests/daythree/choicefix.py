"""A fixture for the decide counter (counters.py): two builds that take 3 units each of two stores, the first of the
store a quarter of the hands' time makes and the second of the store the rest makes, so the second is affordable
first. Whichever is first in the queue lands first, since the queue's head waits. Never a shipped chapter (CLAUDE.md,
"Never spoil the owner")."""
from ashfall_app.engine import (
    BP, AtLeast, Amount, CardCount, CardDef, CardId, CardShare, Flow, Mix, MixId, PacingCurve, QueueEntry, Rules, Save,
    SaveMix, SetQueue, SkillDef, SkillId, StoreDef, StoreId, SwitchMix, TapCard, Unlock, UnlockKind, advance, decide,
    new_save, validate_rules,
)

H, U = 3600, 3600 * 3600
S1, S2 = StoreId("s1"), StoreId("s2")
G1, G2, A, B = CardId("g1"), CardId("g2"), CardId("build_a"), CardId("build_b")
MIX = Mix(MixId("quarter"), (CardShare(G1, BP // 4), CardShare(G2, 3 * BP // 4)))
OTHER = Mix(MixId("even"), (CardShare(G1, BP // 2), CardShare(G2, BP // 2)))


def entry(card: CardId) -> QueueEntry:
    return QueueEntry(TapCard(card), AtLeast(CardCount(card), 1, 1))


def rules() -> Rules:
    cards = (CardDef(G1, 60, makes=(Flow(S1, 4 * 3600),)), CardDef(G2, 60, makes=(Flow(S2, 4 * 3600),)),
             CardDef(A, H, inputs=(Amount(S1, 3 * U),), cap=1), CardDef(B, H, inputs=(Amount(S2, 3 * U),), cap=1))
    r = Rules((StoreDef(S1, 10 * U, 0), StoreDef(S2, 10 * U, 0)), (SkillDef(SkillId("k")),), (), PacingCurve((10**15,)),
              1000, cards=cards, opening=(*(Unlock(UnlockKind.STORE, str(s)) for s in (S1, S2)),
                                         *(Unlock(UnlockKind.CARD, str(c.id)) for c in cards)))
    validate_rules(r)
    return r


def planned(first: CardId, second: CardId, at: int = 0, queued: bool = True) -> Save:
    """The quarter mix running and, if `queued`, the queue holding both builds, `first` ahead."""
    r = rules()
    s = new_save(r)
    for verb in (SaveMix(MIX), SwitchMix(MIX.id), *((SetQueue((entry(first), entry(second))),) if queued else ())):
        s = decide(s, r, 0, verb)
    return advance(s, r, at)
