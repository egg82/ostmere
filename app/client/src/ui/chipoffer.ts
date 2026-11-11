// The hands strip's first-rule lesson entry (docs/design/opening-screen.md, the hands strip, "rule offer (after the end)"):
// while the rule's lesson may start, a chip's order card shows its rule in the player's words ("While tired → Rest") with
// Show me, which opens a new rule on the real editor where the lesson walks it. Nothing is ever built from the row: once
// the lesson is done or skipped no row is drawn and the chip carries a quiet mark instead (ui/story.ts, game/cues.ts
// hintedChips). Only the first card can be the lesson's subject: one at a time, never a twin. It is drawn the first time
// its chip is on with no rule answering it, and stays until such a rule is set (not when the chip clears), so the strip
// moves once, on its arrival.
import type { OrderCard, View } from "../api/types";
import { chipCardOpen, chipCards } from "../game/cues";
import { guidedRule, ruleSubject, ruleWaits } from "../game/lessons";
import { ruleWords } from "../game/orders";
import { UI } from "../game/text";
import { noteOrderShown } from "../telemetry";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

export class ChipOffer {
  readonly root = el("div", "hands-offer hands-rule-offer");
  private card: OrderCard | null = null;

  constructor(private readonly ctx: PartContext) {
    this.root.hidden = true;
  }

  update(view: View): void {
    const behind = this.ctx.endBehind();
    const waits = (c: OrderCard): boolean => ruleWaits(c, this.ctx.lesson(), this.ctx.lessonSubject());   // it waits out another lesson
    const shown = this.card;
    if (shown && (!chipCardOpen(view, shown, behind) || !guidedRule(view, this.ctx.keeps, shown) || waits(shown))) this.drop();
    if (this.card) return;
    const head = chipCards(this.ctx.catalog, view, behind)[0];
    if (head && guidedRule(view, this.ctx.keeps, head) && !waits(head)) this.draw(head);
  }

  private draw(card: OrderCard): void {
    const { catalog } = this.ctx;
    const words = ruleWords(catalog, { when: card.when, then: card.then });
    if (!words) return;
    const sentence = el("p", "rule-sentence");
    const hue = card.then.kind === "tap_card" ? catalog.rank(card.then.card) % 6 : 5;
    sentence.append(el("span", "", words.when), " → ", el("b", `rule-action hue-${hue}`, words.action));
    const button = el("button", "offer-both lesson-go", catalog.text.get(UI.lessonShow));
    button.type = "button";
    Object.assign(button.dataset, { teach: "rule-offer" }, ruleSubject(card));
    button.addEventListener("click", () => { tapFeedback(); this.ctx.actions.openRules("new", card.when); });   // the rule's lesson: built on the editor
    const node = el("span", "rule-pick");
    node.append(sentence, button);
    this.root.replaceChildren(node);
    this.root.hidden = false;
    this.card = card;
    noteOrderShown(card.store);
    this.ctx.arrivals.arrive(this.root, "chip", card.chip ?? card.store);
  }

  private drop(): void {
    this.root.replaceChildren();
    this.root.hidden = true;
    this.card = null;
  }
}
