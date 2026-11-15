// The text keys of the Rules tab and the condition editor (ui/rules.ts, ui/condition.ts, ui/rulewhy.ts; CONTRACT.txt, "Dry rules"),
// merged into `UI`, game/text.ts.
export const RULE_KEYS = {
  ruleFull: "ui.rule.full", // in the place of the New rule button once the rules hold Content.limits.max_orders
  ruleNew: "ui.rule.new", // the Rules tab's way to a new rule (once writing rules is open), and the simple editor's heading
  ruleDo: "ui.rule.do", // the condition editor's row of what a rule does
  ruleMoreOptions: "ui.rule.more_options", // opens the full condition editor from the simple one
  ruleBelow: "ui.rule.below", // "{store}{n}": a rule's condition with no band
  ruleBelowUntil: "ui.rule.below_until", // "{store}{n}{m}"
  ruleReaches: "ui.rule.reaches", // "{store}{n}"
  ruleReachesUntil: "ui.rule.reaches_until", // "{store}{n}{m}"
  ruleDownToUntil: "ui.rule.down_to_until", // "{store}{n}{m}": a "below" rule whose when is a share (storerule.ts)
  ruleUpToUntil: "ui.rule.up_to_until", // "{store}{n}{m}": a "reaches" rule, both levels shares
  ruleUpToUntilUnder: "ui.rule.up_to_until_under", // "{store}{n}{m}": a "reaches" rule, a share when and an amount until
  ruleReachesUntilDown: "ui.rule.reaches_until_down", // "{store}{n}{m}": a "reaches" rule, an amount when and a share until
  ruleOfFull: "ui.rule.of_full", // a level's two forms in the editor: a share of the store's cap, or whole items
  ruleExact: "ui.rule.exact",
  ruleQuickDown: "ui.rule.quick_down", // "{store}{test}{n}{task}{m}": the quick add's sentence for a "below" rule (ui/condquick.ts)
  ruleQuickUp: "ui.rule.quick_up", // the same for a "reaches" rule
  ruleFallsTo: "ui.rule.falls_to", // the quick add's two tests, its {test}
  ruleReachesTo: "ui.rule.reaches_to",
  ruleCopy: "ui.rule.copy", // a rule being changed: a new rule from it, the same task and condition, to change
  levelEmpty: "ui.level.empty", // a share level's words: the five named shares, then any other as a percentage
  levelQuarter: "ui.level.quarter",
  levelHalf: "ui.level.half",
  levelThreeQuarters: "ui.level.three_quarters",
  levelFull: "ui.level.full",
  levelPct: "ui.level.pct", // "{pct}"
  levelMarkQuarter: "ui.level.mark_quarter", // the editor's short marks for a quarter, half and three quarters
  levelMarkHalf: "ui.level.mark_half",
  levelMarkThreeQuarters: "ui.level.mark_three_quarters",
  ruleFallsBelow: "ui.rule.falls_below", // the condition editor's two tests
  ruleReachesLabel: "ui.rule.reaches_label",
  ruleWhen: "ui.rule.when", // the editor's two steppers
  ruleUntil: "ui.rule.until",
  ruleLess: "ui.rule.less", // a stepper's buttons, for screen readers
  ruleMore: "ui.rule.more",
  ruleHeading: "ui.rule.heading", // "{mix}": the condition editor's heading
  ruleWhileRuns: "ui.rule.while_runs", // "{mix}": before the store's rate while that mix runs
  ruleExists: "ui.rule.exists", // why Save is off: the same rule is already set
  ruleChip: "ui.rule.chip", // "{chip}": a rule whose condition is a chip's, worded as the chip
  ruleDone: "ui.rule.done", // "{card}{n}": a rule on how many times a task is done
  ruleDoneOnce: "ui.rule.done_once", // "{card}": the same, at once
  ruleReachesLevel: "ui.rule.reaches_level", // "{name}{n}": a rule on a skill's or the Camp's level
  ruleLevels: "ui.rule.levels", // the full editor's When heads: the skills and the Camp, then the tasks
  ruleTasks: "ui.rule.tasks",
  ruleTimes: "ui.rule.times", // the stepper of a count, and of a level
  ruleLevel: "ui.rule.level",
  ruleNeedsBelow: "ui.rule.needs_below", // "{store}{n}{have}": why an "under n" rule is off, and what the store holds now
  ruleNeedsReaches: "ui.rule.needs_reaches", // "{store}{n}{have}": why an "n or more" rule is off
  ruleNeedsDownTo: "ui.rule.needs_down_to", // "{store}{n}{have}": the same for a rule whose when is a share
  ruleNeedsUpTo: "ui.rule.needs_up_to", // "{store}{n}{have}"
  ruleOutranked: "ui.rule.outranked", // "{rule}": an earlier rule has the hands (its condition's words)
  rulePassedOver: "ui.rule.passed_over", // a rule whose mix is greyed or whose task is done
  ruleStuck: "ui.rule.stuck", // "{n}{store}": a rule holding the hands whose release cannot be reached for want of a store
  ruleUnfed: "ui.rule.unfed", // "{store}{n}": a rule's mix consumes a store none of its cards makes, so it may stop short
  rulePassedOverAll: "ui.rule.passed_over_all", // a rule with fallbacks every one of whose actions is dead
  ruleOrElse: "ui.rule.or_else", // "{a}{b}": a rule's actions, one fallback at a time (game/guardwords.ts)
  ruleUnless: "ui.rule.unless", // "{rule}{when}": a rule's condition and its first guard
  ruleAndUnless: "ui.rule.and_unless", // "{rule}{when}": each further guard
  guardFull: "ui.guard.full", // "{store}": a guard on a store, worded as a state, by its level's form
  guardEmpty: "ui.guard.empty", // "{store}"
  guardReaches: "ui.guard.reaches", // "{store}{n}"
  guardBelow: "ui.guard.below", // "{store}{n}"
  guardUpTo: "ui.guard.up_to", // "{store}{n}": n a share's words
  guardDownTo: "ui.guard.down_to", // "{store}{n}"
  guardDone: "ui.guard.done", // "{card}{n}": a guard on how many times a task is done
  guardDoneOnce: "ui.guard.done_once", // "{card}"
  guardLevel: "ui.guard.level", // "{name}{n}": a guard on a skill's or the Camp's level
  rulePaused: "ui.rule.paused", // "{until}": a paused rule's line, the clauses of the guards that hold
  ruleAnd: "ui.rule.and", // "{a}{b}": two of those clauses
  guardUntilUnder: "ui.guard.until_under", // "{store}{n}{have}": where an "n or more" store guard lets go, and the amount now
  guardUntilReaches: "ui.guard.until_reaches", // "{store}{n}{have}": the same for an "under n" store guard
  guardWhile: "ui.guard.while", // "{when}": a held guard off a store (a chip's, a count, a level)
  ruleUnlessLabel: "ui.rule.unless_label", // the full editor's guards, over their list
  ruleUnlessHint: "ui.rule.unless_hint",
  ruleUnlessAdd: "ui.rule.unless_add", // opens the picker of what a new guard watches
  ruleUnlessOrMore: "ui.rule.unless_or_more", // a store guard's two tests: it blocks at the level or more, or under it
  ruleUnlessUnder: "ui.rule.unless_under",
  ruleUnlessDone: "ui.rule.unless_done", // confirms the guard being written
  ruleElseLabel: "ui.rule.else_label", // the full editor's fallbacks, over their list
  ruleElseHint: "ui.rule.else_hint",
  ruleElseAdd: "ui.rule.else_add", // opens the picker of what a new fallback does
  ruleOnDoing: "ui.rule.on_doing", // "{task}": a rule with fallbacks that is on, running one past its first
  ruleOnNone: "ui.rule.on_none", // a rule with fallbacks that is on, none of whose actions can start
  ruleLately: "ui.rule.lately", // the Rules tab's last block: what the rules did lately
  ruleRanOnce: "ui.rule.ran_once", // an entry's count of starts, at one
  ruleRan: "ui.rule.ran", // "{n}": an entry's count of starts
  ruleCameOn: "ui.rule.came_on", // "{ago}": an entry's last start, for a rule on no shown store (a chip's)
  ruleCameOnAt: "ui.rule.came_on_at", // "{have}{store}{ago}": an entry's last start and the store's level then
  ruleLetGo: "ui.rule.let_go", // "{ago}"
  ruleLetGoAt: "ui.rule.let_go_at", // "{have}{store}{ago}"
  ruleEndedSeason: "ui.rule.ended_season", // "{rule}": an entry the game removed at a season's turn
  ruleEndedLeft: "ui.rule.ended_left", // "{rule}{person}": an entry the game removed when its person left
  ruleOtherwise: "ui.rule.otherwise", // the Rules tab's default row
  ruleOn: "ui.rule.on", // the accessible label of a rule's on dot
  ruleUp: "ui.rule.up",
  ruleDown: "ui.rule.down",
  ruleHandle: "ui.rule.handle", // a rule's ≡, for screen readers: it drags, or opens Move up · Move down · Remove
} as const;
