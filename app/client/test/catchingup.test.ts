// A long absence comes back in slices (src/game/session.ts; CONTRACT.txt, "Catching up"): the page asks advance at once
// until a Step reaches now, says how far each slice got, draws the slices as one return from the view the player was
// looking at, and holds a decision until then; a decision refused as catching_up carries on and is sent once caught up.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Decision, LogLine, Step, View } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const TAP: Decision = { kind: "tap_card", card: "stand" };
const line = (at: number): LogLine => ({ at, seq: 0, key: `line.${at}`, card: null });
const slice = (at: number, to: number | null, decisions = 0): Step =>
  ({ ...fixtureStep("standing", at, {}, decisions), save_id: 7, lines: [line(at)], catching_up_to: to });
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };

/** An api whose open and advances answer `slices` in turn; decide answers `decide`. */
function harness(slices: Step[], decide: (after: number) => Step) {
  const calls: string[] = [];
  const catching: string[] = [];
  const stepped: { step: Step; prev: View; away: boolean }[] = [];
  let i = 0;
  const next = (): Step => { const s = slices[i++]; if (!s) throw new Error("no more slices"); return s; };
  const unused = () => Promise.reject(new Error("not in these tests"));
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent),
    me: unused, begin: unused,
    open: () => { calls.push("open"); return Promise.resolve({ save, was: fixtureStep("start", 40).view, history: [], presentation: NEW_SAVE, step: next() }); },
    savedView: () => Promise.reject(new Error("unused")),
    advance: () => { calls.push("advance"); return Promise.resolve(next()); },
    forecast: () => { calls.push("forecast"); return unused(); },
    decide: (_id, _d, after) => { calls.push(`decide@${after}`); try { return Promise.resolve(decide(after)); } catch (e) { return Promise.reject(e); } },
    dryRun: unused, putMePresentation: unused, putMeSettings: unused, putSavePresentation: unused, sendFeedback: unused, makeCode: unused, makeWords: unused, games: unused,
    deleteGame: unused, restoreGame: unused, join: unused, devices: unused, removeDevice: unused,
  };
  const none = (): void => undefined;
  const events: SessionEvents = {
    started: none, build: none, refused: none, connected: none, lost: none, limited: none,
    stepped(step, prev, away) { stepped.push({ step, prev, away }); },
    catchingUp(at, to) { catching.push(`${at}/${to}`); },
  };
  const session = new Session(api, events, undefined, () => Promise.resolve());
  return { calls, catching, stepped, session };
}

{  // an open that stops short asks again at once, and the return is drawn once, with every slice's lines
  const h = harness([slice(100, 1000), slice(500, 1010), slice(1010, null)], () => slice(1010, null, 1));
  const opening = h.session.resume(7);
  const deciding = h.session.decide(TAP);   // made while catching up: held, sent once caught up
  await opening;
  await deciding;
  check(h.calls.join() === "open,advance,advance,decide@0", `advances until caught up, then the decision: ${h.calls.join()}`);
  check(h.catching.join() === "100/1000,500/1010", `each short slice says how far it got: ${h.catching.join()}`);
  const ret = h.stepped[0];
  check(ret !== undefined && ret.away && ret.prev.at === 40, "the return is drawn from the view the player last saw");
  check(ret?.step.lines.map((l) => l.at).join() === "100,500,1010", `one return carries every slice's lines: ${ret?.step.lines.map((l) => l.at).join()}`);
  check(ret?.step.view.at === 1010 && ret.step.catching_up_to === null, "it lands at now");
  check(h.stepped.length === 2 && h.stepped[1]?.away === false, "then the decision's step");
}
{  // a decision refused as catching_up: the slice it carried, more advances, then the decision sent again
  let refusals = 0;
  const h = harness([slice(40, null), slice(700, 900), slice(900, null)], (after) => {
    if (refusals++ === 0) throw new ApiFailure("catching_up", "409", slice(300, 900));
    return slice(900, null, after + 1);
  });
  await h.session.resume(7);
  await h.session.decide(TAP);
  check(h.calls.join() === "open,decide@0,advance,advance,decide@0", `catches up, then sends it again: ${h.calls.join()}`);
  check(h.catching.join() === "300/900,700/900", `from the refusal's step on: ${h.catching.join()}`);
  const caught = h.stepped[1];
  check(caught?.step.lines.map((l) => l.at).join() === "300,700,900" && caught.prev.at === 40, "the refusal's lines come first, drawn from the view in hand");
  check(h.stepped.length === 3 && h.stepped[2]?.step.decisions === 1, "the decision lands once caught up");
}
