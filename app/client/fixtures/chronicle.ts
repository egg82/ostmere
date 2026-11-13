// FIXTURE, never shipped: a chronicle with every kind the fixture content has, each line's cause served, two stretches
// (a return an hour after leaving) and rulestab's rule runs, for screenshots of the chronicle and its filters.
import type { LogLine, Step, Visit } from "../src/api/types";
import { fixtureStep, type Kept } from "./steps";

export type ChroniclePhase = "chronicle";
export const isChronicle = (phase: string): phase is ChroniclePhase => phase === "chronicle";

/** The return the chronicle splits at, in game seconds before Begin. */
export const CHRONICLE_VISITS: Visit[] = [{ left: -5400, back: -1800 }];

const LINES: Array<[string, number]> = [
  ["line.1", -9000], ["line.3", -8000], ["line.6", -7000], ["line.2", -6000],
  ["line.7", -1500], ["line.offer", -1200], ["line.4", -600], ["line.5", -60],
];

export function chronicleStep(at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("rulestab", at, kept, decisions);
  const lines: LogLine[] = LINES.map(([key, t], seq) => ({ at: t, seq, key, card: null }));
  return { ...base, lines };
}
