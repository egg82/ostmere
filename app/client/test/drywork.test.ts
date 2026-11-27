// A dry store is an alarm only when the player's own work waits on it (issue 467; game/dryneed.ts, ui/ledger/ledger.ts): a card
// of the hands' running mix, or one a rule or the queue would run, takes from it. A store only a townsperson's share
// takes from reads "ran dry" quietly in its place, and is not seated with the red lines at the top of a phone's Tasks.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { workNeeds } from "../src/game/dryneed";
import { Ledger } from "../src/ui/ledger/ledger";
import { keepsOf, NEW_FLAT } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const catalog = new Catalog(fixtureContent);
const mid = fixtureStep("mid", AT).view;   // the hands run gather and tend: neither takes stone; look takes stone
const dry: LedgerLine = { store: "stone", segment: { start: AT, start_value: 0, rate: 0, limit: null }, net_per_hour: 0, contributions: [],
  empties_at: null, fills_at: null, falling: false, covered: false, starved: true, cap: 20 * Q };
const base: View = { ...mid, ledger: [dry, ...mid.ledger.filter((l) => l.store === "camp")] };
const queued: View = { ...base, queue: [{ verb: { kind: "tap_card", card: "look" }, until: { kind: "after_time", at: 0 } }] };
const inMix: View = { ...base, mixes: base.mixes.map((m) => (m.id === base.running_mix_id ? { ...m, components: [...m.components, { kind: "card_share" as const, card: "look", share_bp: 1000 }] } : m)) };
const ruled: View = { ...base, orders: [...base.orders, { when: { kind: "after_time", at: 0 }, then: { kind: "tap_card", card: "look" }, unless: [], or_else: [], below_next: false }] };

expect("nothing the player runs takes stone", workNeeds(catalog, base, "stone"), false);
expect("a queued tap that takes it", workNeeds(catalog, queued, "stone"), true);
expect("a card of the running mix that takes it", workNeeds(catalog, inMix, "stone"), true);
expect("a rule's tap that takes it", workNeeds(catalog, ruled, "stone"), true);

function drawn(v: View): { alarm: boolean; eta: string; top: boolean } {
  const { ctx } = testContext(undefined, catalog);
  const part = new Ledger({ ...ctx, keeps: keepsOf(NEW_FLAT, []) });
  part.setSplit(true);   // a phone: red and full lines sit apart, above the cards
  part.update(v, null);
  part.tick(AT);
  const named = (root: Element): Element | undefined => Array.from(root.querySelectorAll(".line")).find((n) => n.querySelector(".line-name")?.textContent === catalog.storeLabel("stone"));
  const top = named(part.asks);
  const row = top ?? named(part.root);
  if (!row) throw new Error("no line for stone");
  return { alarm: row.classList.contains("alarm"), eta: row.querySelector(".line-eta")?.textContent ?? "", top: top !== undefined };
}

expect("only the townsfolk wait on it: quiet, in its place", drawn(base), { alarm: false, eta: "ran dry", top: false });
expect("the player's queued work waits on it: an alarm, at the top", drawn(queued), { alarm: true, eta: "ran dry", top: true });
