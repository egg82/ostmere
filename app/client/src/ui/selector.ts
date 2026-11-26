// The Mixes list (docs/design/opening-screen.md, "The Mixes list"), opened from the strip: the player's saved mixes, the
// player's own first, never a town mix (it runs by rules and is changed in the town's editor). Tapping one makes it the default (what runs when no rule's mix does): each such row says Run;
// ● and "running" (or how long it runs) mark the one running now. A mix rules run says how many ("used by 2 rules") where Delete would be: a rule's mix can't be deleted. A
// greyed mix (it holds a retired or completed card) can't be run, only edited or deleted. New mix last. The rules
// themselves are the Rules tab's (rules.ts).
import type { Mix, MixRow, MixRows, View } from "../api/types";
import { mixesFull, mixNamedBy } from "../game/mix";
import { rulesUsing } from "../game/orders";
import { isTownMix } from "../game/town";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import { openSheet } from "./back";
import { goalLabel, goalLeft } from "./goaltimes";
import { segmentSpecs } from "./hands";
import { keyItem } from "./sharebar";
import type { PartContext } from "./part";

export class MixSelector {
  readonly root = el("dialog", "sheet selector");
  private readonly list = el("div", "sheet-mixes");
  private view: View | null = null;
  private asking: string | null = null;
  private numbers: MixRows | null = null;

  constructor(private readonly ctx: PartContext) {
    const close = el("button", "quiet", ctx.catalog.text.get(UI.close));
    close.type = "button";
    close.addEventListener("click", () => this.root.close());
    const actions = el("div", "sheet-actions");
    actions.append(close);
    this.root.append(this.list, actions);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
  }

  show(view: View): void {
    this.view = view;
    this.asking = null;
    this.numbers = null;
    this.draw();
    if (!this.root.open) openSheet(this.root);
    void this.ctx.actions.mixRows().then((rows) => {
      if (rows === null || !this.root.open) return;
      this.numbers = rows;
      this.draw();
    });
  }

  update(view: View): void {
    this.view = view;
    if (this.root.open) this.draw();
  }

  private draw(): void {
    const view = this.view;
    if (!view) return;
    const { text } = this.ctx.catalog;
    const add = mixesFull(this.ctx.catalog, view) ? el("p", "rules-full", text.get(UI.mixFull)) : this.newButton();
    const hands = view.mixes.filter((m) => !isTownMix(this.ctx.catalog, view, m));
    const own = hands.filter((m) => m.id === view.active_mix_id);
    const others = hands.filter((m) => m.id !== view.active_mix_id);
    this.list.replaceChildren(el("h2", "panel-heading", text.get(UI.mixesHeading)), ...[...own, ...others].map((m) => this.mixRow(view, m)), add);
  }

  private newButton(): HTMLButtonElement {
    const add = el("button", "quiet selector-new", this.ctx.catalog.text.get(UI.newMix));
    add.type = "button";
    add.addEventListener("click", () => { tapFeedback(); this.root.close(); this.ctx.actions.newMix(null); });
    return add;
  }

  /** A saved mix: tap to make it the default (the player's own is it already). Edit, then Delete or why not. */
  private mixRow(view: View, mix: Mix): HTMLElement {
    const { catalog } = this.ctx;
    const own = mix.id === view.active_mix_id;
    const running = view.running_mix_id === mix.id;
    const greyed = view.greyed_mix_ids.includes(mix.id);
    const row = el("div", "selector-row");
    row.classList.toggle("active", running);
    row.classList.toggle("greyed", greyed);
    const run = el("button", "selector-run");
    run.type = "button";
    run.dataset["mix"] = mix.id;   // a lesson's mark of this row's Run
    run.disabled = greyed || own;
    const note = running ? (own && view.mix_order === null && !greyed ? catalog.format.runs(view.runs_out_at, view.at) : catalog.text.get(UI.mixRunning))
      : run.disabled ? "" : catalog.text.get(UI.runMix);
    run.append(el("span", "selector-dot", running ? "●" : ""), el("span", "selector-name", mix.id), ...this.miniBar(view, mix), el("span", "selector-note", note));
    run.addEventListener("click", () => {
      tapFeedback();
      this.ctx.actions.decide({ kind: "switch_mix", mix_id: mix.id });
      this.root.close();
    });
    const edit = el("button", "quiet", catalog.text.get(UI.edit));
    edit.type = "button";
    edit.addEventListener("click", () => { tapFeedback(); this.root.close(); this.ctx.actions.editMix(mix.id); });
    const tools = el("span", "selector-tools");
    tools.append(edit, ...this.deleteControls(view, mix.id));
    row.append(run, tools);
    const row_ = this.numbers?.rows.find((r) => r.id === mix.id);
    if (row_ && !greyed) row.append(...this.numbersOf(row_));
    return row;
  }

