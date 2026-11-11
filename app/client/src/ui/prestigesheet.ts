// The prestige sheet (docs/design/prestige-phases.md, "The click and the menu"), opened from a skill row's Push past or
// Choose: the levels the top lifts from and to, and the level the carried XP takes the skill to, then the menu's nodes
// in track order, each with its rank ("2/5"), what one more rank changes as plain numbers before and after
// (game/prestige.ts), and its own button. The sheet stays open after the click: it says the skill is past its top and
// offers Undo while undo_open; an undo brings the same menu back to choose again; it also lists the picks, each with Move
// (ui/movepicks.ts). Every number is the view's.
import type { MenuNode, SkillPrestige, View } from "../api/types";
import { changeText, liftedTop } from "../game/prestige";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { moveLines, type Moving } from "./movepicks";
import type { PartContext } from "./part";

export class PrestigeSheet {
  readonly root = el("dialog", "sheet prestige-sheet");
  private readonly body = el("div", "sheet-mixes");
  private view: View | null = null;
  private skill = "";
  /** The picked node whose rank is being moved (ui/movepicks.ts), null otherwise. */
  private moving: string | null = null;

  constructor(private readonly ctx: PartContext) {
    const close = el("button", "quiet", ctx.catalog.text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    const actions = el("div", "sheet-actions");
    actions.append(close);
    this.root.append(this.body, actions);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  show(view: View, skill: string): void {
    this.view = view;
    this.skill = skill;
    this.moving = null;
    this.draw();
    if (!this.root.open) this.root.showModal();
  }

  update(view: View): void {
    this.view = view;
    if (this.root.open) this.draw();
  }

  private draw(): void {
    const { catalog } = this.ctx;
    const { text, format } = catalog;
    const bar = this.view?.skills.find((s) => s.skill === this.skill);
    const p = bar?.prestige;
    if (!bar || !p) { this.root.close(); return; }
    const heading = el("h2", "panel-heading", text.fill(UI.prestigeHeading, { skill: catalog.skillLabel(this.skill) }));
    if (!p.pick_owed && !(p.at_top && !p.mastered)) {
      if (this.moving !== null && !p.picked.includes(this.moving)) this.moving = null;
      const moving = { node: this.moving, start: (node: string | null) => { this.moving = node; this.draw(); } };
      this.body.replaceChildren(heading, ...(this.moving === null ? this.begun(p) : []), ...moveLines(this.ctx, this.skill, p, moving));
      return;
    }
    const intro = p.pick_owed ? text.get(UI.prestigeOwed)
      : text.fill(UI.prestigeStarts, {
        before: format.count(p.level_counted), after: format.count(liftedTop(bar, p)),
        n: format.count(p.level_counted + p.waiting_levels),
      });
    this.body.replaceChildren(heading, el("p", "prestige-intro", intro), ...p.menu_nodes.map((n) => this.nodeRow(n, p.pick_owed)));
  }

  /** After the click: the level the skill stands at, and Undo while the pick can be taken back. */
  private begun(p: SkillPrestige): HTMLElement[] {
    const { text, format } = this.ctx.catalog;
    const said = el("p", "prestige-intro", text.fill(UI.prestigeBegun, { n: format.count(p.level_counted) }));
    if (!p.undo_open) return [said];
    const undo = el("button", "quiet", text.get(UI.prestigeUndo));
    undo.type = "button";
    undo.addEventListener("click", () => { tapFeedback(); this.ctx.actions.decide({ kind: "undo_pick", skill: this.skill }); });
    const row = el("div", "prestige-undo");
    row.append(said, undo);
    return [row];
  }

  private nodeRow(n: MenuNode, owed: boolean): HTMLElement {
    const { catalog } = this.ctx;
    const row = el("div", "prestige-node");
    const head = el("div", "prestige-head");
    head.append(el("span", "prestige-name", catalog.label(catalog.nodes.get(n.node)?.label_key)),
      el("span", "prestige-rank", catalog.format.completions(n.ranks_taken, n.ranks)));
    const pick = el("button", "primary", catalog.text.get(owed ? UI.prestigeChoose : UI.prestigeButton));
    pick.type = "button";
    pick.dataset["node"] = n.node;
    pick.addEventListener("click", () => { tapFeedback(); this.ctx.actions.decide({ kind: "prestige", skill: this.skill, node: n.node }); });
    row.append(head, el("span", "prestige-change", changeText(catalog, n)), pick);
    return row;
  }
}
