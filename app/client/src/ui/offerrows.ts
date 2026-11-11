// The offer rows (docs/design/opening-screen.md, the hands strip, "Offer"; CONTRACT.txt, "Offers"), in the hands strip
// where the mix offer sits: someone asks the player something. Each open offer is one row, its text and a button per
// answer naming what it takes (its cost_key, {d} from takes_s, left out while takes_s is null; {pct} from change_bp, {gain} from gains). No dismiss: it stays
// until answered, and a tap sends answer_offer (a refused one, answered since, is the session's: it asks again). It
// arrives through the arrival queue after the last of its lines in this Step, or at once when the Step holds none of
// them (it showed before the page's last view). An offer that arrives already answered draws no row. Not a guided
// offer: no lesson starts on it, so it never waits for one. It is told apart from the routine mix and rule rows by a
// plain panel with an ember edge (.offer-ask), and it takes the one glow, as the whole row, when the glow is free: a
// lesson's step keeps or takes it before the offer, and the offer waits for it (GlowWhile) until it is answered.
import type { Offer, View } from "../api/types";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { GlowWhile } from "./fresh";
import type { PartContext } from "./part";

interface Row { node: HTMLElement; costs: Map<string, HTMLElement>; glow: GlowWhile }

export class OfferRows {
  readonly root = el("div", "hands-offers");
  private readonly rows = new Map<string, Row>();

  constructor(private readonly ctx: PartContext) {}

  update(view: View): void {
    const open = view.offers.filter((o) => o.answer === null);
    for (const [id, row] of this.rows) {
      if (open.some((o) => o.offer === id)) continue;
      row.glow.used();
      row.node.remove();
      this.rows.delete(id);
    }
    for (const offer of open) this.costs(offer, this.rows.get(offer.offer) ?? this.add(offer));
  }

  /** Every frame: an offer that has not had the glow yet asks again once the control holding it lets go. */
  tick(): void {
    for (const row of this.rows.values()) row.glow.tick();
  }

  /** Each answer's cost: its time from takes_s now, its changes from change_bp and the stores it puts in from gains. */
  private costs(offer: Offer, row: Row): void {
    const { catalog } = this.ctx;
    const info = catalog.offers.get(offer.offer);
    for (const a of offer.answers) {
      const cost = row.costs.get(a.answer);
      const served = info?.answers.find((i) => i.answer === a.answer);
      const key = served?.cost_key;
      if (!cost) continue;
      cost.textContent = !served || !key || (a.takes_s === null && catalog.text.get(key).includes("{d}")) ? "" : catalog.text.fill(key, {
        d: a.takes_s === null ? "" : catalog.format.duration(a.takes_s), ...catalog.format.figures(served.change_bp), ...catalog.format.gains(served.gains),
      });
      cost.hidden = cost.textContent === "";
    }
  }

  private add(offer: Offer): Row {
    const { catalog } = this.ctx;
    const info = catalog.offers.get(offer.offer);
    const node = el("div", "hands-offer offer-row offer-ask");
    node.dataset.offer = offer.offer;
    const buttons = el("span", "offer-buttons");
    const costs = new Map<string, HTMLElement>();
    for (const a of info?.answers ?? []) {
      const b = el("button", "offer-both offer-answer");
      b.type = "button";
      b.dataset.answer = a.answer;
      const cost = el("span", "offer-cost");
      costs.set(a.answer, cost);
      b.append(el("span", "offer-label", catalog.label(a.label_key)), cost);
      b.addEventListener("click", () => { tapFeedback(); this.ctx.actions.decide({ kind: "answer_offer", offer: offer.offer, answer: a.answer }); });
      buttons.append(b);
    }
    node.append(el("p", "offer-text", catalog.label(info?.text_key)), buttons);
    this.root.append(node);
    const row = { node, costs, glow: new GlowWhile(this.ctx.glow, node) };
    this.rows.set(offer.offer, row);
    const keys = new Set(info?.line_keys ?? []);
    if (this.ctx.lines().some((l) => keys.has(l.key))) this.ctx.arrivals.arrive(node, "chip", `offer:${offer.offer}`);   // after its lines
    row.glow.update(true);   // after the arrival has held the row: the glow comes when it shows
    return row;
  }
}
