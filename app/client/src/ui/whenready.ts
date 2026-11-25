// "When ready" on a card (docs/design/opening-screen.md, "Cards" and "The Rules tab"): a small button on a step that
// will turn ready by itself, or is ready on a lane running another tap (game/queue.canQueue), beside the card's own tap
// target, never inside it. It adds one tap of the card to the queue, and the card flies to the Rules tab, where Next lists it. Once queued it stays as a quiet
// "in Next" mark, so the card does not change size under the finger. The first time it is on show it takes the one
// glow (once a page session), the queue's taught step. On a staged card a tap runs it is "Until done" instead
// (game/untildone.ts), the hands' card panel and a person's page alike.
import type { Card, View } from "../api/types";
import { canQueue, onFace, queuedCards, queueFull, whenReady } from "../game/queue";
import { UI } from "../game/text";
import { untilDone } from "../game/untildone";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";

export class WhenReady {
  private glowed = false;
  private view: View | null = null;

  constructor(private readonly ctx: PartContext) {}

  /** The button for `card`'s node; `node` is what flies to the Rules tab. */
  make(card: string, node: HTMLElement): HTMLButtonElement {
    const b = el("button", "card-ready");
    b.type = "button";
    b.hidden = true;
    b.addEventListener("click", () => {
      const decision = this.view === null ? null : untilDone(this.ctx.catalog, this.view, card) ?? whenReady(this.ctx.catalog, this.view, card);
      if (decision === null) return;
      tapFeedback();
      this.ctx.actions.orderSent(node);
      this.ctx.actions.decide(decision);
    });
    return b;
  }

  /** Shown while the card can be queued, or is (then off, reading "in Next"), or can run on to its cap; hidden on a
   * finished card. The queue never holds a ruled lane's card, so there only Until done shows. */
  sync(button: HTMLButtonElement, card: Card | undefined, view: View): void {
    this.view = view;
    const { catalog } = this.ctx;
    const done = card !== undefined && untilDone(catalog, view, card.card) !== null;
    const c = done || card === undefined || catalog.ruled(card.card) ? undefined : card;   // one When ready may take
    const queued = c !== undefined && queuedCards(view).includes(c.card);
    const offered = c !== undefined && canQueue(catalog, view, c);
    const full = c !== undefined && !queued && queueFull(catalog, view) && onFace(catalog, view, c);
    button.hidden = !done && !queued && !offered && !full;
    button.disabled = !done && !offered;
    button.classList.toggle("queued", queued);
    setText(button, catalog.text.get(done ? UI.queueUntilDone : queued ? UI.queueQueued : full ? UI.queueFull : UI.queueWhenReady));
    if (offered && !this.glowed && !button.closest(".held")) this.glowed = this.ctx.glow.offer(button);
  }
}
