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
  ruleOutranked: "ui.rule.outranked", // "{rule}": an earlier rule has the hands (its condition's words)
  rulePassedOver: "ui.rule.passed_over", // a rule whose mix is greyed or whose task is done
  ruleStuck: "ui.rule.stuck", // "{n}{store}": a rule holding the hands whose release cannot be reached for want of a store
  ruleUnfed: "ui.rule.unfed", // "{store}{n}": a rule's mix consumes a store none of its cards makes, so it may stop short
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
