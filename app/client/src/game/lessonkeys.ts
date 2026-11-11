// The text keys of the lessons and the journal (merged into `UI`, game/text.ts).
export const LESSON_KEYS = {
  lessonTag: "ui.lesson.tag",   // the note's label: the guide is talking
  lessonNext: "ui.lesson.next",   // the note's tap target on a read step
  lessonSkip: "ui.lesson.skip",   // the lesson's way out, at every step
  lessonShow: "ui.lesson.show",   // a first offer's guided button, in place of its one-tap one
  lessonMixOffer: "ui.lesson.mix_offer",
  lessonMixAdd: "ui.lesson.mix_add",   // "{card}"
  lessonMixAddMore: "ui.lesson.mix_add_more",   // "{card}"
  lessonMixBar: "ui.lesson.mix_bar",
  lessonMixSave: "ui.lesson.mix_save",
  lessonMixRuns: "ui.lesson.mix_runs",
  lessonMixList: "ui.lesson.mix_list",   // where the player's mixes live: the strip's Mixes
  lessonRuleHands: "ui.lesson.rule_hands",
  lessonRuleLane: "ui.lesson.rule_lane",
  lessonRuleDo: "ui.lesson.rule_do",   // "{task}"
  lessonRuleWhen: "ui.lesson.rule_when",   // "{when}"
  lessonRuleAdd: "ui.lesson.rule_add",
  lessonRuleKept: "ui.lesson.rule_kept",
  lessonRuleOn: "ui.lesson.rule_on",   // "{task}"
  lessonSecondHint: "ui.lesson.second_hint",   // "{card}": the card tapped by hand again and again
  lessonSecondOpen: "ui.lesson.second_open",   // the strip's Mixes: the list
  lessonSecondNew: "ui.lesson.second_new",
  lessonSecondAdd: "ui.lesson.second_add",   // the whole Add row: the tasks are the player's pick
  lessonSecondBar: "ui.lesson.second_bar",
  lessonSecondName: "ui.lesson.second_name",
  lessonSecondSave: "ui.lesson.second_save",   // saving runs nothing
  lessonSecondRun: "ui.lesson.second_run",   // switching is Run in the list
  lessonCapFull: "ui.lesson.cap_full",   // "{store}": the full line, what is lost past the top
  lessonCapRules: "ui.lesson.cap_rules",   // the Rules tab: a rule can move the hands on
  lessonCapNew: "ui.lesson.cap_new",
  lessonCapMore: "ui.lesson.cap_more",   // More options: every store
  lessonCapLevels: "ui.lesson.cap_levels",
  lessonCapReaches: "ui.lesson.cap_reaches",   // "{store}"
  lessonCapDo: "ui.lesson.cap_do",   // the Do row: the player's own pick
  lessonDryLine: "ui.lesson.dry_line",   // "{store} {card}": the dry line, the mix card stopped on it
  lessonDryEdit: "ui.lesson.dry_edit",   // "{task} {store}": the card that makes it; points at Edit
  lessonDrySave: "ui.lesson.dry_save",   // "{card} {task} {store}": where the stopped card's time goes
  lessonDryRule: "ui.lesson.dry_rule",   // the other answer, a rule, in one line
  lessonTownChange: "ui.lesson.town_change",
  lessonTownBar: "ui.lesson.town_bar",
  lessonTownSave: "ui.lesson.town_save",
  lessonTownRuns: "ui.lesson.town_runs",
  lessonStoppedEdit: "ui.lesson.stopped_edit",   // "{card}": the done card the greyed mix holds; points at Edit
  lessonStoppedEditWith: "ui.lesson.stopped_edit_with",   // "{card} {task}": the done card, and the one that takes its place
  lessonStoppedAdd: "ui.lesson.stopped_add",   // "{task}": the editor's add button for it
  lessonStoppedDrop: "ui.lesson.stopped_drop",   // "{card}": the editor's ✕ on that card
  lessonStoppedSave: "ui.lesson.stopped_save",
  lessonSwitchMixes: "ui.lesson.switch_mixes",   // "{build} {store} {mix}": the build's wait, the mix that makes it; points at the way to the list
  lessonSwitchRun: "ui.lesson.switch_run",   // "{mix}": its Run in the list
  lessonSwitchEdit: "ui.lesson.switch_edit",   // "{build} {store} {task}": the build's wait, the card that makes it; points at Edit
  lessonSwitchSave: "ui.lesson.switch_save",   // "{store}"
  lessonJournalOpen: "ui.lesson.journal_open", // the Journal button: what gets written in it
  lessonJournalNotes: "ui.lesson.journal_notes", // the open page's last note: notes are added, a dot says one is new
  lessonJournalNumbers: "ui.lesson.journal_numbers", // the page's numbers: exact once fought
  journalHeading: "ui.journal.heading",
  journalPrev: "ui.journal.prev",
  journalNext: "ui.journal.next",
  journalDays: "ui.journal.days",
  journalCreatures: "ui.journal.creatures",
  journalPlaces: "ui.journal.places",
  lessonClock: "ui.lesson.clock",   // the countdown of a wait the player is not shown the store of: the night
} as const;
