// One skill's row (ui/skills.ts lists them): its label, level, an XP bar between the level's own bounds (level_xp to
// next_level_xp, sampled; full at the last level), and what the next level pays, shown before it is reached
// (SkillInfo.levels, the first entry above the level; a story unlock's words are the content's own), with the time to
// it when the view's forecast has one (game/forecast.ts: so a change of mix shows at once in the time, and the time
// comes true). A row with nothing ahead says so ("no more yet") and its bar is drawn muted, so it never reads as
// progress toward something.
// Under prestige (SkillBar.prestige; docs/design/prestige-phases.md, "What the page shows") the level is the one counted
// across phases (level_counted), which never falls at a click, and SkillInfo.levels count the same way. The foot says "tops out in" when
// the forecast has the top; at the top the bar is full and marked, the foot counts the levels waiting and holds the
// Push past control, which opens the sheet (ui/prestigesheet.ts) and is where its lesson starts, so the note shows
// nowhere earlier. A mastered skill at its top reads as mastered, with no control. While the last pick can be taken
// back the foot holds Undo; while a pick is owed, Choose; with picks or parked ranks to show, Picks.
import type { SkillBar, SkillPrestige, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { sample } from "../game/clock";
import { levelAt, topAt } from "../game/forecast";
import { shownLevel, waitingText } from "../game/prestige";
import { UI } from "../game/text";
import { el, setText, tapFeedback } from "./dom";
import type { Actions } from "./part";

/** What a row's controls ask for: the sheet on a skill, or a decision. */
export interface RowActions {
  open(skill: string): void;
  decide: Actions["decide"];
}

export class SkillRow {
  readonly node = el("div", "skill");
  private readonly level = el("span", "skill-level");
  private readonly next = el("span", "skill-next");
  private readonly fill = el("span", "bar-fill");
  private readonly foot = el("div", "skill-foot");
  private readonly note = el("span", "skill-note");
  private readonly act = el("button", "primary");
  private readonly undo = el("button", "quiet");
  private readonly picks = el("button", "quiet picks");
  /** What the next level pays (null: nothing ahead, or the row is at its top). */
  private pays: string | null = null;
  /** The foot's words at the top ("+6 levels waiting"); null below it. */
  private waiting: string | null = null;

  constructor(private readonly catalog: Catalog, public bar: SkillBar, actions: RowActions) {
    this.node.tabIndex = -1;
    const track = el("div", "bar-track");
    track.append(this.fill);
    const head = el("div", "skill-head");
    head.append(el("span", "skill-name", catalog.skillLabel(bar.skill)), this.level, this.next);
    this.act.type = this.undo.type = this.picks.type = "button";
    this.act.dataset["skill"] = bar.skill;
    setText(this.undo, catalog.text.get(UI.prestigeUndo));
    setText(this.picks, catalog.text.get(UI.prestigePicks));
    this.picks.addEventListener("click", () => { tapFeedback(); actions.open(this.bar.skill); });
    this.act.addEventListener("click", () => { tapFeedback(); actions.open(this.bar.skill); });
    this.undo.addEventListener("click", () => { tapFeedback(); actions.decide({ kind: "undo_pick", skill: this.bar.skill }); });
    this.foot.append(this.note, this.act, this.undo, this.picks);
    this.foot.hidden = true;
    this.node.append(head, track, this.foot);
  }

  draw(bar: SkillBar): void {
    const { catalog } = this;
    const { text, format } = catalog;
    const p = bar.prestige;
    this.bar = bar;
    setText(this.level, text.fill(UI.level, { n: format.count(shownLevel(bar)) }));
    const next = catalog.skills.get(bar.skill)?.levels.find((l) => l.level > (p?.level_counted ?? bar.level));
    const top = p?.at_top === true;
    const mastered = top && p.mastered;
    this.pays = next && !top ? text.fill(next.pays_key, format.figures(next.change_bp)) : null;
    this.node.classList.toggle("at-top", top && !mastered);
    this.node.classList.toggle("done-for-now", top ? mastered : !next);
    if (top) setText(this.next, text.get(mastered ? UI.prestigeMastered : UI.prestigeTop));
    else if (!next) setText(this.next, text.get(UI.skillNone));
    this.drawFoot(p, top && !mastered);
  }

  /** Push past at the top (the lesson's trigger), Choose while a pick is owed, Undo while the last pick can be taken back. */
  private drawFoot(p: SkillPrestige | null, waits: boolean): void {
    const owed = p?.pick_owed === true;
    this.act.hidden = !waits && !owed;
    setText(this.act, this.catalog.text.get(owed ? UI.prestigeChoose : UI.prestigeButton));
    if (waits && !owed) this.act.dataset["teach"] = "prestige";
    else delete this.act.dataset["teach"];
    this.undo.hidden = p?.undo_open !== true;
    this.picks.hidden = !(p && !owed && !waits && (p.picked.length > 0 || p.parked.length > 0) && p.menu_nodes.length > 0);
    this.waiting = waits && p ? waitingText(this.catalog, p.waiting_levels) : null;
  }

  tick(view: View | null, t: number): void {
    const { catalog } = this;
    if (this.pays !== null) {
      const at = view ? levelAt(view, this.bar.skill, t) : null;
      setText(this.next, at !== null
        ? catalog.text.fill(UI.skillNextIn, { pays: this.pays, d: catalog.format.duration(at - t) }) : this.pays);
    }
    const top = view && this.bar.prestige && !this.bar.prestige.at_top ? topAt(view, this.bar.skill, t) : null;
    const note = this.waiting ?? (top !== null ? catalog.text.fill(UI.prestigeTopsOut, { d: catalog.format.duration(top - t) }) : "");
    setText(this.note, note);
    this.foot.hidden = note === "" && this.act.hidden && this.undo.hidden && this.picks.hidden;
    const { xp, level_xp, next_level_xp } = this.bar;
    const span = next_level_xp === null ? 0 : next_level_xp - level_xp;
    const done = next_level_xp === null ? 1 : span > 0 ? Math.min(1, Math.max(0, (sample(xp, t) - level_xp) / span)) : 0;
    this.fill.style.transform = `scaleX(${done})`;
  }
}
