// The bounds the server serves (Content.limits; api/CONTRACT.txt, "Request limits"): at the most rules the Rules tab
// stops offering a new one and says so in one line; at the most queued taps "When ready" stops, reading as full.
import { install } from "./fake-dom";
import { TAUGHT, testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, QueueEntry, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { canQueue } from "../src/game/queue";
import { RulesTab } from "../src/ui/rules";
import { WhenReady } from "../src/ui/whenready";
import { keepsOf } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const { max_orders, max_queue } = fixtureContent.limits;
const writing = { ...testContext().ctx, keeps: keepsOf({ ...TAUGHT, rule_seen: true }) };   // writing rules is open

const tab = fixtureStep("rulestab", 100).view;
const rules = (n: number): View => ({ ...tab, orders: Array.from({ length: n }, () => tab.orders[0]!) });
const drawn = (view: View): HTMLElement => {
  const t = new RulesTab(writing);
  document.body.replaceChildren(t.root);
  t.update(view);
  return t.root;
};
const count = (root: HTMLElement, sel: string): number => root.querySelectorAll(sel).length;

const room = drawn(rules(max_orders - 1));
expect("below the bound: New rule", [count(room, ".rules-new"), count(room, ".rules-full")], [1, 0]);
const full = drawn(rules(max_orders));
expect("at the bound: no New rule, one plain line", [count(full, ".rules-new"), [...full.querySelectorAll(".rules-full")].map((n) => n.textContent)],
  [0, ["That is all the room there is for rules"]]);

const larder: Card = {
  card: "larder", completions: 0, cap: 1, bar: { start: 100, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 12, release: 12 }, ready_at: 400 }, needs: [],
};
const ended = fixtureStep("restoffer", 100).view;
const entry = (card: string): QueueEntry => ({ verb: { kind: "tap_card", card }, until: { kind: "at_least", watched: { kind: "card_count", card }, value: 1, release: 1 } });
const queued = (n: number): View => ({ ...ended, cards: [...ended.cards, larder], queue: Array.from({ length: n }, () => entry("other")) });
expect("below the bound: offered", canQueue(catalog, queued(max_queue - 1), larder), true);
expect("at the bound: not offered", canQueue(catalog, queued(max_queue), larder), false);

const button = (view: View): HTMLButtonElement => {
  const w = new WhenReady(testContext().ctx);
  const b = w.make("larder", document.createElement("div"));
  w.sync(b, larder, view);
  return b;
};
const open = button(queued(max_queue - 1)), shut = button(queued(max_queue));
expect("room: When ready", [open.textContent, open.disabled, open.hidden], ["When ready", false, false]);
expect("full: shown, disabled, reading as full", [shut.textContent, shut.disabled, shut.hidden], ["Next is full", true, false]);
