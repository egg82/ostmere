// What each sound-map voice plays through the locator (docs/design/sound.md, "The ladder"). A ladder rung, a served
// beat line and the end name their voice as a field; nothing here reads a name or a line's words.
import { sound } from "./locator";

/** The cues an arrival batch picks from, highest first: one cue per batch. */
export const CUES = ["end", "beat", "level", "new"] as const;
export type Cue = (typeof CUES)[number];
export type Voice = Cue | "knock" | "failed" | "page" | "settle";

export function isCue(voice: Voice | null | undefined): voice is Cue {
  return voice != null && (CUES as readonly string[]).includes(voice);
}

/** The first of the highest cue among `items`; none when none has a cue. */
export function pickCue<T extends { cue?: Cue }>(items: readonly T[]): T | null {
  let best: T | null = null;
  for (const item of items) {
    if (item.cue && (best === null || CUES.indexOf(item.cue) < CUES.indexOf(best.cue!))) best = item;
  }
  return best;
}

/** The level's three notes: the First note at 1, 5/4 and 3/2, LEVEL_GAP_MS apart. */
export const LEVEL_RATIOS = [1, 5 / 4, 3 / 2] as const;
export const LEVEL_GAP_MS = 110;
/** The chain's ticks, rising; the first link is the tap's own knock, so the ticks are links 2 to 6. */
export const TICK_RATIOS = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3] as const;
/** Taps closer than this play one knock. */
export const KNOCK_GAP_MS = 100;
/** The knock's pitch steps through five small offsets, each within a third of a semitone. */
export const KNOCK_CYCLE_SEMITONES = [0, 0.2, -0.15, 0.3, -0.25] as const;

let lastKnock = -Infinity;
let knocks = 0;

/** Back to a fresh page (tests). */
export function resetCues(): void {
  lastKnock = -Infinity;
  knocks = 0;
}

/** The tap's knock, once per KNOCK_GAP_MS; its gain is the slot's, so a repeat never grows. */
function knock(nowMs: number): () => void {
  if (nowMs - lastKnock < KNOCK_GAP_MS) return () => undefined;
  lastKnock = nowMs;
  const semis = KNOCK_CYCLE_SEMITONES[knocks % KNOCK_CYCLE_SEMITONES.length]!;
  knocks += 1;
  return sound().play("tap", 2 ** (semis / 12));
}

type Listener = (voice: Voice, nowMs: number) => void;
const listeners: Listener[] = [];

/** `fn` hears every voice sung (the evening piece ducks under the story cue and the strike). Returns its removal. */
export function onSing(fn: Listener): () => void {
  listeners.push(fn);
  return () => { listeners.splice(listeners.indexOf(fn), 1); };
}

/** Plays `voice` now, or `delayMs` on. Returns the cut for what has not begun. */
export function sing(voice: Voice, delayMs = 0, nowMs = performance.now()): () => void {
  for (const fn of listeners) fn(voice, nowMs);
  switch (voice) {
    case "knock": return knock(nowMs);
    case "new": return sound().play("first", 1, delayMs);
    case "beat": return sound().play("story", 1, delayMs);
    case "end": return sound().play("strike", 1, delayMs);
    case "failed": return sound().play("failed", 1, delayMs);
    case "page": return sound().play("page", 1, delayMs);
    case "settle": return sound().play("settle", 1, delayMs);
    case "level": {
      const cuts = LEVEL_RATIOS.map((r, i) => sound().play("level", r, delayMs + i * LEVEL_GAP_MS));
      return () => { for (const cut of cuts) cut(); };
    }
  }
}

/** Link `n` (1 to 5) of a chain's ticks, `delayMs` on. */
export function tick(n: number, delayMs: number): () => void {
  return sound().play("tick", TICK_RATIOS[n - 1] ?? 1, delayMs);
}
