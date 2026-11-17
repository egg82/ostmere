// One-shot player over Web Audio. One context, made by `start()` at the first tap; every slot with an asset is
// decoded then, and a slot not decoded when its moment comes is skipped, since silence is better than late.
import { BEDS, SLOTS, type BedName, type Slot, type SlotName } from "./slots";
import type { Sound } from "./locator";
import { createLoops } from "./loop";

/** Hidden or muted: everything ramps to silence in this long, then the context suspends. */
export const CUT_MS = 50;

export interface ParamLike {
  value: number;
  cancelScheduledValues(t: number): unknown;
  setValueAtTime(v: number, t: number): unknown;
  linearRampToValueAtTime(v: number, t: number): unknown;
}
export interface NodeLike { connect(to: unknown): unknown }
export interface GainLike extends NodeLike { gain: ParamLike }
export interface SourceLike extends NodeLike {
  buffer: unknown;
  loop: boolean;
  playbackRate: { value: number };
  start(when?: number): void;
}
export interface ContextLike {
  currentTime: number;
  destination: unknown;
  createGain(): GainLike;
  createBufferSource(): SourceLike;
  decodeAudioData(bytes: ArrayBuffer): Promise<unknown>;
  resume(): Promise<void>;
  suspend(): Promise<void>;
}

export interface PlayerDeps {
  /** Makes the page's one context with the interactive latency hint. */
  makeContext: () => ContextLike;
  /** The bytes of an asset path; a rejection skips that slot. */
  fetchBytes: (path: string) => Promise<ArrayBuffer>;
  /** Runs `fn` after `ms`; the suspend that follows the ramp. */
  after?: (fn: () => void, ms: number) => void;
  slots?: Readonly<Record<SlotName, Slot>>;
  beds?: Readonly<Record<BedName, Slot>>;
}

export interface Player extends Sound {
  /** Make the context and decode the slots, at the page's first tap. Safe to call again. */
  start(): Promise<void>;
  /** Silent (hidden or muted) cuts in CUT_MS and suspends; false resumes. Waiting sounds are dropped, none replayed. */
  setSilent(silent: boolean): void;
}

/** Decodes every entry with an asset into `buffers`; one that fails to load or decode is skipped. */
async function decodeAll(c: ContextLike, entries: [SlotName | BedName, Slot][], fetchBytes: PlayerDeps["fetchBytes"], buffers: Map<SlotName | BedName, unknown>): Promise<void> {
  for (const [name, slot] of entries) {
    if (slot.asset === null) continue;
    try { buffers.set(name, await c.decodeAudioData(await fetchBytes(slot.asset))); } catch { /* skipped */ }
  }
}

export function createPlayer(deps: PlayerDeps): Player {
  const slots = deps.slots ?? SLOTS;
  const after = deps.after ?? ((fn, ms) => { setTimeout(fn, ms); });
  const beds = deps.beds ?? BEDS;
  const buffers = new Map<SlotName | BedName, unknown>();
  let ctx: ContextLike | null = null;
  let master: GainLike | null = null;
  let silent = false;
  let starting: Promise<void> | null = null;
  let cuts = 0;

  const loops = createLoops({ context: () => ctx, master: () => master, buffer: (name) => buffers.get(name) }, beds);

  function ramp(to: number): void {
    if (!ctx || !master) return;
    const g = master.gain;
    const t = ctx.currentTime;
    g.cancelScheduledValues(t);
    g.setValueAtTime(g.value, t);
    g.linearRampToValueAtTime(to, t + CUT_MS / 1000);
  }

  return {
    start() {
      starting ??= (async () => {
        const c = deps.makeContext();
        ctx = c;
        master = c.createGain();
        master.connect(c.destination);
        if (silent) master.gain.value = 0;
        await decodeAll(c, [...Object.entries(slots), ...Object.entries(beds)] as [SlotName | BedName, Slot][], deps.fetchBytes, buffers);
        loops.attachAll();
      })();
      return starting;
    },
    setSilent(next) {
      if (next === silent) return;
      silent = next;
      const mine = ++cuts;
      if (!ctx) return;
      if (next) {
        ramp(0);
        after(() => { if (mine === cuts) void ctx?.suspend(); }, CUT_MS);
      } else {
        void ctx.resume();
        ramp(1);
      }
    },
    loop: loops.loop,
    play(name, pitch = 1, delayMs = 0) {
      try {
        const buffer = buffers.get(name);
        if (silent || !ctx || !master || buffer === undefined) return () => undefined;
        const slot = slots[name];
        const gain = ctx.createGain();
        gain.gain.value = slot.gain;
        gain.connect(master);
        const src = ctx.createBufferSource();
        src.buffer = buffer;
        src.playbackRate.value = slot.pitch * pitch;
        src.connect(gain);
        src.start(ctx.currentTime + delayMs / 1000);
        const c = ctx;
        return () => {
          try {
            gain.gain.cancelScheduledValues(c.currentTime);
            gain.gain.setValueAtTime(gain.gain.value, c.currentTime);
            gain.gain.linearRampToValueAtTime(0, c.currentTime + CUT_MS / 1000);
          } catch { /* already gone */ }
        };
      } catch { /* a sound must never break the tap that asked for it */ }
      return () => undefined;
    },
  };
}
