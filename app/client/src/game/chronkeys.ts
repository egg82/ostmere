// The text keys of the chronicle (merged into `UI`, game/text.ts): its button, a stretch's title, the filters, a
// rule's entries, and the words of a cause (CONTRACT.txt, "Line causes").
export const CHRONICLE_KEYS = {
  chronicle: "ui.chronicle.open",
  chronAway: "ui.chronicle.away", // "{d}": an older stretch's title, d its awaySpan
  chronAwayM: "ui.chronicle.away_m", // "{m}": how long the player was away, under an hour
  chronAwayH: "ui.chronicle.away_h",
  chronAwayHm: "ui.chronicle.away_hm",
  chronAwayD: "ui.chronicle.away_d",
  chapter: "ui.chapter.title",
  chapterStores: "ui.chapter.stores",
  chapterLevels: "ui.chapter.levels",
  chapterRules: "ui.chapter.rules",
  chapterWaiting: "ui.chapter.waiting",
  chapterGain: "ui.chapter.gain", // "{n}{store}"
  chapterLoss: "ui.chapter.loss", // "{n}{store}"
  chapterLevel: "ui.chapter.level", // "{name}{before}{after}"
  chapterTimes: "ui.chapter.times", // "{rule}{n}": a rule that came on n times, n of 2 or more
  chapterAsk: "ui.chapter.ask", // "{n}": one ask waiting
  chapterAsks: "ui.chapter.asks", // "{n}"
  chapterStill: "ui.chapter.still", // nothing changed while the player was away
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
