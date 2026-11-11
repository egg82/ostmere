// A card's needs (docs/design/opening-screen.md, "Cards"): one line per store need as have/need, then each skill-level
// need, then each step it waits on. Needs read in the card's quiet tone; a short one marks only the number it is short
// of while it holds the card back (red is the ledger's alarm, not a need). A store need with a gate (Need.gate: what
// the trigger that grants the store waits on) draws the gate in its place, as a skill-level or step row, and never names
// the store; a tap of a short store need's row lights its makers (Need.makers, ui/makerlight.ts) and does not tap the
// card. A spent one (Need.spent: nothing in play makes it and nothing is left to grant it) says so on its row.
// A need on a store the player has never been shown (a clock) draws no row, unless it has a gate: the card's countdown
// is all of it. A skill
// level or a step once met stays met (levels and completions never fall), so its row goes; a store can fall, so its row stays.
// While the card works (Card.run full or held) its needs are not drawn: its inputs are drawn as it runs, so the store
// reads short of a whole input; a run paused for want of one (run paused) draws them.
// Rebuilt only when what is needed changes; store needs are sampled every frame. A failed tap marks the row that shows
// what its blocker names (shows()).
import type { Card, Condition, Need, View } from "../api/types";
import { sample } from "../game/clock";
import { completionsOf } from "../game/cues";
import { shownLevel } from "../game/prestige";
import { el } from "./dom";
import { lightMakers } from "./makerlight";
import type { PartContext } from "./part";

const MARK = "\u0001";   // where the have number goes in a need's words

/** A need's words with its have number put in; marked while the need is short. Rebuilt only when either changes. */
function drawNeed(node: HTMLElement, words: string, have: string, short: boolean): void {
  const [pre = "", post = ""] = words.split(MARK);
  node.classList.toggle("short", short);
  if (node.textContent === pre + have + post && (node.querySelector(".need-have") !== null) === short) return;
  node.replaceChildren(...(short ? [pre, el("b", "need-have", have), post] : [pre + have + post]).filter((k) => k !== ""));
}

/** Whether the card is drawing its inputs as it works (full): a paused run, waiting or yielded one is not. */
function working(card: Card): boolean {
  return card.run === "full";
}

export class CardNeeds {
  readonly root = el("span", "card-needs");
  private storeRows: HTMLElement[] = [];
  private stores: string[] = [];
  private needs: Need[] = [];
  private shape: string | null = null;

  constructor(private readonly ctx: PartContext, private readonly id: string) {}

  /** Rebuilt only when what is needed changes. */
  draw(card: Card, view: View, done: boolean): void {
    const { catalog } = this.ctx;
    const info = catalog.cards.get(this.id);
    const skillNeeds = info?.skill_needs ?? [];
    const stepNeeds = info?.step_needs ?? [];
    const seen = new Set(view.unlocked.filter((u) => u.category === "store").map((u) => u.id));
    this.needs = card.needs;
    const shape = card.needs.map((n) => `${n.store}:${n.quantity}:${seen.has(n.store)}:${JSON.stringify(n.gate)}`).join("|");
    if (shape !== this.shape) {
      this.shape = shape;
      this.stores = card.needs.map((n) => n.store);
      this.storeRows = card.needs.map((n, i) => this.storeRow(n.gate !== null ? "card-need gate" : seen.has(n.store) ? "card-need" : "card-need unseen", i));
      for (const row of this.storeRows) row.hidden = row.classList.contains("unseen");
      const skills = skillNeeds.map(() => el("span", "card-need skill"));
      const steps = stepNeeds.map(() => el("span", "card-need step"));
      this.root.replaceChildren(...this.storeRows, ...skills, ...steps);
    }
    const skillNodes = [...this.root.querySelectorAll<HTMLElement>(".card-need.skill")];
    skillNeeds.forEach((need, i) => {
      const node = skillNodes[i];
      if (!node) return;
      const bar = view.skills.find((s) => s.skill === need.skill);
      const have = bar ? shownLevel(bar) : 1;
      node.hidden = have >= need.level;
      drawNeed(node, catalog.format.needSkill(catalog.skillLabel(need.skill), MARK, need.level), catalog.format.count(have), have < need.level);
    });
    card.needs.forEach((need, i) => { if (need.gate !== null && this.storeRows[i]) this.drawGate(this.storeRows[i], need.gate, view); });
    const stepNodes = [...this.root.querySelectorAll<HTMLElement>(".card-need.step")];
    stepNeeds.forEach((need, i) => {
      const node = stepNodes[i];
      if (!node) return;
      const have = completionsOf(view, need.card);
      node.hidden = have >= need.count;
      drawNeed(node, catalog.format.needStep(catalog.cardLabel(need.card), MARK, need.count), catalog.format.count(have), have < need.count);
    });
    const shown = [...this.storeRows, ...skillNodes, ...stepNodes].filter((row) => !row.hidden).length;
    this.root.hidden = done || shown === 0 || working(card);
  }

