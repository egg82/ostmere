"""The economy engine: a pure, deterministic discrete-event simulation. Imports only the stdlib and itself.
Semantics and the invariants tests check: engine/design/ beside this file."""
from .core.api import (
    Line, Step, advance, advance_logged, decide, decide_logged, explain, explain_work, level, new_save, next_event,
    segment, value, xp,
)
from .offers.answers import AnswerKind, AnswerOffer
from .savefile.context import DecisionContext, context_from_json, context_to_json, decision_context
from .savefile.codec import FORMAT, decode, encode, rules_digest, verb_from_json, verb_to_json
from .core.errors import (
    EngineError, InvalidRulesError, InvalidVerbError, StateFormatError, TimeOrderError,
)
from .core.events import CascadeLimit, Event, EventKind
from .cards.cards import (
    HELD_PREFIX, Amount, Blocker, CapRaise, Cast, CastPick, CardDef, CardState, ChainDef, FightDef, HeldSpeed, Join,
    LaneState, Leave, Mark, Outcome, RuleInstall, WhileRunning,
)
from .core.flows import Flow
from .lookahead.forecast import Forecast, ForecastPath, forecast
from .core.ids import (
    HANDS, TOWN_PREFIX, ActionId, AnswerId, CardId, ChipId, EntryId, FeatureId, IdKind, KindId, LaneId, LineKey, MixId, NodeId, NoteId, OfferId, RoleId, Runner, SkillId,
    SideId, SourceId, StoreId, ThreatId, TriggerId,
)
from .orders.lanes import LaneDef, TapCard
from .mixes.mixes import MAX_MIXES, CardShare, Mix, SpentShare, SubMix, SwitchMix, flatten_shares
from .modifiers.modifiers import (
    ChainReach, Explanation, FlowKind, LaneSpeed, Modifier, ModifierKind, RateRef, Run, RunKind, SideStrength, StoreCap, Target,
    ThreatStrength, WorkRef, modified_rate,
)
from .orders.orders import (
    MAX_ACTIONS, MAX_GUARDS, AfterTime, AtLeast, AtMost, CardCount, Condition, GuardedLatch, LaneRules, Latch, Order, OrderVerb,
    QueueEntry, Running, SkillLevel, StoreValue, Subject, Unlocked,
)
from .offers.offers import AnswerDef, OfferDef
from .orders.plan import OrderState
from .savefile.rebase import rebase, rebase_logged
from .orders.rulelog import Ended, RuleChange
from .combat.powers import explain_strength, strength
from .combat.strengthmath import StrengthExplanation
from .prestige.nodes import NODE_PREFIX, NodeDef, NodeTarget, PrestigeDef
from .prestige.prestigeverbs import MovePick, Prestige, PrestigeRefusal, PrestigeRefused, UndoPick
from .core.rules import PacingCurve, Rules, SkillDef, StandingDef, StoreDef, validate_rules
from .core.segments import Segment, reach_time, value_at
from .core.skills import level_for, xp_for
from .combat.strengthdefs import SideDef, ThreatDef
from .core.state import FIRST_PHASE, ParkedRank, Pause, PhaseState, Save, SkillState, StoreState
from .cards.status import ChipDef, TriggerDef
from .unlocks.unlocks import Unlock, UnlockKind, unlock_key
from .savefile.upgrade import OLDEST_FORMAT, UPGRADES
from .core.units import BP, QUANTITY_SCALE, RATE_SCALE, SECONDS_PER_HOUR, ceil_div, per_hour, units
from .core.verbs import DeleteMix, SaveMix, SetOrders, SetQueue, Verb
from .cards.needs import store_need
from .cards.pending import Pending, pending
from .mixes.spent import spent_stores
from .read.view import View, view
from .read.fightview import FightView
from .combat.chains import ChainView, chain_views
from .read.viewparts import (
    AnswerShift, AnswerView, CardView, CompletedCard, Contribution, GuardView, HeldView, LaneBar, LedgerLine, MenuNode, Need, OfferView, RunBy,
    SkillBar, SkillPhase, StandingBar,
)

__all__ = [
    "Line", "Step", "advance", "advance_logged", "decide", "decide_logged", "explain", "explain_work", "level",
    "new_save", "next_event", "segment", "value", "xp",
    "DecisionContext", "context_from_json", "context_to_json", "decision_context",
    "FORMAT", "decode", "encode", "rules_digest", "verb_from_json", "verb_to_json",
    "OLDEST_FORMAT", "UPGRADES", "Ended", "RuleChange", "rebase", "rebase_logged",
    "EngineError", "InvalidRulesError", "InvalidVerbError", "StateFormatError", "TimeOrderError",
    "CascadeLimit", "Event", "EventKind",
    "HELD_PREFIX", "Amount", "Cast", "CastPick", "Blocker", "CapRaise", "CardDef", "CardState", "FightDef", "Join", "LaneState", "Leave", "Mark", "Outcome",
    "RuleInstall", "WhileRunning", "HeldSpeed", "ChainDef", "ChainReach", "ChainView", "chain_views",
    "AnswerDef", "OfferDef",
    "Flow",
    "Forecast", "ForecastPath", "forecast",
    "HANDS", "TOWN_PREFIX", "ActionId", "AnswerId", "CardId", "ChipId", "EntryId", "FeatureId", "NoteId", "IdKind", "KindId", "LaneId", "LineKey", "MixId", "OfferId", "RoleId",
    "NodeId", "Runner", "SideId", "SkillId", "SourceId", "ThreatId",
    "StoreId", "TriggerId",
    "LaneDef", "TapCard",
    "MAX_MIXES", "CardShare", "Mix", "SpentShare", "SubMix", "SwitchMix", "flatten_shares",
    "Explanation", "FlowKind", "LaneSpeed", "Modifier", "ModifierKind", "RateRef", "Run", "RunKind", "StoreCap",
    "SideStrength", "ThreatStrength", "Target", "WorkRef",
    "SideDef", "ThreatDef", "StrengthExplanation", "explain_strength", "strength",
    "modified_rate",
    "AfterTime", "AtLeast", "AtMost", "CardCount", "Condition", "LaneRules", "Order", "OrderVerb", "OrderState", "QueueEntry", "Running",
    "SkillLevel", "StoreValue", "Subject", "Unlocked", "MAX_ACTIONS", "MAX_GUARDS", "GuardedLatch", "Latch",
    "PacingCurve", "Rules", "SkillDef", "StandingDef", "StoreDef", "validate_rules",
    "NODE_PREFIX", "NodeDef", "NodeTarget", "PrestigeDef", "Prestige", "PrestigeRefusal", "PrestigeRefused", "UndoPick",
    "MovePick",
    "Segment", "reach_time", "value_at",
    "level_for", "xp_for",
    "FIRST_PHASE", "ParkedRank", "Pause", "PhaseState", "Save", "SkillState", "StoreState",
    "ChipDef", "TriggerDef",
    "Unlock", "UnlockKind", "unlock_key",
    "BP", "QUANTITY_SCALE", "RATE_SCALE", "SECONDS_PER_HOUR", "ceil_div", "per_hour", "units",
    "DeleteMix", "SaveMix", "SetOrders", "SetQueue", "Verb",
    "CardView", "CompletedCard", "Contribution", "GuardView", "HeldView", "LaneBar", "LedgerLine", "MenuNode", "Need", "RunBy", "SkillBar", "SkillPhase",
    "StandingBar",
    "AnswerKind", "AnswerOffer", "AnswerShift", "AnswerView", "OfferView", "FightView",
    "View", "store_need", "view", "Pending", "pending", "spent_stores",
]
