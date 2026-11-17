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
// Sound (docs/design/sound.md, "The ladder"): what arrives together is a batch, and a batch plays its highest cue once, at
// that thing's own turn (audio/cues.ts); a tap's cascade also ticks, link by link, scheduled when it starts.
import { ArrivalQueue, LINK_GAP_MS, LINK_PACE, LINKS, type ArrivalKind, type Link } from "../game/arrivals";
import { isCue, pickCue, sing, tick, TICK_RATIOS, type Cue } from "../audio/cues";
import { markLink, reducedMotion } from "./dom";
import { LADDER, play, type Rung } from "./ladder";

const TOUCHES = ["click", "keydown"] as const;

/** What a part calls when it draws something new. `holdMs`: its reading time, which the next kind waits out (a ledger
 * line, read before the cards). */
export interface Arrivals {
  arrive(node: HTMLElement, kind: ArrivalKind, id: string, holdMs?: number): void;
  /** A one-off change on `node` (a ring, a burst, the glow): `run` now, or at its turn after what is waiting; with a
   * `link`, at its turn in the step's cascade. `rung` is the ladder rung it plays: its sound comes with it, a `tap`
   * makes the cascade one a tap started, and `run` is told to stay `quiet` when a higher cue in its batch plays. */
  effect(node: HTMLElement, kind: ArrivalKind, run: (quiet: boolean) => void, link?: Link, rung?: Rung): void;
  /** A story line: first in its batch, holding what follows for `readMs`. `cue`: the line opens a beat (`beat`) or is
   * the first of the end's (`end`), and sounds as such if it is its batch's highest. */
  line(nodes: HTMLElement[], id: string, readMs: number, cue?: "beat" | "end"): void;
  /** Something is waiting its turn. */
  readonly busy: boolean;
}

interface Held {
  node: HTMLElement;
  line?: boolean;
  run?: (quiet: boolean) => void;
  /** A link of a chain of two or more: lit at its turn. */
  lit?: boolean;
  link?: Link;
  /** The cue it would sound in its batch (the rung's, or a line's), and whether it is the batch's highest. */
  cue?: Cue;
  plays?: boolean;
  /** Already shown, silently, in the step's cascade: its cue sounds at start() if it is the highest. */
  shown?: boolean;
}

