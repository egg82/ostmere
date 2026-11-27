// Next's order (docs/design/opening-screen/rules-tab.md, "The Rules tab"): each row a lane is not already running has a ≡ in
// the row's handle gap, dragged as a rule's is (ruledrag.ts) or moved by ArrowUp / ArrowDown; either moves one entry
// (a row of several runs gives up its last) past the next row and sends the queue whole in its new order
// (game/mixes/queue.ts, "moveQueued", "rowStep").
import type { View } from "../../api/types";
import { moveQueued, movableEntries, queueRows, rowStep, runsNow } from "../../game/mixes/queue";
import { UI } from "../../game/page/text";
import { el, tapFeedback } from "../dom";
import type { PartContext } from "../part";
import { RuleDrag } from "../rules/ruledrag";

export class NextOrder {
  private readonly drag: RuleDrag;
  /** The entry whose ≡ takes the focus once the new order is drawn (it was moved by a key). */
  private focus: number | null = null;

  /** `view`: what the tab shows; `ended`: a drag is over and the tab redraws. */
  constructor(private readonly ctx: PartContext, root: HTMLElement, view: () => View | null, ended: () => void) {
    this.drag = new RuleDrag({
      root, view, group: (v) => movableEntries(v),
      dropped: (what, target) => this.send(view(), what.rule, dropAt(view(), what.rule, Number(target.dataset["next"]))),
      ended,
    }, "next");
  }

  /** The ≡ for entry `index` (`one`: the last of a row of several runs, which it moves alone), or the gap it fills
   * when the entry stays put or has nothing to move past. */
  handle(view: View, index: number, one = false): HTMLElement {
    const rows = queueRows(view).filter((r) => !runsNow(view, r[0]!));
    if (rows.length < 2 || !movableEntries(view).includes(index)) return el("span", "rule-handle-gap");
    const handle = el("button", "rule-handle", "≡");
    handle.type = "button";
    handle.setAttribute("aria-label", this.ctx.catalog.text.get(one ? UI.queueMoveOne : UI.queueMove));
    handle.addEventListener("keydown", (e) => {
      const step = e.key === "ArrowUp" ? -1 : e.key === "ArrowDown" ? 1 : 0;
      if (step === 0) return;
      e.preventDefault();
      const to = rowStep(view, index, step);
      if (to !== null && this.send(view, index, to)) this.focus = to;
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

/** The entry a drop on the row starting at `first` moves `from` to: before that row when it is above, after its last
 * entry when below. */
function dropAt(view: View | null, from: number, first: number): number {
  const row = view === null ? undefined : queueRows(view).find((r) => r[0] === first);
  return row === undefined || first < from ? first : row[row.length - 1]!;
}
