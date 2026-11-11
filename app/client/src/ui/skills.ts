// One row per unlocked skill the view lists (ui/skillrow.ts draws each), and the prestige sheet its rows open
// (ui/prestigesheet.ts). A level landing bursts on the row.
import type { View } from "../api/types";
import { shownLevel } from "../game/prestige";
import { storyMarks } from "../game/story";
import { el, keyed } from "./dom";
import { play } from "./ladder";
import type { Part, PartContext } from "./part";
import { PrestigeSheet } from "./prestigesheet";
import { SkillRow, type RowActions } from "./skillrow";

export class Skills implements Part {
  readonly root = el("section", "skills");
  private rows = new Map<string, SkillRow>();
  private view: View | null = null;
  private readonly sheet: PrestigeSheet;
  private readonly actions: RowActions;

  constructor(private readonly ctx: PartContext) {
    this.sheet = new PrestigeSheet(ctx);
    this.root.append(this.sheet.root);
    this.actions = { open: (skill) => { if (this.view) this.sheet.show(this.view, skill); }, decide: (d) => ctx.actions.decide(d) };
  }

  update(view: View, prev: View | null): void {
    this.view = view;
    const { catalog } = this.ctx;
    const bars = view.skills.filter((s) => catalog.unlocked(view, "skill", s.skill));
    this.root.hidden = bars.length === 0;
    const known = new Set(this.rows.keys());
    this.rows = keyed(this.root, bars, (b) => b.skill, this.rows, (b) => new SkillRow(catalog, b, this.actions));
    const story = storyMarks(catalog, view).skills;
    for (const bar of bars) {
      const row = this.rows.get(bar.skill);
      if (!row) continue;
      row.node.classList.toggle("story", story.has(bar.skill));   // the story mark (game/story.ts)
      const before = shownLevel(row.bar);
      row.draw(bar);
      if (prev && known.has(bar.skill) && shownLevel(bar) > before) this.ctx.arrivals.effect(row.node, "skill", () => play(row.node, "level"));
      if (prev && !known.has(bar.skill)) this.ctx.arrivals.arrive(row.node, "skill", bar.skill);
    }
    this.sheet.update(view);
  }

  tick(t: number): void {
    for (const row of this.rows.values()) row.tick(this.view, t);
  }
}
