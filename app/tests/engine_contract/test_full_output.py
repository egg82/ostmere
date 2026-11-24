"""FULL OUTPUT (engine DESIGN.txt, invariants 179-183): a card with inputs and no cap pauses when every one of its outcome
stores is full, keeps its inputs, gives its share to the rest of its mix, and resumes when one store falls to half its
cap. Written from that part alone, through the engine's public names.

Every card here takes 10 s a completion, so at a full share it pays 1 item of each lump every 10 s: Q / 10 units a
second. The pool p holds far more than any test draws; y and z are the outcome stores."""
from ashfall_app.engine import (
    BP, QUANTITY_SCALE as Q, ActionId, Amount, CardDef, CardId, CardShare, Flow, Mix, MixId, Outcome, PacingCurve,
    Rules, RunKind, Save, SaveMix, SkillDef, SkillId, StandingDef, StoreDef, StoreId, SwitchMix, TapCard, advance, decide,
    explain_work, new_save, per_hour, validate_rules, view,
)

P, Y, Z = StoreId("p"), StoreId("y"), StoreId("z")
PULL, GATHER, OTHER = CardId("pull"), CardId("gather"), CardId("other")
M = MixId("m")
POOL = 10_000
BIG = 10**6


def _rules(*cards: CardDef, y_cap: int = 4, z_cap: int = BIG, y0: int = 0,
           standing: tuple[StandingDef, ...] = ()) -> Rules:
    stores = (StoreDef(P, BIG * Q, POOL * Q), StoreDef(Y, y_cap * Q, y0 * Q), StoreDef(Z, z_cap * Q, 0))
    r = Rules(stores, (SkillDef(SkillId("k")),), standing, PacingCurve((10**15,)), cards=cards)
    validate_rules(r)
    return r


def _pull(*outs: StoreId, cap: int | None = None, card: CardId = PULL) -> CardDef:
    return CardDef(card, 10, inputs=(Amount(P, Q),), outcome=Outcome(stores=tuple(Amount(s, Q) for s in outs)), cap=cap)


def _mixed(rules: Rules, *shares: tuple[CardId, int]) -> Save:
    s = decide(new_save(rules), rules, 0, SaveMix(Mix(M, tuple(CardShare(c, b) for c, b in shares))))
    return decide(s, rules, 0, SwitchMix(M))


def _store(save: Save, store: StoreId) -> int:
    return next(st.segment.start_value for st in save.stores if st.store == store)


def _done(save: Save, card: CardId) -> int:
    """Completions: the card's work over 10 s of work at a full share."""
    return next(cs.work.start_value for cs in save.cards if cs.card == card) // (10 * BP)


def _used(save: Save) -> int:
    return POOL * Q - _store(save, P)


def test_a_card_whose_only_outcome_store_is_full_stops_drawing_its_pool():
    """Invariants 179, 183: the outcome store fills at t = 40 and the card pauses there; the pool keeps the rest."""
    rules = _rules(_pull(Y))
    s = _mixed(rules, (PULL, BP))
    a = advance(s, rules, 1000)
    assert _store(a, Y) == 4 * Q
    assert _used(a) == 4 * Q
    assert [p.runner for p in a.pauses] == [PULL]
    assert explain_work(a, rules, PULL).run.kind is RunKind.PAUSED


def test_a_card_with_no_inputs_keeps_gathering_at_the_cap():
    """Invariant 180: gathering keeps today's cap loss: the card runs on, completing every 10 s."""
    rules = _rules(CardDef(GATHER, 10, outcome=Outcome(stores=(Amount(Y, Q),))))
    a = advance(_mixed(rules, (GATHER, BP)), rules, 1000)
    assert _done(a, GATHER) == 100
    assert _store(a, Y) == 4 * Q and a.pauses == ()


def test_a_capped_card_is_never_paused_full():
    """Invariant 180: a capped card's completions count toward its cap, so it runs to the cap at a full store."""
    rules = _rules(_pull(Y, cap=10))
    a = advance(_mixed(rules, (PULL, BP)), rules, 1000)
    assert _done(a, PULL) == 10
    assert _used(a) == 10 * Q and a.pauses == ()


def test_a_by_product_with_room_keeps_the_card_running():
    """Invariant 181: y is full but z has room, so the card runs and y's overflow is lost."""
    rules = _rules(_pull(Y, Z))
    a = advance(_mixed(rules, (PULL, BP)), rules, 1000)
    assert _store(a, Z) == 100 * Q and _store(a, Y) == 4 * Q
    assert _used(a) == 100 * Q and a.pauses == ()


