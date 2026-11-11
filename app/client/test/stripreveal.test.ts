// The hands strip arrives with the first mix (hands.ts, game/shown.ts; docs/design/opening-screen.md, "The hands
// strip"): before the first mix's offer it takes no room; from the offer on it is, and once drawn it
// stays for the page session.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Hands } from "../src/ui/hands";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const drawn = (h: Hands): boolean => !h.root.hidden;

{
  const h = new Hands(testContext().ctx);
  h.update(fixtureStep("start", 10).view);
  expect("before the first mix's offer: not drawn", drawn(h), false);
  h.update(fixtureStep("standing", 12).view);
  expect("a tap on the hands: still not drawn", drawn(h), false);
  h.update(fixtureStep("firstmix", 20).view);
  expect("the first mix's offer: drawn", drawn(h), true);
  expect("with the offer showing", h.root.dataset["state"], "offer");
  h.update(fixtureStep("start", 30).view);
  expect("once drawn it stays", drawn(h), true);
}

{
  const { ctx } = testContext();
  const arrived: string[] = [];
  const h = new Hands({ ...ctx, arrivals: { ...ctx.arrivals, arrive: (_node, kind, id) => { arrived.push(`${kind}:${id}`); } } });
  h.update(fixtureStep("start", 10).view);
  expect("nothing arrives while it is not drawn", arrived, []);
  h.update(fixtureStep("firstmix", 20).view);
  h.update(fixtureStep("firstmix", 21).view);
  expect("it arrives once, through the arrival queue", arrived, ["feature:hands"]);
}

{
  const h = new Hands(testContext().ctx);
  h.update(fixtureStep("mid", 100).view);
  expect("a page opened on a running mix: drawn at once", drawn(h), true);
}

{
  const start = fixtureStep("start", 10).view;
  const ruled: View = { ...start, orders: fixtureStep("covered", 10).view.orders };
  const h = new Hands(testContext().ctx);
  h.update(ruled);
  expect("a rule saved with no mix: drawn", drawn(h), true);
}

// The mix row opens bare: its bar and name. Edit comes once a mix greys or an action card the first mix does not hold
// is in play; Mixes ▾ once a mix is saved; "runs …" with the ledger. Each stays once drawn.
const shown = (h: Hands, cls: string): boolean => !(h.root.querySelector(cls) as HTMLElement).hidden;
const mid = fixtureStep("mid", 100).view;
const noLedger: View = { ...mid, unlocked: mid.unlocked.filter((u) => u.id !== "ledger") };
const repeatable = (v: View, id: string): View => ({
  ...v, cards: [...v.cards, {
    card: id, completions: 0, cap: null, bar: { start: v.at, start_value: 0, rate: 0, limit: null }, bar_total: 5, by: null,
    completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 5, needs: [],
  }],
});

{
  const h = new Hands(testContext().ctx);
  h.update(noLedger);
  h.tick(100);
  expect("the first mix, running: its name", h.root.querySelector(".hands-mix-name")?.textContent, mid.running_mix_id);
  expect("no Edit yet", shown(h, ".hands-edit"), false);
  expect("Mixes ▾ with the first mix saved", shown(h, ".hands-meta .hands-name"), true);
  expect("no runs … before the ledger", shown(h, ".hands-runs"), false);
  h.update(mid);
  h.tick(100);
  expect("runs … with the ledger", shown(h, ".hands-runs"), true);
}

{
  const h = new Hands(testContext().ctx);
  h.update(repeatable(mid, "scavenge"));
  expect("a new task the mix could take: Edit", shown(h, ".hands-edit"), true);
  h.update(mid);
  expect("and Edit stays", shown(h, ".hands-edit"), true);
}

{
  const h = new Hands(testContext().ctx);
  h.update(repeatable(mid, "gather"));
  expect("a first-mix card again is not new: no Edit", shown(h, ".hands-edit"), false);
  h.update(repeatable(mid, "take_stock"));
  expect("a narrative step is not a task for the mix: no Edit", shown(h, ".hands-edit"), false);
  h.update(fixtureStep("greyed", 100).view);
  expect("the mix greys: Edit", shown(h, ".hands-edit"), true);
}

{
  const h = new Hands(testContext().ctx);
  const two = fixtureStep("covered", 100).view;
  expect("the control: two mixes saved", two.mixes.length, 2);
  h.update(two);
  expect("two mixes: Mixes ▾", shown(h, ".hands-meta .hands-name"), true);
  h.update(mid);
  expect("and Mixes ▾ stays", shown(h, ".hands-meta .hands-name"), true);
}
