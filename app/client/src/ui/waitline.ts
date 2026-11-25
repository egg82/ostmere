// The wait line (CONTRACT.txt, "Goals"; decisions.md, "Progress is stated, never hinted"): when a story beat waits on the
// clock alone, or on a card's fights lost, one line of plain text at the top of the deck says so: "Something new", the
// fights lost against the count a card's beat waits on, the time left, and the store whose running dry stops the
// clock, whose line carries the story mark. It names no beat. Not a card and not a control: nothing to tap or focus.
// Gone while no story beat waits on either.
import type { Goal, View } from "../api/types";
import { sample } from "../game/clock";
import { storyMarks } from "../game/story";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

export class WaitLine {
  readonly root = el("p", "wait-line");
  private at: number | null = null;
  private feed: string | null = null;
  private fights: Goal[] = [];

  constructor(private readonly ctx: PartContext) {
    this.root.hidden = true;
  }

  update(view: View): void {
    const { clock, fights } = storyMarks(this.ctx.catalog, view);
    this.root.hidden = clock === null && fights.length === 0;
    this.fights = fights;
    this.at = clock?.at ?? null;
    this.feed = clock?.feeds[0] ?? null;
  }

  tick(t: number): void {
    if (this.root.hidden) return;
    const { catalog } = this.ctx;
    const { text, format } = catalog;
    const title = text.get(UI.nextUnnamed);
    const store = this.feed === null ? "" : catalog.storeLabel(this.feed);
    const left = this.at === null ? "" : text.fill(UI.goalIn, { d: format.duration(Math.max(0, this.at - t)) });
    const feed = this.feed === null ? "" : text.fill(this.at === null ? UI.goalPaused : UI.goalWhile, { store });
    const lost = this.fights.map((g) => text.fill(UI.goalLost, {
      card: catalog.cardLabel(g.card ?? ""), n: format.amount(g.value ? sample(g.value, t) : 0, g.target),
    }));
    setText(this.root, [title.charAt(0).toUpperCase() + title.slice(1), ...lost, left, feed].filter((s) => s).join(" · "));
  }
}
