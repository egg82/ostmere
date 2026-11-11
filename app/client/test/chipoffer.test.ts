// The strip's first-rule lesson entry (ui/chipoffer.ts, cues.chipCards): hidden before the end and while its lines are being
// read; shown while the lesson may start, when tired with no rule on energy's at_most; staying after the chip clears; gone
// once any such rule is set or the lesson is behind; arriving as the chip; opening the editor, never building.
import { fixtureContent, Q, TIRED } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { chipCards, offeredCard } from "../src/game/cues";
import { ChipOffer } from "../src/ui/chipoffer";
import { FIRST_MIX } from "../src/game/lessons";
import type { PartContext } from "../src/ui/part";
import { keepsOf } from "./kept";
import { TAUGHT } from "./context";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

class Fake {
  dataset: Record<string, string> = {}; className = ""; textContent = ""; type = ""; hidden = false; isConnected = true; kids: (Fake | string)[] = [];
  private on = new Map<string, (() => void)[]>();
  constructor(readonly tag: string) {}
  get classList() {
    const names = () => new Set(this.className.split(" ").filter(Boolean));
    return {
      add: (c: string) => { this.className = [...names().add(c)].join(" "); },
      remove: (c: string) => { const s = names(); s.delete(c); this.className = [...s].join(" "); },
      contains: (c: string) => names().has(c),
    };
  }
  addEventListener(name: string, f: () => void) { this.on.set(name, [...(this.on.get(name) ?? []), f]); }
  click() { for (const f of this.on.get("click") ?? []) f(); }
  append(...k: (Fake | string)[]) { this.kids.push(...k); }
  replaceChildren(...k: (Fake | string)[]) { for (const c of this.kids) if (typeof c !== "string") c.isConnected = false; this.kids = k; }
  text(): string { return [this.textContent, ...this.kids.map((k) => (typeof k === "string" ? k : k.text()))].join(""); }
  find(tag: string): Fake | undefined { for (const k of this.kids) if (typeof k !== "string") { if (k.tag === tag) return k; const f = k.find(tag); if (f) return f; } return undefined; }
}
Object.assign(globalThis, { document: { createElement: (tag: string) => new Fake(tag) } });

const catalog = new Catalog(fixtureContent);
const offer = { ...fixtureStep("restoffer", 100).view, orders: [], orders_on: [] };   // ended ten minutes back, tired, no rule yet

interface Rig { node: ChipOffer; root: Fake; decided: Decision[]; opened: unknown[]; arrived: string[]; behind: { v: boolean }; lesson: { v: string | null } }

/** `taught`: the first rule's lesson is behind the player (done or skipped), else it may start. */
function rig(taught: boolean, using: Catalog = catalog): Rig {
  const decided: Decision[] = [];
  const opened: unknown[] = [];
  const arrived: string[] = [];
  const behind = { v: true };
  const lesson: { v: string | null } = { v: null };
  const ctx = {
    catalog: using,
    actions: { decide: (d: Decision) => decided.push(d), openRules: (...a: unknown[]) => opened.push(a) },
    arrivals: { arrive: (_n: Fake, kind: string, id: string) => { arrived.push(`${kind}:${id}`); } },
    endBehind: () => behind.v,
    lesson: () => lesson.v,
    lessonSubject: () => null,
    keeps: keepsOf(taught ? TAUGHT : { ...TAUGHT, lessons: [FIRST_MIX] }),
  } as unknown as PartContext;   // a fake DOM double -- it has only what this test reads
  const node = new ChipOffer(ctx);
  return { node, root: node.root as unknown as Fake, decided, opened, arrived, behind, lesson };   // a fake DOM double -- it has only what this test reads
}

