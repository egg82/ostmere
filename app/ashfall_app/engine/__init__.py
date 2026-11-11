"""The economy engine: a pure, deterministic discrete-event simulation. Imports only the stdlib and itself.
Semantics and the invariants tests check: DESIGN.txt beside this file."""
from .api import (
    Line, Step, advance, advance_logged, decide, decide_logged, explain, explain_work, level, new_save, next_event,
    segment, value, xp,
)
from .answers import AnswerKind, AnswerOffer
from .context import DecisionContext, context_from_json, context_to_json, decision_context
from .codec import FORMAT, decode, encode, rules_digest, verb_from_json, verb_to_json
from .errors import (
    EngineError, InvalidRulesError, InvalidVerbError, RebaseError, StateFormatError, TimeOrderError,
)
from .events import CascadeLimit, Event, EventKind
from .cards import (
    HELD_PREFIX, Amount, Blocker, CapRaise, CardDef, CardState, FightDef, HeldSpeed, Join, LaneState, Leave, Outcome,
    RuleInstall, WhileRunning,
)
from .flows import Flow
from .forecast import Forecast, forecast
from .ids import (
    HANDS, TOWN_PREFIX, ActionId, AnswerId, CardId, ChipId, EntryId, FeatureId, IdKind, KindId, LaneId, LineKey, MixId, NodeId, NoteId, OfferId, RoleId, Runner, SkillId,
    SideId, SourceId, StoreId, ThreatId, TriggerId,
)
from .lanes import LaneDef, TapCard
from .mixes import MAX_MIXES, CardShare, Mix, SpentShare, SubMix, SwitchMix, flatten_shares
from .modifiers import (
    Explanation, FlowKind, LaneSpeed, Modifier, ModifierKind, RateRef, Run, RunKind, SideStrength, StoreCap, Target,
    ThreatStrength, WorkRef, modified_rate,
)
from .orders import (
    AfterTime, AtLeast, AtMost, CardCount, Condition, LaneRules, Order, OrderVerb, QueueEntry, Running, SkillLevel,
    StoreValue, Subject, Unlocked,
)
from .offers import AnswerDef, OfferDef
from .plan import OrderState
from .rebase import rebase, rebase_logged
from .rulelog import Ended, RuleChange
from .renaming import Rename
from .powers import explain_strength, strength
from .strengthmath import StrengthExplanation
from .nodes import NODE_PREFIX, NodeDef, NodeTarget, PrestigeDef
from .prestigeverbs import MovePick, Prestige, PrestigeRefusal, PrestigeRefused, UndoPick
from .rules import PacingCurve, Rules, SkillDef, StandingDef, StoreDef, validate_rules
from .segments import Segment, reach_time, value_at
from .skills import level_for, xp_for
from .strengthdefs import SideDef, ThreatDef
from .state import FIRST_PHASE, ParkedRank, Pause, PhaseState, Save, SkillState, StoreState
from .status import ChipDef, TriggerDef
from .unlocks import Unlock, UnlockKind, unlock_key
from .upgrade import OLDEST_FORMAT, UPGRADES
from .units import BP, QUANTITY_SCALE, RATE_SCALE, SECONDS_PER_HOUR, ceil_div, per_hour, units
from .verbs import DeleteMix, SaveMix, SetOrders, SetQueue, Verb
from .needs import store_need
from .pending import Pending, pending
from .spent import spent_stores
from .view import View, view
from .fightview import FightView
from .viewparts import (
    AnswerView, CardView, CompletedCard, Contribution, HeldView, LaneBar, LedgerLine, MenuNode, Need, OfferView, RunBy,
    SkillBar, SkillPhase, StandingBar,
)

__all__ = [
    "Line", "Step", "advance", "advance_logged", "decide", "decide_logged", "explain", "explain_work", "level",
    "new_save", "next_event", "segment", "value", "xp",
    "DecisionContext", "context_from_json", "context_to_json", "decision_context",
    "FORMAT", "decode", "encode", "rules_digest", "verb_from_json", "verb_to_json",
    "OLDEST_FORMAT", "UPGRADES", "Ended", "Rename", "RuleChange", "rebase", "rebase_logged",
    "EngineError", "InvalidRulesError", "InvalidVerbError", "RebaseError", "StateFormatError", "TimeOrderError",
    "CascadeLimit", "Event", "EventKind",
    "HELD_PREFIX", "Amount", "Blocker", "CapRaise", "CardDef", "CardState", "FightDef", "Join", "LaneState", "Leave", "Outcome",
    "RuleInstall", "WhileRunning", "HeldSpeed",
    "AnswerDef", "OfferDef",
    "Flow",
    "Forecast", "forecast",
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
    "SkillLevel", "StoreValue", "Subject", "Unlocked",
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
    "CardView", "CompletedCard", "Contribution", "HeldView", "LaneBar", "LedgerLine", "MenuNode", "Need", "RunBy", "SkillBar", "SkillPhase",
    "StandingBar",
    "AnswerKind", "AnswerOffer", "AnswerView", "OfferView", "FightView",
    "View", "store_need", "view", "Pending", "pending", "spent_stores",
]
