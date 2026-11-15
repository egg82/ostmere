// Plan adds a card too (ui/stintplan.ts, game/queue.ts; docs/design/opening-screen.md, "The Rules tab"): one queue, two
// ways in. A card's When ready and Plan's pick of the same card send the same entry; Plan lists the cards it could take
// now, then those still waiting with what they wait on in their face's words, then the mixes.
import { install } from "./fake-dom";
import { TAUGHT, testContext } from "./context";
import { keepsOf } from "./kept";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Mix, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { planCards } from "../src/game/queue";
import { waitWords } from "../src/game/waitwords";
import { CardNeeds } from "../src/ui/cardneeds";
import { StintPlan } from "../src/ui/stintplan";
import { WhenReady } from "../src/ui/whenready";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const still = (v = 0) => ({ start: 100, start_value: v, rate: 0, limit: null });
const waiting = (id: string, readyAt: number | null, over: Partial<Card> = {}): Card => ({
  card: id, completions: 0, cap: 1, bar: still(), bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, speed: 1,
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

// One queue, two ways in: the same entry from the card's When ready and from Plan's pick.
{
  const card = testContext();
  const w = new WhenReady(card.ctx);
  const button = w.make("larder", document.createElement("div"));
  w.sync(button, larder, view);
  button.click();
  const plan = planner(view);
  plan.rows()[0]?.click();
  const row = plan.rows().find((r) => r.textContent?.startsWith("Larder"));
  row?.click();
  expect("the card's When ready sent one entry", card.got.decided.length, 1);
  expect("Plan's pick sends the same entry", plan.got.decided, card.got.decided);
  expect("Plan closes after the pick", plan.rows().map((r) => r.textContent), ["+ Plan"]);
}

// What Plan lists: the cards it can take now, then the waiting ones with their face's words, then the mixes.
{
  const plan = planner(view);
  plan.rows()[0]?.click();
  const rows = plan.rows();
  expect("the card it can take now first, the mixes last", [...rows.slice(0, 2), ...rows.slice(-2)].map((r) => r.textContent), ["Plan✕", "LarderWhen ready", "a", "b"]);
  const waits = rows.slice(2, -2) as HTMLButtonElement[];
  const faceSays = (card: Card): string => {
    const face = new CardNeeds(testContext().ctx, card.card);
    face.draw(card, view, false);
    face.tick(card, view, view.at);
    return face.shows(card.blocker!.condition)?.textContent ?? "(no row)";
  };
  const name = (r: HTMLElement) => r.querySelector(".selector-name")?.textContent ?? "";
  const said = waits.map((r) => { const c = view.cards.find((k) => catalog.cardLabel(k.card) === name(r))!; return name(r) + faceSays(c); });
  expect("between them each waiting step, saying what its face says", waits.map((r) => r.textContent), said);
  expect("the lean-to among them", waits.some((r) => name(r) === "Lean-to"), true);
  expect("a waiting card is off", waits.every((r) => r.disabled), true);
  waits.forEach((r) => r.click());
  expect("and sends nothing", plan.got.decided, []);
}

// Plan opens on a card alone (no mix to run), and not before the end, when no card could be taken.
{
  expect("a card to plan and no mix: offered", planner({ ...view, mixes: [] }).rows().map((r) => r.textContent), ["+ Plan"]);
  expect("only a waiting card and no mix: nothing", planner({ ...view, mixes: [], cards: [...ended.cards, lean] }).rows(), []);
  expect("a card queued already is not offered again", planner({ ...view, mixes: [], queue: [{ verb: { kind: "tap_card", card: "larder" },
    until: { kind: "at_least", watched: { kind: "card_count", card: "larder" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false } }] }).rows(), []);
}

// A step waiting on a clock with a part of the day reads as when it opens, and a gated need as its gate, as on its face.
{
  const night = { store: "night", label_key: "store.night", cap: 20 * Q, made_by: [], hidden: false, tally: false, clock: "night" as const, bonus_bp: null };
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
    expect(`${label}: waiting, never taken now`, planCards(clocked, v).waiting.includes(card), true);
    expect(`${label}: Plan's words are the face's`, waitWords(clocked, v, card), face.shows(card.blocker!.condition)?.textContent ?? "(no row)");
  }
  expect("the night's words", waitWords(clocked, view, onNight(null)), "Opens after dark");
}
