// A feature's card (CONTRACT.txt, "A feature's card"): the content's end card is one. Shown once, when the page first sees
// its feature unlocked, after what arrived with it; docked at the panel's foot (the bottom edge on a phone) and not
// modal, so the scene stays in view and play goes on under it. Its one button puts it away. A page whose first view
// already holds the feature never shows it, so nothing is kept for it.
import type { FeatureCard as CardText, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { el } from "./dom";
import type { Part } from "./part";
import type { Arrivals } from "./reveal";

const SETTLE_MS = 1500;   // after the last thing that came with the feature, before the card comes up

export class FeatureCard implements Part {
  readonly root = el("dialog", "sheet end-card end-dock");
  /** The card waiting for what came with its feature to be revealed. */
  private pending: CardText | null = null;

  constructor(private readonly catalog: Catalog, private readonly arrivals: Arrivals, host: Pick<HTMLElement, "append">) {
    host.append(this.root);
  }

  update(view: View, prev: View | null): void {
    if (!prev) return;
    const had = new Set(prev.unlocked.filter((u) => u.category === "feature").map((u) => u.id));
    for (const f of this.catalog.content.feature_infos) {
      const now = view.unlocked.some((u) => u.category === "feature" && u.id === f.feature);
      if (f.feature_card && now && !had.has(f.feature)) this.pending = f.feature_card;
    }
  }

  tick(): void {
    const card = this.pending;
    if (!card || this.arrivals.busy) return;
    this.pending = null;
    window.setTimeout(() => this.show(card), SETTLE_MS);
  }

  private show(card: CardText): void {
    if (this.root.open) return;
    const { text } = this.catalog;
    const done = el("button", "primary", text.get(card.button_key));
    done.type = "button";
    done.addEventListener("click", () => this.root.close());
    const row = el("div", "sheet-actions");
    row.append(done);
    this.root.replaceChildren(el("h2", "end-title", text.get(card.title_key)),
      ...card.line_keys.map((k) => el("p", "end-body", text.get(k))), row);
    this.root.show();   // not modal: nothing dims the scene
    this.reserve();
  }

  /** Publishes the card's height as --end-h while it is up, for the phone layout to pad the page by. */
  private reserve(): void {
    const style = document.documentElement.style;
    const watch = new ResizeObserver(() => style.setProperty("--end-h", `${this.root.offsetHeight}px`));
    watch.observe(this.root);
    this.root.addEventListener("close", () => { watch.disconnect(); style.removeProperty("--end-h"); }, { once: true });
  }
}
