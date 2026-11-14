// The figures each answer of an ask moves (game/asks.ts, answerFigures): one dry run per answer that installs a
// modifier (AnswerInfo.change_bp; an answer that starts a card or puts in stores says so in its cost text), never kept.
// Asked again only when what the figures are read against moves (the view's rates, caps and card times); until the
// new runs answer, the last ones stand.
import type { View } from "../api/types";
import { answerFigures } from "../game/asks";
import type { PartContext } from "./part";

/** What an answer's figures are read against: each store's net rate and cap, and each card's time. */
function basis(view: View): string {
  return JSON.stringify([view.ledger.map((l) => [l.store, l.net_per_hour, l.cap]), view.cards.map((c) => [c.card, c.tap_s])]);
}

export class AskRuns {
  private readonly got = new Map<string, { against: string; figures: Map<string, string[]> }>();
  private readonly asking = new Set<string>();

  /** `landed`: new figures came in, so the asks draw again. */
  constructor(private readonly ctx: PartContext, private readonly landed: () => void) {}

  /** The figures of `offer`'s answers so far, by answer; asks for them when none were read against this view. */
  figures(view: View, offer: string): ReadonlyMap<string, string[]> {
    const against = basis(view);
    const had = this.got.get(offer);
    if (had?.against !== against && !this.asking.has(offer)) void this.ask(view, offer, against);
    return had?.figures ?? new Map<string, string[]>();
  }

  private async ask(view: View, offer: string, against: string): Promise<void> {
    this.asking.add(offer);
    const figures = new Map<string, string[]>();
    try {
      for (const a of this.ctx.catalog.offers.get(offer)?.answers ?? []) {
        if (a.change_bp.length === 0) continue;
        const after = await this.ctx.actions.dryRun([{ kind: "answer_offer", offer, answer: a.answer }]);
        if (after) figures.set(a.answer, answerFigures(this.ctx.catalog, view, after));
      }
    } finally {
      this.asking.delete(offer);
    }
    this.got.set(offer, { against, figures });
    this.landed();
  }
}
