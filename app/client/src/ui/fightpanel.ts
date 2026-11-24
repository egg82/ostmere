// A fight's odds (docs/design/opening-screen.md, "Fights"; CONTRACT.txt, "FIGHTS"): what the fight is worth, as served.
// "1 in 5 lost" (a percentage when no small pair is exact), the two strengths beside it ("yours 12, theirs 9"), each a
// button that opens its entries, the base first, and what one lost fight costs. A standing fight adds its tally. The
// card draws it beside its tap (never inside the button), the ledger under a threat's name.
import type { Fight, FightInfo, Strength, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { COMBAT, fightOf, oddsWords } from "../game/fights";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import { Bonus } from "./bonus";
import { strengthItems } from "./strength";

type Side = "power" | "threat";
const GAP = ["\u0001", "\u0002"] as const;   // where the two strengths go in the vs words

/** A fight card's parts: its tap and When ready in a body of their own with the odds under it, so the button stays
 * in the foot's band under the bar, never over the odds. A card's bonus line (bonus.ts) sits between the two. */
export function seatFight(node: HTMLElement, tap: HTMLElement, ready: HTMLElement, panel: FightPanel | null, bonus: Bonus | null = null): void {
  const body = el("div", "card-body");
  body.append(tap, ready);
  node.classList.add("fighting");
  node.append(body, ...(bonus ? [bonus.line] : []), ...(panel ? [panel.root] : []));
}

export class FightPanel {
  readonly root = el("div", "fight");
  private readonly odds = el("span", "fight-odds");
  private readonly vs = el("span", "fight-vs");
  private readonly loss = el("span", "fight-loss");
  private readonly tally = el("span", "fight-tally");
  private readonly entries = el("ul", "fight-entries");
  private open: Side | null = null;
  private shown = "";
  private fight: Fight | null = null;

  constructor(private readonly catalog: Catalog, private readonly info: FightInfo, tally = false) {
    this.entries.hidden = true;
    this.tally.hidden = !tally;
    const items = (a: { quantity: number }): string => catalog.format.level(a.quantity);
    const costs = info.loses.map((a) => `${items(a)} ${catalog.storeLabel(a.store)}`);
    const hurts = info.wounds.map((a) => catalog.text.fill(UI.fightOnWound, { store: catalog.storeLabel(a.store), n: items(a) }));
    const own = info.on_loss_key ? catalog.text.get(info.on_loss_key) : null;   // LOSS LINES: the card's words
    const words = own !== null ? [own] : [...(costs.length ? [catalog.text.fill(UI.fightOnLoss, { costs: costs.join(", ") })] : []), ...hurts];
    this.loss.textContent = words.join("; ");
    this.loss.hidden = words.length === 0;
    this.root.append(this.odds, this.vs, this.entries, this.loss, this.tally);
  }

  /** Shown while the `combat` feature is on and the view serves this runner's fight; else hidden. */
  sync(view: View, runner: string): void {
    const fight = this.catalog.unlocked(view, "feature", COMBAT) ? fightOf(view, runner) : undefined;
    this.root.hidden = fight === undefined;
    if (fight) this.draw(fight);
  }

  /** Draws the fight as the view serves it; the strengths are rebuilt only when they change, so an open list stays open. */
  draw(fight: Fight): void {
    this.fight = fight;
    const key = JSON.stringify([fight.fought === 0, fight.loss_bp, fight.power, fight.threat_strength]);
    if (key !== this.shown) {
      this.shown = key;
      this.drawOdds(fight);
      this.drawVs(fight);
      this.drawEntries();
    }
    if (!this.tally.hidden) setText(this.tally, this.catalog.text.fill(UI.fightTally, { fought: String(fight.fought), lost: String(fight.lost) }));
  }

  private drawOdds(fight: Fight): void {
    this.odds.textContent = oddsWords(this.catalog.text, fight, this.catalog.content.scales.bp);
  }

  private drawVs(fight: Fight): void {
    const { catalog, info } = this;
    const words = catalog.text.fill(UI.fightVs, { side_name: catalog.sideLabel(info.side), power: GAP[0], threat_name: catalog.threatLabel(info.threat), threat: GAP[1] });
    const parts = words.split(/([\u0001\u0002])/).filter((p) => p !== "");
    this.vs.replaceChildren(...parts.map((p) => (p === GAP[0] ? this.button("power", fight.power) : p === GAP[1] ? (fight.fought === 0 ? this.catalog.text.get(UI.fightThreatUnknown) : this.button("threat", fight.threat_strength)) : p)));
  }

  private button(side: Side, strength: Strength): HTMLButtonElement {
    const b = el("button", "fight-strength", String(strength.value));
    b.type = "button";
    b.setAttribute("aria-expanded", String(this.open === side));
    b.addEventListener("click", () => {
      tapFeedback();
      this.open = this.open === side ? null : side;
      this.drawEntries();
      for (const other of this.vs.querySelectorAll("button")) other.setAttribute("aria-expanded", String(other === b && this.open === side));
    });
    return b;
  }

  /** The open strength's sheet (strength.ts): the label of the side or threat it belongs to, then its entries. */
  private drawEntries(): void {
    const fight = this.fight;
    const strength = fight && this.open ? (this.open === "power" ? fight.power : fight.threat_strength) : null;
    this.entries.hidden = strength === null;
    if (!strength) { this.entries.replaceChildren(); return; }
    const { catalog, info } = this;
    this.entries.replaceChildren(...strengthItems(catalog, strength, this.open === "power" ? catalog.sideLabel(info.side) : catalog.threatLabel(info.threat)));
  }
}
