// The Camp bar, the thing to work toward (CONTRACT.txt): drawn from the ledger line of Content.camp.store, which
// is never drawn as a ledger line. Its level is how many of camp_levels' `at` the sample has reached; the bar runs from
// the level's own `at` to the next one's, and the next marker states what that level pays. A held level is a marker
// past the opening: the bar fills to it and holds, its marker still showing, and it is not counted as reached until the
// step that lifts it (one of lifted_by) has finished, when the bar fills on to it and passes. A marker words its pays only
// once what that names is unlocked (CampLevel.names), so it never names a store or card the player has not met; until
// then it reads UI.nextUnnamed, so the bar still shows there is a next thing to reach. Warm,
// because it is the player's; not a control, so it does not look like one. It arrives at its first level, its burst
// with it, already pointing at the next; a level landing bursts on it (ui/ladder.ts). Under the level, a story beat's
// store with no line yet (ui/goals.ts): the box shows for one alone before the first level.
import type { CampLevel, LedgerLine, View } from "../api/types";
import { sample } from "../game/clock";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import { GoalRows } from "./goals";
import { play } from "./ladder";
import type { Part, PartContext } from "./part";

export class CampBar implements Part {
  readonly root = el("div", "camp");
  private readonly level = el("span", "camp-level");
  private readonly next = el("span", "camp-next");
  private readonly fill = el("span", "camp-fill");
  private readonly head = el("span", "camp-head");
  private readonly track = el("span", "camp-track");
  private readonly goals: GoalRows;
  private goalsShown = false;
  private line: LedgerLine | null = null;
  private completed: ReadonlySet<string> = new Set();
  private view: View | null = null;
  /** The store's line is in the view and unlocked: the bar is drawn once a level is reached. */
  private armed = false;
  private shown = -1;

  constructor(private readonly ctx: PartContext) {
    this.goals = new GoalRows(ctx);
    this.track.append(this.fill);
    this.head.append(this.level, this.next);
    this.root.append(this.head, this.track, this.goals.root);
    this.root.hidden = true;
  }

  update(view: View): void {
    const { catalog } = this.ctx;
    const store = catalog.campStore;
    this.line = store ? view.ledger.find((l) => l.store === store) ?? null : null;
    this.completed = new Set(view.completed.map((c) => c.card));
    this.view = view;
    this.armed = store !== null && this.line !== null && catalog.unlocked(view, "store", store);
    this.goalsShown = this.goals.update(view);
    if (!this.armed) this.show(0);
  }

  tick(t: number): void {
    this.goals.tick(t);
    const camp = this.ctx.catalog.content.camp;
    if (!camp || !this.line || !this.armed) return;
    const v = sample(this.line.segment, t);
    const levels = camp.camp_levels;
    const reached = levels.filter((l) => (!l.held || this.lifted(l)) && v >= l.at).length;
    const from = levels[reached - 1]?.at ?? 0;
    const to = levels[reached]?.at ?? null;
    this.fill.style.transform = `scaleX(${to === null ? 1 : Math.min(1, Math.max(0, (v - from) / (to - from)))})`;
    const next = levels[reached];
    this.next.hidden = !next;
    const { catalog } = this.ctx;
    if (next && !this.named(next)) setText(this.next, catalog.text.get(UI.nextUnnamed));   // there is a next; what it is waits
    else if (next) setText(this.next, this.pays(next, reached + 1));
    this.show(reached);
    if (reached === this.shown) return;
    if (this.shown === 0 && reached > 0) this.ctx.arrivals.arrive(this.root, "chip", "camp");
    if (this.shown >= 0 && reached > this.shown) this.ctx.arrivals.effect(this.root, "chip", () => play(this.root, "level"));
    this.shown = reached;
    setText(this.level, `${catalog.storeLabel(camp.store)} ${catalog.text.fill(UI.level, { n: catalog.format.count(reached) })}`);
  }

  /** The level and its bar from the first level reached; the box while either they or a goal show. */
  private show(reached: number): void {
    this.head.hidden = this.track.hidden = reached === 0;
    this.root.hidden = reached === 0 && !this.goalsShown;
  }

  /** The marker's sentence: the level it names, then its pays words, their {from}, {to} and {pct} filled when it has a number. */
  private pays(next: CampLevel, level: number): string {
    const { catalog } = this.ctx;
    const items: Record<string, string> = next.pays_from !== null && next.pays_to !== null
      ? { from: catalog.format.items(next.pays_from), to: catalog.format.items(next.pays_to) } : {};
    const pays = catalog.text.fill(next.pays_key, { ...items, ...catalog.format.figures(next.change_bp) });
    return catalog.text.fill(UI.campPays, { level: catalog.format.count(level), pays });
  }

  /** The marker may word what its level pays: everything that names is unlocked (CampLevel.names). */
  private named(level: CampLevel): boolean {
    const view = this.view;
    return view !== null && level.names.every((u) => this.ctx.catalog.unlocked(view, u.category, u.id));
  }

  /** A held level counts once one of the steps that lift it has finished. */
  private lifted(level: CampLevel): boolean {
    return level.lifted_by.some((card) => this.completed.has(card));
  }
}
