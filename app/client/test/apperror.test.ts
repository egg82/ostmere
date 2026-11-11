// A request the app itself answered with a 5xx (X-Ashfall-Server: app, a body that is not an ApiError) is asked again a
// bounded number of times and then refused, so one that fails every time does not freeze the save's queue behind
// "reconnecting"; a 5xx the app did not answer (a gateway's, no header) and a request that got no answer are asked again
// without bound, because a deploy or a pod restart must recover (api/CONTRACT.txt, "THE CLIENT MAY").
import { httpApi, type GameApi } from "../src/api/api";
import type { Decision, NewSave, Step } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session } from "../src/game/session";
import { NEW_SAVE } from "../src/game/keeps";

const TAP: Decision = { kind: "tap_card", card: "stand" };
const APP_RETRIES = 3;
const MANY = 10;
const step = (decisions: number): Step => ({ ...fixtureStep("standing", 100, {}, decisions), save_id: 7, rules_digest: fixtureContent.rules_digest });
const save = { save_id: 7, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 };
const none = (): Promise<never> => Promise.reject(new Error("not in this test"));
const api: GameApi = {
  content: () => Promise.resolve(fixtureContent), me: none, begin: () => Promise.resolve<NewSave>({ save, presentation: NEW_SAVE, step: { ...step(0), lines: [] } }),
  open: none, savedView: none, advance: httpApi.advance, forecast: none, decide: httpApi.decide, dryRun: none, putMePresentation: none, putMeSettings: none, putSavePresentation: none, sendFeedback: none,
  makeCode: none, makeWords: none, join: none, games: none, deleteGame: none, restoreGame: none,
  devices: none, removeDevice: none,
};

type Answer = (n: number) => Response | Promise<Response>;
const text = (status: number, headers: Record<string, string> = {}): Response => new Response("Internal Server Error", { status, headers });
const ok = (): Response => Response.json(step(1));
const gone = (): Response => Response.json({ code: "not_found", message: "no such save" }, { status: 404 });

/** A session on the real request code, the decisions route answering as `answer` says (its n-th request), and what it did. */
async function play(answer: Answer, decisions = 1) {
  let sent = 0;
  globalThis.fetch = ((url: string) => {
    if (!String(url).endsWith("/decisions")) return Promise.resolve(new Response(null, { status: 204 }));   // the error report
    sent += 1;
    return Promise.resolve(answer(sent));
  }) as typeof fetch;
  const seen = { refused: 0, lost: 0, stepped: 0, connected: [] as boolean[], waits: 0 };
  const session = new Session(api, {
    started() { /* drawn */ }, stepped() { seen.stepped += 1; }, build() { /* self-update */ }, refused() { seen.refused += 1; },
    connected(up) { seen.connected.push(up); }, lost() { seen.lost += 1; }, limited() { /* 429 */ }, catchingUp() { /* slices */ },
  }, undefined, () => { seen.waits += 1; return Promise.resolve(); });
  await session.begin();
  for (let i = 0; i < decisions; i++) await session.decide(TAP);
  return { seen, sent: () => sent };
}

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

{  // the app's own 5xx on every try: asked again APP_RETRIES times, then refused; the next decision is not held up
  const app = { "X-Ashfall-Server": "app" };
  const run = await play((n) => (n <= MANY ? text(500, app) : gone()));
  check(run.sent() === APP_RETRIES + 1 && run.seen.waits === APP_RETRIES, `asked ${run.sent()} times, waited ${run.seen.waits}: want ${APP_RETRIES + 1} and ${APP_RETRIES}`);
  check(run.seen.refused === 1 && run.seen.lost === 0, `refused ${run.seen.refused}, lost ${run.seen.lost}`);
  const after = await play((n) => (n <= APP_RETRIES + 1 ? text(500, app) : ok()), 2);
  check(after.seen.stepped === 1 && after.seen.refused === 1, "a decision after a refused one is answered");
}
{  // a 5xx without the app's header (a gateway) and no answer at all keep the unbounded backoff
  const gateway = await play((n) => (n <= MANY ? text(502) : ok()));
  check(gateway.sent() === MANY + 1 && gateway.seen.refused === 0 && gateway.seen.stepped === 1, "a gateway's 5xx is asked again until answered");
  check(gateway.seen.connected.join() === "false,true", `reconnecting shown then cleared: ${gateway.seen.connected.join()}`);
  const silent = await play((n) => (n <= MANY ? Promise.reject(new TypeError("fetch failed")) : ok()));
  check(silent.sent() === MANY + 1 && silent.seen.refused === 0 && silent.seen.stepped === 1, "no answer is asked again until answered");
}
