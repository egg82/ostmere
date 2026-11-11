// FIXTURE, never shipped: wraps a GameApi so the first decision is answered as a long absence coming back in slices
// (Step.catching_up_to), each later advance slow, so a screenshot can catch the page mid-catch-up (#catchup).
import type { GameApi } from "../src/api/api";
import type { Step } from "../src/api/types";

const SLICES = 4;
const SPAN = 4000;   // game seconds the absence covers
const SLICE_MS = 3000;

export function catchingUpApi(inner: GameApi): GameApi {
  let from: number | null = null;
  let done = 0;
  let last: Step | null = null;
  return {
    ...inner,
    decide: async (id, d, seen) => {
      const s = await inner.decide(id, d, seen);
      if (from !== null) return s;
      from = s.view.at;
      last = s;
      return { ...s, catching_up_to: from + SPAN };
    },
    advance: async (id) => {
      if (from === null || last === null || done >= SLICES) return inner.advance(id);
      await new Promise((r) => setTimeout(r, SLICE_MS));
      done += 1;
      if (done < SLICES) return { ...last, lines: [], view: { ...last.view, at: from + (SPAN * done) / SLICES }, catching_up_to: from + SPAN };
      return inner.advance(id);
    },
  };
}
