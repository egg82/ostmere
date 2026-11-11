// The Rules tab (docs/design/opening-screen.md, "The Rules tab"; ui/rules.ts, ui/condition.ts): one line per rule;
// changing a rule's levels never gated, writing a new one gated by the taught step; a chip's rule edited with no level
// and no number; ≡ dragged or moved by key or menu sending the permuted set_orders (task rules keep their places); a
// mix dropped on a slot, or tapped then a slot, or picked, re-pointing the rule; Otherwise setting the default; the
// shortcuts from the ledger and the strip opening the right rule; the Mixes list's "used by" notes; the tab's glow once.
// A slot's mix is picked from its picker (the tab has no mix chips to drag). A new rule opens on the editor's simple
// view: Do, then When for what the chosen task answers, with More options opening the full editor.
import { fakeDocument, FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { fixtureContent, TIRED } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { pointSlot, reorderRule } from "../src/game/orders";
import { HandStreak } from "../src/game/stall";
import { buildRule } from "../src/game/storerule";
import { Flight } from "../src/ui/flight";
import { Glow, GlowWhile } from "../src/ui/fresh";
import { Hands } from "../src/ui/hands";
import { Ledger } from "../src/ui/ledger";
import type { PartContext } from "../src/ui/part";
import type { Arrivals } from "../src/ui/reveal";
import { RulesTab } from "../src/ui/rules";
import { MixSelector } from "../src/ui/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const keeps = new Keeps();   // what the server keeps for the page: writing rules opens partway through
const tab = fixtureStep("rulestab", 100).view;   // wood (0), warmth (1), tired (2, on), bench task (3, on)
const [WOOD, WARMTH, TIRED_RULE, SHELTER] = tab.orders as [Order, Order, Order, Order];
const sent = (d: Decision | undefined): Order[] | null => (d?.kind === "set_orders" ? d.orders : null);

interface Rig { tab: RulesTab; root: FakeEl; decided: Decision[]; opened: (number | null)[]; newMix: (number | null)[] }

function context(decided: Decision[], opened: (number | null)[], newMix: (number | null)[]): PartContext {
  return {
    catalog,
    actions: {
      decide: (d: Decision) => decided.push(d), dryRun: () => Promise.resolve(null), editMix: () => undefined,
      newMix: (r: number | null) => newMix.push(r), openSelector: () => undefined, openRules: (r: number | null) => opened.push(r),
      orderSent: () => undefined, highlight: () => undefined,
    },
    fires: { fresh: [], running: new Set() }, glow: new Glow(), streak: new HandStreak(),
    arrivals: { arrive: () => undefined }, endBehind: () => true, keeps, repeats: () => ({ taps: [], switches: [] }), ruleRuns: () => [], lesson: () => null,
  } as unknown as PartContext;   // a fake DOM double -- it has only what this test reads
}

function rig(view: View = tab): Rig {
  const decided: Decision[] = [], opened: (number | null)[] = [], newMix: (number | null)[] = [];
  const t = new RulesTab(context(decided, opened, newMix));
  const root = t.root as unknown as FakeEl;   // a fake DOM double -- it has only what this test reads
  fakeDocument.body.replaceChildren(root);
  t.update(view);
  return { tab: t, root, decided, opened, newMix };
}

const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string, n = 0): FakeEl => {
  const found = q(root, sel)[n];
  if (!found) throw new Error(`no ${sel} [${n}]`);
  return found;
};

// One line per rule: the three hands rules in priority order, Otherwise last, the bench rule under its lane.
{
  const r = rig();
  const rows = q(r.root, ".rules-list > .rules-row");
  expect("hands rules then Otherwise", rows.map((n) => n.dataset.rule ?? "otherwise"), ["0", "1", "2", "otherwise"]);
  expect("each line: handle, dot, condition, arrow, slot", rows.slice(0, 3).map((n) => n.children.map((c) => c.className.split(" ")[0])),
    [0, 1, 2].map(() => ["rule-handle", "selector-dot", "rule-cond", "rule-arrow", "rule-slot"]));
  expect("conditions in words, with an edit mark", q(r.root, ".rules-list .rule-cond").map((n) => n.textContent),
    ["Under 10 Dead wood, until 20✎", "Under 40 Warmth, until 60✎", "While tired✎"]);
  expect("slots name their mixes", q(r.root, ".rules-list .rule-slot-name").map((n) => n.textContent), ["Gather by hand", "Rest by the fire", "Rest", tab.active_mix_id]);
  expect("the running rule is marked", rows.map((n) => n.classList.contains("active")), [false, false, true, false]);
  expect("no mix chips above the rules", q(r.root, ".mix-chip").length, 0);
  expect("the bench rule under its lane", q(r.root, ".rules-lane .task-rule").length, 1);
  expect("no New rule before the taught step", q(r.root, ".rules-new").length, 0);
}

