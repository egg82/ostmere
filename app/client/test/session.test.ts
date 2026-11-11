// The page's side of a save the server holds (src/game/session.ts): Begin and open, decisions sent with the count the
// page last saw, another page's decision (409) drawn at once, a server away (503, no answer) asked again with backoff
// while the page shows it is reconnecting, a deploy redrawing the game, and what the page keeps sent to the server.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { Content, Decision, Step, View } from "../src/api/types";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { Session, type SessionEvents } from "../src/game/session";
import { NEW_SAVE, NEW_SETTINGS } from "../src/game/keeps";
import type { Past } from "../src/game/loggroups";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const TAP: Decision = { kind: "tap_card", card: "stand" };
const save = (decisions = 0) => ({ save_id: 7, number: 1, decisions, game_time: 0, ended_at: null, started_at: "2026-10-17T09:00:00Z", played_at: "2026-10-17T09:00:00Z", camp_level: 0 });

interface Log {
  calls: string[]; afters: number[]; started: (Past[] | null)[]; stepped: boolean[]; refused: (Decision | null)[];
  connected: boolean[]; lost: number; lostFresh: boolean[]; limited: number; waits: number[]; puts: string[]; feedback: string[];
}

/** An api whose answers can be scripted per call: `fail` is consulted before each call and may throw. */
function harness(content: Content = fixtureContent, fail: (call: string, n: number) => ApiFailure | null = () => null) {
  const log: Log = { calls: [], afters: [], started: [], stepped: [], refused: [], connected: [], lost: 0, lostFresh: [], limited: 0, waits: [], puts: [], feedback: [] };
  let decisions = 0;
  const rules = { digest: content.rules_digest };   // a deploy changes it
  const step = (at: number): Step => ({ ...fixtureStep("standing", at, {}, decisions), save_id: 7, rules_digest: rules.digest });
  const answer = <T>(call: string, value: () => T): Promise<T> => {
    log.calls.push(call);
    const e = fail(call, log.calls.filter((c) => c === call).length);
    return e ? Promise.reject(e) : Promise.resolve(value());
  };
  const api: GameApi = {
    content: () => answer("content", () => ({ ...content, rules_digest: rules.digest })),
    me: () => answer("me", () => ({ account: null, saves: [], max_saves: 5, kept_days: 30 })),
    begin: () => answer("begin", () => ({ save: save(), presentation: NEW_SAVE, step: { ...step(0), lines: [] } })),
    open: (id) => answer("open", () => ({ save: save(3), was: fixtureStep("start", 40).view, history: [{ n: 0, at: 0, key: "line.1" }], presentation: NEW_SAVE, step: { ...step(100), save_id: id } })),
    savedView: () => Promise.reject(new Error("unused")),
    advance: () => answer("advance", () => step(100)),
    forecast: () => answer("forecast", () => ({ decisions, forecast: { horizon_at: 100 + 6 * 3600, level_ups: [], tops_out: [], fills: [], empties: [] } })),
    decide: (_id, _d, after) => answer("decide", () => { log.afters.push(after); decisions += 1; return step(100); }),
    dryRun: (_id, ds) => answer("dryRun", () => ({ ...fixtureStep("mid", 100).view, mixes: ds.length === 2 ? [] : fixtureStep("mid", 100).view.mixes })),
    putMePresentation: (p) => { log.puts.push(`me ${JSON.stringify(p)}`); return Promise.resolve({ presentation: p, settings: NEW_SETTINGS, has_words: false, words_due: false }); },
    putMeSettings: () => Promise.reject(new Error("not in these tests")),
    putSavePresentation: (id, p) => { log.puts.push(`save ${id} ${JSON.stringify(p)}`); return Promise.resolve(p); },
    sendFeedback: (text, id) => answer("feedback", () => { log.feedback.push(`${id}: ${text}`); }),
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
    started(_c, _s, keeps, history) { log.started.push(history); held.keeps = keeps; },
    stepped(_step, _prev, away) { log.stepped.push(away); },
    build() { /* the self-update's */ },
    refused(d) { log.refused.push(d); },
    connected(ok) { log.connected.push(ok); },
    lost(fresh) { log.lost += 1; log.lostFresh.push(fresh); },
    limited() { log.limited += 1; },
    catchingUp() { /* catchingup.test.ts */ },
  };
  const held: { keeps: Parameters<SessionEvents["started"]>[2] | null } = { keeps: null };
  const session = new Session(api, events, undefined, (ms) => { log.waits.push(ms); return Promise.resolve(); });
  return { log, session, held, rules };
}

