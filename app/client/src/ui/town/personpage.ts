// A person's page, or a group's (docs/design/opening-screen/town-and-book.md, "The Town view"): opened by Change on their Town row, laid out as the
// Tasks page is: once they have joined the town their split as a share bar (personmix.ts), then every task of theirs
// in full, as the Tasks panel draws a card (cardpick.ts), its bar and countdown moving with the clock, then the rules
// that run them (rulelanes.ts), each a button into the Rules tab. A tap on a task joins it to their time or takes it
// out; a capped task, which the town's mix never holds (contract/the-towns-mix.txt, "The town's mix"), is tapped for its next
// completion, as a hands one-off is, and their split comes back once it lands. It takes the card area's place while open; its
// one root is what a tab would seat later. Opening it is what clears the quiet dot on the person's row.
// A group's page is this page for a pooled lane's id: the group's split as the one bar with the crew under it, its tasks as
// faces, its members (groupmembers.ts) in place of rules (no rule names a pooled lane); a group of one is titled with the
// member's name. While every card holding their time is stopped, the note under the split says so
// and offers the tasks they could run now (stucknote.ts).
// A station's page (the pot on the fire, LaneInfo.station) is a lane's that never joins: a tap on a task makes it the lane's
// one task, its always rule changed in place (game/lanes.ts, laneTask), and the task it runs is drawn pressed.
import type { Card, View } from "../../api/types";
import { sectioned } from "../../game/cardsections";
import { laneTap } from "../../game/holder";
import { isAlways, laneTask, ruledLaneOf } from "../../game/lanes";
import { rulesFull, taskRules } from "../../game/orders";
import { UI } from "../../game/text";
import { members, people, soloOf } from "../../game/town";
import { pickFace, tickFace } from "../cards/cardpick";
import type { Row } from "../cards/cardrow";
import { sectionHead } from "../condition/condrows";
import { GroupMembers } from "./groupmembers";
import { el, revealBelow, setText, tapFeedback } from "../dom";
import { markNew, unmark } from "../feedback/fresh";
import type { PartContext, RuleTarget } from "../part";
import { PersonMix } from "./personmix";
import { StuckNote } from "./stucknote";
import { condButton } from "../rules/rulecond";
import { taskRow } from "../rules/rulelanes";
import { laneRulable } from "../rules/rulewho";
import { WhenReady } from "../cards/whenready";

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
  private readonly members: GroupMembers;
  private readonly stuck: StuckNote;
  private view: View | null = null;
  private lane = "";
  /** The faces drawn, which tick moves on. */
  private faces: Row[] = [];
  /** The tasks whose upside line has its strength sheet open: a redraw keeps them open. */
  private readonly strengthOpen = new Set<string>();
  /** A one-off the player tapped: Until done beside its tap (game/untildone.ts). */
  private readonly untilDone: WhenReady;

  constructor(private readonly ctx: PartContext, private readonly closed: () => void) {
    this.root.hidden = true;
    this.mix = new PersonMix(ctx);
    this.members = new GroupMembers(ctx);
    this.untilDone = new WhenReady(ctx);
    this.stuck = new StuckNote(ctx, (card) => this.mix.toggle(card), () => this.cards.scrollIntoView?.({ block: "start", behavior: "smooth" }));
    const close = el("button", "editor-close", "✕");
    close.type = "button";
    close.setAttribute("aria-label", ctx.catalog.text.get(UI.close));
    close.addEventListener("click", () => this.close());
    const head = el("div", "editor-head");
    head.append(this.heading, close);
    this.root.append(head, this.mix.root, this.stuck.root, this.members.root, this.cards, this.rules);
  }

  get open(): boolean {
    return !this.root.hidden;
  }

  /** The lane whose page is open, or null. */
  get shown(): string | null {
    return this.open ? this.lane : null;
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

  /** The clock moved: each face's bar and countdown, and a holding tap's time left on the split. */
  tick(t: number): void {
    if (!this.open || !this.view) return;
    for (const row of this.faces) tickFace(this.ctx, row, this.view, t);
    this.mix.tick(t);
    this.members.tick(t);
  }

  private pooled(): boolean {
    return this.ctx.catalog.lanes.get(this.lane)?.pooled === true;
  }

  /** The person is in the town; a group, with a member in it. */
  private joined(view: View): boolean {
    const { catalog } = this.ctx;
    return this.pooled() ? members(catalog, view, this.lane).length > 0 : people(catalog, view).includes(this.lane);
  }

  /** A task's face: with the person in the town, a tap (see the top); the share it holds is on the face. */
  private face(card: Card, view: View, joined: boolean, share: number | undefined): HTMLElement {
    const { catalog, actions } = this.ctx;
    if (!joined && catalog.lanes.get(this.lane)?.station === true) return this.station(card, view);
    if (!joined) return this.kept(pickFace(this.ctx, card, view, undefined, this.strengthOpen)).node;
    const capped = card.cap !== null;
    const tap = capped ? () => actions.decide({ kind: "tap_card", card: card.card }) : () => this.mix.toggle(card.card);
    const row = this.kept(pickFace(this.ctx, card, view, tap, this.strengthOpen));
    const face = row.node;
    if (capped) {
      const held = laneTap(view, this.lane);
      face.classList.toggle("running", held?.card === card.card);
      row.tap.disabled = held !== null;   // as the card panel's: one tap at a time on the lane
      row.tap.setAttribute("aria-pressed", String(held?.card === card.card));
      const until = this.untilDone.make(card.card, face);
      face.append(until);
      this.untilDone.sync(until, card, view);
      return face;
    }
    row.tap.setAttribute("aria-pressed", String(share !== undefined));
    if (share !== undefined) face.querySelector(".card-head")?.append(el("span", "card-share", catalog.format.share(share)));
    return face;
  }

  /** A station's task: tapped, it becomes the lane's one task. */
  private station(card: Card, view: View): HTMLElement {
    const { catalog, actions } = this.ctx;
    const always = view.orders.findIndex((o) => isAlways(o) && ruledLaneOf(catalog, o) === this.lane);
    const row = this.kept(pickFace(this.ctx, card, view, () => actions.decide(laneTask(view, always < 0 ? null : always, card.card)), this.strengthOpen));
    const on = always >= 0 && view.orders[always]?.then.kind === "tap_card" && view.orders[always]?.then.card === card.card;
    row.node.classList.toggle("running", on);
    row.tap.setAttribute("aria-pressed", String(on));
    return row.node;
  }

  private kept(row: Row): Row {
    this.faces.push(row);
    if (this.view) tickFace(this.ctx, row, this.view, this.view.at);
    return row;
  }

  private draw(): void {
    const { view, lane } = this;
    if (!view) return;
    this.faces = [];
    const { catalog, actions } = this.ctx;
    const label = catalog.laneLabel(soloOf(catalog, view, lane) ?? lane, view);
    setText(this.heading, label);
    const joined = this.joined(view);
    this.members.root.hidden = !this.pooled();
    if (this.pooled()) this.members.update(view, lane);
    this.mix.root.hidden = !joined;
    if (joined) this.mix.show(view, lane);
    const solo = soloOf(catalog, view, lane);
    if (!(joined && solo !== null && this.stuck.update(view, solo))) this.stuck.root.hidden = true;
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
    if (own.length === 0 && !this.joined(view) && !this.pooled()) add(catalog.text.get(UI.laneChange), { lane, rule: null });
    if (!this.pooled() && !rulesFull(catalog, view) && laneRulable(catalog, view, lane)) add(`+ ${catalog.text.get(UI.ruleNew)}`, { newFor: lane });
  }
}
