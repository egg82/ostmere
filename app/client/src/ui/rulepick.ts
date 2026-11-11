// The Rules tab's mix picker (docs/design/opening-screen.md, "The Rules tab"): choosing a slot's mix, every saved mix
// (greyed ones off) with the current one marked, or a new mix.
import type { Order, View } from "../api/types";
import { conditionWords, type RuleSlot as Slot } from "../game/orders";
import { mixesFull } from "../game/mix";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** What the tab does with a choice. */
export interface PickerActions {
  /** A saved mix chosen for the slot. */
  place(mixId: string): void;
  /** A new mix, for the slot. */
  fresh(): void;
  close(): void;
}

export function slotPicker(ctx: PartContext, view: View, slot: Slot, on: PickerActions): HTMLElement[] {
  const { catalog } = ctx;
  const { text } = catalog;
  const order: Order | undefined = slot === "otherwise" ? undefined : view.orders[slot];
  const current = slot === "otherwise" ? view.active_mix_id : order?.then.kind === "switch_mix" ? order.then.mix_id : null;
  const rows = view.mixes.map((m) => {
    const b = el("button", "selector-run");
    b.type = "button";
    b.disabled = view.greyed_mix_ids.includes(m.id);
    b.setAttribute("aria-pressed", String(m.id === current));
    b.append(el("span", "selector-dot", m.id === current ? "●" : ""), el("span", "selector-name", m.id));
    b.addEventListener("click", () => { tapFeedback(); on.place(m.id); });
    return b;
  });
  const fresh = mixesFull(catalog, view) ? el("p", "rules-full", text.get(UI.mixFull)) : newMixButton(ctx, on);
  const close = el("button", "editor-close", "✕");
  close.type = "button";
  close.setAttribute("aria-label", text.get(UI.close));
  close.addEventListener("click", () => on.close());
  const head = el("div", "cond-head");
  head.append(el("h2", "panel-heading", order ? conditionWords(catalog, order.when) ?? "" : text.get(UI.ruleOtherwise)), close);
  const group = el("div", "rule-picker");
  group.append(...rows, fresh);
  return [head, group];
}

function newMixButton(ctx: PartContext, on: PickerActions): HTMLButtonElement {
  const fresh = el("button", "quiet selector-new", ctx.catalog.text.get(UI.newMix));
  fresh.type = "button";
  fresh.addEventListener("click", () => { tapFeedback(); on.fresh(); });
  return fresh;
}
