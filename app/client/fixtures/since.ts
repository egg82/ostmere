// FIXTURE, never shipped: a return after time away, for screenshots of the chronicle's "Since you left" chapter. Each
// phase opens on the camp as the player left it (rulestab's rules and mixes, still stores, an earlier visit and its
// lines); the page shown again (dev-main's #back) lands on its `back` phase, that long later. sincelong brings every
// section (stores up and down, two skills and the Camp up, two rules run, a find, a level, an ask); sinceshort one store
// and one line; sincenone nothing at all; sincejoin one store, a line and a person's joining; sincemention the same with
// the day's mention of two people in place of the joining (the people section, CONTRACT.txt, "PEOPLE").
import type { Content, LedgerLine, LogLine, RuleRun, Step, View, Visit } from "../src/api/types";
import { Q } from "./content";
import { fixtureStep, type Kept } from "./steps";

const AWAY = { sincelong: 54 * 60, sinceshort: 40 * 60, sincenone: 35 * 60, sincejoin: 3 * 3600, sincemention: 5 * 3600 } as const;
type Away = keyof typeof AWAY;
export type SincePhase = Away | `${Away}back`;
export const isSince = (phase: string): phase is SincePhase => phase.startsWith("since") && (phase.replace(/back$/, "") in AWAY);
const away = (phase: SincePhase): Away => phase.replace(/back$/, "") as Away;
/** The phase the page lands on when it is shown again after `phase`. */
export const sinceBack = (phase: SincePhase): SincePhase | null => (phase.endsWith("back") ? null : `${away(phase)}back`);

/** An earlier return, before Begin, so the chronicle has an older stretch under the chapter. */
export const SINCE_VISITS: Visit[] = [{ left: -9000, back: -5400 }];

/** Camp levels at 50, 200 and 600, the last held: the long return crosses the second. */
export function withSince(content: Content): Partial<Content> {
  const camp = content.camp;
  if (!camp) return {};
  const [first, second] = camp.camp_levels;
  if (!first || !second) return {};
  return { camp: { ...camp, camp_levels: [first, { ...second, held: false }, { ...second, at: 600 * Q, held: true }] } };
}

const still = (line: LedgerLine, items: number): LedgerLine => ({
  ...line, segment: { start: 0, start_value: items * Q, rate: 0, limit: null }, net_per_hour: 0, falling: false,
  empties_at: null, fills_at: null,
});

const BEFORE: Record<string, number> = { wood: 14, warmth: 38, stone: 3, camp: 60 };
const AFTER: Record<Away, Record<string, number>> = {
  sincelong: { wood: 340, warmth: 12, stone: 25, camp: 230 },
  sinceshort: { wood: 52, warmth: 38, stone: 3, camp: 60 },
  sincenone: BEFORE,
  sincejoin: { wood: 52, warmth: 38, stone: 3, camp: 60 },
  sincemention: { wood: 52, warmth: 38, stone: 3, camp: 60 },
};

function lines(...at: Array<[string, number]>): LogLine[] {
  return at.map(([key, t], seq) => ({ at: t, seq, key, card: null }));
}

function viewAt(base: View, at: number, stores: Record<string, number>, levels: [number, number], ask: boolean): View {
  return {
    ...base, at, next_event_at: null,
    ledger: base.ledger.map((l) => still(l, stores[l.store] ?? 0)),
    skills: base.skills.map((s, i) => ({ ...s, level: levels[i] ?? s.level, next_level_at: null, xp: { ...s.xp, rate: 0 } })),
    offers: ask ? [{ offer: "ask", answer: null, answers: [{ answer: "wait", card: null, takes_s: null }, { answer: "go", card: "haul", takes_s: 750 }] }] : [],
  };
}

/** rulestab's wood and tired rules: `starts` and the last run of each as `at` sees them. */
function runs(view: View, left: number, back: number | null): RuleRun[] {
  const [wood, , tired] = view.orders;
  if (!wood || !tired) return [];
  const woodRun: RuleRun = { order: wood, starts: 3, on_at: left - 3 * 3600, on_level: 2 * Q, off_at: left - 2 * 3600, off_level: 20 * Q, ended: null, made: [] };
  const tiredRun: RuleRun = { order: tired, starts: 1, on_at: left - 4 * 3600, on_level: null, off_at: left - 3 * 3600, off_level: null, ended: null, made: [] };
  if (back === null) return [woodRun, tiredRun];
  return [{ ...woodRun, starts: 5, on_at: back - 1500, on_level: 9 * Q, off_at: back - 900, off_level: 20 * Q },
    { ...tiredRun, starts: 2, on_at: back - 600, off_at: null, off_level: null }];
}

/** `at`: the fixture's game second (wall seconds since Begin); a `back` phase is drawn AWAY seconds after it. */
export function sinceStep(phase: SincePhase, at: number, kept: Kept = {}, decisions = 0): Step {
  const base = fixtureStep("rulestab", at, kept, decisions);
  const which = away(phase);
  if (sinceBack(phase) !== null) {
    const earlier = lines(["line.3", -12000], ["line.4", -11000], ["line.5", -5000], ["line.6", -4000]);
    return { ...base, view: viewAt(base.view, at, BEFORE, [2, 1], false), lines: earlier, rule_runs: runs(base.view, at, null) };
  }
  const back = at + AWAY[which];
  const left = back - AWAY[which];
  const long = which === "sincelong";
  const said = long ? lines(["line.1", left + 600], ["line.6", left + 1200], ["line.7", left + 1800], ["line.offer", back - 300], ["line.2", back - 100])
    : which === "sinceshort" ? lines(["line.4", back - 200])
    : which === "sincejoin" ? lines(["line.4", back - 2000], ["line.joins", back - 200])
    : which === "sincemention" ? lines(["line.4", back - 4000], ["people.joined.mason", back - 3000], ["people.joined.helper", back - 3000]) : [];
  return {
    ...base, view: viewAt(base.view, back, AFTER[which], long ? [4, 2] : [2, 1], long), lines: said,
    rule_runs: long ? runs(base.view, left, back) : runs(base.view, left, null),
  };
}
