// A person's page (docs/design/opening-screen.md, "The Town view"): opened by Change on their Town row, laid out as the
// Tasks page is: their cards in full, as the Tasks panel draws a card (cardpick.ts), then their mix and the mix editor
// (townedit.ts, scoped to them) once they have joined the town, then the rules that run them (rulelanes.ts), each a
// button into the Rules tab. It takes the card area's place while open, as the town editor does; its one root is what
// a tab would seat later. Opening it is what clears the quiet dot on the person's row.
import type { Card, View } from "../api/types";
import { sectioned } from "../game/cardsections";
import { ruledLaneOf } from "../game/lanes";
import { taskRules } from "../game/orders";
import { UI } from "../game/text";
import { people } from "../game/town";
import { pickRow } from "./cardpick";
import { sectionHead } from "./condrows";
import { el, revealBelow, setText, tapFeedback } from "./dom";
import { markNew, unmark } from "./fresh";
import type { PartContext } from "./part";
import { condButton } from "./rulecond";
import { taskRow } from "./rulelanes";
import { TownEditor } from "./townedit";

/** A person's tasks: their cards in the view. */
export function laneTasks(ctx: PartContext, view: View, lane: string): Card[] {
  return view.cards.filter((c) => ctx.catalog.laneOf(c.card) === lane);
}

/** The quiet dot on a person's Change while a task of theirs has not been in front of the player; opening their page keeps them. */
export function dotChange(ctx: PartContext, view: View, lane: string, change: HTMLElement): void {
  const tasks = laneTasks(ctx, view, lane).map((c) => c.card);
  if (tasks.some((c) => !ctx.keeps.laneTaskSeen(c))) markNew(change, () => ctx.keeps.keepLaneTasksSeen(tasks));
  else unmark(change);
}

export class PersonPage {
  readonly root = el("section", "editor person-page");
  private readonly heading = el("span", "town-title");
  private readonly cards = el("div", "person-cards");
  private readonly rules = el("div", "person-rules");
  private readonly mix: TownEditor;
  private view: View | null = null;
  private lane = "";

  constructor(private readonly ctx: PartContext, private readonly closed: () => void) {
    this.root.hidden = true;
    this.mix = new TownEditor(ctx, () => this.close(), true);
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", ctx.catalog.text.get(UI.close));
    close.addEventListener("click", () => this.close());
    const head = el("div", "editor-head");
    head.append(this.heading, close);
    this.root.append(head, this.cards, this.mix.root, this.rules);
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
    if (this.joined(view)) this.mix.show(view, lane);
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
    this.mix.root.hidden = true;
    this.closed();
  }

  /** A new view while open: the cards and rules follow it; a mix being edited keeps its edit. */
  update(view: View): void {
    this.view = view;
    if (!this.open) return;
    if (this.joined(view)) this.mix.update(view);
    this.draw();
  }

  private joined(view: View): boolean {
    return people(this.ctx.catalog, view).includes(this.lane);
  }

  private draw(): void {
    const { view, lane } = this;
    if (!view) return;
    const { catalog, actions } = this.ctx;
    const label = catalog.laneLabel(lane, view);
    setText(this.heading, label);
    this.cards.replaceChildren(...sectioned(catalog, laneTasks(this.ctx, view, lane), (c) => c.card, view).flatMap((g) => {
      const list = el("div", "card-list");
      list.append(...g.items.map((c) => pickRow(this.ctx, c, view)));
      return [...sectionHead(g.heading === label ? "" : g.heading), list];
    }));
    const own = taskRules(view).filter((i) => ruledLaneOf(catalog, view.orders[i]!) === lane);
    const opens = { lane: (l: string, rule: number) => actions.openRules({ lane: l, rule }), edit: (rule: number) => actions.openRules(rule) };
    this.rules.replaceChildren(...own.map((i) => taskRow(this.ctx, view, i, (rule) => condButton(this.ctx, view, rule, opens))));
    if (own.length === 0) {
      const add = el("button", "quiet", catalog.text.get(UI.laneChange));
      add.type = "button";
      add.addEventListener("click", () => { tapFeedback(); actions.openRules({ lane, rule: null }); });
      this.rules.append(add);
    }
  }
}
