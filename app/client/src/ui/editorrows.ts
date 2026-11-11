// The mix editor's entry rows (ui/editor.ts): one per component, with its share, what it does at that share (from the
// dry run's view, `after`) and a ✕ that drops it.
import type { Mix, View } from "../api/types";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import { segmentSpecs } from "./hands";
import type { PartContext } from "./part";

export function entryRows(ctx: PartContext, mix: Mix, view: View, after: View | null, drop: (i: number) => void): HTMLElement[] {
  const { catalog } = ctx;
  const specs = segmentSpecs(ctx, mix, view);
  return mix.components.map((c, i) => {
    const spec = specs[i];
    const row = el("div", `editor-entry hue-${(spec?.hue ?? 0) % 6}`);
    if (spec?.struck) row.classList.add("struck");
    const name = el("span", "entry-name", spec?.label ?? "");
    if (spec?.struck && c.kind === "card_share" && catalog.retired(view, c.card)) name.append(el("span", "entry-note", ` (${catalog.text.get(UI.retired)})`));
    const does = el("span", "entry-does");
    if (c.kind === "card_share" && after) {
      const parts = after.ledger.flatMap((l) => l.contributions.filter((k) => k.runner === c.card && k.per_hour !== 0)
        .map((k) => `${catalog.storeLabel(l.store)} ${catalog.format.perMinute(k.per_hour)}`));
      setText(does, parts.join(" · "));
    }
    const remove = el("button", "entry-remove", "✕");
    remove.type = "button";
    if (c.kind === "card_share") remove.dataset["card"] = c.card;   // a lesson's step names the card it points at
    remove.setAttribute("aria-label", `${catalog.text.get(UI.close)} ${spec?.label ?? ""}`);
    remove.disabled = mix.components.length < 2;
    remove.addEventListener("click", () => drop(i));
    row.append(el("i", "swatch"), name, el("span", "entry-share", catalog.format.share(c.share_bp)), does, remove);
    return row;
  });
}
