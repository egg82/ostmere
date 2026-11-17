// A person's page (docs/design/opening-screen.md, "The Town view"): opened by Change on their Town row, laid out as the
// Tasks page is: once they have joined the town their split as a share bar (personmix.ts), then every task of theirs
// in full, as the Tasks panel draws a card (cardpick.ts), then the rules that run them (rulelanes.ts), each a button
// into the Rules tab. A tap on a task joins it to their time or takes it out; a capped task, which the town's mix never
// holds (CONTRACT.txt, "The town's mix"), adds or takes out the always rule that has them do it. It takes the card area's place while open; its
// one root is what a tab would seat later. Opening it is what clears the quiet dot on the person's row.
import type { Card, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import { oneOffRule, ruledLaneOf, toggleOneOff } from "../game/lanes";
import { rulesFull, taskRules } from "../game/orders";
import { UI } from "../game/text";
import { people } from "../game/town";
import { pickRow } from "./cardpick";
import { sectionHead } from "./condrows";
import { el, revealBelow, setText, tapFeedback } from "./dom";
import { markNew, unmark } from "./fresh";
import type { PartContext, RuleTarget } from "./part";
import { PersonMix } from "./personmix";
import { condButton } from "./rulecond";
import { taskRow } from "./rulelanes";

/** A person's tasks: their cards in the view. */
export function laneTasks(ctx: PartContext, view: View, lane: string): Card[] {
  return view.cards.filter((c) => ctx.catalog.laneOf(c.card) === lane);
}

/** A task of `lane` has not been in front of the player: the lane's Change wears a quiet dot, and so does the Town tab. */
export function hasNewTask(ctx: PartContext, view: View, lane: string): boolean {
  return laneTasks(ctx, view, lane).some((c) => !ctx.keeps.laneTaskSeen(c.card));
}

/** The quiet dot on a person's Change while a task of theirs has not been in front of the player; opening their page keeps them. */
export function dotChange(ctx: PartContext, view: View, lane: string, change: HTMLElement): void {
  if (hasNewTask(ctx, view, lane)) markNew(change, () => ctx.keeps.keepLaneTasksSeen(laneTasks(ctx, view, lane).map((c) => c.card)));
  else unmark(change);
}

export class PersonPage {
  readonly root = el("section", "editor person-page");
  private readonly heading = el("span", "town-title");
  private readonly cards = el("div", "person-cards");
  private readonly rules = el("div", "person-rules");
  private readonly mix: PersonMix;
  private view: View | null = null;
  private lane = "";
  /** The tasks whose upside line has its strength sheet open: a redraw keeps them open. */
  private readonly strengthOpen = new Set<string>();

  constructor(private readonly ctx: PartContext, private readonly closed: () => void) {
    this.root.hidden = true;
    this.mix = new PersonMix(ctx);
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", ctx.catalog.text.get(UI.close));
    close.addEventListener("click", () => this.close());
    const head = el("div", "editor-head");
    head.append(this.heading, close);
    this.root.append(head, this.mix.root, this.cards, this.rules);
  }

  get open(): boolean {
    return !this.root.hidden;
  }

  /** Opens on `lane`'s person; their tasks are now in front of the player. */
  show(view: View, lane: string): void {
    this.lane = lane;
    this.view = view;
    this.root.hidden = false;
    this.ctx.keeps.keepLaneTasksSeen(laneTasks(this.ctx, view, lane).map((c) => c.card));
    this.draw();
  }

  /** Once shown: the page's top is in view, clear of a phone's pinned strip, whatever the Town tab was scrolled to. */
  reveal(): void {
    const pinned = document.querySelector<HTMLElement>(".panel-top");
    if (pinned) revealBelow(this.root, pinned, [".game", ".panel"].flatMap((s) => document.querySelector<HTMLElement>(s) ?? []));
  }

  close(): void {
    if (!this.open) return;
    this.root.hidden = true;
    this.closed();
  }

  /** A new view while open: the split, the cards and the rules follow it. */
  update(view: View): void {
    this.view = view;
    if (!this.open) return;
    this.draw();
  }

  private joined(view: View): boolean {
    return people(this.ctx.catalog, view).includes(this.lane);
  }

  /** A task's face: with the person in the town, a tap (see the top); the share it holds is on the face. */
  private face(card: Card, view: View, joined: boolean, share: number | undefined): HTMLElement {
    const { catalog, actions } = this.ctx;
    if (!joined) return pickRow(this.ctx, card, view, undefined, this.strengthOpen);
    const capped = card.cap !== null;
    const tap = capped ? () => actions.decide(toggleOneOff(catalog, view, this.lane, card.card)) : () => this.mix.toggle(card.card);
    const face = pickRow(this.ctx, card, view, tap, this.strengthOpen);
    if (capped) {
      face.querySelector(".card-tap")?.setAttribute("aria-pressed", String(oneOffRule(catalog, view, this.lane, card.card) >= 0));
      face.querySelector(".card-tap")?.append(el("span", "card-need oneoff", catalog.text.get(UI.personOneOff)));
      return face;
    }
    face.querySelector(".card-tap")?.setAttribute("aria-pressed", String(share !== undefined));
    if (share !== undefined) face.querySelector(".card-head")?.append(el("span", "card-share", catalog.format.share(share)));
    return face;
  }

  private draw(): void {
    const { view, lane } = this;
    if (!view) return;
    const { catalog, actions } = this.ctx;
    const label = catalog.laneLabel(lane, view);
    setText(this.heading, label);
    const joined = this.joined(view);
    this.mix.root.hidden = !joined;
    if (joined) this.mix.show(view, lane);
    const held = joined ? this.mix.shares() : new Map<string, number>();
    this.cards.replaceChildren(...sectioned(catalog, laneTasks(this.ctx, view, lane), (c) => c.card, view).flatMap((g) => {
      const list = el("div", "card-list");
      list.append(...g.items.map((c) => this.face(c, view, joined, held.get(c.card))));
      return [...sectionHead(g.heading === label ? "" : g.heading), list];
    }));
    const own = taskRules(view).filter((i) => ruledLaneOf(catalog, view.orders[i]!) === lane);
    const opens = { lane: (l: string, rule: number) => actions.openRules({ lane: l, rule }), edit: (rule: number) => actions.openRules(rule) };
    this.rules.replaceChildren(...own.map((i) => taskRow(this.ctx, view, i, (rule) => condButton(this.ctx, view, rule, opens))));
    const add = (label: string, target: RuleTarget): void => {
      const b = el("button", "quiet", label);
      b.type = "button";
      b.addEventListener("click", () => { tapFeedback(); actions.openRules(target); });
      this.rules.append(b);
    };
    if (own.length === 0) add(catalog.text.get(UI.laneChange), { lane, rule: null });
    if (!rulesFull(catalog, view)) add(`+ ${catalog.text.get(UI.ruleNew)}`, { newFor: lane });
  }
}
