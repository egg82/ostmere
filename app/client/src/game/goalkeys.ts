// The text keys of the editors' goal rows (ui/goaltimes.ts; CONTRACT.txt, "Goal rows") and of goal stints (ui/stint.ts;
// "Goal stints"), merged into `UI`, game/text.ts.
export const GOAL_ROW_KEYS = {
  goalHead: "ui.goal.head",   // the rows' first column
  goalStore: "ui.goal.store",   // "{store} {n}": a store goal, the store's title and its target
  goalLevel: "ui.goal.level",   // "{skill} {n}": a level goal
  goalNever: "ui.goal.never",   // a goal the rates as set do not land
  goalLimited: "ui.goal.limited",   // "{store} {n}": the dry store a card moving the goal waits on, and what comes in
  goalXp: "ui.goal.xp",   // "{n}": a level goal's own line
  stintRun: "ui.stint.run",   // the mix editor's button that lists goals to run the mix until (ui/stint.ts)
  stintEntry: "ui.stint.entry",   // "{mix} until {goal}": a goal stint in Next
  stintWhich: "ui.stint.which",   // "{mix} until…": Next's Plan, once a mix is picked and its goals are listed
  stintRan: "ui.stint.ran",   // "{d}": how long a popped stint ran, in Lately
  stintLanded: "ui.stint.landed",   // "{ago}": when its goal landed, in Lately
  stintMade: "ui.stint.made",   // "{n}{store}": what the save gained in a store while the stint ran, in Lately
  stintMadeTwo: "ui.stint.made_two",   // "{n}{store}{m}{store_b}": the same for two stores
} as const;
