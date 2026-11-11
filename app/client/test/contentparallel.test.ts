// The content is asked for alongside /open, not after it (src/game/session.ts): a resume's two calls overlap.
import type { GameApi } from "../src/api/api";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE } from "../src/game/keeps";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const unused = () => Promise.reject(new Error("not in this test"));
const calls: string[] = [];
let answerOpen: () => void = () => undefined;
const step = { ...fixtureStep("mid", 100, {}, 0), save_id: 7, rules_digest: fixtureContent.rules_digest, catching_up_to: null };
const api: GameApi = {
  content: () => { calls.push("content"); return Promise.resolve(fixtureContent); },
  me: unused, begin: unused,
  open: () => { calls.push("open"); return new Promise((r) => { answerOpen = () => r({ save, was: step.view, history: [], presentation: NEW_SAVE, step }); }); },
  savedView: unused, advance: unused, forecast: unused, decide: unused, dryRun: unused, putMePresentation: unused, putMeSettings: unused, putSavePresentation: unused, sendFeedback: unused,
  makeCode: unused, makeWords: unused, games: unused, deleteGame: unused, restoreGame: unused, join: unused,
  devices: unused, removeDevice: unused,
};
const none = (): void => undefined;
const events: SessionEvents = {
  started: none, stepped: none, build: none, refused: none, connected: none, lost: none, limited: none, catchingUp: none,
};
const session = new Session(api, events, undefined, () => Promise.resolve(), () => 0);
const resumed = session.resume(7);
await new Promise((r) => setTimeout(r, 0));
check(calls.join() === "content,open", `content is requested before /open answers: ${calls.join()}`);
answerOpen();
await resumed;
check(calls.filter((c) => c === "content").length === 1, `one content request serves the open: ${calls.join()}`);