  /** One mix's own numbers, never a score: when each open goal lands under it (and the earlier best for that goal,
   * with the mix that set it), then each store's net per minute. */
  private numbersOf(r: MixRow): HTMLElement[] {
    const { catalog } = this.ctx;
    const { text, format } = catalog;
    const at = this.numbers?.at ?? 0;
    const best = new Map((this.numbers?.best ?? []).map((b) => [b.goal, b]));
    const lines = r.goals.filter((g) => g.lands_at !== null && g.lands_at > at).flatMap((g) => {
      const kept = best.get(`${g.kind}|${g.store ?? ""}|${g.skill ?? ""}|${g.target}`);
      const mine = el("div", "totals-row goal-row mix-goal");
      mine.append(el("span", "totals-store", goalLabel(catalog, g)), el("span", "", goalLeft(catalog, g, at)));
      if (!kept || kept.lands_at <= at) return [mine];
      return [mine, el("div", "goal-binds", text.fill(UI.mixEarlier, { mix: kept.mix_id, when: format.duration(kept.lands_at - at) }))];
    });
    const nets = r.nets.filter((n) => n.per_hour !== 0).map((n) => `${catalog.storeLabel(n.store)} ${format.perMinute(n.per_hour)}`);
    const out = [...lines];
    if (nets.length > 0) out.push(el("div", "goal-binds mix-nets", text.fill(UI.mixNets, { n: nets.join(", ") })));
    if (r.runs_out_at !== null) out.push(el("div", "goal-binds", format.runs(r.runs_out_at, at)));
    const box = el("div", "mix-numbers");
    box.append(...out);
    return [box];
  }

  /** The mix's split as a small bar of hues, and its legend beneath naming each task and its share. */
  private miniBar(view: View, mix: Mix): HTMLElement[] {
    const bar = el("span", "mini-bar");
    const key = el("span", "share-key");
    for (const [i, spec] of segmentSpecs(this.ctx, mix, view).entries()) {
      const share = mix.components[i]?.share_bp ?? 0;
      const seg = el("i", `mini-seg hue-${spec.hue % 6}`);
      seg.style.flexGrow = String(share);
      const { item, name, pct } = keyItem(spec);
      name.textContent = spec.label;
      pct.textContent = this.ctx.catalog.format.share(share);
      bar.append(seg);
      key.append(item);
    }
    return [bar, key];
  }

  /** Delete asks once, in place. A mix rules run says how many instead; one nested in another, or queued, says so. */
  private deleteControls(view: View, id: string): HTMLElement[] {
    const { catalog } = this.ctx;
    const { text } = catalog;
    const used = rulesUsing(view, id);
    if (used > 0) return [el("span", "editor-note used-by", used === 1 ? text.get(UI.usedByOne) : text.fill(UI.usedBy, { n: catalog.format.count(used) }))];
    const named = mixNamedBy(view, id);
    if (named) return [el("span", "editor-note", text.get(named === "order" ? UI.namedByOrder : UI.nested))];
    if (this.asking !== id) {
      const del = el("button", "quiet danger", text.get(UI.deleteMix));
      del.type = "button";
      del.addEventListener("click", () => { this.asking = id; this.draw(); });
      return [del];
    }
    const yes = el("button", "quiet danger", text.get(UI.yes));
    const no = el("button", "quiet", text.get(UI.no));
    yes.type = no.type = "button";
    yes.addEventListener("click", () => { tapFeedback(); this.asking = null; this.ctx.actions.decide({ kind: "delete_mix", mix_id: id }); });
    no.addEventListener("click", () => { this.asking = null; this.draw(); });
    return [el("span", "editor-note", text.get(UI.deleteAsk)), yes, no];
  }
}
