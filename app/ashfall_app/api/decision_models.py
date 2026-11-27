"""Wire models of the game API's decisions and the shapes they share with the view: requests, conditions, mixes,
orders and the queue. The conventions are models.py's; models.py re-exports every name here, so callers keep
importing from it."""
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .limits import MAX_MIX_PARTS, MAX_OR_ELSE, MAX_ORDERS, MAX_QUEUE, MAX_UNLESS, NO_NUL

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
    """An offer shown (contract/offers.txt, "Offers")."""
    ANSWERED = "answered"
    """An offer answered, by any answer; the id is the offer's."""
    ANSWER = "answer"
    """The answer given; the id is the answer's."""
    JOINED = "joined"
    """A ruled lane's person has joined the town; the id is the lane (contract/the-towns-mix.txt, "The town's mix")."""
    LEFT = "left"
    """A ruled lane's person has left the town for good; the id is the lane (contract/leaves.txt, "LEAVES")."""
    ENTRY = "entry"
    """A journal page written; the id is the entry's (contract/journal.txt, "JOURNAL")."""
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
    """1 while the runner runs, else 0. In set_orders, taken only on an order whose every action is a tap_card of a card
    on one lane other than the hands, watching a card of another lane (the hands' or another person's); every other
    order's, and every queue entry's, is 422 invalid_decision (contract/endpoints.txt, "Decisions")."""

    kind: Literal["running"] = "running"
    runner: str


type Subject = Annotated[
    StoreValue | SkillLevel | CardCount | Unlocked | Running, Field(discriminator="kind")
]


class AtLeast(BaseModel):
    """value_of_cap, release_of_cap: that level is basis points (0..10000) of the watched store's cap now, not a
    quantity; on a store_value, in orders and queue entries only (contract/the-client-may.txt, "a store rule"; engine design/share-levels.txt,
    "SHARE LEVELS")."""

    kind: Literal["at_least"] = "at_least"
    watched: Subject
    value: int
    release: int
    value_of_cap: bool = False
    release_of_cap: bool = False


class AtMost(BaseModel):
    """value_of_cap, release_of_cap as AtLeast's."""

    kind: Literal["at_most"] = "at_most"
    watched: Subject
    value: int
    release: int
    value_of_cap: bool = False
    release_of_cap: bool = False


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
    """Answer a shown, open offer (contract/offers.txt, "Offers"): 422 when the answer is not one of the offer's, or the
    offer is not shown or already answered."""

    kind: Literal["answer_offer"] = "answer_offer"
    offer: str
    answer: str


class AnswerKind(Request):
    """Order verb only (never a Decision): answer the first open offer of `offer_kind` with its answer of `role`
    (contract/offers.txt, "Offers"). 422 when no offer declares that kind and role."""

    kind: Literal["answer_kind"] = "answer_kind"
    offer_kind: str
    role: str


type OrderVerb = Annotated[SwitchMix | TapCard | AnswerOffer | AnswerKind, Field(discriminator="kind")]


class Order(BaseModel):
    """A rule. Its actions are `then` followed by `or_else`: the first that can act is the one it runs. While any
    guard in `unless` holds, the rule is paused. Both lists are left out when empty (contract/endpoints.txt, "Rule guards")."""

    when: Condition
    then: OrderVerb
    unless: list[Condition] = Field(default=[], max_length=MAX_UNLESS)
    """Guards, each the condition that blocks the rule (engine design/rule-guards.txt, "RULE GUARDS")."""
    or_else: list[OrderVerb] = Field(default=[], max_length=MAX_OR_ELSE)
    """Fallback actions, tried after `then` in this order."""
    below_next: bool = False
    """The rule sits under Next, the queue's row: a ready queue entry outranks it (contract/endpoints.txt, "Next's row")."""


class OrderGuard(BaseModel):
    """One guard of a rule as the engine reads it now (View.order_guards)."""

    on: bool
    """Its latch: true while the guard blocks the rule."""
    lets_go: int | None
    """The quantity of the watched store at which it lets go, a share level read against the cap now; null off a store."""


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
    """By hand only, never an order's or a queue entry's verb (contract/prestige-phases.txt, "PRESTIGE PHASES"): one rank into `node`
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