{  // Begin: one new save, a story that starts empty
  const h = harness();
  await h.session.begin();
  check(h.log.calls.join() === "content,begin", `begin asks for a save with the content alongside: ${h.log.calls.join()}`);
  check(h.log.started.length === 1 && h.log.started[0]?.length === 0, "a new game starts its story empty");
}
{  // open: the save as last seen (its last lines restored), then the time away as a return
  const h = harness();
  await h.session.resume(7);
  check(h.log.calls.slice(0, 2).join() === "content,open" && h.log.started[0]?.map((p) => p.key).join() === "line.1", "an open restores the save's last lines");
  check(h.log.stepped.join() === "true", "what arrived while away comes as a return");
  check(h.session.view?.at === 100 && Math.floor(h.session.clock.now()) === 100, "the clock runs from the server's time");
}
{  // decisions carry the count the page last saw; advances carry none
  const h = harness();
  await h.session.begin();
  await h.session.decide(TAP);
  await h.session.decide(TAP);
  await h.session.advance();
  check(h.log.afters.join() === "0,1", `each decision is sent after the last one seen: ${h.log.afters.join()}`);
  check(h.log.stepped.join() === "false,false,false", "live steps are not returns");
  await h.session.advance(true);
  check(h.log.stepped.at(-1) === true, "the page shown again is a return");
}
{  // another page decided first: the 409's step is drawn at once and nothing is refused
  const theirs = { ...fixtureStep("mid", 300, {}, 4), rules_digest: fixtureContent.rules_digest };
  const h = harness(fixtureContent, (call) => (call === "decide" ? new ApiFailure("stale", "409", theirs) : null));
  await h.session.begin();
  await h.session.decide(TAP);
  check(h.session.view?.at === 300 && h.log.refused.length === 0, "a stale decision draws the save as it is");
  check(h.log.stepped.join() === "false", "the stale step lands like any");
}
{  // the server away (a deploy): asked again with backoff, Retry-After honoured, the page told it is reconnecting
  const h = harness(fixtureContent, (call, n) => (call === "decide" && n <= 2 ? new ApiFailure("save_unavailable", "503", null, 3) : null));
  await h.session.begin();
  await h.session.decide(TAP);
  check(h.log.calls.filter((c) => c === "decide").length === 3, "the decision is sent until it is answered");
  check(h.log.waits.join() === "3000,3000", `each wait honours Retry-After over the backoff: ${h.log.waits.join()}`);
  check(h.log.connected.join() === "false,true", `reconnecting once, then connected: ${h.log.connected.join()}`);
  check(h.log.afters.join() === "0", "the decision that landed carried the count from before");
}
{  // no answer at all: the backoff grows
  const h = harness(fixtureContent, (call, n) => (call === "advance" && n <= 3 ? new ApiFailure("network", "down") : null));
  await h.session.begin();
  await h.session.advance();
  check(h.log.waits.join() === "1000,2000,4000", `the backoff doubles: ${h.log.waits.join()}`);
}
{  // refusals: a decision that does not fit, an account or save gone, Begin limited
  const bad = harness(fixtureContent, (call) => (call === "decide" ? new ApiFailure("invalid_decision", "422") : null));
  await bad.session.begin();
  await bad.session.decide(TAP);
  check(bad.log.refused.length === 1 && bad.log.refused[0] === TAP, "an invalid decision is refused and redrawn");
  const slow = harness(fixtureContent, (call) => (call === "decide" ? new ApiFailure("rate_limited", "429") : null));
  await slow.session.begin();
  await slow.session.decide(TAP);
  check(slow.log.refused.length === 1 && slow.log.refused[0] === TAP && slow.log.limited === 0,
    "a decision past its save's limit is refused and redrawn, not the front page's Begin line");
  const answered = harness(fixtureContent, (call) => (call === "decide" ? new ApiFailure("invalid_decision", "422") : null));
  await answered.session.begin();
  await answered.session.decide({ kind: "answer_offer", offer: "ask", answer: "go" });
  check(answered.log.calls.slice(-2).join() === "decide,advance" && answered.log.refused.length === 0 && answered.log.stepped.join() === "false",
    `an answer refused (answered since the page's last view) asks advance and draws that: ${answered.log.calls.join()}`);
  const gone = harness(fixtureContent, (call) => (call === "open" ? new ApiFailure("not_found", "404") : null));
  await gone.session.resume(9);
  check(gone.log.lost === 1 && gone.log.started.length === 0, "a save that is gone sends the page back to the front");
  const many = harness(fixtureContent, (call) => (call === "begin" ? new ApiFailure("rate_limited", "429") : null));
  await many.session.begin();
  check(many.log.limited === 1 && many.log.started.length === 0, "a limited Begin says so on the front page");
}
{  // lost right after Begin (a cookie the browser refused) is told apart from lost later in a game
  const refused = harness(fixtureContent, (call) => (call === "advance" ? new ApiFailure("no_account", "401") : null));
  await refused.session.begin();
  await refused.session.advance();
  check(refused.log.lostFresh.join() === "true", "a session lost before any answer since Begin is fresh");
  const later = harness(fixtureContent, (call, n) => (call === "advance" && n === 2 ? new ApiFailure("no_account", "401") : null));
  await later.session.begin();
  await later.session.advance();
  await later.session.advance();
  check(later.log.lostFresh.join() === "false", "a session lost after an answer is not fresh");
}
{  // a deploy mid-game (a Step under new rules): the content is fetched again and the game redrawn
  const h = harness();
  await h.session.begin();
  h.rules.digest = "newer";
  await h.session.advance();
  check(h.log.started.length === 2 && h.log.calls.filter((c) => c === "content").length === 2, "a new digest redraws the game");
  check(h.log.started[1] === null, "a redraw keeps the story it has");
  await h.session.advance();
  check(h.log.started.length === 2 && h.log.stepped.length === 1, "under the rules it now holds, steps land as usual");
}
{  // a dry run sends the save's id and the decisions, and keeps nothing
  const h = harness();
  await h.session.begin();
  const before: View | null = h.session.view;
  const after = await h.session.dryRun([{ kind: "switch_mix", mix_id: "a" }, { kind: "switch_mix", mix_id: "b" }]);
  check(after !== null && after.mixes.length === 0 && h.session.view === before, "the dry run's view comes back and nothing is kept");
  check(h.log.calls.filter((c) => c === "dryRun").length === 1, "one request for the whole edit");
}
{  // what the page keeps goes to the server, once: about the save to that save, about the player to the account
  const h = harness();
  await h.session.resume(7);
  h.held.keeps?.keepRuleSeen();
  h.held.keeps?.keepRuleSeen();
  h.held.keeps?.keepRulesOpened();
  check(h.log.puts.join(" | ") === 'save 7 {"rule_seen":true,"mix_offered":[],"lessons":[],"lesson_ends":[]} | me {"rules_opened":true,"devices_opened":false,"ledger_lines":[],"mix_stopped":[],"switch_offered":[],"journal_read":[]}', `sent: ${h.log.puts.join(" | ")}`);
}
{  // feedback: sent once with the save being played, outside the save's queue; any failure is just "not kept"
  const h = harness();
  check(await h.session.feedback("before a game") && h.log.feedback.join() === "null: before a game", "feedback with no game carries no save");
  await h.session.begin();
  check(await h.session.feedback("the third tap") && h.log.feedback.at(-1) === "7: the third tap", "feedback carries the save being played");
  const limited = harness(fixtureContent, (call) => (call === "feedback" ? new ApiFailure("rate_limited", "429") : null));
  await limited.session.begin();
  check(!(await limited.session.feedback("again")), "a limited feedback is not kept");
  check(limited.log.calls.filter((c) => c === "feedback").length === 1 && limited.log.limited === 0 && limited.log.refused.length === 0,
    "it is asked once and does not touch the game's states");
  const down = harness(fixtureContent, (call) => (call === "feedback" ? new ApiFailure("network", "down") : null));
  check(!(await down.session.feedback("offline")) && down.log.waits.length === 0, "no answer is not asked again");
}
