// The town's people (docs/design/opening-screen.md, "The Town view"): first in the Town tab, once a person has joined,
// one row per person present: their face and who, their time split into the cards that hold a share (each with its
// share) and the idle remainder (while a one-off holds their lane, that card alone with its time left and "then {split}",
// as the hands strip draws a tap), under it the split that runs now while a card of theirs is stopped (runningnow.ts),
// and the card they are working now with its bar, sampled as the card panel samples it.
// Each person's Change opens their page (personpage.ts), where their split is set. A lane that has joined has no row of its own any more (lanerows.ts);
// the strip comes through the arrival queue once, then stays. It takes its numbers from the view and adds none.
import type { View } from "../api/types";
import { laneOneOff } from "../game/holder";
import { people, personOf } from "../game/town";
import { UI } from "../game/text";
import { el, keyed, setText, tapFeedback } from "./dom";
import type { Part, PartContext } from "./part";
import { dotChange } from "./personpage";
import { drawBar, drawWho, personRow, type PersonRow as Row } from "./personrow";
import { RunningNow } from "./runningnow";
import { splitOf, splitParts, thenSplit } from "./townsplit";

/** `held`: while a tap holds the lane, its key item, which tick words with the time left. */
interface PersonRow extends Row { split: HTMLElement; now: RunningNow; change: HTMLElement; held: { item: HTMLElement; card: string; endsAt: number | null } | null }

export class TownStrip implements Part {
  readonly root = el("section", "hands town");
  private readonly list = el("div", "town-people");
  private rows = new Map<string, PersonRow>();
  private view: View | null = null;
  private arrived = false;

  constructor(private readonly ctx: PartContext, private readonly openPage: (lane: string) => void) {
    const body = el("div", "hands-body");
    body.append(this.list);
    this.root.append(body);
    this.root.hidden = true;
  }

  update(view: View): void {
    this.view = view;
    const { catalog } = this.ctx;
    const present = people(catalog, view);
    if (present.length === 0) return;
    if (!this.arrived) {
      this.arrived = true;
      this.root.hidden = false;
      this.ctx.arrivals.arrive(this.root, "feature", "town");
    }
    this.rows = keyed(this.list, present, (lane) => lane, this.rows, (lane) => this.make(lane));
    for (const lane of present) this.draw(lane, view);
    this.tick(view.at);
  }

  tick(t: number): void {
    const view = this.view;
    if (!view) return;
    for (const [lane, row] of this.rows) {
      drawBar(row, view, personOf(this.ctx.catalog, view, lane).running, t);
      if (row.held) setText(row.held.item, this.heldWords(row.held.card, row.held.endsAt, t));
    }
  }

  /** A holding tap's key: its card, and its time left while it has an end. */
  private heldWords(card: string, endsAt: number | null, t: number): string {
    const { catalog } = this.ctx;
    return endsAt === null ? catalog.cardLabel(card) : `${catalog.cardLabel(card)} ${catalog.format.duration(endsAt - t)}`;
  }

  private make(lane: string): PersonRow {
    const row = personRow("town-person", lane);
    const split = el("div", "town-split-of");
    const now = new RunningNow(this.ctx, lane);
    row.node.insertBefore(split, row.track);
    row.node.insertBefore(now.root, row.track);
    const change = el("button", "hands-edit lane-change person-change", this.ctx.catalog.text.get(UI.laneChange));
    change.type = "button";
    change.dataset.teach = "town-change";   // a lesson's mark of the way into the town's mix
    change.addEventListener("click", () => { tapFeedback(); this.openPage(lane); });
    row.node.insertBefore(change, row.track);
    return { ...row, split, now, change, held: null };
  }

  private draw(lane: string, view: View): void {
    const { catalog } = this.ctx;
    const row = this.rows.get(lane);
    if (!row) return;
    const person = personOf(catalog, view, lane);
    const label = catalog.laneLabel(lane, view);
    drawWho(this.ctx, row, lane, label, person.running);
    const tap = laneOneOff(view, lane);
    const { bar, key } = splitOf(tap ? [{ text: "", bp: catalog.content.scales.bp, hue: catalog.rank(tap.card) % 6, idle: false }] : splitParts(this.ctx, view, lane));
    row.held = tap && { item: key.firstElementChild as HTMLElement, card: tap.card, endsAt: tap.endsAt };
    if (tap) key.append(el("span", "town-key-then", thenSplit(this.ctx, view, lane)));
    row.split.replaceChildren(bar, key);
    row.now.update(view);
    dotChange(this.ctx, view, lane, row.change);
  }
}