// The content side: the chip's card is never a ledger line's, and chipCard gates it.
expect("a chip's card is no ledger line's card", catalog.orderCardsFor("energy").length, 0);
expect("offeredCard never draws it", offeredCard(catalog, offer, "energy"), undefined);
expect("chipCard: due", chipCards(catalog, offer, true)[0]?.store, "energy");
expect("chipCard: before the end", chipCards(catalog, { ...offer, ended_at: null }, true)[0], undefined);
expect("chipCard: end lines being read", chipCards(catalog, offer, false)[0], undefined);
expect("chipCard: not tired", chipCards(catalog, { ...offer, chips: ["warm"] }, true)[0], undefined);
const waits = new Catalog({ ...fixtureContent, order_cards: fixtureContent.order_cards.map((c) =>
  c.chip ? { ...c, offered_after: { category: "card" as const, id: "not_yet" } } : c) });
expect("chipCard: its offered_after not unlocked", chipCards(waits, offer, true)[0], undefined);
expect("chipCard: its offered_after unlocked", chipCards(waits, { ...offer, unlocked: [...offer.unlocked, { category: "card", id: "not_yet" }] }, true)[0]?.store, "energy");

// Hidden before the end, and while its lines are being read.
{
  const r = rig(false);
  r.node.update({ ...offer, ended_at: null });
  expect("hidden before ended_at", r.root.hidden, true);
  r.behind.v = false;
  r.node.update(offer);
  expect("hidden while the end lines are being read", r.root.hidden, true);
  expect("nothing arrived yet", r.arrived, []);
}

// While the rule's lesson may start: its entry, worded as the chip, with Show me; arrives as the chip; stays after the chip
// clears; one arrival. Its button opens a new rule on the editor and decides nothing.
const shown = rig(false);
shown.node.update(offer);
expect("shown when tired, after the end, with the card behind", shown.root.hidden, false);
expect("worded as the chip, no number, with Show me", shown.root.text(), "While tired → RestShow me");
expect("arrives as the chip", shown.arrived, ["chip:tired"]);
shown.node.update({ ...offer, chips: ["warm"] });
expect("stays after the chip clears", shown.root.hidden, false);
expect("drawn once", shown.arrived, ["chip:tired"]);
shown.root.find("button")?.click();
expect("Show me opens a new rule on the tired chip's condition", shown.opened, [["new", TIRED]]);
expect("and builds nothing", shown.decided, []);

// Once the lesson is done or skipped no row is drawn, so nothing can be built from the strip: the chip carries a mark instead.
{
  const r = rig(true);
  r.node.update(offer);
  expect("no row once the first rule's lesson is behind", [r.root.hidden, r.arrived], [true, []]);
}

// Gone once any rule on energy's at_most is set, whatever its levels or what it runs.
{
  const r = rig(false);
  r.node.update(offer);
  const other = { when: { ...TIRED, value: 5 * Q, release: 9 * Q }, then: { kind: "switch_mix" as const, mix_id: "Lie down" } };
  r.node.update({ ...offer, orders: [...offer.orders, other], orders_on: [...offer.orders_on, false] });
  expect("gone once an energy rule is set", r.root.hidden, true);
  const reaches = { when: { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "energy" }, value: 9 * Q, release: 5 * Q }, then: other.then };
  expect("a reaches rule on energy does not answer it", chipCards(catalog, { ...offer, orders: [...offer.orders, reaches] }, true)[0]?.store, "energy");
}

// Another lesson under way: the entry waits, and comes back when it ends.
{
  const r = rig(false);
  r.lesson.v = "journal";
  r.node.update(offer);
  expect("waits while another lesson runs", r.root.hidden, true);
  r.lesson.v = null;
  r.node.update(offer);
  expect("back when it ends", r.root.hidden, false);
}

// Two order cards on one chip: only the first is the lesson's entry, never a twin.
{
  const rest = fixtureContent.order_cards.find((c) => c.chip === "tired")!;
  const twin = { ...rest, then: { kind: "tap_card" as const, card: "gather" } };
  const two = new Catalog({ ...fixtureContent, order_cards: [...fixtureContent.order_cards, twin] });
  expect("chipCards: both, in content order", chipCards(two, offer, true).map((c) => c.then), [rest.then, twin.then]);
  const r = rig(false, two);
  r.node.update(offer);
  expect("one entry for the pair", r.root.text(), "While tired → RestShow me");
}
