"""A fixture chapter for a season's chore with no order card (week-four-plan item 4), as the engine sees it: a standing
action piles up a film an item an hour from 0; a chip shows at 12 and cuts the table's making while it shows; the
trigger at the chip's first showing opens its cures, a hands card and a helper's twin on a ruled lane, each taking 12
film. No order card: the rule is the player's (daythree/moves.chip_rule). Never a shipped chapter (CLAUDE.md, "Never
spoil the owner")."""
from ashfall_app.engine import (
    QUANTITY_SCALE, RATE_SCALE, ActionId, Amount, AtLeast, CardDef, CardId, ChipDef, ChipId, Flow, FlowKind, LaneDef,
    LaneId, Modifier, ModifierKind, Outcome, PacingCurve, RateRef, Rules, SourceId, StandingDef, StoreDef, StoreId,
    StoreValue, TriggerDef, TriggerId, Unlock, UnlockKind,
)

HOUR = 3600
FILM, MEAL = StoreId("film"), StoreId("meal")
SETTLE, TABLE = ActionId("settle"), ActionId("table")
WASH, HELPER_WASH = CardId("wash"), CardId("helper_wash")
HELPER = LaneId("helper")
ASHED = ChipId("ashed")
SHOWS_AT = 12
"""Film items at which the chip shows: 12 hours after the start."""
WHEN = AtLeast(StoreValue(FILM), SHOWS_AT * QUANTITY_SCALE, SHOWS_AT * QUANTITY_SCALE)


def rules() -> Rules:
    cures = (CardDef(WASH, 600, inputs=(Amount(FILM, SHOWS_AT * QUANTITY_SCALE),)),
             CardDef(HELPER_WASH, 2400, lane=HELPER, inputs=(Amount(FILM, SHOWS_AT * QUANTITY_SCALE),)))
    cut = Modifier(RateRef(TABLE, FlowKind.MAKE, MEAL), ModifierKind.MUL_BP, 7500, SourceId(str(ASHED)))
    first = Outcome(unlocks=(Unlock(UnlockKind.CHIP, str(ASHED)), *(Unlock(UnlockKind.CARD, str(c.id)) for c in cures)))
    return Rules(
        (StoreDef(FILM, 24 * QUANTITY_SCALE, 0), StoreDef(MEAL, 10**6 * QUANTITY_SCALE, 0)), (),
        (StandingDef(SETTLE, makes=(Flow(FILM, RATE_SCALE),)), StandingDef(TABLE, makes=(Flow(MEAL, 2 * RATE_SCALE),))),
        PacingCurve((10**15,)), lanes=(LaneDef(HELPER, ruled=True),), cards=cures,
        chips=(ChipDef(ASHED, WHEN, effects=(cut,)),),
        triggers=(TriggerDef(TriggerId("first_film"), WHEN, first),),
        opening=(*(Unlock(UnlockKind.STORE, str(s)) for s in (FILM, MEAL)),
                 *(Unlock(UnlockKind.ACTION, str(a)) for a in (SETTLE, TABLE))))
