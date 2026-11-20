// The camp header's one control for the permanent bonuses carried (FeatureInfo.label_key; chips are the passing states,
// ui/chipnode.ts): a count that opens their list, each bonus with what it does (FeatureInfo.effect_key, figured as an
// answer's cost is). The header keeps what changes; these only ever grow, and every figure
// that uses them counts them whether or not the list is open.
import type { Content } from "../api/types";
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import { markNew } from "./fresh";

export class KeptBonuses {
  readonly root = el("span", "kept");
  private readonly button = el("button", "kept-button");
  private readonly list = el("ul", "kept-list");
  private ids: string[] = [];
  /** `arrive`: called when the control first appears. */
  constructor(private readonly catalog: Catalog, private readonly arrive: (node: HTMLElement, id: string) => void) {
    this.button.type = "button";
    this.button.setAttribute("aria-expanded", "false");
    this.list.hidden = true;
    this.root.hidden = true;
    this.root.append(this.button, this.list);
    this.button.addEventListener("click", () => { tapFeedback(); this.toggle(this.list.hidden); });
    document.addEventListener("pointerdown", (e) => { if (!this.list.hidden && !this.root.contains(e.target as Node)) this.toggle(false); });
    this.root.addEventListener("keydown", (e) => { if (e.key === "Escape" && !this.list.hidden) { this.toggle(false); this.button.focus(); } });
  }

  private toggle(open: boolean): void {
    this.list.hidden = !open;
    this.button.setAttribute("aria-expanded", String(open));
  }

  /** The features carried that are bonuses, in content order; the list opened stays open across redraws. */
  update(features: Content["feature_infos"]): void {
    const ids = features.map((f) => f.feature);
    const grew = this.ids.length > 0 && ids.some((id) => !this.ids.includes(id));
    const first = this.ids.length === 0 && ids.length > 0;
    this.ids = ids;
    this.root.hidden = ids.length === 0;
    if (ids.length === 0) this.toggle(false);
    setText(this.button, this.catalog.text.fill(UI.keptBonuses, { n: String(ids.length) }));
    this.list.replaceChildren(...features.map((f) => {
      const li = el("li", "");
      li.dataset["keep"] = f.feature;
      li.append(el("span", "kept-name", this.catalog.label(f.label_key)));
      if (f.effect_key) li.append(el("span", "kept-effect", this.catalog.text.fill(f.effect_key, this.catalog.format.figures(f.change_bp))));
      return li;
    }));
    if (first) this.arrive(this.root, ids[0]!);
    else if (grew && this.list.hidden) markNew(this.root, () => undefined);
  }
}
