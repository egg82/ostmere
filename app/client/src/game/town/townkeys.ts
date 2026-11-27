// The text keys of a person with nothing to do and the tasks offered them (game/town/stuck.ts; merged into `UI`, game/page/text.ts).
export const TOWN_KEYS = {
  townStuck: "ui.town.stuck",   // a person's row and page while every card holding their time is stopped
  townStoppedSpent: "ui.town.stopped_spent",   // "{card}{store}": a held card stopped on a store nothing makes now
  townStoppedFull: "ui.town.stopped_full",   // "{card}{store}": a held card stopped with no room in a store it fills
  townStoppedDry: "ui.town.stopped_dry",   // "{card}{store}": a held card waiting on a store it needs
  townStoppedWaiting: "ui.town.stopped_waiting",   // "{card}": a held card stopped with no short need to name
  townCanDo: "ui.town.can_do",   // the label before the tasks they could run now, each a one-tap join
  townMore: "ui.town.more",   // "{n}": the strip's way to the page, past the offers it shows
  cardSpentOn: "ui.card.spent_on",   // "{store}": a spent card's face, where its needs sit
  cardWasted: "ui.card.wasted",   // "{store}": a card running on a share while every store it makes is full (game/cards/wasted.ts)
  townWasted: "ui.town.wasted",   // "{card}{store}": a person's row while the card they work makes only into full stores
} as const;
