// Moving to another device, on the page: a join link leaves the address bar before the analytics load, a link never
// joins by itself, the refusals are told apart, a device with games of its own is asked before they move (and only its
// tap sends merge), a join that goes through reloads, and the QR code is drawn whole.
import { ApiFailure, type GameApi } from "../src/api/api";
import type { JoinWay, Joined } from "../src/api/types";
import { boot } from "../src/app/boot";
import { takeJoinLink } from "../src/app/joinlink";
import { fixtureContent } from "../fixtures/content";
import { askLine, joinWith, refusal, refusalLine } from "../src/game/joining";
import { Text, UI } from "../src/game/text";
import { qrSvg } from "../src/ui/qr";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const saved = { location: (globalThis as { location?: unknown }).location, history: (globalThis as { history?: unknown }).history };
const replaced: string[] = [];
function at(hash: string): void {
  Object.assign(globalThis, {
    location: { hash, pathname: "/", search: "" },
    history: { state: null, replaceState: (_s: unknown, _t: string, url: string) => { replaced.push(url); } },
  });
}

at("#join=K7QM-4XRT");
check(takeJoinLink() === "K7QM-4XRT", "the link's code is read");
check(replaced.join() === "/", `the fragment leaves the address bar: ${replaced.join()}`);
replaced.length = 0;
for (const hash of ["", "#phase=start", "#join"]) {
  at(hash);
  check(takeJoinLink() === null && replaced.length === 0, `no join link in "${hash}": nothing taken, nothing replaced`);
}
Object.assign(globalThis, saved);

// boot takes the link before the tracker loads (telemetry.ts loads Umami), and hands the code on without joining
const order: string[] = [];
boot({ takeJoin: () => { order.push("take"); return "K7QM-4XRT"; }, telemetry: () => order.push("telemetry"),
  begin: (join) => order.push(`begin ${join ?? ""}`) });
check(order.join() === "take,telemetry,begin K7QM-4XRT", `boot order: ${order.join()}`);

for (const [code, want] of [["no_such_code", "none"], ["invalid_decision", "none"], ["rate_limited", "limited"],
  ["confirm_merge", "ask"], ["too_many_saves", "full"], ["save_unavailable", "away"], ["network", "away"]] as const) {
  check(refusal(new ApiFailure(code, "x")) === want, `${code} reads as ${want}`);
}
check(refusal(new Error("boom")) === "away", "an unexpected failure reads as away");

const joined: Joined = { moved: 0, account: { presentation: { rules_opened: false, devices_opened: false, reminder_mentioned: false, ledger_lines: [], mix_stopped: [], switch_offered: [], journal_read: [] }, settings: { lessons: true }, has_words: false, words_due: false } };
let reloads = 0;
const sent: string[] = [];
const api = (answer: () => Promise<Joined>): GameApi =>
  ({ join: (_typed: string, way: JoinWay) => { sent.push(way); return answer(); } } as Partial<GameApi> as GameApi);
const reload = (): void => { reloads += 1; };
check(await joinWith(api(() => Promise.resolve(joined)), "K7QM-4XRT", "plain", reload) === null && reloads === 1,
  "a join that goes through reloads into GET /api/me");
const summary = { here: 3, there: 3, there_newest_game_time: 0, max_saves: 5, words_replaced: false };
const asked = await joinWith(api(() => Promise.reject(new ApiFailure("confirm_merge", "x", null, null, summary))), "K7QM-4XRT",
  "plain", reload);
check(asked?.why === "ask" && reloads === 1, "a device with games of its own is asked, and stays on the page");

// the question names the words that stop working only when the server says both accounts have words
const t = new Text(fixtureContent);
const wordsClause = t.get(UI.mergeWords);
const worded = await joinWith(api(() => Promise.reject(new ApiFailure("confirm_merge", "x", null, null,
  { ...summary, words_replaced: true }))), "K7QM-4XRT", "plain", reload);
check(wordsClause !== "" && worded !== null && asked !== null, "the clause has text and both joins were refused");
const plain = askLine(t, asked?.wordsReplaced ?? true);
const warned = askLine(t, worded?.wordsReplaced ?? false);
check(plain.startsWith(t.get(UI.mergeAsk)) && !plain.includes(wordsClause), `no clause without the field: ${plain}`);
check(warned.startsWith(t.get(UI.mergeAsk)) && warned.includes(wordsClause), `the clause with it: ${warned}`);
const full = await joinWith(api(() => Promise.reject(new ApiFailure("too_many_saves", "x", null, null, summary))), "K7QM-4XRT",
  "move", reload);
check(full?.why === "full" && full.max === 5 && reloads === 1, `over the cap: refused, with the cap: ${JSON.stringify(full)}`);
check(sent.join() === "plain,plain,plain,move", `move is sent only when asked for: ${sent.join()}`);
const fullLine = refusalLine(new Text(fixtureContent), 600, "full", 5);
check(fullLine.includes(" 5 ") && !fullLine.includes("{"), `the cap is filled in from the summary: ${fullLine}`);

// the QR code: every dark module drawn, inside a quiet zone of four, on a light tile
type Node = { tag: string; attrs: Map<string, string>; kids: Node[]; setAttribute(k: string, v: string): void; append(...n: Node[]): void };
const make = (tag: string): Node => {
  const n: Node = { tag, attrs: new Map(), kids: [], setAttribute: (k, v) => { n.attrs.set(k, v); }, append: (...k) => { n.kids.push(...k); } };
  return n;
};
Object.assign(globalThis, { document: { createElementNS: (_ns: string, tag: string) => make(tag) } });
const rows = ["1101", "0000", "0111", "1001"];
const svg = Object(qrSvg(rows, "K7QM-4XRT")) as Node;
check(svg.attrs.get("viewBox") === "0 0 12 12", `the quiet zone: ${svg.attrs.get("viewBox")}`);
const dark = svg.kids.filter((k) => k.attrs.get("class") === "qr-dark");
check(svg.kids[0]?.attrs.get("class") === "qr-light", "a light tile first");
const cells = new Set<string>();
for (const r of dark) {
  const [x, y, w] = ["x", "y", "width"].map((a) => Number(r.attrs.get(a)));
  for (let i = 0; i < (w ?? 0); i += 1) cells.add(`${(x ?? 0) + i - 4},${(y ?? 0) - 4}`);
}
const want = new Set(rows.flatMap((row, y) => [...row].flatMap((c, x) => (c === "1" ? [`${x},${y}`] : []))));
check(cells.size === want.size && [...want].every((c) => cells.has(c)), "every dark module, and only those");
check(dark.length === 5, `one rect per run: ${dark.length}`);

// the miss line names the code's lifetime from Content.transfer_code_s, never from its own words
const said = refusalLine(new Text(fixtureContent), 600, "none");
check(said.includes(" 10 minutes") && !said.includes("{"), `the lifetime is filled in: ${said}`);
check(refusalLine(new Text(fixtureContent), 900, "none").includes(" 15 minutes"), "and follows the served value");
