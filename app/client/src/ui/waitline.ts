// The wait line (CONTRACT.txt, "Goals"; decisions.md, "Progress is stated, never hinted"): when a story beat waits on the
// clock alone, one line of plain text at the top of the deck says so: "Something new", the time left, and the store
// whose running dry stops the clock, whose line carries the story mark. It names no beat. Not a card and not a control:
// nothing to tap or focus. Gone while no story beat waits on the clock.
import type { View } from "../api/types";
import { storyMarks } from "../game/story";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { PartContext } from "./part";

export class WaitLine {
  readonly root = el("p", "wait-line");
  private at: number | null = null;
  private feed: string | null = null;

  constructor(private readonly ctx: PartContext) {
    this.root.hidden = true;
  }

  update(view: View): void {
    const clock = storyMarks(this.ctx.catalog, view).clock;
    this.root.hidden = clock === null;
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
    setText(this.root, [title.charAt(0).toUpperCase() + title.slice(1), left, feed].filter((s) => s).join(" · "));
  }
}
