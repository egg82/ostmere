"""Wire models of the game API's decisions and the shapes they share with the view: requests, conditions, mixes,
orders and the queue. The conventions are models.py's; models.py re-exports every name here, so callers keep
importing from it."""
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .limits import MAX_MIX_PARTS, MAX_ORDERS, MAX_QUEUE, NO_NUL

class Request(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------- shared shapes ----------

class Segment(BaseModel):
    """value(t) = start_value + rate * (t - start), held at limit once reached. The client samples this."""

    start: int
    start_value: int
    rate: int
    limit: int | None


class StoreValue(BaseModel):
    kind: Literal["store_value"] = "store_value"
    store: str


class SkillLevel(BaseModel):
    kind: Literal["skill_level"] = "skill_level"
    skill: str


class CardCount(BaseModel):
    """Completions of a card, taps and mix together."""

    kind: Literal["card_count"] = "card_count"
    card: str


class UnlockKind(StrEnum):
    ACTION = "action"
    CARD = "card"
    SKILL = "skill"
    STORE = "store"
    CHIP = "chip"
    FEATURE = "feature"
    RETIRED = "retired"
    """A card a newer one replaced: it is in View.completed, drawn as retired."""
    OFFER = "offer"
    """An offer shown (CONTRACT.txt, "Offers")."""
    ANSWERED = "answered"
    """An offer answered, by any answer; the id is the offer's."""
    ANSWER = "answer"
    """The answer given; the id is the answer's."""
    JOINED = "joined"
    """A ruled lane's person has joined the town; the id is the lane (CONTRACT.txt, "The town's mix")."""
    LEFT = "left"
    """A ruled lane's person has left the town for good; the id is the lane (CONTRACT.txt, "LEAVES")."""
    ENTRY = "entry"
    """A journal page written; the id is the entry's (CONTRACT.txt, "JOURNAL")."""
    NOTE = "note"
    """A note written on a page; the id is the note's."""


class Unlock(BaseModel):
    """`category`, not `kind`: on the wire `kind` is only ever a union's discriminator string."""

    category: UnlockKind
    id: str


class Unlocked(BaseModel):
    kind: Literal["unlocked"] = "unlocked"
    unlock: Unlock


class Running(BaseModel):
    kind: Literal["running"] = "running"
    runner: str


type Subject = Annotated[
    StoreValue | SkillLevel | CardCount | Unlocked | Running, Field(discriminator="kind")
]


class AtLeast(BaseModel):
    kind: Literal["at_least"] = "at_least"
    watched: Subject
    value: int
    release: int


class AtMost(BaseModel):
    kind: Literal["at_most"] = "at_most"
    watched: Subject
    value: int
    release: int


class AfterTime(BaseModel):
    kind: Literal["after_time"] = "after_time"
    at: int


type Condition = Annotated[AtLeast | AtMost | AfterTime, Field(discriminator="kind")]


# ---------- decisions (the engine's verbs) ----------

class CardShare(BaseModel):
    kind: Literal["card_share"] = "card_share"
    card: str
    share_bp: int = Field(ge=0, le=10_000)


class SubMix(BaseModel):
    kind: Literal["sub_mix"] = "sub_mix"
    mix_id: str
    share_bp: int = Field(ge=0, le=10_000)


class Mix(BaseModel):
    id: str = Field(min_length=1, max_length=40, pattern=NO_NUL)
    """The player's own name for the mix, shown verbatim (a tab, "runs" header): the one id that is player text.
    Content never names a mix, so no text entry or template refers to one."""
    components: list[Annotated[CardShare | SubMix, Field(discriminator="kind")]] = Field(max_length=MAX_MIX_PARTS)


class SwitchMix(Request):
    kind: Literal["switch_mix"] = "switch_mix"
    mix_id: str


class TapCard(Request):
    """One completion of a card by hand: a tap, a craft, a story step. The same verb from an order or the queue."""

    kind: Literal["tap_card"] = "tap_card"
    card: str


class AnswerOffer(Request):
    """Answer a shown, open offer (CONTRACT.txt, "Offers"): 422 when the answer is not one of the offer's, or the
    offer is not shown or already answered."""

    kind: Literal["answer_offer"] = "answer_offer"
    offer: str
    answer: str


class AnswerKind(Request):
    """Order verb only (never a Decision): answer the first open offer of `offer_kind` with its answer of `role`
    (CONTRACT.txt, "Offers"). 422 when no offer declares that kind and role."""

    kind: Literal["answer_kind"] = "answer_kind"
    offer_kind: str
    role: str


type OrderVerb = Annotated[SwitchMix | TapCard | AnswerOffer | AnswerKind, Field(discriminator="kind")]


class Order(BaseModel):
    when: Condition
    then: OrderVerb


class QueueEntry(BaseModel):
    verb: OrderVerb
    until: Condition


class SaveMix(Request):
    kind: Literal["save_mix"] = "save_mix"
    mix: Mix


class DeleteMix(Request):
    """Delete a saved mix (422 while another mix nests it or an order or queue entry names it)."""

    kind: Literal["delete_mix"] = "delete_mix"
    mix_id: str


class SetOrders(Request):
    kind: Literal["set_orders"] = "set_orders"
    orders: list[Order] = Field(max_length=MAX_ORDERS)


class SetQueue(Request):
    kind: Literal["set_queue"] = "set_queue"
    entries: list[QueueEntry] = Field(max_length=MAX_QUEUE)


class Prestige(Request):
    """By hand only, never an order's or a queue entry's verb (CONTRACT.txt, "PRESTIGE PHASES"): one rank into `node`
    on `skill`'s track. At the skill's top it is the click into the next phase; with SkillPrestige.pick_owed it fills
    that pick. A refusal is 422 invalid_decision, its message naming why."""

    kind: Literal["prestige"] = "prestige"
    skill: str
    node: str


class UndoPick(Request):
    """By hand only: take back `skill`'s last pick while SkillPrestige.undo_open, leaving it owed. A refusal is 422
    invalid_decision."""

    kind: Literal["undo_pick"] = "undo_pick"
    skill: str


class MovePick(Request):
    """By hand only: move the rank `node` holds on `skill`'s track to `to`, a node on SkillPrestige.menu_nodes. The rank
    is out of play, held by neither node, until the click that lifts the skill into the phase after next. A refusal
    is 422 invalid_decision."""

    kind: Literal["move_pick"] = "move_pick"
    skill: str
    node: str
    to: str


type Decision = Annotated[
    SwitchMix | TapCard | SaveMix | DeleteMix | SetOrders | SetQueue | AnswerOffer | Prestige | UndoPick | MovePick,
    Field(discriminator="kind"),
]
