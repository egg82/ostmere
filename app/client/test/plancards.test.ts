// Plan adds a card too (ui/next/stintplan.ts, game/queue.ts; docs/design/opening-screen/rules-tab.md, "The Rules tab"): one queue, two
// ways in. A card's When ready and Plan's pick of the same card send the same entry; Plan lists the cards it could take
// now, one that waits saying what in its face's words, then the mixes.
import { install } from "./fake-dom";
import { TAUGHT, testContext } from "./context";
import { keepsOf } from "./kept";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Mix, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { planCards, whenReady } from "../src/game/queue";
import { waitWords } from "../src/game/needwords";
import { CardNeeds } from "../src/ui/cards/cardneeds";
import { StintPlan } from "../src/ui/next/stintplan";
import { WhenReady } from "../src/ui/cards/whenready";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const still = (v = 0) => ({ start: 100, start_value: v, rate: 0, limit: null });
const waiting = (id: string, readyAt: number | null, over: Partial<Card> = {}): Card => ({
  card: id, completions: 0, cap: 1, bar: still(), bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, full_store: null, gained: [], crew: null, tap_s: 20, speed: 1,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "stone" }, value: 12 * Q, release: 12 * Q, value_of_cap: false, release_of_cap: false }, ready_at: readyAt },
  needs: [{ store: "stone", quantity: 12 * Q, segment: still(3 * Q), gate: null, makers: [], spent: false }], ...over,
});
const mix = (id: string): Mix => ({ id, components: [] });
const catalog = new Catalog(fixtureContent);
const ended = fixtureStep("restoffer", 100).view;   // the end ten minutes back
const larder = waiting("larder", 400);
const lean = waiting("lean_to", null);   // stone nothing makes now: no ready time
const view: View = { ...ended, cards: [...ended.cards, lean, larder], queue: [], mixes: [mix("a"), mix("b")], active_mix_id: "a", running_mix_id: "a", greyed_mix_ids: [] };

function planner(v: View, ctx = testContext()) {
  const c = { ...ctx.ctx, keeps: keepsOf({ ...TAUGHT, rule_seen: true }) };
  let rows: HTMLElement[] = [];
  const p: StintPlan = new StintPlan(c, () => { rows = p.rows(v); });
  rows = p.rows(v);
  return { got: ctx.got, rows: () => rows };
}

// One queue, two ways in: the same entry from the card's When ready and from Plan's pick, for a step with a ready time
// and for one ready now while its lane runs another tap (the build waits for the task under way).
const stool = ended.cards.find((c) => c.card === "stool")!;
const busy: View = { ...view, lanes: view.lanes.map((l) => (l.lane === catalog.laneOf("stool") ? { ...l, running_card: "gather" } : l)) };
expect("the stool is ready now", stool.blocker, null);
for (const [label, v, c] of [["a ready time", view, larder], ["ready now, its lane busy", busy, stool]] as const) {
  const card = testContext();
  const w = new WhenReady(card.ctx);
  const button = w.make(c.card, document.createElement("div"));
  w.sync(button, c, v);
  expect(`${label}: the card offers When ready`, [button.hidden, button.disabled], [false, false]);
  button.click();
  const plan = planner(v);
  plan.rows()[0]?.click();
  plan.rows().find((r) => r.querySelector(".selector-name")?.textContent === catalog.cardLabel(c.card))?.click();
  expect(`${label}: the card's When ready sent one entry`, card.got.decided.length, 1);
  expect(`${label}: Plan's pick sends the same entry`, plan.got.decided, card.got.decided);
  expect(`${label}: Plan closes after the pick`, plan.rows().map((r) => r.textContent), ["+ Plan"]);
}
{
  const w = new WhenReady(testContext().ctx);
  const button = w.make("stool", document.createElement("div"));
  w.sync(button, stool, view);
  expect("ready now on a free lane: the face leaves it to a tap", button.hidden, true);
}

