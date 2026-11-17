// One thing at a time (docs/design/opening-screen.md, "One thing at a time" and "Coming back"). What a return brings,
// and a live step's story lines with what they announce, are drawn at once, so the layout moves only then, but each new
// thing stays invisible until its turn in the arrival queue (game/arrivals.ts): a line first, holding the next turn for
// its reading time, then the rest, each with the usual arrive pulse. Outside those, a new thing shows at once unless
// something is still waiting, when it takes the next turn. Out of sight (below the fold on a phone), it shows at once.
// While story lines wait their turn, a tap or key moves on to the next at once; Escape, or a tap on the story strip,
// shows everything still waiting. With no line waiting, the first tap or key shows everything. The tap itself goes
// through as usual: it moves things on at its click, once it has landed, since a line shown at the press grows the strip
// for a frame and moves what is under the finger before the release.
// A cascade (docs/design/redesign.md, "Feel"): while a live step with no lines is drawn, each effect that is a link in a
// chain (a Link: a card finishing, a store moving, a level, a rule acting) joins a second queue at LINK_PACE, ordered by
// cause, and takes its turn on the same tick, lit (dom.markLink) when the chain has two links or more. What arrives
// in that step shows at once as ever, and a tap or key sets off every link still waiting.
import { ArrivalQueue, LINK_PACE, LINKS, type ArrivalKind, type Link } from "../game/arrivals";
import { markLink, reducedMotion } from "./dom";
import { play } from "./ladder";

const TOUCHES = ["click", "keydown"] as const;

/** What a part calls when it draws something new. `holdMs`: its reading time, which the next kind waits out (a ledger
 * line, read before the cards). */
export interface Arrivals {
  arrive(node: HTMLElement, kind: ArrivalKind, id: string, holdMs?: number): void;
  /** A one-off change on `node` (a ring, a burst, the glow): `run` now, or at its turn after what is waiting; with a
   * `link`, at its turn in the step's cascade; `tap`, it is a tap's completion (the ladder's `tap` rung), which makes the
   * cascade one a tap started. */
  effect(node: HTMLElement, kind: ArrivalKind, run: () => void, link?: Link, tap?: boolean): void;
  /** A story line: first in its batch, holding what follows for `readMs`. */
  line(nodes: HTMLElement[], id: string, readMs: number): void;
  /** Something is waiting its turn. */
  readonly busy: boolean;
}

interface Held {
  node: HTMLElement;
  line?: boolean;
  run?: () => void;
  /** A link of a chain of two or more: lit at its turn. */
  lit?: boolean;
}

export class Reveal implements Arrivals {
  private readonly queue = new ArrivalQueue<Held>();
  /** The cascade's links, ordered by Link (given as each one's `at`). */
  private readonly links = new ArrivalQueue<Held>(LINK_PACE);
  /** A live step's draw is under way and its links join one chain; what they are, sent so far. */
  private chain: Held[] | null = null;
  /** The last cascade begun was set off by a tap: one of its links is a tap's completion. */
  tapStarted = false;
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

  effect(node: HTMLElement, kind: ArrivalKind, run: () => void, link?: Link, tap = false): void {
    if (!this.busy && link && this.chain) {
      if (tap) this.tapStarted = true;
      const held: Held = { node, run };
      this.chain.push(held);
      this.links.push(kind, `link:${this.chain.length}`, LINKS.indexOf(link), held);
      return;
    }
    if (!this.busy) {
      run();
      return;
    }
    this.effects += 1;
    this.queue.push(kind, `effect:${this.effects}`, null, { node, run });
    if (!this.collecting) this.start(performance.now());
  }

  arrive(node: HTMLElement, kind: ArrivalKind, id: string, holdMs = 0): void {
    if (!this.busy) {
      show([{ node }]);
      return;
    }
    node.classList.add("held");
    this.queue.push(kind, id, null, { node }, holdMs);   // the view gives no unlock times yet: shown in kind order
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

  /** A live step with no batch is being drawn: its links make one cascade, set off at start(). */
  cascade(): void {
    this.chain = [];
    this.tapStarted = false;
  }

  /** The batch is drawn: begin showing it (the first thing at once), and the cascade's links. */
  start(nowMs: number): void {
    this.collecting = false;
    if (this.chain) {
      for (const held of this.chain) held.lit = this.chain.length > 1;
      this.chain = null;
      this.links.start(nowMs, reducedMotion(), (held) => held.some((h) => inSight(h.node)));
    }
    this.queue.start(nowMs, reducedMotion(), (held) => held.some((h) => h.line === true || inSight(h.node)));
    if (!(this.queue.quiet(nowMs) && this.links.idle) && !this.listening) {
      for (const t of TOUCHES) document.addEventListener(t, this.skip, { capture: true });
      this.listening = true;
    }
    this.tick(nowMs);
  }

  tick(nowMs: number): void {
    for (const held of [...this.links.due(nowMs), ...this.queue.due(nowMs)]) show(held);
    if (this.queue.quiet(nowMs) && this.links.idle && !this.collecting) this.stopListening();
  }

  private advance(): void {
    const now = performance.now();
    for (const held of [...this.links.skip(), ...this.queue.advance(now)]) show(held);
    if (this.queue.quiet(now) && !this.collecting) this.stopListening();
  }

  private finish(): void {
    for (const held of [...this.links.skip(), ...this.queue.skip()]) show(held);
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
  for (const { node, run, lit } of held) {
    if (lit) markLink(node);
    if (run) {
      run();
      continue;
    }
    node.classList.remove("held");
    play(node, "first");
  }
}
