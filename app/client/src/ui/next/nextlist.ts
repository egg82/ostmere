// "Next", the queue in the Rules tab (docs/design/opening-screen/rules-tab.md, "The Rules tab"): what the queue will tap or run
// (a goal stint, ui/next/stint.ts), in its order, one line each with Remove, or "under way" for a tap a lane already runs.
// Each tap is one run: runs of the same card one after another are one line, "×N", whose Remove and ≡ act on one. Its
// heading is a row among the hands rules, moved as one (game/nextrow.ts): the rules above it outrank a ready head, the
// rules under it wait for one (contract/endpoints.txt, "Next's row"). It starts at the bottom, just above "Otherwise".
import type { QueueEntry, View } from "../../api/types";
import { NEXT } from "../../game/rules/nextrow";
import { actionWords } from "../../game/rules/orders";
import { entryRuns, queueRows, runsNow, unqueue } from "../../game/mixes/queue";
import { UI } from "../../game/page/text";
import { el, tapFeedback } from "../dom";
import { ruleMenu } from "../rules/rulemenu";
import type { Catalog } from "../../game/page/catalog";
import { stintFacts, stintWords } from "./stint";
import type { NextOrder } from "./nextorder";
import type { PartContext } from "../part";
import type { StintPlan } from "./stintplan";

/** Next's row (`head`: its ≡ and the lines hanging under it, game/nextrow.ts), one line per queue entry and the Plan
 * control; nothing for an empty queue Plan does not offer, unless the row is kept off the bottom (head.kept: it stays
 * where the player can move it back). */
export function nextRows(ctx: PartContext, view: View, plan: StintPlan, order: NextOrder, head: NextHead = { handle: el("span", "rule-handle-gap"), under: [], kept: false }): HTMLElement[] {
  const planning = plan.rows(view);
  if (view.queue.length === 0 && planning.length === 0 && !head.kept) return [];
  const { catalog } = ctx;
  const rows = queueRows(view).map((run) => {
    const i = run[0]!, last = run[run.length - 1]!, entry = view.queue[i]!;
    const row = el("div", "rules-row next-row");
    row.dataset["next"] = String(i);
    const hue = entry.verb.kind === "tap_card" ? catalog.rank(entry.verb.card) % 6 : 5;
    const end = runsNow(view, i) ? el("span", "next-running", catalog.text.get(UI.queueRunning)) : removeButton(ctx, view, last, run.length > 1);
    const runs = run.reduce((n, k) => n + (entryRuns(view, k) ?? 0), 0);
    const action = el("b", `rule-action hue-${hue}`, entryWords(catalog, view, entry, runs));
    const facts = stintFacts(catalog, view, i);
    if (facts !== null) action.append(el("span", "next-facts", facts));
    row.append(order.handle(view, last, run.length > 1), action, end);
    return row;
  });
  const heading = el("div", "rules-row next-head");
  heading.dataset["rule"] = String(NEXT);
  heading.append(head.handle, el("h3", "rules-next", catalog.text.get(UI.queueHeading)));
  return [heading, ...head.under, ...rows, ...planning];
}

/** What the Rules tab hangs on Next's row: its ≡ (or the gap), the lines under it (its open menu), and whether the
 * row is off the bottom. */
export interface NextHead {
  handle: HTMLElement;
  under: HTMLElement[];
  kept: boolean;
}

/** An entry's words: a stint's mix and goal; a tap's card, "once" (the tap under way's too) or ×`runs`; an answer's. */
function entryWords(catalog: Catalog, view: View, entry: QueueEntry, runs: number): string {
  if (entry.verb.kind === "switch_mix") return stintWords(catalog, view, entry);
  if (entry.verb.kind !== "tap_card") return actionWords(catalog, view, entry.verb);
  const card = catalog.cardLabel(entry.verb.card);
  return runs > 1 ? catalog.text.fill(UI.queueRuns, { card, n: catalog.format.count(runs) }) : catalog.text.fill(UI.queueOnce, { card });
}

function removeButton(ctx: PartContext, view: View, i: number, one: boolean): HTMLElement {
  const remove = el("button", "quiet", ctx.catalog.text.get(one ? UI.queueRemoveOne : UI.orderRemove));
  remove.type = "button";
  remove.addEventListener("click", () => { tapFeedback(); ctx.actions.decide(unqueue(view, i)); });
  return remove;
}

/** Next's row's ≡ (`handle`, built only when there is a rule to move past; else the gap) and, `open`, its menu: moved as a
 * rule's is, never removed. `items`: the hands' rows, with NEXT among them while its row is drawn. */
export function nextHead(catalog: Catalog, items: readonly number[], open: boolean, handle: () => HTMLElement, move: (step: -1 | 1) => void): NextHead {
  if (items.length < 2) return { handle: el("span", "rule-handle-gap"), under: [], kept: false };
  const first = items[0] === NEXT, last = items[items.length - 1] === NEXT;
  return { handle: handle(), under: open ? [ruleMenu(catalog, { first, last, move })] : [], kept: !last };
}
