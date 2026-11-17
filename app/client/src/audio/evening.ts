// The evening piece (docs/design/sound.md, "Music: the evening piece"): when a layer the manifest marks as the evening's
// begins to show while the page is in view, one piece plays once through and ends. Driven by the scene's explicit
// `sound` field and by cue events, never by a layer's name or a line's words.
import { GRADE_S } from "../scene/manifest";
import { sound, type Piece } from "./locator";
import type { Cue } from "./cues";

export const ENTRY_AFTER_END_MS = 4000;   // the opening's strike is over by then
export const DUCK_DB = -9;
export const DUCK_MS = 200;
export const DUCK_BACK_MS = 2500;
/** How long each cue holds the piece down: its own length at most (the story cue 2.5 s, the strike 4 s). */
export const DUCK_HOLD_MS: Partial<Record<Cue, number>> = { beat: 2500, end: 4000 };
const DUCKED = 10 ** (DUCK_DB / 20);

/** What the scene shows of the evening's layer this frame. */
export interface EveningFrame {
  /** The layer that sounds as the evening's is wanted now (its `when` holds and its `until` does not). */
  shown: boolean;
  /** The grade in force and the seconds it takes to move into. */
  grade: string;
  easeS: number;
}

export interface Evening {
  /** One frame while the page is in view, at `nowMs`. */
  frame(f: EveningFrame, nowMs: number): void;
  /** A cue was sung at `nowMs`. */
  cue(voice: string, nowMs: number): void;
  /** The page was hidden: what waits is dropped, and the next frame only resets what it saw. */
  away(): void;
}

export function createEvening(): Evening {
  let prev: boolean | null = null;   // null: nothing seen yet since the page came into view
  let armed: { grade: string; entryAt: number } | null = null;
  let piece: Piece | null = null;
  let grade = "";
  let endAt = -Infinity;
  let duckUntil = -Infinity;
  let ducked = false;

  const drop = () => { armed = null; piece = null; ducked = false; duckUntil = -Infinity; };
  const leave = (easeS: number) => {
    armed = null;
    if (!piece) return;
    const p = piece;
    piece = null;
    p.stop(easeS * 1000);
  };

  function begin(): void {
    const p = sound().piece("evening");
    p.onEnd(() => { if (piece === p) drop(); });
    p.setLevel(0, 0);
    p.setLevel(1, GRADE_S * 1000);
    piece = p;
    grade = armed!.grade;
    armed = null;
  }

  return {
    frame(f, now) {
      const rose = f.shown && prev === false;
      prev = f.shown;
      if (rose) {
        armed = { grade: f.grade, entryAt: now - endAt < ENTRY_AFTER_END_MS ? endAt + ENTRY_AFTER_END_MS : now };
        grade = f.grade;
      }
      if ((armed || piece) && f.grade !== grade) { leave(f.easeS); return; }
      if (armed && now >= armed.entryAt) begin();
      if (piece && ducked && now >= duckUntil) { ducked = false; piece.setLevel(1, DUCK_BACK_MS); }
    },
    cue(voice, now) {
      if (voice === "end") {
        endAt = now;
        if (armed) armed.entryAt = now + ENTRY_AFTER_END_MS;
      }
      const hold = DUCK_HOLD_MS[voice as Cue];
      if (!piece || hold === undefined) return;
      duckUntil = Math.max(duckUntil, now + hold);
      if (!ducked) { ducked = true; piece.setLevel(DUCKED, DUCK_MS); }
    },
    away() {
      prev = null;
      armed = null;
    },
  };
}
