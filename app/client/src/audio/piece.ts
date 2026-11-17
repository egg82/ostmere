// A piece of music over the player's context: one source, played once through, its gain ramped by the caller. Begun
// only when its buffer is decoded and sound is on, since silence is better than late.
import type { Piece } from "./locator";
import type { ContextLike, GainLike } from "./player";
import type { PieceName, Slot } from "./slots";

/** A piece cut off by hidden or mute carries on from where it stopped if sound returns within this long; later it is over. */
export const RESUME_MS = 30000;

export interface PieceHost {
  context(): ContextLike | null;
  master(): GainLike | null;
  buffer(name: PieceName): unknown;
  silent(): boolean;
  /** Wall-clock milliseconds: the audio clock stops while the context is suspended. */
  now(): number;
}

const OVER: Piece = { setLevel: () => undefined, stop: () => undefined, onEnd: (fn) => fn() };

export function createPieces(host: PieceHost, slots: Readonly<Record<PieceName, Slot>>): { piece: (name: PieceName) => Piece; silence: (on: boolean) => void } {
  const live = new Set<{ stop(ms: number): void }>();
  let cutAt = 0;
  return {
    piece(name) {
      try {
        const ctx = host.context(), master = host.master(), buffer = host.buffer(name);
        if (!ctx || !master || buffer === undefined || host.silent()) return OVER;
        const gain = ctx.createGain();
        gain.gain.value = 0;
        gain.connect(master);
        const src = ctx.createBufferSource();
        src.buffer = buffer;
        src.connect(gain);
        const ends: (() => void)[] = [];
        let over = false;
        const ramp = (to: number, ms: number) => {
          const g = gain.gain, t = ctx.currentTime;
          g.cancelScheduledValues(t);
          g.setValueAtTime(g.value, t);
          g.linearRampToValueAtTime(to, t + ms / 1000);
        };
        const handle = {
          setLevel(level: number, ms: number) { try { if (!over) ramp(level * slots[name].gain, ms); } catch { /* a ramp must not break its caller */ } },
          stop(ms: number) {
            if (over) return;
            try { ramp(0, ms); src.stop?.(ctx.currentTime + ms / 1000); } catch { /* already gone */ }
            finish();
          },
          onEnd(fn: () => void) { if (over) fn(); else ends.push(fn); },
        };
        function finish(): void {
          if (over) return;
          over = true;
          live.delete(handle);
          ends.splice(0).forEach((fn) => fn());
        }
        src.onended = finish;
        src.start();
        live.add(handle);
        return handle;
      } catch { /* a piece must never break what started it */ }
      return OVER;
    },
    silence(on) {
      if (on) { cutAt = host.now(); return; }
      if (host.now() - cutAt > RESUME_MS) for (const p of [...live]) p.stop(0);
    },
  };
}