def test_a_card_pauses_when_every_outcome_store_is_full():
    """Invariant 179 with two outcome stores: both full at t = 40, the card pauses."""
    rules = _rules(_pull(Y, Z), z_cap=4)
    a = advance(_mixed(rules, (PULL, BP)), rules, 1000)
    assert _used(a) == 4 * Q and [p.runner for p in a.pauses] == [PULL]


def test_a_full_card_gives_its_share_to_the_rest_of_its_mix():
    """SPENT's giver: at half a share each, y fills at t = 80; from then the gatherer runs the whole share."""
    rules = _rules(_pull(Y), CardDef(GATHER, 10, outcome=Outcome(stores=(Amount(Z, Q),))))
    a = advance(_mixed(rules, (PULL, BP // 2), (GATHER, BP // 2)), rules, 1000)
    assert _used(a) == 4 * Q
    assert _store(a, Z) == (4 + 92) * Q


def test_the_pause_lifts_when_the_store_falls_to_half_its_cap():
    """Invariant 182: a standing chore eats 36 y an hour. The card fills y, pauses, and resumes only once y is down to 2
    items (half of 4), never sooner; over the hour the pool pays for what y holds plus what was eaten, and at most under a
    second's make more at each pause (KNOWN GAPS)."""
    eat = StandingDef(ActionId("eat"), costs=(Flow(Y, per_hour(36)),))
    rules = _rules(_pull(Y), standing=(eat,))
    s = _mixed(rules, (PULL, BP))
    paused_lows: list[int] = []
    resumed_at: list[int] = []
    was_paused, pauses = False, 0
    for t in range(1, 3601):
        s = advance(s, rules, t)
        y = _store(s, Y)
        if s.pauses:
            paused_lows.append(y)
            pauses += not was_paused
        elif was_paused:
            resumed_at.append(y)
        else:
            assert y < 4 * Q   # never running at a full store
        was_paused = bool(s.pauses)
    assert resumed_at and max(resumed_at) <= 2 * Q
    assert min(paused_lows) > 2 * Q
    lost = _used(s) - _store(s, Y) - 36 * Q   # KNOWN GAPS: under a second of make lost at each pause
    assert 0 <= lost < pauses * Q // 10


def test_a_tap_runs_its_one_completion_at_a_full_store():
    """Taps: a tap is never full and a full pause holds no tap. y starts full: the player's tap runs one completion,
    drawing one item, and y's overflow is lost."""
    rules = _rules(_pull(Y), y0=4)
    s = decide(new_save(rules), rules, 0, TapCard(PULL))
    assert s.pauses == ()
    a = advance(s, rules, 500)
    assert _used(a) == Q and _store(a, Y) == 4 * Q and _done(a, PULL) == 1


def test_a_tap_of_a_full_paused_mix_card_runs_and_the_pause_stands():
    """The mix card pauses full at t = 40; the player taps it at 100: one completion is drawn, and once the tap lands the
    card is paused in its mix again."""
    rules = _rules(_pull(Y))
    s = advance(_mixed(rules, (PULL, BP)), rules, 100)
    assert [p.runner for p in s.pauses] == [PULL]
    a = advance(decide(s, rules, 100, TapCard(PULL)), rules, 500)
    assert _used(a) == 5 * Q
    assert [p.runner for p in a.pauses] == [PULL]


def test_a_card_drawing_a_store_something_in_play_makes_keeps_the_cap_loss():
    """Fillable card: only a card drawing a pool pauses full. A card in play that can make p (idle, never run) makes p no
    pool, so pull runs on at the full store, as gathering does."""
    refill = CardDef(OTHER, 10, outcome=Outcome(stores=(Amount(P, Q),)))
    rules = _rules(_pull(Y), refill)
    a = advance(_mixed(rules, (PULL, BP)), rules, 1000)
    assert _used(a) == 100 * Q and a.pauses == ()


def test_a_store_drained_below_a_full_pause_reads_covered():
    """Read model: while the chore eats y down toward half its cap, the card paused full will refill it, so y's falling
    line is covered (white), not one that needs the player."""
    eat = StandingDef(ActionId("eat"), costs=(Flow(Y, per_hour(36)),))
    rules = _rules(_pull(Y), standing=(eat,))
    a = advance(_mixed(rules, (PULL, BP)), rules, 100)
    assert [p.runner for p in a.pauses] == [PULL]
    line = next(ln for ln in view(a, rules).ledger if ln.store == Y)
    assert line.falling and line.covered