// Editing a rule's levels is never gated (the taught step not yet seen): the condition opens the editor with steppers.
{
  const r = rig();
  one(r.root, ".rules-list .rule-cond", 0).click();
  const cond = one(r.root, ".cond");
  expect("the editor opens in the tab", cond.isConnected, true);
  expect("its levels show, unfolded", [one(cond, ".cond-fold-body").hidden, one(cond, ".cond-fold").hidden], [false, true]);
  expect("on the rule's levels", q(cond, ".cond-fold-body .cond-value").map((n) => n.textContent), ["10", "20"]);
  one(cond, ".cond-stepper .cond-step", 1).click();   // When +1
  one(cond, ".cond-actions .primary").click();
  expect("Save sends the rule in place", sent(r.decided[0])?.[0]?.when, buildRule({ store: "wood", test: "below", n: 11, m: 20 }, fixtureContent.scales.quantity_per_item));
  expect("the others untouched", sent(r.decided[0])?.slice(1), [WARMTH, TIRED_RULE, SHELTER]);
  expect("back on the list", q(r.root, ".rules-list > .rules-row").length, 4);
  const lane = rig();
  one(lane.root, ".rules-lane .rule-cond").click();
  expect("a lane rule's condition opens the editor too", one(lane.root, ".cond-steppers").hidden, false);
}

// A chip's rule: the editor offers its mix and Remove, never a level or a number.
{
  const r = rig();
  one(r.root, ".rules-list .rule-cond", 2).click();
  const cond = one(r.root, ".cond");
  for (const part of [".cond-stores", ".cond-levels"]) expect(`chip rule: no ${part}`, one(cond, part).hidden, true);
  expect("named by its chip", one(cond, ".cond-heading").textContent, "While tired");
  expect("no number shown anywhere", /\d/.test(cond.shown()), false);
  expect("what it does pressed", q(cond, ".cond-mix, .cond-task").filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.textContent), ["Rest"]);
  one(cond, ".cond-task[data-card=\"gather\"]").click();   // the task of the saved solo mix "Gather by hand"
  one(cond, ".cond-actions .primary").click();
  expect("Save keeps the chip's condition, with the new mix", sent(r.decided[0])?.[2], { when: TIRED, then: { kind: "switch_mix", mix_id: "Gather by hand" } });
  const s = rig();
  one(s.root, ".rules-list .rule-cond", 2).click();
  one(s.root, ".cond-actions .danger").click();
  expect("Remove drops it", sent(s.decided[0]), [WOOD, WARMTH, SHELTER]);
}

// Reordering: the permutation, task rules keeping their places.
expect("down two", sent(reorderRule(tab, 0, 2) ?? undefined), [WARMTH, TIRED_RULE, WOOD, SHELTER]);
expect("up two", sent(reorderRule(tab, 2, 0) ?? undefined), [TIRED_RULE, WOOD, WARMTH, SHELTER]);
expect("in place is nothing", reorderRule(tab, 1, 1), null);
expect("a task rule doesn't move", reorderRule(tab, 3, 0), null);
{
  const mixed: View = { ...tab, orders: [WOOD, SHELTER, WARMTH, TIRED_RULE], orders_on: [false, true, false, true] };
  expect("a task rule between keeps its index", sent(reorderRule(mixed, 3, 0) ?? undefined), [TIRED_RULE, SHELTER, WOOD, WARMTH]);
}

// Dragging ≡: a press that moves past the threshold lifts a ghost; letting go on another row sends the permutation.
{
  const r = rig();
  const rows = q(r.root, ".rules-list > .rules-row[data-rule]");
  rows.forEach((row, i) => { row.rect = { left: 0, top: i * 50, width: 300, height: 48, right: 300, bottom: i * 50 + 48 }; });
  const handle = one(r.root, ".rule-handle", 0);
  handle.dispatchEvent(pointer("pointerdown", 10, 10));
  handle.dispatchEvent(pointer("pointermove", 10, 12));
  expect("a small move is still a tap", q(fakeDocument.body, ".drag-ghost").length, 0);
  handle.dispatchEvent(pointer("pointermove", 10, 120));
  expect("mid-drag: a ghost follows", q(fakeDocument.body, ".drag-ghost").length, 1);
  expect("mid-drag: the drop mark after the third", rows.map((n) => n.classList.contains("drop-after")), [false, false, true]);
  handle.dispatchEvent(pointer("pointerup", 10, 120));
  handle.click();   // the click a real press makes after a drag: swallowed, no menu
  expect("drop sends the permuted list", sent(r.decided[0]), [WARMTH, TIRED_RULE, WOOD, SHELTER]);
  expect("the ghost is gone", q(fakeDocument.body, ".drag-ghost").length, 0);
  expect("the drag's click opened no menu", q(r.root, ".rule-menu").length, 0);
}

