// What is new on screen, shown one thing at a time: an Event Queue (Nystrom, Game Programming Patterns). The parts that
// draw a new thing send it here as they draw; the reveal pulls them off over the next few seconds, so sending is
// decoupled from showing in time. Two uses (docs/design/opening-screen.md): what arrived while the player was away
// ("Coming back"), and a live step's story lines, each shown before what it announces ("One thing at a time"). It is
// the first piece of the planned chronicle (docs/systems.md, "Chronicle and unwrap"), whose events will carry times.
// No DOM here: the payload is whatever the reader shows (ui/reveal.ts).
import type { Unlock } from "../api/types";

/** The kinds of thing that arrive, in the order they are shown when nothing says when each happened. */
export const KIND_ORDER = ["feature", "chip", "store", "skill", "card"] as const satisfies readonly Unlock["category"][];
/** A story line goes first in its batch, ahead of every kind above, and holds the next turn for its reading time. */
export type ArrivalKind = "line" | (typeof KIND_ORDER)[number];

/** Time between two reveals: the spread is CAP_MS over the batch, held within these. */
export const MIN_GAP_MS = 400;
export const MAX_GAP_MS = 700;
/** A batch's reveal never runs longer than this after its lines; whatever is still waiting then arrives together. */
export const CAP_MS = 4000;

interface Arrival<T> {
  kind: ArrivalKind;
  id: string;
  /** Game time it happened, when the view says; null: unknown, ordered by kind after the timed ones. */
  at: number | null;
  payloads: T[];
  seq: number;
  /** How long the next turn waits after this one is shown (a line's reading time; for another kind, the next kind's
   * turn: a ledger line read before the cards); 0: the batch's pace. */
  holdMs: number;
  dueMs: number;
}

export class ArrivalQueue<T> {
  /** Scheduled and not yet shown, in the order they are due. */
  private waiting: Arrival<T>[] = [];
  /** Sent since the last start. */
  private batch: Arrival<T>[] = [];
  /** Until when the last line shown is still being read: nothing else shows before then. */
  private heldUntil = -Infinity;

  /** Nothing waiting and nothing being sent. */
  get idle(): boolean {
    return this.waiting.length === 0 && this.batch.length === 0;
  }

  /** Nothing waiting and no line still being read at `nowMs`: a new thing may show at once. */
  quiet(nowMs: number): boolean {
    return this.idle && nowMs >= this.heldUntil;
  }

  /** One thing arrived, into the next batch. A second send of the same kind and id joins the first (a ledger line and
   * its rule offer, a line on the band and on its card), even one already waiting, and keeps the longer hold. */
  push(kind: ArrivalKind, id: string, at: number | null, payload: T, holdMs = 0): void {
    const same = [...this.waiting, ...this.batch].find((a) => a.kind === kind && a.id === id);
    if (same) {
      same.payloads.push(payload);
      same.holdMs = Math.max(same.holdMs, holdMs);
      return;
    }
    this.batch.push({ kind, id, at, payloads: [payload], seq: this.batch.length, holdMs, dueMs: 0 });
  }

  /** Orders the batch and times each reveal, after whatever is still waiting: its lines first, each holding the next
   * turn for its reading time, then the rest evenly within the cap, a held kind (the ledger's lines) holding the next
   * kind for its longest reading time. Under reduced motion the rest are due together, a held kind's wait kept (the
   * lines still lead: a wait is not motion). Whatever `seen` says is out of sight is due at once and takes no turn. */
  start(nowMs: number, reduced: boolean, seen: (payloads: T[]) => boolean = () => true): void {
    const batch = this.batch.sort(order);
    this.batch = [];
    const turns = batch.filter((a) => seen(a.payloads));
    const unseen = batch.filter((a) => !turns.includes(a));
    for (const a of unseen) {
      a.dueMs = nowMs;
      a.holdMs = 0;
    }
    let t = Math.max(nowMs, this.freeAt());
    const lines = turns.filter((a) => a.kind === "line");
    for (const a of lines) {
      a.dueMs = t;
      t += a.holdMs;
    }
    const rest = turns.filter((a) => a.kind !== "line");
    const n = rest.length;
    const gap = reduced || n < 2 ? 0 : Math.min(MAX_GAP_MS, Math.max(MIN_GAP_MS, CAP_MS / (n - 1)));
    let held = 0;   // the held kinds' waits so far, past the gap each replaces
    let run = 0;   // the longest hold in the kind under way
    rest.forEach((a, i) => {
      const prev = rest[i - 1];
      if (prev && prev.kind !== a.kind) { held += Math.max(0, run - gap); run = 0; }
      run = Math.max(run, a.holdMs);
      a.dueMs = t + held + Math.min(CAP_MS, i * gap);
    });
    this.waiting = [...this.waiting, ...unseen, ...lines, ...rest].sort((a, b) => a.dueMs - b.dueMs);   // stable
  }

  /** The payloads whose turn has come by `nowMs`, in order, each group once. */
  due(nowMs: number): T[][] {
    const out: T[][] = [];
    while (this.waiting.length > 0 && (this.waiting[0]?.dueMs ?? Infinity) <= nowMs) {
      const a = this.waiting.shift();
      if (!a) break;
      if (a.holdMs > 0) this.heldUntil = Math.max(this.heldUntil, a.dueMs + a.holdMs);
      out.push(a.payloads);
    }
    return out;
  }

  /** The player tapped while a line waits its turn: the line being read is done, so every turn waiting comes that much
   * sooner and the next one is due at `nowMs`. With no line waiting, everything shows at once (skip). */
  advance(nowMs: number): T[][] {
    if (this.batch.length > 0 || !this.waiting.some((a) => a.kind === "line")) return this.skip();
    const sooner = Math.max(0, (this.waiting[0]?.dueMs ?? nowMs) - nowMs);
    for (const a of this.waiting) a.dueMs -= sooner;
    this.heldUntil = -Infinity;
    return this.due(nowMs);
  }

  /** Everything still waiting or being sent, at once: the player skipped. */
  skip(): T[][] {
    if (this.batch.length > 0) this.start(-Infinity, true);
    const out = this.waiting.map((a) => a.payloads);
    this.waiting = [];
    this.heldUntil = -Infinity;
    return out;
  }

  /** The earliest the batch's first turn may come: after the last one waiting, by its hold or the pace's gap, and
   * never while a line shown is still being read. */
  private freeAt(): number {
    const last = this.waiting[this.waiting.length - 1];
    return Math.max(this.heldUntil, last ? last.dueMs + Math.max(last.holdMs, MIN_GAP_MS) : -Infinity);
  }
}

function order<T>(a: Arrival<T>, b: Arrival<T>): number {
  if (a.at !== null && b.at !== null && a.at !== b.at) return a.at - b.at;
  if ((a.at === null) !== (b.at === null)) return a.at === null ? 1 : -1;
  return kindRank(a.kind) - kindRank(b.kind) || a.seq - b.seq;
}

function kindRank(kind: ArrivalKind): number {
  return kind === "line" ? -1 : KIND_ORDER.indexOf(kind);
}
