// The line the game shows while a long absence comes back in slices (Session's catchingUp): how far through the time
// away the server is, as a share of it, never an estimate of how long is left. Still text, no motion.
import { UI, type Text } from "../game/text";
import { el, setText } from "./dom";

export class CatchingUp {
  readonly root = el("p", "catching-up");

  constructor(private readonly text: Text) {
    this.root.setAttribute("role", "status");
    this.root.hidden = true;
  }

  /** The save is at `at` of `to`, coming from `from`, the time of the view the player is looking at. */
  show(from: number, at: number, to: number): void {
    const share = to > from ? Math.min(99, Math.max(0, Math.floor((100 * (at - from)) / (to - from)))) : 0;
    setText(this.root, this.text.fill(UI.catchingUp, { percent: String(share) }));
    this.root.hidden = false;
    document.body.classList.add("catching-up");
  }

  hide(): void {
    this.root.hidden = true;
    document.body.classList.remove("catching-up");
  }
}
