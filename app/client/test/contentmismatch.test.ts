// The content asked for alongside /open is used only when its digest is the one /open names; otherwise (a deploy between
// the calls), or when it failed, it is asked for as before, and a failed /open leaves nothing unhandled.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Content } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const unused = () => Promise.reject(new Error("not in this test"));
const none = (): void => undefined;

function apiOf(content: () => Promise<Content>, open: () => Promise<unknown>): GameApi {
  return {
    content, open, me: unused, begin: unused, savedView: unused, advance: unused, forecast: unused, decide: unused, dryRun: unused,
    putMePresentation: unused, putMeSettings: unused, putSavePresentation: unused, sendFeedback: unused, makeCode: unused, makeWords: unused, games: unused, deleteGame: unused,
    restoreGame: unused, join: unused, devices: unused, removeDevice: unused,
  } as GameApi;
}

async function resumed(content: () => Promise<Content>, open: () => Promise<unknown>) {
  const started: string[] = [];
  const lost: boolean[] = [];
  const events: SessionEvents = {
    started: (c) => { started.push(c.rules_digest); }, stepped: none, build: none, refused: none, connected: none,
    lost: (fresh) => { lost.push(fresh); }, limited: none, catchingUp: none,
  };
  await new Session(apiOf(content, open), events, undefined, () => Promise.resolve(), () => 0).resume(7);
  return { started, lost };
}

const opened = (digest: string) => () => {
  const step = { ...fixtureStep("mid", 100, {}, 0), save_id: 7, rules_digest: digest, catching_up_to: null };
  return Promise.resolve({ save, was: step.view, history: [], step });
};

// A deploy between the two calls: the content fetched alongside is the old rules', /open names the new.
let asked = 0;
const mismatch = await resumed(
  () => { asked += 1; return Promise.resolve({ ...fixtureContent, rules_digest: asked === 1 ? "old" : "new" }); },
  opened("new"),
);
check(asked === 2, `a content with another digest is asked for again: ${asked}`);
check(mismatch.started.at(-1) === "new", `the page ends drawn with the digest /open names: ${mismatch.started.join()}`);

// The content fetched alongside failed: /open's answer still draws the page, with the content asked for as before.
let tries = 0;
const failed = await resumed(
  () => { tries += 1; return tries === 1 ? Promise.reject(new ApiFailure("network", "down")) : Promise.resolve(fixtureContent); },
  opened(fixtureContent.rules_digest),
);
check(tries === 2, `a failed early content is asked for again: ${tries}`);
check(failed.started.join() === fixtureContent.rules_digest, `the page is drawn: ${failed.started.join()}`);

// /open fails while the content is still out and then fails too: neither leaves an unhandled rejection (test.mjs fails
// the run on one) and the page goes back to the front.
const lateFailure = (): Promise<Content> => new Promise((_r, rej) => { setTimeout(() => rej(new ApiFailure("network", "down")), 5); });
const gone = await resumed(lateFailure, () => Promise.reject(new ApiFailure("not_found", "no such save")));
await new Promise((r) => setTimeout(r, 30));
check(gone.lost.length === 1 && gone.started.length === 0, `a failed open goes back to the front: ${JSON.stringify(gone)}`);
