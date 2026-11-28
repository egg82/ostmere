// The town's people (docs/design/opening-screen/town-and-book.md, "The Town view"): first in the Town tab, once a person has joined,
// one row per person who runs their own split (the marked) and one per group with a member (a group of one draws as its
// member, and the row's key is the group's, so a second member joining changes the row's name and adds the count, nothing else):
// their face and who, their time split into the cards that hold a share (each with its
// share) and the idle remainder (while a one-off holds their lane, that card alone with its time left and "then {split}",
// as the hands strip draws a tap), under it the split that runs now while a card of theirs is stopped (runningnow.ts),
// and the card they are working now with its bar, sampled as the card panel samples it. A person whose held cards are all
// stopped reads "nothing to do" with what each is stopped on and the tasks they could run now (stucknote.ts).
// Each person's Change opens their page (personpage.ts), where their split is set. A lane that has joined has no row of its own any more (lanerows.ts);
// the strip comes through the arrival queue once, then stays. It takes its numbers from the view and adds none.
import type { View } from "../../api/types";
import { laneOneOff } from "../../game/hands/holder";
import { groups, marked, members, personOf, soloOf, townJoin } from "../../game/town/town";
import { UI } from "../../game/page/text";
import { face } from "../asks/asknode";
import { el, keyed, setText, tapFeedback } from "../dom";
import type { Part, PartContext } from "../part";
import { dotChange } from "./personpage";
import { drawBar, drawWho, personRow, type PersonRow as Row } from "./personrow";
import { RunningNow } from "../mixes/runningnow";
import { StuckNote } from "./stucknote";
import { wastedOn } from "../../game/cards/wasted";
import { splitOf, splitParts, thenSplit } from "./townsplit";

/** How many members' faces a group's row stacks. */
const FACES = 2;

/** `held`: while a tap holds the lane, its key item, which tick words with the time left. */
interface PersonRow extends Row { split: HTMLElement; now: RunningNow; stuck: StuckNote; change: HTMLElement; held: { item: HTMLElement; card: string; endsAt: number | null } | null }

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
    const present = [...marked(catalog, view), ...groups(catalog, view)];
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
      drawBar(row, view, this.runningOf(view, lane), t);
      if (row.held) setText(row.held.item, this.heldWords(row.held.card, row.held.endsAt, t));
    }
  }

  /** The card the row is on: for a group of one its member's tap first, else the card the person's or group's split is running. */
  private runningOf(view: View, lane: string): string | null {
    const { catalog } = this.ctx;
    const solo = soloOf(catalog, view, lane);
    return (solo !== null && solo !== lane ? view.lanes.find((l) => l.lane === solo)?.running_card : null) ?? personOf(catalog, view, lane).running;
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
    const stuck = new StuckNote(this.ctx, (card) => this.join(card), () => this.openPage(lane));
    row.node.insertBefore(stuck.root, row.track);
    const change = el("button", "hands-edit lane-change person-change", this.ctx.catalog.text.get(UI.laneChange));
    change.type = "button";
    change.dataset.teach = "town-change";   // a lesson's mark of the way into the town's mix
    change.addEventListener("click", () => { tapFeedback(); this.openPage(lane); });
    row.node.insertBefore(change, row.track);
    return { ...row, split, now, stuck, change, held: null };
  }

  /** A task offered a person with nothing to do: it joins their time, as a tap on its face on their page does. */
  private join(card: string): void {
    const view = this.view;
    if (!view) return;
    for (const d of townJoin(this.ctx.catalog, view, this.ctx.catalog.townTitle(view), card)) this.ctx.actions.decide(d);
  }

  /** Under the split, while the card the row works runs on a share into full stores: that its work is wasted. */
  private wastedLine(row: PersonRow, view: View, lane: string): HTMLElement[] {
    const { catalog } = this.ctx;
    const on = view.cards.find((c) => c.card === this.runningOf(view, lane));
    const store = on ? wastedOn(catalog, view, on) : null;
    row.doing.classList.toggle("wasted", store !== null);
    return on && store !== null ? [el("p", "stuck-line wasted-line", catalog.text.fill(UI.townWasted, { card: catalog.cardLabel(on.card), store: catalog.storeLabel(store) }))] : [];
  }

  /** A group of more than one: its own label, a stack of its first members' faces and the head count. */
  private drawCrowd(row: PersonRow, view: View, group: string): void {
    const { catalog } = this.ctx;
    const all = members(catalog, view, group);
    setText(row.name, catalog.laneLabel(group, view));
    row.faceSlot.replaceChildren(...all.slice(0, FACES).map((m) => face(this.ctx, m, catalog.laneLabel(m, view))));
    setText(row.count, catalog.text.fill(UI.townCount, { n: String(all.length) }));
  }

  private draw(lane: string, view: View): void {
    const { catalog } = this.ctx;
    const row = this.rows.get(lane);
    if (!row) return;
    const solo = soloOf(catalog, view, lane);
    const role = solo === null ? null : catalog.castTitle(solo, view);
    const own = solo === null ? undefined : catalog.lanes.get(solo)?.name_key;
    const named = role !== null && own ? catalog.text.get(own) : "";
    drawWho(this.ctx, row, solo ?? lane, role !== null && named ? role : catalog.laneLabel(solo ?? lane, view), this.runningOf(view, lane), role !== null ? named : "");
    row.faceSlot.classList.toggle("stack", solo === null);
    if (solo === null) this.drawCrowd(row, view, lane);
    const tap = solo === null ? null : laneOneOff(view, solo);
    const { bar, key } = splitOf(tap ? [{ text: "", bp: catalog.content.scales.bp, hue: catalog.rank(tap.card) % 6, idle: false }] : splitParts(this.ctx, view, lane, solo ?? lane));
    row.held = tap && { item: key.firstElementChild as HTMLElement, card: tap.card, endsAt: tap.endsAt };
    if (tap) key.append(el("span", "town-key-then", thenSplit(this.ctx, view, lane, solo ?? lane)));
    row.split.replaceChildren(bar, key, ...this.wastedLine(row, view, lane));
    row.now.update(view);
    const stuck = solo !== null && row.stuck.update(view, solo);
    row.node.classList.toggle("stuck", stuck);
    row.doing.classList.toggle("stuck", stuck);
    if (stuck) setText(row.doing, catalog.text.get(UI.townStuck));
    dotChange(this.ctx, view, lane, row.change);
  }
}
