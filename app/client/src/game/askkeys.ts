// The text keys of the Asks list (merged into `UI`, game/text.ts; contract/offers.txt, "OFFERS").
export const ASK_KEYS = {
  asks: "ui.asks.heading",
  asksMore: "ui.asks.more", // "{n}": how many open asks wait behind the one shown; opens the whole list
  askShift: "ui.ask.shift", // "{before}{after}": a lasting change's total now and once given, in a cost text's {pct} slot
  askFigure: "ui.ask.figure", // "{name}{before}{after}": a figure an answer moves, now and once given
} as const;
