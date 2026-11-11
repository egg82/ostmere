// The split a mix runs now, under the split the player set (CONTRACT.txt, "SPENT"; docs/decisions.md, "A mix keeps
// going without a dry store"): shown only while a card of the mix is stopped, its slice greyed and each other card's
// gain named by its source. It arrives through the arrival queue the first time; after that its row keeps its room
// while it shows nothing, so its coming and going never moves what is under a finger. One per lane: the hands strip
// has one under its bar, each person of the town one under theirs. The numbers are the view's; it adds none.
import type { View } from "../api/types";
import { type RunningPart, runningNow } from "../game/spent";
import { UI } from "../game/text";
import { el } from "./dom";
import type { PartContext } from "./part";

export class RunningNow {
  readonly root = el("div", "running-now");
  private readonly bar = el("div", "town-shares running-bar");
  private readonly key = el("div", "town-key running-key");
  private shown = false;
  private drawn = "";

  constructor(private readonly ctx: PartContext, private readonly lane: string) {
    this.root.append(el("span", "running-label", ctx.catalog.text.get(UI.runningNow)), this.bar, this.key);
    this.root.hidden = true;
  }

  update(view: View): void {
    const parts = runningNow(this.ctx.catalog, view, this.lane);
    if (parts && !this.shown) {
      this.shown = true;
      this.root.hidden = false;
      this.ctx.arrivals.arrive(this.root, "feature", `running-now:${this.lane}`);
    }
    this.root.classList.toggle("matched", parts === null);
    const drawn = JSON.stringify(parts);
    if (parts && drawn !== this.drawn) this.draw(parts);
    this.drawn = drawn;
  }

  private draw(parts: RunningPart[]): void {
    const { catalog } = this.ctx;
    const { bp } = catalog.content.scales;
    this.bar.replaceChildren();
    this.key.replaceChildren();
    for (const p of parts) {
      const hue = `hue-${catalog.rank(p.card) % 6}`;
      const seg = el("span", `town-seg ${hue}${p.stopped ? " stopped" : ""}`);
      seg.style.flexGrow = String(p.bp);
      this.bar.append(seg);
      this.key.append(el("span", `town-key-item ${hue}${p.stopped ? " stopped" : ""}`, this.label(p)));
    }
    const rest = bp - parts.reduce((n, p) => n + p.bp, 0);
    if (rest > 0) {
      const idle = el("span", "town-seg idle");
      idle.style.flexGrow = String(rest);
      this.bar.append(idle);
    }
  }

  /** "Gather 75% · +25% from Fish", or "Fish waiting" for a stopped card. */
  private label(p: RunningPart): string {
    const { catalog } = this.ctx;
    const name = catalog.cardLabel(p.card);
    if (p.stopped) return catalog.text.fill(UI.waiting, { card: name });
    const from = p.from.map((g) => catalog.text.fill(UI.gainFrom, { pct: catalog.format.share(g.share_bp), card: catalog.cardLabel(g.card) }));
    return [`${name} ${catalog.format.share(p.bp)}`, ...from].join(" · ");
  }
}