// The keyboard and tap fallbacks: arrow keys on ≡, and its menu's Move up / Move down / Remove.
{
  const r = rig();
  one(r.root, ".rule-handle", 2).dispatchEvent(new FakeEvent("keydown", { key: "ArrowUp" }));
  expect("ArrowUp moves it up one", sent(r.decided[0]), [WOOD, TIRED_RULE, WARMTH, SHELTER]);
  const m = rig();
  one(m.root, ".rule-handle", 1).click();
  const menu = one(m.root, ".rule-menu");
  expect("tap on ≡ opens its menu", q(menu, "button").map((b) => b.textContent), ["Move up", "Move down", "Remove"]);
  q(menu, "button")[1]!.click();
  expect("Move down", sent(m.decided[0]), [WOOD, TIRED_RULE, WARMTH, SHELTER]);
  const top = rig();
  one(top.root, ".rule-handle", 0).click();
  expect("the top rule can't move up", q(one(top.root, ".rule-menu"), "button")[0]!.disabled, true);
  q(one(top.root, ".rule-menu"), "button")[2]!.click();
  expect("Remove from the menu", sent(top.decided[0]), [WARMTH, TIRED_RULE, SHELTER]);
}

// A mix onto a slot: picked from the slot's picker.
{
  const p = rig();
  one(p.root, ".rule-slot", 1).click();
  const picks = q(p.root, ".rule-picker .selector-run");
  expect("the picker lists every mix, the current marked", picks.map((b) => [b.textContent.replace("●", ""), b.getAttribute("aria-pressed")]),
    tab.mixes.map((m) => [m.id, String(m.id === "Rest by the fire")]));
  picks.find((b) => b.textContent.endsWith("Gather by hand"))!.click();
  expect("picked: re-pointed", sent(p.decided[0])?.[1], { ...WARMTH, then: { kind: "switch_mix", mix_id: "Gather by hand" } });
  const n = rig();
  one(n.root, ".rule-slot", 1).click();
  one(n.root, ".rule-picker .selector-new").click();
  expect("New mix from a slot points that rule at it", n.newMix, [1]);
  expect("the same mix again is nothing", pointSlot(tab, 0, "Gather by hand"), null);
  expect("a greyed mix can't be placed", pointSlot({ ...tab, greyed_mix_ids: ["Rest"] }, 0, "Rest"), null);
}

// Otherwise: the player's own mix; a mix placed there becomes the default.
{
  const p = rig();
  one(p.root, ".rules-row.otherwise .rule-slot").click();
  q(p.root, ".rule-picker .selector-run").find((b) => b.textContent.endsWith("Gather by hand"))!.click();
  expect("picked for Otherwise", p.decided, [{ kind: "switch_mix", mix_id: "Gather by hand" }]);
  expect("the default again is nothing", pointSlot(tab, "otherwise", tab.active_mix_id!), null);
}

// New rule: gated by the taught step; it opens simple, nothing chosen. Choosing a task offers what it makes; More
// options opens the full editor, levels folded behind one row.
{
  keeps.keepRuleSeen();
  const r = rig();
  one(r.root, ".rules-new").click();
  const cond = one(r.root, ".cond");
  const pressed = () => q(cond, ".cond-mix, .cond-task, .cond-store").filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.textContent);
  expect("nothing chosen, Add rule off", [pressed(), one(cond, ".cond-actions .primary").disabled], [[], true]);
  expect("simple: no mixes, no When row yet, no levels", [q(cond, ".cond-mix").length, one(cond, ".cond-stores").hidden, one(cond, ".cond-levels").hidden], [0, true, true]);
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  expect("a task chosen: When offers what it makes", q(cond, ".cond-stores .cond-store").map((b) => b.dataset.store ?? b.dataset.chip), ["wood"]);
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  expect("two taps: Add rule on", one(cond, ".cond-actions .primary").disabled, false);
  one(cond, ".cond-more").click();
  expect("More options: the mixes, the levels folded", [q(cond, ".cond-mix").length > 0, one(cond, ".cond-levels").hidden, one(cond, ".cond-fold-body").hidden], [true, false, true]);
  expect("the fold states them", q(cond, ".cond-fold-value").map((n) => n.textContent), q(cond, ".cond-fold-body .cond-value").map((n) => n.textContent));
  one(cond, ".cond-fold").click();
  expect("one tap opens them", [one(cond, ".cond-fold-body").hidden, one(cond, ".cond-fold").hidden], [false, true]);
  one(cond, ".cond-actions .primary").click();
  expect("Add rule appends it, the task run as its saved solo mix", sent(r.decided[0])?.at(-1)?.then, { kind: "switch_mix", mix_id: "Gather by hand" });
  expect("appended", sent(r.decided[0])?.length, 5);
}

