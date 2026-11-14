// The text keys of the Asks list (merged into `UI`, game/text.ts; CONTRACT.txt, "OFFERS").
export const ASK_KEYS = {
  asks: "ui.asks.heading",
  asksMore: "ui.asks.more", // "{n}": how many open asks wait behind the one shown; opens the whole list
  askFigure: "ui.ask.figure", // "{name}{before}{after}": a figure an answer moves, now and once given
  askAnswerWas: "ui.ask.answer_was", // "{answer}": the earlier answer that led to an ask, by its label
} as const;
