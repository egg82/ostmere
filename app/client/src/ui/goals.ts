// A story beat's store with no ledger line yet (CONTRACT.txt, "Goals"; game/story.ts, unlined): nothing on screen to
// mark, so the Camp bar's box states it under its level as the store's label, how far along against its target, and a
// bar, with the bar's "▸ something new", never what.
import type { Goal, View } from "../api/types";
import { sample } from "../game/clock";
import { storyMarks } from "../game/story";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

interface Row {
  what: HTMLElement;
  fill: HTMLElement;
}

export class GoalRows {
  readonly root = el("div", "goals");
  private goals: Goal[] = [];
  private rows: Row[] = [];
  private key = "";

  constructor(private readonly ctx: PartContext) {}

  /** True when there is a goal to show. */
  update(view: View): boolean {
    this.goals = storyMarks(this.ctx.catalog, view).unlined;
    const key = this.goals.map((g) => `${g.store ?? ""}|${g.target}`).join(",");
    if (key !== this.key) {
      this.key = key;
      const made = this.goals.map(() => this.make());
      this.rows = made.map((m) => m.row);
      this.root.replaceChildren(...made.map((m) => m.node));
    }
    this.root.hidden = this.goals.length === 0;
    return this.goals.length > 0;
  }

  tick(t: number): void {
    const { catalog } = this.ctx;
    this.goals.forEach((g, i) => {
      const row = this.rows[i];
      if (!row || g.store === null) return;
      const now = g.value ? sample(g.value, t) : 0;
      setText(row.what, `${catalog.storeLabel(g.store)} ${catalog.format.amount(now, g.target)}`);
      row.fill.style.transform = `scaleX(${g.target > 0 ? Math.min(1, Math.max(0, now / g.target)) : 0})`;
    });
  }

  private make(): { node: HTMLElement; row: Row } {
    const node = el("div", "goal");
    const head = el("span", "camp-head");
    const what = el("span", "goal-what");
    head.append(what, el("span", "camp-next", this.ctx.catalog.text.get(UI.nextUnnamed)));
    const track = el("span", "camp-track");
    const fill = el("span", "camp-fill");
    track.append(fill);
    node.append(head, track);
    return { node, row: { what, fill } };
  }
}
