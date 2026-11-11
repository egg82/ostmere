// The aim (docs/design/opening-screen.md, "One column of attention"): one line just above the art saying what this
// stretch of play is for, in the story's voice (game/shown.ts, currentAim). Its room is there from the start, so it
// never moves the layout; when the story moves on, the new aim takes its turn after the lines that came with it
// (ui/reveal.ts).
import type { View } from "../api/types";
import { currentAim } from "../game/shown";
import { el, pulse, setText } from "./dom";
import type { PartContext } from "./part";

export class AimLine {
  readonly root = el("p", "aim");
  private shown: string | null = null;

  constructor(private readonly ctx: PartContext) {}

  update(view: View): void {
    const key = currentAim(this.ctx.catalog, view)?.text_key ?? null;
    if (key === this.shown) return;
    const first = this.shown === null;
    this.shown = key;
    const draw = (): void => {
      setText(this.root, key === null ? "" : this.ctx.catalog.text.get(key));
      if (!first) pulse(this.root, "aim-new");
    };
    if (first) draw();
    else this.ctx.arrivals.effect(this.root, "feature", draw);
  }
}
