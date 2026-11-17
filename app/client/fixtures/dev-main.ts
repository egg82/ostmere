// FIXTURE entry, never shipped (node build.mjs --fixtures build-dev): the front page and game against fixtures.
// URL hash: #stale answers every step 503 (the reconnecting state); #phase=… picks the first Step (steps.ts, Phase);
// #play also presses Begin (for screenshots); #sheet then opens the Mixes list from the strip. #rules opens the Rules
// tab (#camp, on its Camp side), #rule=N the condition editor on its Nth rule's condition, #pick=N the picker on its Nth mix slot. #seen opens
// writing rules (as if a rule had been seen on then off); #new then opens the Rules tab's New rule, #plan its Next's Plan. #limited makes a send of feedback answer 429. The shortcuts:
// #change (the ledger's Change), #covered (a ledger line's "covered"), #strip (the strip's "until …"). #due marks
// recovery words due; #devices opens the "Another device" sheet; #settings the Settings sheet; #join=CODE is a join link; #have opens "I have a code".
// #kept=a,b marks those lessons kept in the new save (the stopped-mix lesson needs the mix's: #phase=greyed&kept=first_mix); #swap lets
// `look` make what `tend` made, so the stopped row offers a swap. #kinded makes the fixture's "ask" offer a kind of its own, roles "no" and "yes" on its answers (the answer rule's builder).
// #chronicle opens the Chronicle (phase chronicle fills it); #done opens the Book on its Done page (#manydone finishes every card) and #town the Town tab (a phone's). #journal opens the Book on its Journal (phases journal, journallesson). #prestigesheet opens the first skill row's Prestige or Choose (phases prestige, prestigeowed). #games opens the Games sheet. #catchup answers the first decision as a long absence coming back in slow slices. #back shows the page again 1.5 s in (a return: phases sincelong, sinceshort, sincenone). Phases asksone and asksmany open the Asks list (asks.ts); phase feel lands a chain on each tap (feel.ts).
import "../src/controls.css";
import "../src/game.css";
import "../src/front.css";
import "../src/fights.css";
import "../src/slider.css";
import "../src/reminders.css";
import { wireBegin } from "../src/begin";
import { fixtureContent, Q } from "./content";
import { isFights, withHurtChip } from "./fights";
import { isJournal, withJournal } from "./journal";
import { isPrestige, withPrestige } from "./prestige";
import { isSince, withSince } from "./since";
import { fixtureApi } from "./fixture-api";
import { catchingUpApi } from "./catchup";
import { fixtureManifestUrl } from "./scene-manifest";
import type { Decision, Order, Step, View } from "../src/api/types";
import type { Phase } from "./steps";

const hash = new URLSearchParams(location.hash.slice(1));
if (hash.has("kinded")) {
  for (const o of fixtureContent.offer_infos.filter((x) => x.offer === "ask")) {
    o.kind = "q";
    for (const a of o.answers) a.role = a.answer === "go" ? "yes" : "no";
  }
}
if (hash.has("swap")) for (const s of fixtureContent.store_infos) if (s.made_by.includes("tend")) s.made_by = [...s.made_by, "look"];
const phase = (hash.get("phase") ?? "start") as Phase;
// #townname: the content's later town name ("Town", after a feature the view may unlock), #founded unlocking it.
if (hash.has("townname")) {
  fixtureContent.town_later_labels.push({ after: { category: "feature", id: "founded" }, label_key: "ui.town.later" });
  fixtureContent.text_entries.push({ key: "ui.town.later", text: "Town" });
}
if (isFights(phase)) Object.assign(fixtureContent, withHurtChip(fixtureContent));
if (isJournal(phase)) Object.assign(fixtureContent, withJournal(fixtureContent));
if (isPrestige(phase)) Object.assign(fixtureContent, withPrestige(fixtureContent));
if (isSince(phase)) Object.assign(fixtureContent, withSince(fixtureContent));
const fixture = fixtureApi(phase, hash.has("stale"), hash.has("seen"), hash.has("limited"), hash.has("due"));
const kept = (hash.get("kept") ?? "").split(",").filter((l) => l.length > 0);
// #stuck stands in for the server's View.order_dry (CONTRACT.txt, "Dry rules"; tested in tests/test_rule_dry.py): the rule
// holding the hands cannot let go, and a dry run says the rule being written may stop short.
const dryOf = (v: View, holding: boolean): View => ({ ...v, order_dry: v.orders.map((o, i) => (!holding || v.order_states[i] === "on" ? (o.then.kind === "switch_mix" ? { store: "stone", holding } : null) : null)) });
const stuck = hash.has("stuck");
// #manydone: every card of the content finished, for the Book's Done page at its fullest.
const manyDone = (v: View): View => (hash.has("manydone") ? { ...v, completed: fixtureContent.card_infos.map((c) => ({ card: c.card, completions: 3 })) } : v);
// #shares: the first rule's levels as shares of the cap (down to a quarter, until three quarters), the second's until
// as full (CONTRACT.txt, "Share levels"), for the editor and the rule rows in both forms.
const share = (o: Order, i: number): Order => (o.when.kind !== "at_most" || i > 1 ? o : { ...o, when: i === 0
  ? { ...o.when, value: 2500, release: 7500, value_of_cap: true, release_of_cap: true } : { ...o.when, release: 10000, release_of_cap: true } });
