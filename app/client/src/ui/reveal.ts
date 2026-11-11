// One thing at a time (docs/design/opening-screen.md, "One thing at a time" and "Coming back"). What a return brings,
// and a live step's story lines with what they announce, are drawn at once, so the layout moves only then, but each new
// thing stays invisible until its turn in the arrival queue (game/arrivals.ts): a line first, holding the next turn for
// its reading time, then the rest, each with the usual arrive pulse. Outside those, a new thing shows at once unless
// something is still waiting, when it takes the next turn. Out of sight (below the fold on a phone), it shows at once.
// While story lines wait their turn, a tap or key moves on to the next at once; Escape, or a tap on the story strip,
// shows everything still waiting. With no line waiting, the first tap or key shows everything. The tap itself goes
// through as usual: it moves things on at its click, once it has landed, since a line shown at the press grows the strip
// for a frame and moves what is under the finger before the release.
import { ArrivalQueue, type ArrivalKind } from "../game/arrivals";
import { reducedMotion } from "./dom";
import { play } from "./ladder";

const TOUCHES = ["click", "keydown"] as const;

/** What a part calls when it draws something new. `takes`: a node on screen it replaces as it shows (a card's slot,
 * which the finished card keeps until then); sight is judged by that node. `holdMs`: its reading time, which the next
 * kind waits out (a ledger line, read before the cards). */
export interface Arrivals {
  arrive(node: HTMLElement, kind: ArrivalKind, id: string, takes?: HTMLElement, holdMs?: number): void;
  /** A one-off change on `node` (a ring, a burst, the glow): `run` now, or at its turn after what is waiting. */
  effect(node: HTMLElement, kind: ArrivalKind, run: () => void): void;
  /** A story line, in the strip and perhaps on its card: first in its batch, holding what follows for `readMs`. */
  line(nodes: HTMLElement[], id: string, readMs: number): void;
  /** Something is waiting its turn. */
  readonly busy: boolean;
}

interface Held {
  node: HTMLElement;
  takes?: HTMLElement;
  line?: boolean;
  run?: () => void;
}

export class Reveal implements Arrivals {
  private readonly queue = new ArrivalQueue<Held>();
  private collecting = false;
  private listening = false;
  private readonly skip = (e?: Event): void => {
    const onStrip = (e?.target as Element | null | undefined)?.closest?.(".strip") != null;
    if (onStrip || (e as KeyboardEvent | undefined)?.key === "Escape") this.finish();
    else this.advance();
  };
  private effects = 0;

  get busy(): boolean {
    return this.collecting || !this.queue.quiet(performance.now());
  }

  effect(node: HTMLElement, kind: ArrivalKind, run: () => void): void {
    if (!this.busy) {
      run();
      return;
    }
    this.effects += 1;
    this.queue.push(kind, `effect:${this.effects}`, null, { node, run });
    if (!this.collecting) this.start(performance.now());
  }

  arrive(node: HTMLElement, kind: ArrivalKind, id: string, takes?: HTMLElement, holdMs = 0): void {
    if (!this.busy) {
      show([{ node, takes }]);
      return;
    }
    node.classList.add("held");
    this.queue.push(kind, id, null, { node, takes }, holdMs);   // the view gives no unlock times yet: shown in kind order
    if (!this.collecting) this.start(performance.now());   // a straggler: its turn comes after what is waiting
  }

  /** A story line, in the strip and perhaps on its card: first in this batch, holding what follows for `readMs`. */
  line(nodes: HTMLElement[], id: string, readMs: number): void {
    for (const node of nodes) {
      node.classList.add("held");
      this.queue.push("line", id, null, { node, line: true }, readMs);
    }
  }

  /** A batch is being drawn: what arrives until start() waits its turn, after anything still waiting. */
  collect(): void {
    this.collecting = true;
  }

  /** The batch is drawn: begin showing it (the first thing at once). */
  start(nowMs: number): void {
    this.collecting = false;
    this.queue.start(nowMs, reducedMotion(), (held) => held.some((h) => h.line === true || inSight(h.takes ?? h.node)));
    if (!this.queue.quiet(nowMs) && !this.listening) {
      for (const t of TOUCHES) document.addEventListener(t, this.skip, { capture: true });
      this.listening = true;
    }
    this.tick(nowMs);
  }

  tick(nowMs: number): void {
    for (const held of this.queue.due(nowMs)) show(held);
    if (this.queue.quiet(nowMs) && !this.collecting) this.stopListening();
  }

  private advance(): void {
    const now = performance.now();
    for (const held of this.queue.advance(now)) show(held);
    if (this.queue.quiet(now) && !this.collecting) this.stopListening();
  }

  private finish(): void {
    for (const held of this.queue.skip()) show(held);
    this.stopListening();
  }

  private stopListening(): void {
    if (!this.listening) return;
    this.listening = false;
    for (const t of TOUCHES) document.removeEventListener(t, this.skip, { capture: true });
  }
}

/** On screen now (scrolled out of view, it shows at once rather than spend a turn unseen). */
function inSight(node: HTMLElement): boolean {
  const r = node.getBoundingClientRect();
  return r.bottom > 0 && r.right > 0 && r.top < window.innerHeight && r.left < window.innerWidth;
}

function show(held: Held[]): void {
  for (const { node, takes, run } of held) {
    if (run) {
      run();
      continue;
    }
    if (takes?.isConnected) takes.replaceWith(node);
    node.classList.remove("held");
    play(node, "first");
  }
}
