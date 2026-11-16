// The Rules page's switch, Mine | Camp (docs/decisions/mixes.md, "Mine and Camp"): two buttons at the top of the rules
// list, the side shown pressed. Camp is named as the town is (ui.town.title).
import type { SideKept } from "../app/ruleside";
import type { Decision, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { landedSide, ruleSideOf, sideSwitchShown, type RuleSide } from "../game/ruleside";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";

export function sideSwitch(catalog: Catalog, side: RuleSide, pick: (side: RuleSide) => void): HTMLElement {
  const box = el("div", "rules-side");
  for (const [which, label] of [["mine", UI.ruleSideMine], ["camp", UI.townTitle]] as const) {
    const b = el("button", "cond-test rules-side-pick", catalog.text.get(label));
    b.type = "button";
    b.dataset.side = which;
    b.setAttribute("aria-pressed", String(which === side));
    b.addEventListener("click", () => { if (which === side) return; tapFeedback(); pick(which); });
    box.append(b);
  }
  return box;
}

/** The side the page shows: the one this device kept once the switch shows, else null (one list). */
export class RuleSides {
  constructor(private readonly catalog: Catalog, private readonly kept: SideKept) {}

  now(view: View): RuleSide | null {
    return sideSwitchShown(this.catalog, view) ? this.kept.get() : null;
  }

  set(side: RuleSide): void {
    this.kept.set(side);
  }

  /** Shows the side of rule `index`, or `side` itself, while the switch shows. */
  follow(view: View, to: number | RuleSide): void {
    if (this.now(view) !== null) this.kept.set(typeof to === "number" ? ruleSideOf(this.catalog, view, to) : to);
  }

  /** Shows the side of the first rule `d` adds or changes. */
  land(view: View, d: Decision): void {
    const to = this.now(view) === null ? null : landedSide(this.catalog, view, d);
    if (to !== null) this.kept.set(to);
  }
}
