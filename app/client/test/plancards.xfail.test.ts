// Plan adds a card too (ui/stintplan.ts, game/queue.ts; docs/design/opening-screen.md, "The Rules tab"): one queue, two
// ways in. A card's When ready and Plan's pick of the same card send the same entry; Plan lists the cards it could take
// now, then those still waiting with what they wait on in their face's words, then the mixes.
import { install } from "./fake-dom";
import { TAUGHT, testContext } from "./context";
import { keepsOf } from "./kept";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Mix, View } from "../src/api/types";
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
  const face = new CardNeeds(testContext().ctx, "lean_to");
  face.draw(lean, view, false);
  face.tick(lean, view, view.at);
  const said = face.shows(lean.blocker!.condition)?.textContent ?? "(no row)";
  expect("cards now, waiting cards, then mixes", plan.rows().map((r) => r.textContent), ["Plan✕", "LarderWhen ready", `Lean-to${said}`, "a", "b"]);
  const wait = plan.rows()[2] as HTMLButtonElement;
  expect("a waiting card is off", wait.disabled, true);
  wait.click();
  expect("and sends nothing", plan.got.decided, []);
}

// Plan opens on a card alone (no mix to run), and not before the end, when no card could be taken.
{
  expect("a card to plan and no mix: offered", planner({ ...view, mixes: [] }).rows().map((r) => r.textContent), ["+ Plan"]);
  expect("only a waiting card and no mix: nothing", planner({ ...view, mixes: [], cards: [...ended.cards, lean] }).rows(), []);
  expect("a card queued already is not offered again", planner({ ...view, mixes: [], queue: [{ verb: { kind: "tap_card", card: "larder" },
    until: { kind: "at_least", watched: { kind: "card_count", card: "larder" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false } }] }).rows(), []);
}
