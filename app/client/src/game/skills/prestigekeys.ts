// The text keys of a skill's prestige: its row, its sheet and the line a return brings (merged into `UI`, game/text.ts).
export const PRESTIGE_KEYS = {
  prestigeTopsOut: "ui.prestige.tops_out",   // "{d}": the forecast's time to the phase's top
  prestigeTop: "ui.prestige.top",   // the row's next slot at the top
  prestigeMastered: "ui.prestige.mastered",   // the row's next slot at the top once the track is done
  prestigeWaiting: "ui.prestige.waiting",   // "{n}": levels the carried XP lands the new phase at
  prestigeWaitingOne: "ui.prestige.waiting_one",   // "{n}", at one
  prestigeButton: "ui.prestige.button",   // the row's control at the top, and each node's in the sheet
  prestigeChoose: "ui.prestige.choose",   // the row's control while a pick is owed, and each node's then
  prestigeUndo: "ui.prestige.undo",
  prestigeHeading: "ui.prestige.heading",   // "{skill}"
  prestigeStarts: "ui.prestige.starts",   // "{before}{after}{n}": the level the top lifts from and to, and the level the carried XP takes the skill to
  prestigeOwed: "ui.prestige.owed",   // the sheet's line while a pick is owed
  prestigeBegun: "ui.prestige.begun",   // "{n}": the sheet after a click, beside Undo: the level the skill is at
  prestigeMake: "ui.prestige.make",   // "{store}{runner}{before}{after}": a make per minute, before and after one rank
  prestigeWork: "ui.prestige.work",   // "{card}{before}{after}": a card's time per completion
  prestigeCap: "ui.prestige.cap",   // "{store}{before}{after}": a store's cap in items
  prestigePicks: "ui.prestige.picks",   // the row's control once a skill has picks: opens the sheet to move one
  prestigeMove: "ui.prestige.move",   // a picked node's button: start moving its rank
  prestigeMoveTo: "ui.prestige.move_to",   // "{node}": what moving costs, and the ask for where it goes
  prestigeMoveHere: "ui.prestige.move_here",   // a menu node's button while moving
  prestigeParked: "ui.prestige.parked",   // "{node}{n}": a parked rank, back with the push n from now
  prestigeParkedOne: "ui.prestige.parked_one",   // "{node}", at the next push
  prestigeReached: "ui.prestige.reached",   // "{skill}{d}": a return's line, the skill's top that long ago
  prestigeReachedNow: "ui.prestige.reached_now",   // "{skill}": the same line, live
  lessonPrestige: "ui.lesson.prestige",   // "{skill}": the Push past control, the first time a skill is at its top
} as const;
