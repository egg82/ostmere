// The lane rows (docs/design/opening-screen.md, the hands strip, "A lane run by rules"): under the hands strip, one row
// per lane whose task the player's rules set (CONTRACT.txt, "A lane run by rules"), in the hands strip's shape: the
// lane's label, what it does (the running card, or idle), the running card's bar (sampled as the card panel samples
// it), and Change, which opens the lane's task editor in the Rules tab on the rule that acts (game/lanes.ts,
// changeTarget). A row arrives through the arrival queue the first time its lane is in view, then stays. A lane whose
// person has joined the town has no row of its own: the town strip (townstrip.ts) draws them, and this part holds it and
// the town editor its Change opens (townedit.ts), whose root the screen places in the card area.
import type { View } from "../api/types";
import { sample } from "../game/clock";
import { changeTarget, ruledLanes } from "../game/lanes";
import { type Leaver, leaversOf, withLeavers } from "../game/leaving";
import { people } from "../game/town";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import type { Part, PartContext } from "./part";
import { TownEditor } from "./townedit";
import { TownStrip } from "./townstrip";

interface Row { node: HTMLElement; label: HTMLElement; text: HTMLElement; fill: HTMLElement }

export class LaneRows implements Part {
  readonly root = el("div", "lane-rows");
  readonly town: TownEditor;
  private readonly strip: TownStrip;
  private readonly rows = new Map<string, Row>();
  /** What is drawn: the view with the people who are leaving still in it. */
  private view: View | null = null;
  /** The view as the game has it: what Change and the town editor work on. */
  private raw: View | null = null;
  private leaving: Leaver[] = [];

  constructor(private readonly ctx: PartContext, changed: () => void = () => undefined) {
    this.town = new TownEditor(ctx, changed);
    this.strip = new TownStrip(ctx, () => { if (this.raw) this.town.show(this.raw); changed(); });
  }

  /** How many rows are drawn: the town's people, then each lane run by rules that has no person in the town. */
  get count(): number {
    return (this.view ? people(this.ctx.catalog, this.view).length : 0) + this.rows.size;
  }

  /** `prev`: the view before; a person it had who has left stays drawn until the lines the moment brought are read. */
  update(raw: View, prev: View | null = null): void {
    this.raw = raw;
    const gone = prev && this.ctx.arrivals.busy ? leaversOf(prev, raw) : [];
    if (gone.length > 0) {
      this.leaving.push(...gone);
      this.ctx.arrivals.effect(this.root, "line", () => {
        this.leaving = this.leaving.filter((l) => !gone.includes(l));
        if (this.raw) this.update(this.raw);
      });
    }
    const view = withLeavers(this.ctx.catalog, raw, this.leaving);
    this.view = view;
    const { catalog } = this.ctx;
    const joined = people(catalog, view);
    if (joined.length > 0 && !this.strip.root.isConnected) this.root.prepend(this.strip.root);   // before the first join the page is day two's
    this.strip.update(view);
    this.town.update(raw);
    for (const bar of ruledLanes(catalog, view).filter((b) => !joined.includes(b.lane))) {
      const row = this.rows.get(bar.lane) ?? this.add(bar.lane);
      setText(row.label, catalog.laneLabel(bar.lane, view));
      setText(row.text, bar.running_card ? catalog.cardLabel(bar.running_card) : catalog.text.get(UI.laneIdle));
      row.text.classList.toggle("idle", bar.running_card === null);
    }
    this.tick(view.at);
  }

  tick(t: number): void {
    const view = this.view;
    if (!view) return;
    this.strip.tick(t);
    for (const bar of view.lanes) {
      const row = this.rows.get(bar.lane);
      if (!row) continue;
      const card = view.cards.find((c) => c.card === bar.running_card);
      const span = card?.bar_total ?? 0;
      const v = card ? sample(card.bar, t) : 0;
      row.fill.style.transform = `scaleX(${span > 0 ? (((v % span) + span) % span) / span : 0})`;
    }
  }

  private add(lane: string): Row {
    const node = el("section", "hands lane-row");
    node.dataset.lane = lane;
    const label = el("span", "hands-label");
    const text = el("span", "hands-text");
    const change = el("button", "hands-edit lane-change", this.ctx.catalog.text.get(UI.laneChange));
    change.type = "button";
    change.addEventListener("click", () => {
      if (!this.view) return;
      tapFeedback();
      this.ctx.actions.openRules({ lane, rule: changeTarget(this.ctx.catalog, this.view, lane) });
    });
    const head = el("div", "hands-row");
    head.append(text, change);
    const track = el("div", "card-track lane-bar");   // the card's own bar, as the card panel draws it
    const fill = el("span", "card-fill lane-fill");
    track.append(fill);
    const body = el("div", "hands-body");
    body.append(head, track);
    node.append(label, body);
    this.root.append(node);
    const row = { node, label, text, fill };
    this.rows.set(lane, row);
    this.ctx.arrivals.arrive(node, "feature", `lane:${lane}`);
    return row;
  }
}
