// A looping bed over the player's context: silent until `setLevel`, and begun only once its buffer is decoded.
import type { Loop } from "./locator";
import type { ContextLike, GainLike } from "./player";
import type { BedName, Slot } from "./slots";

export interface LoopHost {
  context(): ContextLike | null;
  master(): GainLike | null;
  buffer(name: BedName): unknown;
}

/** `attach` starts the source when the context and buffer are there; call it again after decoding. */
function makeLoop(host: LoopHost, slot: Slot, name: BedName): { loop: Loop; attach: () => void } {
  let want = { level: 0, ms: 0 };
  let node: GainLike | null = null;
  const apply = () => {
    const ctx = host.context();
    if (!node || !ctx) return;
    const g = node.gain;
    const t = ctx.currentTime;
    const from = g.value;
    g.cancelScheduledValues(t);
    g.setValueAtTime(from, t);
    g.linearRampToValueAtTime(want.level * slot.gain, t + want.ms / 1000);
  };
  const attach = () => {
    try {
      const ctx = host.context(), master = host.master(), buffer = host.buffer(name);
      if (node || !ctx || !master || buffer === undefined) return;
      const gain = ctx.createGain();
      gain.gain.value = 0;
      gain.connect(master);
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.loop = true;
      src.connect(gain);
      src.start();
      node = gain;
      apply();
    } catch { /* a bed must never break the tap that started it */ }
  };
  const loop: Loop = {
    setLevel(level, ms) {
      want = { level, ms };
      try { apply(); } catch { /* as above */ }
    },
  };
  return { loop, attach };
}

/** The player's loops: `loop` hands one out, `attachAll` starts those whose buffer has since been decoded. */
export function createLoops(host: LoopHost, beds: Readonly<Record<BedName, Slot>>): { loop: (name: BedName) => Loop; attachAll: () => void } {
  const attachers = new Set<() => void>();
  return {
    loop(name) {
      const made = makeLoop(host, beds[name], name);
      attachers.add(made.attach);
      made.attach();
      return made.loop;
    },
    attachAll() { for (const attach of attachers) attach(); },
  };
}
