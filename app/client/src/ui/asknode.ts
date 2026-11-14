// One ask, as the Asks list draws it (ui/asks.ts; CONTRACT.txt, "OFFERS"; docs/design/redesign.md, "Asks"): who
// asks, by face and name; the question; "↳" what led to it; one button per answer with its label, its cost text and
// each figure it moves, before → after (game/asks.ts); then the texts the offer has where it differs from the usual
// (waiting, expiry, permanence). Anything the content leaves out is not drawn. A tap sends answer_offer.
import type { Offer, OfferInfo, View } from "../api/types";
import { askCause, askedBy } from "../game/asks";
import { el, setText, tapFeedback } from "./dom";
import type { PartContext } from "./part";

export interface AskNode {
  readonly node: HTMLElement;
  /** Draw what changes while the ask waits: who asks (a label that moves on), each answer's cost from the view, and
   * the figures each answer moves (undefined while its dry run has not answered). */
  refresh(view: View, figures: ReadonlyMap<string, string[]>): void;
}

/** A person's face: the first letter of the name, in the lane's hue (an ask's, and the Town view's rows). */
export function face(ctx: PartContext, lane: string, name: string): HTMLElement {
  const hue = ctx.catalog.content.lane_infos.findIndex((l) => l.lane === lane);
  const node = el("span", `ask-face hue-${Math.max(hue, 0) % 6}`, name.charAt(0).toUpperCase());
  node.setAttribute("aria-hidden", "true");
  return node;
}

export function askNode(ctx: PartContext, offer: string): AskNode {
  const { catalog } = ctx;
  const info = catalog.offers.get(offer);
  const node = el("div", "ask");
  node.dataset.offer = offer;
  const who = el("p", "ask-who");
  const cause = el("p", "ask-cause");
  const answers = el("div", "ask-answers");
  const costs = new Map<string, { cost: HTMLElement; figures: HTMLElement }>();
  for (const a of info?.answers ?? []) {
    const b = el("button", "ask-answer");
    b.type = "button";
    b.dataset.answer = a.answer;
    const cost = el("span", "ask-cost");
    const figures = el("span", "ask-figures");
    costs.set(a.answer, { cost, figures });
    b.append(el("span", "ask-label", catalog.label(a.label_key)), cost, figures);
    b.addEventListener("click", () => { tapFeedback(); ctx.actions.decide({ kind: "answer_offer", offer, answer: a.answer }); });
    answers.append(b);
  }
  const facts = el("p", "ask-facts");
  for (const key of [info?.waiting_key, info?.expiry_key, info?.permanence_key]) if (key) facts.append(el("span", "ask-fact", catalog.label(key)));
  facts.hidden = facts.childElementCount === 0;
  node.append(who, el("p", "ask-text", catalog.label(info?.text_key)), cause, answers, facts);
  const refresh = (view: View, figures: ReadonlyMap<string, string[]>): void => {
    if (info) drawWho(ctx, who, view, info);
    const led = info ? askCause(catalog, view, info) : null;
    setText(cause, led ?? "");
    cause.hidden = led === null;
    const shown = view.offers.find((o) => o.offer === offer);
    for (const [answer, row] of costs) {
      setText(row.cost, shown ? costText(ctx, info, shown, answer) : "");
      row.cost.hidden = row.cost.textContent === "";
      const moved = figures.get(answer) ?? [];
      row.figures.replaceChildren(...moved.map((f) => el("span", "ask-figure", f)));
      row.figures.hidden = moved.length === 0;
    }
  };
  return { node, refresh };
}

function drawWho(ctx: PartContext, who: HTMLElement, view: View, info: OfferInfo): void {
  const names = askedBy(ctx.catalog, view, info);
  who.hidden = names === "";
  if (who.dataset.names === names) return;
  who.dataset.names = names;
  const faces = info.askers.map((lane) => face(ctx, lane, askedBy(ctx.catalog, view, { ...info, askers: [lane] })));
  who.replaceChildren(...faces, el("span", "ask-names", names));
}

/** An answer's cost text: {d} from takes_s (the text left out while that is null), {pct} from change_bp, {gain} from
 * gains (CONTRACT.txt, "OFFERS"). */
function costText(ctx: PartContext, info: OfferInfo | undefined, shown: Offer, answer: string): string {
  const { catalog } = ctx;
  const served = info?.answers.find((i) => i.answer === answer);
  const takes = shown.answers.find((a) => a.answer === answer)?.takes_s ?? null;
  if (!served || (takes === null && catalog.text.get(served.cost_key).includes("{d}"))) return "";
  return catalog.text.fill(served.cost_key, {
    d: takes === null ? "" : catalog.format.duration(takes), ...catalog.format.figures(served.change_bp), ...catalog.format.gains(served.gains),
  });
}