// The shortcuts: open() lands on the given rule's editor; the ledger's Change and "covered", and the strip's "until …".
{
  const r = rig();
  r.tab.open(tab, 1);
  expect("open(1): rule 1's editor", one(r.root, ".cond-heading").textContent, "Run Rest by the fire when…");
  r.tab.open(tab, null);
  expect("open(null): the list", q(r.root, ".rules-list > .rules-row").length, 4);

  const red = fixtureStep("redrule", 100).view;   // the wood rule set, its line still red
  const decided: Decision[] = [], opened: (number | null)[] = [];
  const ledger = new Ledger(context(decided, opened, []));
  fakeDocument.body.replaceChildren(ledger.root as unknown as FakeEl);   // a fake DOM double -- it has only what this test reads
  ledger.update({ ...red, unlocked: [...red.unlocked, { category: "feature", id: "ledger" }] }, null);
  one(ledger.root as unknown as FakeEl, ".line-order .quiet").click();   // a fake DOM double -- it has only what this test reads
  expect("the ledger's Change opens rule 0, not gated", opened, [0]);

  const covered = fixtureStep("covered", 100).view;
  const falling: View = { ...covered, unlocked: [...covered.unlocked, { category: "feature", id: "ledger" }],
    ledger: covered.ledger.map((l) => (l.store === "wood" ? { ...l, falling: true, covered: true, empties_at: 1000 } : l)) };
  const l2 = new Ledger(context([], [], []));
  fakeDocument.body.replaceChildren(l2.root as unknown as FakeEl);   // a fake DOM double -- it has only what this test reads
  l2.update(falling, null);
  l2.tick(100);
  const root2 = l2.root as unknown as FakeEl;   // a fake DOM double -- it has only what this test reads
  expect("a falling covered line has no covered word or link", [q(root2, ".line-covered").length, q(root2, ".line").length > 0], [0, true]);

  const opened3: (number | null)[] = [];
  const hands = new Hands(context([], opened3, []));
  fakeDocument.body.replaceChildren(hands.root as unknown as FakeEl);   // a fake DOM double -- it has only what this test reads
  hands.update(tab);
  hands.tick(100);
  const until = one(hands.root as unknown as FakeEl, ".hands-meta .hands-rule");   // a fake DOM double -- it has only what this test reads
  expect("the strip says where the tired rule lets go", [until.hidden, until.textContent], [false, "while tired"]);
  until.click();
  expect("and opens the Rules tab, where Lately is", opened3, [null]);
}

// The Mixes list is only mixes, each a rule runs saying how many.
{
  const twice: View = { ...tab, orders: [...tab.orders, { ...WOOD, when: buildRule({ store: "wood", test: "reaches", n: 30, m: 20 }, fixtureContent.scales.quantity_per_item) }] };
  const sel = new MixSelector(context([], [], []));
  sel.show(twice);
  const root = sel.root as unknown as FakeEl;   // a fake DOM double -- it has only what this test reads
  expect("no rule rows in the list", q(root, ".rule-cond").length + q(root, ".rules-row").length, 0);
  const notes = Object.fromEntries(q(root, ".selector-row").map((row) => [one(row, ".selector-name").textContent, row.querySelector(".used-by")?.textContent ?? null]));
  expect("used by notes", notes, { [tab.active_mix_id!]: null, "Gather by hand": "used by 2 rules", "Rest by the fire": "used by a rule", Rest: "used by a rule" });
}

// The tab's glow: on its label once the first rule exists, until the tab is opened; once.
{
  const glow = new Glow();
  const label = new FakeEl("button");
  fakeDocument.body.replaceChildren(label);
  const g = new GlowWhile(glow, label as unknown as HTMLElement);   // a fake DOM double -- it has only what this test reads
  g.update(false);
  expect("no rule, no glow", label.classList.contains("glow"), false);
  g.update(true);
  expect("the first rule: the label glows", label.classList.contains("glow"), true);
  label.click();
  g.update(false);   // opened: rulesOpened() turns the want off
  g.update(false);
  expect("opened: gone, and not back", label.classList.contains("glow"), false);
}

