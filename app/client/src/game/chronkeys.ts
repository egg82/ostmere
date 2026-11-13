// The text keys of the chronicle (merged into `UI`, game/text.ts): its button, a stretch's title, the filters, a
// rule's entries, and the words of a cause (CONTRACT.txt, "Line causes").
export const CHRONICLE_KEYS = {
  chronicle: "ui.chronicle.open",
  chronAwayM: "ui.chronicle.away_m",
  chronAwayH: "ui.chronicle.away_h",
  chronAwayHm: "ui.chronicle.away_hm",
  chronAwayD: "ui.chronicle.away_d",
  chronEarlier: "ui.chronicle.earlier",
  chronNow: "ui.chronicle.now",
  chronStory: "ui.chronicle.story",
  chronFinds: "ui.chronicle.finds",
  chronLevels: "ui.chronicle.levels",
  chronRules: "ui.chronicle.rules",
  chronFights: "ui.chronicle.fights",
  chronTalk: "ui.chronicle.talk",
  chronAll: "ui.chronicle.all",
  chronCount: "ui.chronicle.count", // "{name} {n}": how many entries of a filter a stretch holds
  chronRuleOn: "ui.chronicle.rule_on", // "{rule}"
  chronRuleOff: "ui.chronicle.rule_off", // "{rule}"
  causeStore: "ui.cause.store", // "{store} {n}": a store reached
  causeBelow: "ui.cause.below", // "{store} {n}": a store fell to
  causeLevel: "ui.cause.level", // "{skill} {n}"
  causeSkill: "ui.cause.skill", // "{skill}": a level of the skill, which one not known
  causeCount: "ui.cause.count", // "{card} {n}": times a card was done
  causeCamp: "ui.cause.camp", // "{n}"
  causeTime: "ui.cause.time",
  causeAnswer: "ui.cause.answer",
} as const;