const cueOf = (rung: Rung | undefined): Cue | undefined => {
  const voice = rung ? LADDER[rung].sound : null;
  return isCue(voice) ? voice : undefined;
};
const byCause = (held: Held[]): Held[] => [...held].sort((a, b) => LINKS.indexOf(a.link!) - LINKS.indexOf(b.link!));

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
  /** What was sent to the batch being drawn with a cue, for picking its highest. */
  private members: Held[] = [];
  /** The first draw of a page: nothing sounds. */
  private hushed = false;
  /** The cascade's ticks scheduled and not yet begun, each with when it begins. */
  private ticks: Array<{ at: number; cut: () => void }> = [];

  get busy(): boolean {
    return this.collecting || !this.queue.quiet(performance.now());
  }

  effect(node: HTMLElement, kind: ArrivalKind, run: (quiet: boolean) => void, link?: Link, rung?: Rung): void {
    const held: Held = { node, run, cue: cueOf(rung) };
    if (!this.busy && link && this.chain) {
      if (rung === "tap") this.tapStarted = true;
      held.link = link;
      this.chain.push(held);
      this.links.push(kind, `link:${this.chain.length}`, LINKS.indexOf(link), held);
      return;
    }
    if (!this.busy) {
      this.now(held);
      return;
    }
    this.effects += 1;
    this.queue.push(kind, `effect:${this.effects}`, null, held);
    if (held.cue) this.members.push(held);
    if (!this.collecting) this.start(performance.now());
  }

  /** The first draw of a page has no sound: nothing here is new to the player. */
  hush(): void {
    this.hushed = true;
  }

  /** Shown at once: alone it sounds if in sight; in a step's cascade it joins the batch, whose cue is picked at start(). */
  private now(held: Held): void {
    if (held.cue && this.chain && !this.hushed) {
      held.shown = true;
      this.members.push(held);
    } else held.plays = !this.hushed && inSight(held.node);
    show([held]);
  }

  arrive(node: HTMLElement, kind: ArrivalKind, id: string, holdMs = 0): void {
    const held: Held = { node, cue: "new" };
    if (!this.busy) {
      this.now(held);
      return;
    }
    node.classList.add("held");
    this.members.push(held);
    this.queue.push(kind, id, null, held, holdMs);   // the view gives no unlock times yet: shown in kind order
    if (!this.collecting) this.start(performance.now());   // a straggler: its turn comes after what is waiting
  }

  /** A story line, in the strip and perhaps on its card: first in this batch, holding what follows for `readMs`. */
  line(nodes: HTMLElement[], id: string, readMs: number, cue?: "beat" | "end"): void {
    for (const node of nodes) {
      node.classList.add("held");
      const held: Held = { node, line: true, cue };
      this.queue.push("line", id, null, held, readMs);
      if (cue) this.members.push(held);
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
    const turns = this.chain ? byCause(this.chain) : [];
    this.pick(turns);
    if (this.chain) {
      for (const held of this.chain) held.lit = this.chain.length > 1;
      this.scheduleTicks(turns, nowMs);
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

  /** The batch's highest cue, among what is in sight, is the one that sounds. */
  private pick(turns: Held[]): void {
    const win = pickCue([...this.members, ...turns].filter((h) => h.line === true || inSight(h.node)));
    this.members = [];
    this.hushed = false;
    if (!win) return;
    win.plays = true;
    if (win.shown && win.cue) sing(win.cue);
  }

  /** A tap's cascade ticks: link n after the first at the start plus n x LINK_GAP_MS, scheduled now on the audio clock
   * (a chain the mix or a rule started is silent). A link that plays the level's cue takes no tick; links that light
   * together (reduced motion) play one. */
  private scheduleTicks(turns: Held[], nowMs: number): void {
    if (!this.tapStarted) return;
    const next = turns.filter((h) => inSight(h.node)).slice(1, 1 + TICK_RATIOS.length)
      .flatMap((h, i) => (h.plays ? [] : [i + 1]));
    if (reducedMotion()) {
      if (next.length > 0) tick(1, 0);
      return;
    }
    for (const n of next) this.ticks.push({ at: nowMs + n * LINK_GAP_MS, cut: tick(n, n * LINK_GAP_MS) });
  }

  /** Links set off at once: the ticks not yet begun stop, and one plays. */
  private setOff(): void {
    const now = performance.now();
    const waiting = this.ticks.filter((t) => t.at > now);
    this.ticks = [];
    if (waiting.length === 0) return;
    for (const t of waiting) t.cut();
    tick(1, 0);
  }

  tick(nowMs: number): void {
    for (const held of [...this.links.due(nowMs), ...this.queue.due(nowMs)]) show(held);
    if (this.queue.quiet(nowMs) && this.links.idle && !this.collecting) this.stopListening();
  }

  private advance(): void {
    const now = performance.now();
    const links = this.links.skip();
    if (links.length > 0) this.setOff();
    for (const held of [...links, ...this.queue.advance(now)]) show(held);
    if (this.queue.quiet(now) && !this.collecting) this.stopListening();
  }

  private finish(): void {
    const links = this.links.skip();
    if (links.length > 0) this.setOff();
    for (const held of [...links, ...this.queue.skip()]) show(held);
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
  for (const { node, run, lit, cue, plays, line } of held) {
    if (lit) markLink(node);
    const quiet = cue !== undefined && plays !== true;
    if (run) {
      run(quiet);
      continue;
    }
    node.classList.remove("held");
    play(node, "first", line === true || quiet);   // a line's cue is its own, not the First note
    if (line && plays && cue) sing(cue);
  }
}