// Behind a line (the line-first queue, ui/reveal.ts): a fired rule's pulse, the tab's glow and the flight's landing
// pulse each wait their turn rather than show while a line is read.
{
  const waiting: Array<{ kind: string; run: () => void }> = [];
  const arrivals = { arrive: () => undefined, effect: (_n: unknown, kind: string, run: () => void) => waiting.push({ kind, run }), busy: true };
  const ctx = { ...context([], [], []), fires: { fresh: ["shelter"], running: new Set() }, arrivals } as unknown as PartContext;   // a fake DOM double -- it has only what this test reads
  const t = new RulesTab(ctx);
  const root = t.root as unknown as FakeEl;   // a fake DOM double -- it has only what this test reads
  fakeDocument.body.replaceChildren(root);
  t.update(tab);
  const row = one(root, ".rules-lane .task-rule");
  expect("the fired pulse waits", [row.classList.contains("fired"), waiting.map((w) => w.kind)], [false, ["card"]]);
  waiting.splice(0).forEach((w) => w.run());
  expect("and shows at its turn", row.classList.contains("fired"), true);

  const label = new FakeEl("button");
  fakeDocument.body.replaceChildren(label);
  new GlowWhile(new Glow(arrivals as unknown as Arrivals), label as unknown as HTMLElement).update(true);   // a fake DOM double -- it has only what this test reads
  expect("the tab's glow waits", [label.classList.contains("glow"), waiting.length], [false, 1]);
  arrivals.busy = false;
  waiting.splice(0).forEach((w) => w.run());
  expect("and comes on at its turn", label.classList.contains("glow"), true);

  arrivals.busy = true;
  new Flight(arrivals as unknown as Arrivals).land(label as unknown as HTMLElement);   // no copy flying: only the pulse -- a fake DOM double stands in for the real type
  expect("the landing pulse waits", [label.classList.contains("arrive"), waiting.map((w) => w.kind)], [false, ["feature"]]);
  waiting.splice(0).forEach((w) => w.run());
  expect("and lands at its turn", label.classList.contains("arrive"), true);
}

// A rule's "then" can be a task as well as a mix: the tasks on other lanes that repeat, beside the mixes. One that is
// done for good (a one-off, or at its cap) is not offered; a rule on a task opens with that task chosen.
{
  keeps.keepRuleSeen();
  const proto = tab.cards[0]!;
  const task = (id: string, over: Partial<typeof proto>) => ({ ...proto, card: id, share_bp: 0, run: null, by: null, ...over });
  const view: View = {
    ...tab,
    cards: [...tab.cards, task("smoke_roots", { cap: null }), task("smoke_catch", { cap: 2, completions: 2 }), task("forage", { cap: 1, completions: 0 })],
    unlocked: [...tab.unlocked, { category: "card", id: "smoke_roots" }, { category: "card", id: "smoke_catch" }, { category: "card", id: "forage" }],
  };
  const tasks = (root: FakeEl): string[] => q(root, ".cond-task").map((b) => b.dataset.card ?? "");
  const pressed = (root: FakeEl): string[] => q(root, ".cond-mix, .cond-task").filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.textContent);

  const r = rig(view);
  one(r.root, ".rules-new").click();
  expect("a repeating task on another lane is offered, a capped-out or one-off one is not",
    tasks(one(r.root, ".cond")).filter((c) => ["smoke_roots", "smoke_catch", "forage"].includes(c)), ["smoke_roots"]);
  expect("tasks are labelled from the catalog", q(r.root, ".cond-task").map((b) => b.textContent).includes("Smoke roots"), true);
  one(r.root, ".cond-task[data-card=\"smoke_roots\"]").click();
  expect("the task is chosen, no mix is", pressed(r.root), ["Smoke roots"]);
  one(r.root, ".cond-more").click();
  one(r.root, ".cond-store[data-store=\"wood\"]").click();
  one(r.root, ".cond-actions .primary").click();
  expect("Add rule saves a tap_card order", sent(r.decided[0])?.at(-1)?.then, { kind: "tap_card", card: "smoke_roots" });
  expect("the rule before it is untouched", sent(r.decided[0])?.slice(0, 4), tab.orders);

  const own: Order = { ...WOOD, then: { kind: "tap_card", card: "smoke_roots" } };
  const e = rig({ ...view, orders: [...view.orders, own] });
  e.tab.open({ ...view, orders: [...view.orders, own] }, 4);
  expect("an existing task rule opens on its task", pressed(e.root), ["Smoke roots"]);
  expect("its heading names the task", one(e.root, ".cond-heading").textContent, "Run Smoke roots when…");
}
