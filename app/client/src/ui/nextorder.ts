// Next's order (docs/design/opening-screen.md, "The Rules tab"): each entry a lane is not already running has a ≡ in
// the row's handle gap, dragged as a rule's is (ruledrag.ts) or moved by ArrowUp / ArrowDown; either sends the queue
// whole in its new order (game/queue.ts, "moveQueued").
import type { View } from "../api/types";
import { moveQueued, movableEntries } from "../game/queue";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";
import { RuleDrag } from "./ruledrag";

export class NextOrder {
  private readonly drag: RuleDrag;
  /** The entry whose ≡ takes the focus once the new order is drawn (it was moved by a key). */
  private focus: number | null = null;

  /** `view`: what the tab shows; `ended`: a drag is over and the tab redraws. */
  constructor(private readonly ctx: PartContext, root: HTMLElement, view: () => View | null, ended: () => void) {
    this.drag = new RuleDrag({
      root, view, group: (v) => movableEntries(v),
      dropped: (what, target) => this.send(view(), what.rule, Number(target.dataset["next"])),
      ended,
    }, "next");
  }

  /** The ≡ for entry `index`, or the gap it fills when the entry stays put or has nothing to move past. */
  handle(view: View, index: number): HTMLElement {
    const movable = movableEntries(view);
    if (movable.length < 2 || !movable.includes(index)) return el("span", "rule-handle-gap");
    const handle = el("button", "rule-handle", "≡");
    handle.type = "button";
    handle.setAttribute("aria-label", this.ctx.catalog.text.get(UI.queueMove));
    handle.addEventListener("keydown", (e) => {
      const step = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
      const to = movable[movable.indexOf(index) + step];
      if (step === 0) return;
      e.preventDefault();
      if (to !== undefined && this.send(view, index, to)) this.focus = to;
    });
    this.drag.attach(handle, () => ({ rule: index }));
    if (this.focus === index) { this.focus = null; queueMicrotask(() => handle.focus()); }
    return handle;
  }

  private send(view: View | null, from: number, to: number): boolean {
    const decision = view === null ? null : moveQueued(view, from, to);
    if (decision === null) return false;
    tapFeedback();
    this.ctx.actions.decide(decision);
    return true;
  }
}
