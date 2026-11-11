// The panel's scroll cue (docs/design/opening-screen.md, "Desktop"): on a desktop the panel is its own scroller, and
// nothing said that more lay below the fold. The panel wears `more` while its content runs past the bottom and it is
// not scrolled to the end; game.css fades its foot then. A still fade, so reduced motion keeps it.
import type { Part } from "./part";

const END_PX = 2;   // a fractional scrollTop leaves a pixel short of the end

export class MoreCue implements Part {
  /** `root` is the panel; `sized` is what changes its content's height. */
  constructor(readonly root: HTMLElement, sized: HTMLElement) {
    root.addEventListener("scroll", () => this.update(), { passive: true });
    const watch = new ResizeObserver(() => this.update());
    watch.observe(root);
    watch.observe(sized);
  }

  update(): void {
    const { root } = this;
    const rest = root.scrollHeight - root.clientHeight - root.scrollTop;
    root.classList.toggle("more", root.scrollHeight > root.clientHeight && rest > END_PX);
  }

  tick(): void {
    // nothing per frame: a scroll or a resize moves it
  }
}