const shared = (v: View): View => (hash.has("shares") ? { ...v, orders: v.orders.map(share) } : v);
// #goalrows: a store goal on wood (30, an hour off), for the goal pickers (ui/stint.ts) with a store's shares under it.
const woodGoal = (v: View): View => (!hash.has("goalrows") ? v : { ...v, goal_rows: [{ kind: "store", store: "wood", skill: null, target: 30 * Q,
  lands_at: v.at + 3600, per_hour: 60_000, limit: null, until: { kind: "at_least", watched: { kind: "store_value", store: "wood" }, value: 30 * Q, release: 30 * Q, value_of_cap: false, release_of_cap: false } }] });
// #nextrow: Next's row moved up above the third rule, a Larder build queued, and that rule waiting behind Next
// (CONTRACT.txt, "Next's row"), for the Rules tab with the row between two rules.
const larder = { kind: "at_least" as const, watched: { kind: "card_count" as const, card: "larder" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false };
const nextRow = (v: View): View => (!hash.has("nextrow") ? v : { ...v, orders: v.orders.map((o, i) => ({ ...o, below_next: i >= 2 })),
  queue: [{ verb: { kind: "tap_card", card: "larder" }, until: larder }], order_states: v.order_states.map((s, i) => (i === 2 && s === "on" ? "behind_next" : s)) });
const founded = (v: View): View => (hash.has("founded") ? { ...v, unlocked: [...v.unlocked, { category: "feature", id: "founded" }] } : v);
const asStep = (s: Step): Step => ({ ...s, view: founded(nextRow(woodGoal(shared(manyDone(stuck ? dryOf(s.view, true) : s.view))))) });
const withKept = { ...fixture, begin: () => fixture.begin().then((n) => { n.presentation.lessons.push(...kept); return n; }) };
const api = { ...withKept, begin: () => withKept.begin().then((n) => ({ ...n, step: asStep(n.step) })), advance: (id: number) => withKept.advance(id).then(asStep), decide: (id: number, d: Decision, after: number) => withKept.decide(id, d, after).then(asStep), dryRun: (id: number, ds: Decision[]) => withKept.dryRun(id, ds).then((v) => { const set = ds.find((d) => d.kind === "set_orders"); return stuck && set?.kind === "set_orders" ? dryOf({ ...v, orders: set.orders }, false) : v; }) };
wireBegin(hash.has("catchup") ? catchingUpApi(api) : api,
  hash.has("noscene") ? "/no-scene.json" : fixtureManifestUrl(), hash.get("join"));
if (hash.has("play")) clickWhenShown("#begin");   // once the page has asked who this is: a Begin pressed sooner is undone by that answer

/** Click the `nth` visible match (the first by default) once it exists (the game draws after Begin's first answer). */
function clickWhenShown(selector: string, then?: () => void, tries = 100, nth = 0): void {
  const node = [...document.querySelectorAll<HTMLElement>(selector)].filter((n) => n.offsetParent !== null)[nth];
  if (node) { node.click(); then?.(); return; }
  if (tries > 0) window.setTimeout(() => clickWhenShown(selector, then, tries - 1, nth), 50);
}

if (hash.has("sheet")) clickWhenShown(".hands-name, .hands-plan");
if (hash.has("devices")) clickWhenShown(".devices-open");
if (hash.has("games")) clickWhenShown(".games-open");
if (hash.has("settings")) clickWhenShown(".settings-open");
if (hash.has("journal")) clickWhenShown(".tabs [data-tab=book]", () => clickWhenShown(".book-page[data-page=journal]"));
if (hash.has("chronicle")) clickWhenShown(".tabs [data-tab=book]");
if (hash.has("town")) clickWhenShown(".tabs [data-tab=town]");
if (hash.has("done")) clickWhenShown(".tabs [data-tab=book]", () => clickWhenShown(".book-page[data-page=done]"));
if (hash.has("back")) window.setTimeout(() => document.dispatchEvent(new Event("visibilitychange")), 1500);
if (hash.has("prestigesheet")) clickWhenShown(".skill-foot .primary");
if (hash.has("have")) clickWhenShown("#have-code summary");

const rule = hash.get("rule");
const pick = hash.get("pick");
if (hash.has("rules") || rule !== null || pick !== null || hash.has("new") || hash.has("plan")) {
  const then = rule !== null ? () => clickWhenShown(".rules .rule-cond", undefined, 100, Number(rule))
    : pick !== null ? () => clickWhenShown(".rules .rule-slot", undefined, 100, Number(pick))
      : hash.has("new") ? () => clickWhenShown(".rules-new")
        : hash.has("plan") ? () => clickWhenShown(".stint-plan") : undefined;
  clickWhenShown(".tabs [data-tab=rules]", then);
}
if (hash.has("camp")) clickWhenShown(".tabs [data-tab=rules]", () => clickWhenShown(".rules-side-pick[data-side=camp]"));   // the Rules page on its Camp side
if (hash.has("change")) clickWhenShown(".line-order .quiet");
if (hash.has("covered")) clickWhenShown(".line-covered");
if (hash.has("strip")) clickWhenShown(".hands-rule");
