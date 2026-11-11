"""How a mix card reads: CardView.by is MIX only while its mix share runs, else None; CardView.run
is its mix share's state whoever runs the card, and when several apply the longest-lasting wins (GREYED, PAUSED, WAITING,
YIELDED); explain_work gives a mix card its mix share and Run, and 0 per hour when it does not move (DESIGN.txt,
"Card panel")."""
from ashfall_app.engine import (
    BP, ActionId, Amount, AtLeast, CardDef, CardId, CardShare, Flow, Mix, MixId, Rules, RunBy, RunKind, Save,
    SaveMix, StandingDef, StoreDef, StoreId, StoreValue, SwitchMix, advance, decide, explain_work, new_save,
)
from cards_world import Q, card_view, refill, rules, tap, work

V, U, Y, V2, U2 = (StoreId(n) for n in ("v", "u", "y", "v2", "u2"))
W, CD, FIN, PW, E = (CardId(n) for n in ("w", "cd", "fin", "pw", "e"))
DRAIN = ActionId("drain")
M0 = MixId("m0")


def world():
    """w requires v (empty). cd needs u, which holds half its
    input. fin completes once. pw needs u2 (half its input) and requires v2, which drain empties after 100 s. e is blank.
    refill makes u and u2, so a pause on them is PAUSED."""
    return rules(
        [StoreDef(V, 100 * Q, 0), StoreDef(U, 100 * Q, Q // 2), StoreDef(Y, 100 * Q, 0),
         StoreDef(V2, 100 * Q, 2 * Q), StoreDef(U2, 100 * Q, Q // 2)],
        standing=[StandingDef(DRAIN, costs=(Flow(V2, 36_000),))],
        cards=[CardDef(W, 100, requires=(AtLeast(StoreValue(V), Q, Q),), makes=(Flow(Y, 1000),)),
               CardDef(CD, 100, inputs=(Amount(U, Q),)), CardDef(FIN, 100, cap=1),
               CardDef(PW, 100, inputs=(Amount(U2, Q),), requires=(AtLeast(StoreValue(V2), Q, Q),)),
               CardDef(E, 100), refill(U, U2)])


def started(shares: dict[CardId, int]):
    r = world()
    s = decide(new_save(r), r, 0, SaveMix(Mix(M0, tuple(CardShare(c, b) for c, b in shares.items()))))
    return r, decide(s, r, 0, SwitchMix(M0))


def read(s: Save, r: Rules, card: CardId):
    cv = card_view(s, r, card)
    assert cv is not None
    return cv.by, cv.run


def test_by_is_mix_only_while_the_mix_moves_the_work():
    """CardView.by: MIX for a card running (FULL); None, the bar holding still, for one waiting on a requires, paused
    on a dry input, greyed or yielded to a tap. Each state's own work rate backs the reading."""
    r, waiting = started({W: BP})
    assert read(waiting, r, W) == (None, RunKind.WAITING) and work(waiting, W).rate == 0
    r, paused = started({CD: BP})
    paused = advance(paused, r, 100)
    assert paused.pauses and read(paused, r, CD) == (None, RunKind.PAUSED) and work(paused, CD).rate == 0
    r, greyed = started({FIN: 5000, E: 5000})
    greyed = advance(greyed, r, 200)
    assert read(greyed, r, E) == (None, RunKind.GREYED) and work(greyed, E).rate == 0
    r, yielded = started({E: 5000})
    assert read(yielded, r, E) == (RunBy.MIX, RunKind.FULL)
    yielded = tap(yielded, r, 0, FIN)
    assert read(yielded, r, E) == (None, RunKind.YIELDED)


def test_explain_work_gives_a_mix_card_its_mix_share_and_run_even_when_it_does_not_move():
    """api.explain_work: a card the active mix holds explains its mix share and Run, its per_hour 0 while waiting,
    paused, greyed or yielded (the same card not in the mix, as a tap started now: test_cards_mixable)."""
    r, running = started({E: 2500})
    e = explain_work(running, r, E)
    assert (e.share_bp, e.run.kind, e.per_hour) == (2500, RunKind.FULL, 2500)
    r, waiting = started({W: 4000})
    r, paused = started({CD: 4000})
    r, greyed = started({FIN: 4000, E: 4000})
    r, yielded = started({E: 4000})
    for s, card, kind in ((waiting, W, RunKind.WAITING), (advance(paused, r, 200), CD, RunKind.PAUSED),
                          (advance(greyed, r, 250), E, RunKind.GREYED), (tap(yielded, r, 0, FIN), E, RunKind.YIELDED)):
        e = explain_work(s, r, card)
        assert (e.share_bp, e.run.kind, e.per_hour) == (4000, kind, 0), kind


def test_greyed_outlasts_paused():
    """Card panel: a card paused on a dry input (it empties at 100) whose mix then greys, fin completing at 150 (it runs
    cd's share too from 100), reads GREYED, the longest-lasting; its Pause is still on the save."""
    r, s = started({CD: 5000, FIN: 5000})
    mid = advance(s, r, 149)
    assert read(mid, r, CD) == (None, RunKind.PAUSED) and mid.pauses
    a = advance(s, r, 150)
    assert a.pauses and read(a, r, CD) == (None, RunKind.GREYED)
    assert explain_work(a, r, CD).run.kind is RunKind.GREYED


def test_paused_outlasts_waiting():
    """Card panel: pw is paused on u2 at 50; v2, drained by the fire, falls under pw's requires after 100 s. It reads
    PAUSED, not WAITING, from then on: the pause lasts until u2 refills, the requires until v2 does. The control, w,
    waits with no pause and reads WAITING."""
    r, s = started({PW: BP})
    assert read(advance(s, r, 40), r, PW) == (RunBy.MIX, RunKind.FULL)
    a = advance(s, r, 200)
    assert a.pauses and read(a, r, PW) == (None, RunKind.PAUSED)
    r, w = started({W: BP})
    assert read(advance(w, r, 200), r, W) == (None, RunKind.WAITING)


def test_waiting_outlasts_yielded():
    """Card panel: while the hands tap another card every mix card is yielded, but one waiting on a requires reads
    WAITING (the tap ends in seconds, the requires may not). A yielded card with nothing else reads YIELDED."""
    r, s = started({W: 5000, E: 5000})
    s = tap(s, r, 0, FIN)
    assert read(s, r, W) == (None, RunKind.WAITING)
    assert read(s, r, E) == (None, RunKind.YIELDED)
