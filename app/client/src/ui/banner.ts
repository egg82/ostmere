// A feature's one-time hint banner.
import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { el } from "./dom";
import type { Arrivals } from "./reveal";

/** A feature's hint, shown once when the feature unlocks; a tap puts it away. */
export class Banner {
  readonly root = el("div", "banners");

  constructor(private readonly catalog: Catalog, private readonly arrivals: Arrivals) {}

  update(view: View, prev: View | null): void {
    if (!prev) return;
    const had = new Set(prev.unlocked.filter((u) => u.category === "feature").map((u) => u.id));
    for (const unlock of view.unlocked) {
      if (unlock.category !== "feature" || had.has(unlock.id)) continue;
      const hint = this.catalog.features.get(unlock.id);
      if (hint) this.show(this.catalog.text.get(hint), unlock.id);
    }
  }

  private show(text: string, feature: string): void {
    const node = el("button", "banner", text);
    node.type = "button";
    node.addEventListener("click", () => node.remove());
    this.root.append(node);
    this.arrivals.arrive(node, "feature", feature);
  }
}
