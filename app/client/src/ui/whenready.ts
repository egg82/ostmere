// "When ready" on a card (docs/design/opening-screen.md, "Cards" and "The Rules tab"): a small button on a step that
// will turn ready by itself (game/queue.canQueue), beside the card's own tap target, never inside it. It adds one tap
// of the card to the queue, and the card flies to the Rules tab, where Next lists it. Once queued it stays as a quiet
// "in Next" mark, so the card does not change size under the finger. The first time it is on show it takes the one
// glow (once a page session), the queue's taught step.
import type { Card, View } from "../api/types";
import { canQueue, queuedCards, queueable, queueFull, queueTap } from "../game/queue";
import { UI } from "../game/text";
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
      const view = this.view;
      const live = view?.cards.find((c) => c.card === card);
      if (!view || !live || !canQueue(this.ctx.catalog, view, live)) return;
      tapFeedback();
      this.ctx.actions.orderSent(node);
      this.ctx.actions.decide(queueTap(view, live));
    });
    return b;
  }

  /** Shown while the card can be queued, or is (then off, reading "in Next"); hidden on a finished card. */
  sync(button: HTMLButtonElement, card: Card | undefined, view: View): void {
    this.view = view;
    const { catalog } = this.ctx;
    const queued = card !== undefined && queuedCards(view).includes(card.card);
    const offered = card !== undefined && canQueue(catalog, view, card);
    const full = !queued && card !== undefined && queueFull(catalog, view) && queueable(catalog, view, card);
    button.hidden = !queued && !offered && !full;
    button.disabled = !offered;
    button.classList.toggle("queued", queued);
    setText(button, catalog.text.get(queued ? UI.queueQueued : full ? UI.queueFull : UI.queueWhenReady));
    if (offered && !this.glowed && !button.closest(".held")) this.glowed = this.ctx.glow.offer(button);
  }
}
