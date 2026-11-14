// The town's people (docs/design/opening-screen.md, "The Town view"): first in the Town tab, once a person has joined,
// one row per person present: their face and who, their time split into the cards that hold a share (each with its
// share) and the idle remainder, under it the split that runs now while a card of theirs is stopped (runningnow.ts),
// and the card they are working now with its bar, sampled as the card panel samples it.
// Change opens the town's mix in the town editor. A lane that has joined has no row of its own any more (lanerows.ts);
// the strip comes through the arrival queue once, then stays. It takes its numbers from the view and adds none.
import type { View } from "../api/types";
import { sample } from "../game/clock";
import { people, personOf, townGreyed, townStoppedBy } from "../game/town";
import { UI } from "../game/text";
import { face } from "./asknode";
import { el, keyed, setText, tapFeedback } from "./dom";
import type { Part, PartContext } from "./part";
import { RunningNow } from "./runningnow";
import { splitOf, type Part as Share } from "./townsplit";

interface PersonRow { node: HTMLElement; face: HTMLElement; name: HTMLElement; doing: HTMLElement; split: HTMLElement; fill: HTMLElement; now: RunningNow }

export class TownStrip implements Part {
  readonly root = el("section", "hands town");
  private readonly status = el("span", "hands-text town-status");
  private readonly change = el("button", "hands-edit town-change");
  private readonly list = el("div", "town-people");
  private rows = new Map<string, PersonRow>();
  private view: View | null = null;
  private arrived = false;

  constructor(private readonly ctx: PartContext, edit: () => void) {
    const { text } = ctx.catalog;
    this.change.type = "button";
    this.change.dataset.teach = "town-change";   // a lesson's mark of the way into the town's mix
    setText(this.change, text.get(UI.townChange));
    this.change.addEventListener("click", () => { tapFeedback(); edit(); });
    const head = el("div", "hands-row");
    head.append(this.status, this.change);
    const body = el("div", "hands-body");
    body.append(head, this.list);
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
    const stopped = townStoppedBy(catalog, view);
    this.root.classList.toggle("greyed", townGreyed(catalog, view) !== null);
    setText(this.status, stopped === null ? "" : catalog.text.fill(UI.stopped, { card: catalog.cardLabel(stopped) }));
    this.status.hidden = stopped === null;
    this.rows = keyed(this.list, present, (lane) => lane, this.rows, (lane) => this.make(lane));
    for (const lane of present) this.draw(lane, view);
    this.tick(view.at);
  }

  tick(t: number): void {
    const view = this.view;
    if (!view) return;
    for (const [lane, row] of this.rows) {
      const card = view.cards.find((c) => c.card === personOf(this.ctx.catalog, view, lane).running);
      const span = card?.bar_total ?? 0;
      const v = card ? sample(card.bar, t) : 0;
      row.fill.style.transform = `scaleX(${span > 0 ? (((v % span) + span) % span) / span : 0})`;
    }
  }

  private make(lane: string): PersonRow {
    const node = el("div", "town-person");
    node.dataset.lane = lane;
    const name = el("span", "town-name");
    const doing = el("span", "hands-text town-doing");
    const split = el("div", "town-split-of");
    const track = el("div", "card-track lane-bar");
    const fill = el("span", "card-fill lane-fill");
    track.append(fill);
    const who = el("div", "town-who");
    who.append(name, doing);
    const now = new RunningNow(this.ctx, lane);
    const faceSlot = el("span", "town-face");
    node.append(faceSlot, who, split, now.root, track);
    return { node, face: faceSlot, name, doing, split, fill, now };
  }

  private draw(lane: string, view: View): void {
    const { catalog } = this.ctx;
    const row = this.rows.get(lane);
    if (!row) return;
    const person = personOf(catalog, view, lane, townGreyed(catalog, view));
    const label = catalog.laneLabel(lane, view);
    setText(row.name, label);
    row.face.replaceChildren(face(this.ctx, lane, label));
    setText(row.doing, person.running ? catalog.cardLabel(person.running) : catalog.text.get(UI.laneIdle));
    row.doing.classList.toggle("idle", person.running === null);
    const parts: Share[] = person.shares.map((s) => ({ text: `${catalog.cardLabel(s.card)} ${catalog.format.share(s.bp)}`, bp: s.bp, hue: catalog.rank(s.card) % 6, idle: false }));
    if (person.idleBp > 0) parts.push({ text: `${catalog.text.fill(UI.townIdle, { person: label })} ${catalog.format.share(person.idleBp)}`, bp: person.idleBp, hue: 5, idle: true });
    const { bar, key } = splitOf(parts);
    row.split.replaceChildren(bar, key);
    row.now.update(view);
  }
}
