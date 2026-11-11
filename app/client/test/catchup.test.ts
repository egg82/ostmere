// A long absence comes back in slices (src/game/session.ts; CONTRACT.txt, Step.catching_up_to): a Step still catching up
// is announced with catchingUp(at, to) and asked past at once, never drawn; once one arrives that is not, exactly one
// stepped() follows with every slice's lines. A decision made meanwhile is held and sent after, a catching_up 409 on a
// decision goes on catching up, and no forecast is asked on the way. Written from the contract; the api is scripted.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Decision, Step, View } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE, NEW_ACCOUNT, NEW_SETTINGS } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const TAP: Decision = { kind: "tap_card", card: "stand" };
const save = (decisions = 0) => ({ save_id: 7, number: 1, decisions, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 });

/** A Step at game time `at`, bringing lines `keys`, still catching up to `to` (null: caught up). */
function slice(at: number, to: number | null, keys: string[], decisions = 0): Step {
  const base = fixtureStep("standing", at, {}, decisions);
  const lines = keys.map((key, seq) => ({ at, seq, key, card: null }));
  const extra: { catching_up_to: number | null } = { catching_up_to: to };
  return Object.assign({}, base, { lines, save_id: 7 }, extra);
}

interface Landed { keys: string[]; prevAt: number; away: boolean; at: number; decisions: number }
interface Log {
  calls: string[]; afters: number[]; catching: string[]; stepped: Landed[]; refused: (Decision | null)[]; waits: number[];
}

/** Scripted answers: `open` gives the first Step, each `advance` and `decide` the next of its list (an ApiFailure is
 * thrown). `gate`, while set, holds every advance until it is released. */
function harness(script: { open?: Step; advances?: Step[]; decides?: (Step | ApiFailure)[]; begin?: Step; gated?: boolean }) {
  const log: Log = { calls: [], afters: [], catching: [], stepped: [], refused: [], waits: [] };
  let release: () => void = () => undefined;
  let gate: Promise<void> | null = script.gated ? new Promise<void>((r) => { release = r; }) : null;
  const hooks: { between: (() => void) | null } = { between: null };
  const advances = [...(script.advances ?? [])];
  const decides = [...(script.decides ?? [])];
  const next = (list: Step[], call: string): Step => {
    const step = list.shift();
    if (!step) throw new Error(`${call} asked more often than the script allows: ${log.calls.join()}`);
    return step;
  };
  const api: GameApi = {
    content: () => { log.calls.push("content"); return Promise.resolve(fixtureContent); },
    me: () => Promise.reject(new Error("not in these tests")),
    begin: () => { log.calls.push("begin"); return Promise.resolve({ save: save(), presentation: NEW_SAVE, step: script.begin ?? slice(0, null, []) }); },
    open: () => {
      log.calls.push("open");
      return Promise.resolve({ save: save(), was: fixtureStep("start", 40).view, history: [], presentation: NEW_SAVE, step: script.open ?? slice(100, null, []) });
    },
    savedView: () => Promise.reject(new Error("unused")),
    advance: async () => {
      log.calls.push("advance");
      if (gate) await gate;
      return next(advances, "advance");
    },
    forecast: () => {
      log.calls.push("forecast");
      return Promise.resolve({ decisions: 0, forecast: { horizon_at: 100, level_ups: [], tops_out: [], fills: [], empties: [] } });
    },
    decide: (_id, _d, after) => {
      log.calls.push("decide");
      log.afters.push(after);
      const answer = decides.shift();
      if (!answer) throw new Error("decide asked more often than the script allows");
      return answer instanceof ApiFailure ? Promise.reject(answer) : Promise.resolve(answer);
    },
    dryRun: () => Promise.reject(new Error("not in these tests")),
    putMePresentation: (p) => Promise.resolve({ presentation: p, settings: NEW_SETTINGS, has_words: false, words_due: false }),
    putMeSettings: (settings) => Promise.resolve({ presentation: NEW_ACCOUNT, settings, has_words: false, words_due: false }),
    putSavePresentation: (_id, p) => Promise.resolve(p),
    sendFeedback: () => Promise.resolve(),
    makeCode: () => Promise.reject(new Error("not in these tests")),
    makeWords: () => Promise.reject(new Error("not in these tests")),
    games: () => Promise.reject(new Error("not in these tests")),
    deleteGame: () => Promise.reject(new Error("not in these tests")),
    restoreGame: () => Promise.reject(new Error("not in these tests")),
    devices: () => Promise.reject(new Error("not in these tests")),
    removeDevice: () => Promise.reject(new Error("not in these tests")),
    join: () => Promise.reject(new Error("not in these tests")),
  };
  const events: SessionEvents = {
    started() { /* the page's */ },
    stepped(step: Step, prev: View, away: boolean) {
      log.stepped.push({ keys: step.lines.map((l) => l.key), prevAt: prev.at, away, at: step.view.at, decisions: step.decisions });
    },
    catchingUp(at: number, to: number) { log.catching.push(`${at}>${to}`); hooks.between?.(); },
    build() { /* the self-update's */ },
    refused(d) { log.refused.push(d); },
    connected() { /* the banner's */ },
    lost() { /* the front page */ },
    limited() { /* the front page */ },
  };
  let clockMs = 0;
  const session = new Session(api, events, undefined, (ms) => { log.waits.push(ms); return Promise.resolve(); },
    () => { clockMs += 1_000_000; return clockMs; });   // always long since the last ask and decision
  return { log, session, hooks, open: () => { gate = null; release(); } };
}