// What Plan lists: every card the queue takes once, under its section's heading (the Tasks page's order, a section by name),
// those it takes with When ready and the waiting ones off with their face's words; the mixes last.
{
  const plan = planner(view);
  plan.rows()[0]?.click();
  const rows = plan.rows();
  const name = (r: HTMLElement) => r.querySelector(".selector-name")?.textContent ?? "";
  const cardRows = rows.slice(1, -3);
  const heads = cardRows.filter((r) => !r.className.includes("plan-card")).map((r) => r.textContent);
  expect("one heading per section", heads, ["Craft", "Bench"]);
  expect("the cards in the page's order, work done again and again among them, crafts under their heading by name; the mixes last",
    [rows[0]!.textContent, ...cardRows.map((r) => r.className.includes("plan-card") ? name(r) : r.textContent), ...rows.slice(-3).map((r) => r.textContent)],
    ["Plan✕", "Gather by hand", "Look around", "Rest", "Tend the fire", "Craft", "Hatchet", "Larder", "Lean-to", "Stool", "Bench", "Lean-to of branches, lashed", "Run until…", "a", "b"]);
  const waits = cardRows.filter((r) => r.className.includes("plan-card") && (r.querySelector(".selector-note")?.textContent ?? "") !== "When ready") as HTMLButtonElement[];
  const faceSays = (card: Card): string => {
    const face = new CardNeeds(testContext().ctx, card.card);
    face.draw(card, view, false);
    face.tick(card, view, view.at);
    return face.shows(card.blocker!.condition)?.textContent ?? "(no row)";
  };
  const said = waits.map((r) => { const c = view.cards.find((k) => catalog.cardLabel(k.card) === name(r))!; return name(r) + faceSays(c); });
  expect("between them each waiting step, saying what its face says", waits.map((r) => r.textContent), said);
  expect("the lean-to among them", waits.some((r) => name(r) === "Lean-to"), true);
  expect("a waiting card is on", waits.every((r) => !r.disabled), true);
  waits.find((r) => name(r) === "Lean-to")!.click();
  expect("and picking it queues it, with no ready time to wait for", plan.got.decided.map((d) => JSON.stringify(d)), [JSON.stringify(whenReady(catalog, view, "lean_to"))]);
  expect("the entry is the lean-to's tap", whenReady(catalog, view, "lean_to")?.kind, "set_queue");
}

// Plan opens on a card alone (no mix to run), and not before the end, when no card could be taken.
{
  expect("a card to plan and no mix: offered", planner({ ...view, mixes: [] }).rows().map((r) => r.textContent), ["+ Plan"]);
  expect("only a card nothing makes ready and no mix: offered", planner({ ...view, mixes: [], cards: [lean] }).rows().map((r) => r.textContent), ["+ Plan"]);
  expect("a card whose one run is queued already is not offered again (no room under its cap)", planner({ ...view, mixes: [], cards: [larder], queue: [{ verb: { kind: "tap_card", card: "larder" },
    until: { kind: "at_least", watched: { kind: "card_count", card: "larder" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false } }] }).rows(), []);
}

// A step waiting on a clock with a part of the day reads as when it opens, and a gated need as its gate, as on its face.
{
  const night = { store: "night", label_key: "store.night", cap: 20 * Q, made_by: [], hidden: false, tally: false, clock: "night" as const, rises_in_steps: false, bonus_bp: null, group_key: null };
  const content = { ...fixtureContent, store_infos: [...fixtureContent.store_infos, night],
    text_entries: [...fixtureContent.text_entries, { key: "ui.card.opens", text: "Opens {when}" }, { key: "ui.when.night", text: "after dark" }, { key: "ui.when.night_end", text: "at first light" }, { key: "store.night", text: "night" }] };
  const clocked = new Catalog(content);
  const onNight = (gate: Card["needs"][number]["gate"]): Card => waiting("larder", 900, {
    blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store: "night" }, value: 5 * Q, release: 5 * Q, value_of_cap: false, release_of_cap: false }, ready_at: 900 },
    needs: [{ store: "night", quantity: 5 * Q, segment: still(0), gate, makers: [], spent: false }] });
  const gate = { kind: "at_least" as const, watched: { kind: "card_count" as const, card: "lean_to" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false };
  for (const [label, card] of [["the night", onNight(null)], ["a gate", onNight(gate)]] as const) {
    const v: View = { ...view, cards: [...ended.cards, card] };
    const face = new CardNeeds(testContext(undefined, clocked).ctx, "larder");
    face.draw(card, v, false);
    face.tick(card, v, v.at);
    expect(`${label}: waiting on a store never shown, so not offered`, [planCards(clocked, v).includes(card), whenReady(clocked, v, "larder")], [false, null]);
    expect(`${label}: Plan's words are the face's`, waitWords(clocked, v, card), face.shows(card.blocker!.condition)?.textContent ?? "(no row)");
  }
  expect("the night's words", waitWords(clocked, view, onNight(null)), "Opens after dark");
}
