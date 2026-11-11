"""Days four to six as the routes play them (daythree/chapter.Later): which content step is which story id, read off a
save, and each chapter's sinks, steps, shares and cures, on the rules day three loads (all the chapters in writing
merged). Ids only (CLAUDE.md, "Never spoil the owner")."""
from ashfall_app.engine import AfterTime, AnswerId, CardId, OfferId, Order, StoreId, TapCard, Unlock, UnlockKind
from tests.daythree import content as c3
from tests.daythree.chapter import Cure, Landings, Later, Share
from tests.dayone.sinks import Chapter, Trip

HAND_ON_STONE, STONES, HURT = CardId("hand_on_stone"), StoreId("stones"), StoreId("hurt")
WOODSHED, HEARTH_STONES = CardId("woodshed"), CardId("hearth_stones")
SPEAR, BEDDING = CardId("make_spear"), CardId("pelt_bedding")
HUNT = CardId("hunt_wolf")
DIG_BED = CardId("n3_dig_bed")

FOUR = Landings(
    {"L1": ("t_morning_5",), "L2": ("t_sign",), "L3": ("t_shed_stack",), "SL8": ("t_his_watch",)},
    {"A21": ("sit_up_5",), "B6": ("sit_up_5",)}, {"SL7": ("woodshed", 3)}, {})
FIVE = Landings(
    {"M2": ("t_ridge",), "M1": ("t_pair_joins",), "SL9": ("t_arcana_2",), "SL10": ("t_seed",), "SL11": ("t_old_watch",)},
    {"A25": ("make_bay2", "n3_build_bay"), "A29": ("bank_fire_6",), "B7": ("bank_fire_6",)}, {},
    {"O-pair": OfferId("o_pair")})
SIX = Landings(
    {"SL12": ("t_spear_made",), "G1": ("t_first_pelt",), "N7": ("t_night_7",)},
    {"A27": ("b7_stand",), "A30": ("sit_fire_7",), "G2": ("sit_fire_7",)}, {"SL14": ("pelt_bedding", 6)},
    {"SL13": OfferId("o_pelt")})

ANSWERS = (*c3.ANSWERS, (OfferId("o_pair"), AnswerId("o_pair_room")))
"""Each arrival offer and the answer a route that lets newcomers stay gives; the kind's rule takes the role of the first."""
TRACK_STONES = Trip(c3.TRACK, STONES)
STONE_DAMP = Trip(HAND_ON_STONE, c3.DAMP_WOOD, share_bp=2500, reserve_for=(c3.DRYING,))
"""G2: Arcana's card takes the shared store, kept from drinking the drying wall's damp wood as the track was; the track
moves to another of its supplies."""
BED_RULE = (Unlock(UnlockKind.CARD, DIG_BED), Order(AfterTime(0), TapCard(DIG_BED)))
"""Her bed on her lane is dug by a rule of the player's (a capped card is never a share)."""


def day_four() -> Later:
    return Later(
        start="B5", stop="B6",
        sinks=Chapter(trips=(c3.TRACK_DAMP,), comforts=(*c3.COMFORTS, WOODSHED),
                      arrivals=c3.ANSWERS),
        steps=(CardId("sit_up_5"), CardId("bank_hearth")), order_cards=c3.order_cards(c3.opening3()), keeps=c3.keeps(),
        landed=FOUR.of, news=("L1", "L2", "L3", "A21", "B6", "SL7", "SL8"))


def day_five() -> Later:
    return Later(
        start="B6", stop="B7",
        sinks=Chapter(trips=(STONE_DAMP, TRACK_STONES), comforts=(*c3.COMFORTS, WOODSHED, HEARTH_STONES),
                      arrivals=ANSWERS),
        steps=(CardId("bank_fire_6"), CardId("make_bay2")),
        order_cards=(*c3.order_cards(c3.opening3()), BED_RULE), keeps=c3.keeps(),
        landed=FIVE.of, news=("M2", "O-pair", "A25", "M1", "A29", "B7", "SL9", "SL10", "SL11"))


def day_six() -> Later:
    return Later(
        start="B7", stop="G2",
        sinks=Chapter(trips=(STONE_DAMP, TRACK_STONES), comforts=(*c3.COMFORTS, WOODSHED, HEARTH_STONES, SPEAR, BEDDING),
                      arrivals=ANSWERS),
        steps=(CardId("b7_stand"), CardId("sit_fire_7")),
        order_cards=(*c3.order_cards(c3.opening3()), BED_RULE), keeps=c3.keeps(),
        landed=SIX.of, news=("A27", "G1", "A30", "G2", "SL12", "SL13", "SL14"),
        answers=((OfferId("o_pelt"), AnswerId("o_pelt_give")),),
        shares=(Share(CardId("hunt_wolf"), 1500),), cures=(Cure(CardId("poultice"), HURT),))


def chapters() -> tuple[Later, ...]:
    return (c3.day_three(), day_four(), day_five(), day_six())
