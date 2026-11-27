// A person with nothing to do (game/stuck.ts), on their Town row and their page: a line per held card saying what it is
// stopped on, then the tasks they could run now, each one tap that joins it to their time as a tap on its face does.
// It shows the first few and a way to the rest: the page from the strip, the task faces below on the page. Hidden while
// they have work.
import type { View } from "../../api/types";
import { runnableFor, stuckOf, type Stopped } from "../../game/town/stuck";
import { UI } from "../../game/page/text";
import { el, setText, tapFeedback } from "../dom";
import type { PartContext } from "../part";

/** How many tasks the note offers before "+n more". */
const OFFERS = 3;

export class StuckNote {
  readonly root = el("div", "stuck-note");
  private readonly why = el("div", "stuck-why");
  private readonly label = el("span", "stuck-label");
  private readonly offers = el("div", "stuck-offers");
  private drawn = "";

  /** `join` adds a card to the person's time; `more` leads to the rest (their page from the strip, the task faces on it). */
  constructor(private readonly ctx: PartContext, private readonly join: (card: string) => void, private readonly more: () => void) {
    setText(this.label, ctx.catalog.text.get(UI.townCanDo));
    this.root.append(this.why, this.label, this.offers);
    this.root.hidden = true;
  }

  /** Whether `lane` has nothing to do as of `view`; the note shows exactly then. */
  update(view: View, lane: string): boolean {
    const stuck = stuckOf(this.ctx.catalog, view, lane);
    this.root.hidden = stuck === null;
    if (stuck === null) { this.drawn = ""; return false; }
    const cards = runnableFor(this.ctx.catalog, view, lane);
    const drawn = JSON.stringify([stuck, cards]);
    if (drawn !== this.drawn) this.draw(stuck, cards);
    this.drawn = drawn;
    return true;
  }

  private draw(stuck: Stopped[], cards: string[]): void {
    const { catalog } = this.ctx;
    this.why.replaceChildren(...stuck.map((s) => el("p", `stuck-line ${s.why}`, this.words(s))));
    const shown = cards.slice(0, OFFERS);
    this.label.hidden = cards.length === 0;
    this.offers.replaceChildren(...shown.map((card) => this.button(`+ ${catalog.cardLabel(card)}`, () => this.join(card), `stuck-offer hue-${catalog.rank(card) % 6}`)));
    const rest = cards.length - shown.length;
    if (rest > 0) this.offers.append(this.button(catalog.text.fill(UI.townMore, { n: String(rest) }), this.more, "stuck-more quiet"));
  }

  private button(text: string, act: () => void, cls: string): HTMLElement {
    const b = el("button", cls, text);
    b.type = "button";
    b.addEventListener("click", () => { tapFeedback(); act(); });
    return b;
  }

  private words(s: Stopped): string {
    const { catalog } = this.ctx;
    const card = catalog.cardLabel(s.card);
    const store = s.store === null ? "" : catalog.storeLabel(s.store);
    if (s.store === null) return catalog.text.fill(UI.townStoppedWaiting, { card });
    const key = s.why === "spent" ? UI.townStoppedSpent : s.why === "full" ? UI.townStoppedFull : UI.townStoppedDry;
    return catalog.text.fill(key, { card, store });
  }
}