  /** The row drawn for what `condition` watches (a blocker's): its store's have/need, its skill level or its step;
   * null when the card draws none (a store never shown, a time, a row already met and hidden). */
  shows(condition: Condition): HTMLElement | null {
    if (condition.kind === "after_time") return null;
    const w = condition.watched;
    const info = this.ctx.catalog.cards.get(this.id);
    const nth = (kind: string, i: number): HTMLElement | undefined =>
      i < 0 ? undefined : [...this.root.querySelectorAll<HTMLElement>(`.card-need.${kind}`)][i];
    const node = w.kind === "store_value" ? this.storeRows[this.stores.indexOf(w.store)]
      : w.kind === "skill_level" ? nth("skill", (info?.skill_needs ?? []).findIndex((n) => n.skill === w.skill))
        : w.kind === "card_count" ? nth("step", (info?.step_needs ?? []).findIndex((n) => n.card === w.card)) : undefined;
    return node && !node.hidden ? node : null;
  }

  /** The store needs at game time t; a gated one is drawn with the view (draw). */
  tick(card: Card, _view: View | null, t: number): void {
    const { catalog } = this.ctx;
    card.needs.forEach((need, i) => {
      const node = this.storeRows[i];
      if (!node || node.classList.contains("unseen") || need.gate !== null) return;
      const have = sample(need.segment, t);
      const short = card.blocker !== null && have < need.quantity;   // red only while it holds the card back
      drawNeed(node, catalog.format.need(catalog.storeTitle(need.store), MARK, need.quantity, need.spent), catalog.format.items(have), short);
    });
  }

  /** The row of the i-th store need: a tap of it while it is short lights that need's makers, not the card. */
  private storeRow(cls: string, i: number): HTMLElement {
    const row = el("span", cls);
    row.addEventListener("click", (e) => {
      const makers = this.needs[i]?.makers ?? [];
      if (!row.classList.contains("short") || makers.length === 0) return;
      e.stopPropagation();
      lightMakers(this.ctx.actions, makers);
    });
    return row;
  }

  /** A gate in a store need's place: the skill level or the card's completions the grant waits on, short while unmet. */
  private drawGate(node: HTMLElement, gate: Condition, view: View): void {
    const { catalog } = this.ctx;
    if (gate.kind === "after_time") return;
    const w = gate.watched;
    if (w.kind === "skill_level") {
      const bar = view.skills.find((s) => s.skill === w.skill);
      const have = bar ? shownLevel(bar) : 1;
      drawNeed(node, catalog.format.needSkill(catalog.skillLabel(w.skill), MARK, gate.value), catalog.format.count(have), have < gate.value);
    } else if (w.kind === "card_count") {
      const have = completionsOf(view, w.card);
      drawNeed(node, catalog.format.needStep(catalog.cardLabel(w.card), MARK, gate.value), catalog.format.count(have), have < gate.value);
    }
  }
}