/** Until the session has asked nothing new for a few turns. */
async function quiet(h: ReturnType<typeof harness>): Promise<void> {
  for (let stable = 0; stable < 3;) {
    const n = h.log.calls.length;
    await h.session.settled();
    for (let i = 0; i < 5; i += 1) await Promise.resolve();
    stable = h.log.calls.length === n ? stable + 1 : 0;
  }
}

async function until(what: string, done: () => boolean): Promise<void> {
  for (let i = 0; i < 200 && !done(); i += 1) await new Promise((r) => setTimeout(r, 0));
  check(done(), `never reached: ${what}`);
}

const ONE_SLICE_LATE = [slice(2000, 3600, ["b1"]), slice(3600, null, ["c1", "c2"])];

{  // an open that is behind: each slice announced and asked past at once, one stepped with every line, a return
  const h = harness({ open: slice(1000, 3600, ["a1", "a2"]), advances: [...ONE_SLICE_LATE] });
  await h.session.resume(7);
  await quiet(h);
  check(h.log.calls.filter((c) => c === "advance").length === 2, `a slice is asked past at once, to the end: ${h.log.calls.join()}`);
  check(h.log.catching.join() === "1000>3600,2000>3600", `each slice before the last is announced with where it got and where it heads: ${h.log.catching.join()}`);
  check(h.log.stepped.length === 1, `one stepped for the whole catch-up, none per slice: ${h.log.stepped.length}`);
  const [landed] = h.log.stepped;
  check(landed?.keys.join() === "a1,a2,b1,c1,c2", `every slice's lines, in order: ${landed?.keys.join()}`);
  check(landed?.at === 3600 && landed.prevAt === 40 && landed.away, `it lands at the end, from the view the player was last shown, as a return: ${JSON.stringify(landed)}`);
  check(h.session.view?.at === 3600 && h.log.waits.length === 0, "the view is the last slice's, and nothing waited between slices");
}
{  // not behind: no announcement, one stepped as ever
  const h = harness({ open: slice(100, null, ["a1"]) });
  await h.session.resume(7);
  await quiet(h);
  check(h.log.catching.length === 0 && h.log.stepped.length === 1 && h.log.stepped[0]?.keys.join() === "a1", "a caught-up open is the ordinary one");
  check(h.log.calls.join() === "content,open", `and asks nothing more: ${h.log.calls.join()}`);
}
{  // an advance (the clock passing, the page shown again) that is behind: the same, away only when the page was hidden
  for (const away of [false, true]) {
    const h = harness({ advances: [slice(500, 1000, ["a"]), slice(800, 1000, ["b"]), slice(1000, null, ["c"])] });
    await h.session.begin();
    await h.session.advance(away);
    await quiet(h);
    check(h.log.catching.join() === "500>1000,800>1000", `announced: ${h.log.catching.join()}`);
    check(h.log.stepped.length === 1 && h.log.stepped[0]?.keys.join() === "a,b,c", `one stepped, all lines: ${JSON.stringify(h.log.stepped)}`);
    check(h.log.stepped[0]?.away === away && h.log.stepped[0].prevAt === 0, `away is ${away}, prev is the view before the catch-up`);
  }
}
{  // a decision made while a slice is in flight is held, and sent once, after the catch-up, with its count
  const h = harness({ open: slice(1000, 3600, ["a1"]), advances: [...ONE_SLICE_LATE], decides: [slice(3700, null, ["d1"], 1)], gated: true });
  const opening = h.session.resume(7);
  await until("the first slice asked past", () => h.log.calls.includes("advance"));
  const decided = h.session.decide(TAP);
  h.open();
  await Promise.all([opening, decided]);
  await quiet(h);
  const last = h.log.calls.lastIndexOf("advance");
  check(h.log.calls.filter((c) => c === "decide").length === 1, `the decision is sent, once: ${h.log.calls.join()}`);
  check(h.log.calls.indexOf("decide") > last, `and only after the catch-up: ${h.log.calls.join()}`);
  check(h.log.afters.join() === "0" && h.log.refused.length === 0, "with the count of the save it caught up to");
  check(h.log.stepped.length === 2 && h.log.stepped[0]?.keys.join() === "a1,b1,c1,c2" && h.log.stepped[1]?.keys.join() === "d1",
    `the catch-up lands whole, then the decision: ${JSON.stringify(h.log.stepped)}`);
}
{  // the same when it is made between two slices, as the page announces one
  const h = harness({ open: slice(1000, 3600, ["a1"]), advances: [...ONE_SLICE_LATE], decides: [slice(3700, null, ["d1"], 1)] });
  let made: Promise<void> | null = null;
  h.hooks.between = () => { made ??= h.session.decide(TAP); };
  await h.session.resume(7);
  await quiet(h);
  check(made !== null, "the decision was made between slices");
  check(h.log.calls.filter((c) => c === "decide").length === 1 && h.log.calls.indexOf("decide") > h.log.calls.lastIndexOf("advance"),
    `held until caught up, then sent once: ${h.log.calls.join()}`);
  check(h.log.stepped.length === 2 && h.log.stepped[1]?.keys.join() === "d1", "and its answer drawn");
}
{  // a decision the server turned away as catching up: not refused, and the catch-up goes on from the step it brings
  const refusal = new ApiFailure("catching_up", "409", slice(2000, 3600, ["x1"]));
  const h = harness({ begin: slice(0, null, []), decides: [refusal, slice(3700, null, ["d1"], 1)], advances: [slice(3600, null, ["y1"])] });
  await h.session.begin();
  await h.session.decide(TAP);
  await quiet(h);
  check(h.log.refused.length === 0, "a decision met by a catch-up is not a refused one");
  check(h.log.catching.join() === "2000>3600", `the step the 409 brought is announced: ${h.log.catching.join()}`);
  const first = h.log.stepped[0];
  check(first?.keys.join() === "x1,y1" && first.at === 3600 && first.prevAt === 0 && !first.away,
    `it lands whole, from the view before: ${JSON.stringify(h.log.stepped)}`);
  check(h.log.stepped.filter((s) => s.keys.includes("x1")).length === 1, "once");
}
{  // no forecast asked on the way, though one is due; asked once caught up
  const h = harness({ open: slice(1000, 3600, ["a1"]), advances: [...ONE_SLICE_LATE], gated: true });
  h.hooks.between = () => h.session.tick();
  const opening = h.session.resume(7);
  await until("the first slice asked past", () => h.log.calls.includes("advance"));
  h.session.tick();
  h.open();
  await opening;
  await quiet(h);
  check(!h.log.calls.includes("forecast"), `no forecast while catching up: ${h.log.calls.join()}`);
  check(h.log.stepped.length === 1, "and so no extra stepped");
  h.session.tick();
  await quiet(h);
  check(h.log.calls.includes("forecast"), "the forecast was due all along: it is asked once the save has caught up");
}
