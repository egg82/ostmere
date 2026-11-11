// "Next", the queue in the Rules tab (docs/design/opening-screen.md, "The Rules tab"): what the queue will tap or run
// (a goal stint, ui/stint.ts), in its order, one line each with Remove, or "under way" for a tap a lane already runs. It sits between the hands rules and "Otherwise" because that is the order the
// engine gives the hands: a rule that is on first, then the queue's head once it is ready, else the player's own mix.
import type { QueueEntry, View } from "../api/types";
import { actionWords } from "../game/orders";
import { unqueue } from "../game/queue";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { stintFacts, stintWords } from "./stint";
import type { PartContext } from "./part";
import type { StintPlan } from "./stintplan";

/** The heading, one line per queue entry and the Plan control; nothing for an empty queue Plan does not offer. */
export function nextRows(ctx: PartContext, view: View, plan: StintPlan): HTMLElement[] {
  const planning = plan.rows(view);
  if (view.queue.length === 0 && planning.length === 0) return [];
  const { catalog } = ctx;
  const rows = view.queue.map((entry, i) => {
    const row = el("div", "rules-row next-row");
    const hue = entry.verb.kind === "tap_card" ? catalog.rank(entry.verb.card) % 6 : 5;
    const end = runsNow(view, entry) ? el("span", "next-running", catalog.text.get(UI.queueRunning)) : removeButton(ctx, view, i);
    const words = entry.verb.kind === "switch_mix" ? stintWords(catalog, view, entry) : actionWords(catalog, entry.verb);
    const action = el("b", `rule-action hue-${hue}`, words);
    const facts = stintFacts(catalog, view, i);
    if (facts !== null) action.append(el("span", "next-facts", facts));
    row.append(el("span", "rule-handle-gap"), action, end);
    return row;
  });
  return [el("h3", "rules-next", catalog.text.get(UI.queueHeading)), ...rows, ...planning];
}

/** Whether a lane is running the card the entry taps: the entry stays queued until that tap completes, and taking it
 * out would not stop the work, so it is not offered. */
function runsNow(view: View, entry: QueueEntry): boolean {
  const verb = entry.verb;
  return verb.kind === "tap_card" && view.lanes.some((l) => l.running_card === verb.card);
}

function removeButton(ctx: PartContext, view: View, i: number): HTMLElement {
  const remove = el("button", "quiet", ctx.catalog.text.get(UI.orderRemove));
  remove.type = "button";
  remove.addEventListener("click", () => { tapFeedback(); ctx.actions.decide(unqueue(view, i)); });
  return remove;
}
