// A chip's node on the band (ui/story.ts): its word, beside it the level when the store it watches is one a lost fight
// adds to (Catalog.isLevel; "hurt 2"), and under it what it costs (ChipInfo.cost_key). The level follows the store's
// served level (View.levels) as it heals.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { sample } from "../game/clock";
import { chipStore } from "../game/ruleoffers";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

const LEVEL = "chip-level";

export function chipNode(catalog: Catalog, id: string): HTMLElement {
  const info = catalog.chips.get(id);
  const node = el("span", "chip", catalog.label(info?.label_key));
  const store = info ? chipStore(info) : null;
  if (store !== null && catalog.isLevel(store)) {
    const level = el("span", LEVEL);
    level.dataset["store"] = store;
    node.append(level);
  }
  if (info?.cost_key) node.append(el("span", "chip-cost", catalog.text.fill(info.cost_key, catalog.format.figures(info.change_bp))));
  node.dataset["tone"] = info?.tone ?? "";
  return node;
}

/** Each level on the band at game second t, as its store's served segment has it then. */
export function drawLevels(catalog: Catalog, band: HTMLElement, view: View, t: number): void {
  for (const level of band.querySelectorAll<HTMLElement>(`.${LEVEL}`)) {
    const served = view.levels.find((l) => l.store === level.dataset["store"]);
    setText(level, served ? ` ${catalog.format.level(sample(served.segment, t))}` : "");
  }
}

/** A node of the band's row, by its key: `chip:<id>`, or `keep:<id>` for the book carried (ui/story.ts). */
export function bandItem(ctx: PartContext, key: string): HTMLElement {
  const [kind, id = ""] = key.split(":");
  const { catalog } = ctx;
  if (kind === "chip") {
    const node = chipNode(catalog, id);
    ctx.arrivals.arrive(node, "chip", id);
    return node;
  }
  const node = el("span", "chip keep", catalog.label(catalog.content.feature_infos.find((f) => f.feature === id)?.label_key));
  node.dataset["keep"] = id;
  ctx.arrivals.arrive(node, "feature", id);
  return node;
}
