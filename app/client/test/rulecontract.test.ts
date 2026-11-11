// Blind contract tests for the simple rule editor and the mixes list, written from the contract alone (not from the
// implementation): + New rule opens simple (Do, then When for what the task makes), More options opens the full
// editor, saving a mix never switches the running one, the Mixes list and the strip say what runs.
// Each numbered check is independent; every failure is reported at the end.
import { fakeDocument, FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, Decision, LedgerLine, Mix, Order, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { NewMarks } from "../src/game/marks";
import { Hands } from "../src/ui/hands";
import { MixEditor } from "../src/ui/editor";
import type { PartContext } from "../src/ui/part";
import type { RuleTarget } from "../src/ui/part";
import { RulesTab } from "../src/ui/rules";
import { MixSelector } from "../src/ui/selector";

install();

const failures: string[] = [];
const settle = (): Promise<void> => new Promise((done) => setTimeout(done, 0));
async function check(name: string, run: () => void | Promise<void>): Promise<void> {
  try { await run(); } catch (e) { failures.push(`${name}: ${e instanceof Error ? e.message : String(e)}`); }
}
function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
/** Key order does not matter for a condition. */
function canon(v: unknown): unknown {
  if (Array.isArray(v)) return v.map(canon);
  if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).sort(([a], [b]) => a.localeCompare(b)).map(([k, x]) => [k, canon(x)]));
  return v;
}
function same(label: string, got: unknown, want: unknown): void { expect(label, canon(got), canon(want)); }

const solo = (id: string, card: string): Mix => ({ id, components: [{ kind: "card_share", card, share_bp: 10_000 }] });
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);
const one = (root: FakeEl, sel: string, n = 0): FakeEl => {
  const found = q(root, sel)[n];
  if (!found) throw new Error(`no ${sel} [${n}]`);
  return found;
};
const flat = (s: string): string => s.replace(/\s+/g, " ").trim();

// ---------------------------------------------------------------- rigs

/** The Rules tab's fixture view with its four rules dropped (a clean slate) and a few more tasks in play. */
function viewWith(over: (v: View) => View = (v) => v, orders: Order[] = [], extra: Mix[] = []): View {
  const base = fixtureStep("rulestab", 100, { orders, extra }).view;
  const proto = base.cards[0]!;
  const task = (id: string, o: Partial<typeof proto> = {}) => ({ ...proto, card: id, share_bp: 0, run: null, by: null, ...o });
  const v: View = {
    ...base,
    cards: [...base.cards, task("woodcutting"), task("smoke_roots", { cap: null }), task("smoke_catch", { cap: 2, completions: 2 }),
      task("forage", { cap: 1, completions: 0 })],
  };
  return over(v);
}
const ledgerLine = (v: View, store: string): LedgerLine => ({ ...v.ledger[0]!, store, cap: 20 * Q });
/** A store the player has, with its ledger line. */
const withStore = (v: View, id: string): View => ({
  ...v, ledger: [...v.ledger, ledgerLine(v, id)], unlocked: [...v.unlocked, { category: "store", id }],
});
const tiredRule: Order = { when: fixtureContent.chip_infos.find((c) => c.chip === "tired")!.when, then: { kind: "switch_mix", mix_id: "Rest" } };

/** Put a part's root on the page and return it as the fake element it is under test. */
function mounted(el: HTMLElement): FakeEl {
  document.body.replaceChildren(el);
  const root = fakeDocument.body.firstElementChild;
  if (!root) throw new Error("nothing mounted");
  return root;
}
interface Rig { tab: RulesTab; root: FakeEl; decided: Decision[]; opened: RuleTarget[] }
function rig(view: View, catalog = new Catalog(fixtureContent)): Rig {
  const { ctx, got } = testContext(undefined, catalog);
  ctx.keeps.keepRuleSeen();
  const tab = new RulesTab(ctx);
  const root = mounted(tab.root);
  tab.update(view);
  return { tab, root, decided: got.decided, opened: got.opened };
}
/** Open + New rule and return the editor. */
function newRule(r: Rig): FakeEl {
  one(r.root, ".rules-new").click();
  return one(r.root, ".cond");
}
const doTasks = (cond: FakeEl): string[] => q(cond, ".cond-task").map((b) => b.dataset.card ?? "");
const whenIds = (cond: FakeEl): string[] => q(cond, ".cond-stores .cond-store").map((b) => b.dataset.chip ?? b.dataset.store ?? "");
const pressed = (cond: FakeEl): string[] => q(cond, ".cond-mix, .cond-task, .cond-store").filter((b) => b.getAttribute("aria-pressed") === "true")
  .map((b) => b.dataset.card ?? b.dataset.store ?? b.dataset.chip ?? b.textContent);
const addRule = (cond: FakeEl): FakeEl => one(cond, ".cond-actions .primary");
const sentOrders = (ds: Decision[]): Order[] | null => {
  const d = ds.find((x) => x.kind === "set_orders");
  return d && d.kind === "set_orders" ? d.orders : null;
};
/** "Below a quarter of the cap" to within one raw unit; "until halfway" read loosely: above the low level, no lower than
 *  half the cap, no higher than the cap (the contract does not say halfway of what). */
function quarterThenUp(id: string, capItems: number, when: Order["when"] | undefined): void {
  if (!when || when.kind === "after_time") throw new Error(`not a store condition: ${JSON.stringify(when)}`);
  const w = when as { kind: string; watched: unknown; value: number; release: number };
  const where = `${w.value / Q} until ${w.release / Q} items of ${capItems}`;
  expect(`${id} is the store watched`, w.watched, { kind: "store_value", store: id });
  expect("below", w.kind, "at_most");
  if (Math.abs(w.value - (capItems / 4) * Q) > 1) throw new Error(`low level is not a quarter of the cap: ${where}`);
  if (w.release < (capItems / 2) * Q - 1 || w.release > capItems * Q) throw new Error(`release is not between half the cap and the cap: ${where}`);
}
const chipWhen = (chip: string) => fixtureContent.chip_infos.find((c) => c.chip === chip)!.when;
const store = (s: string, n: number, m: number): Order["when"] =>
  ({ kind: "at_most", watched: { kind: "store_value", store: s }, value: n * Q, release: m * Q });

// ---------------------------------------------------------------- 1: opens empty; Do lists the repeatable tasks

await check("1 opens with nothing chosen, Add rule disabled", () => {
  const r = rig(viewWith());
  const cond = newRule(r);
  expect("nothing pressed", pressed(cond), []);
  expect("Add rule label", addRule(cond).textContent, "Add rule");
  expect("Add rule disabled", addRule(cond).disabled, true);
});

await check("1 Do lists every repeatable task, hands and other lanes", () => {
  const cond = newRule(rig(viewWith()));
  const tasks = doTasks(cond);
  for (const id of ["gather", "tend", "rest", "woodcutting", "shelter", "smoke_roots"]) {
    if (!tasks.includes(id)) throw new Error(`${id} (repeatable) missing from Do: ${JSON.stringify(tasks)}`);
  }
  for (const id of ["stool", "forage", "smoke_catch"]) {
    if (tasks.includes(id)) throw new Error(`${id} (one-off or at its cap) offered in Do: ${JSON.stringify(tasks)}`);
  }
});

await check("1 Do leaves out a retired task", () => {
  const v = viewWith((x) => ({
    ...x, cards: x.cards.filter((c) => c.card !== "tend"), unlocked: [...x.unlocked, { category: "retired", id: "tend" }],
  }));
  const tasks = doTasks(newRule(rig(v)));
  if (tasks.includes("tend")) throw new Error(`retired tend offered: ${JSON.stringify(tasks)}`);
  if (!tasks.includes("gather")) throw new Error("gather vanished with it");
});

await check("1 Do shows no saved mixes, no levels, no rate", () => {
  const cond = newRule(rig(viewWith((v) => v, [], [solo("Sit on stool", "stool")])));
  expect("no mix buttons", q(cond, ".cond-mix").length, 0);
  expect("no levels shown", one(cond, ".cond-levels").shown(), "");
  expect("no rate fact shown", one(cond, ".cond-fact").shown(), "");
});

await check("1 simple view: no levels and no rate even with a store chosen", () => {
  const cond = newRule(rig(viewWith()));
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  expect("no levels shown", one(cond, ".cond-levels").shown(), "");
  expect("no rate fact shown", one(cond, ".cond-fact").shown(), "");
  expect("no mixes", q(cond, ".cond-mix").length, 0);
});

// ---------------------------------------------------------------- 2: When

await check("2 no When row before a task is chosen", () => {
  const cond = newRule(rig(viewWith()));
  expect("When row hidden", [one(cond, ".cond-stores").hidden, q(cond, ".cond-stores .cond-store").length], [true, 0]);
});

await check("2 When: the chips the task makes, then stores of at least two items", () => {
  const v = viewWith((x) => withStore(x, "energy"));
  const cond = newRule(rig(v));
  one(cond, ".cond-task[data-card=\"rest\"]").click();
  expect("rest makes energy: the tired chip, then the energy store", whenIds(cond), ["tired", "energy"]);
  expect("the chip's label", one(cond, ".cond-stores .cond-store").textContent, "tired");
  const other = newRule(rig(v));
  one(other, ".cond-task[data-card=\"gather\"]").click();
  expect("gather makes wood only", whenIds(other), ["wood"]);
});

await check("2 a store of less than two items is not offered", () => {
  const tiny = { store: "spark", label_key: "store.spark", cap: 1 * Q, made_by: ["tend"], hidden: false, bonus_bp: null };
  const content: Content = { ...fixtureContent, store_infos: [...fixtureContent.store_infos, tiny],
    text_entries: [...fixtureContent.text_entries, { key: "store.spark", text: "Spark" }] };
  const v = viewWith((x) => ({ ...x, ledger: [...x.ledger, { ...ledgerLine(x, "spark"), cap: 1 * Q }] }));
  const cond = newRule(rig(v, new Catalog(content)));
  one(cond, ".cond-task[data-card=\"tend\"]").click();
  expect("tend makes stone (20) and spark (1): spark left out", whenIds(cond), ["stone"]);
});

// ---------------------------------------------------------------- 3: a chip saves its own condition

await check("3 a chip saves the chip's own condition; the sentence has no number", () => {
  const v = viewWith((x) => withStore(x, "energy"));
  const r = rig(v);
  const cond = newRule(r);
  one(cond, ".cond-task[data-card=\"rest\"]").click();
  one(cond, ".cond-store[data-chip=\"tired\"]").click();
  expect("sentence", flat(one(cond, ".cond-sentence").shown()), "While tired → Rest");
  expect("Add rule enabled", addRule(cond).disabled, false);
  addRule(cond).click();
  const orders = sentOrders(r.decided);
  if (!orders) throw new Error(`no set_orders sent: ${JSON.stringify(r.decided)}`);
  expect("one rule appended", orders.length, 1);
  same("the chip's own condition, exactly", orders[0]!.when, chipWhen("tired"));
  expect("it runs Rest's solo mix", orders[0]!.then, { kind: "switch_mix", mix_id: "Rest" });
});

// ---------------------------------------------------------------- 4: a store gets default levels

await check("4 a store: below a quarter of the cap, until halfway", () => {
  const r = rig(viewWith());
  const cond = newRule(r);
  one(cond, ".cond-task[data-card=\"tend\"]").click();
  one(cond, ".cond-store[data-store=\"stone\"]").click();   // cap 20 items: under 5, until 10
  addRule(cond).click();
  quarterThenUp("stone", 20, sentOrders(r.decided)?.[0]?.when);
  const w = rig(viewWith());
  const c2 = newRule(w);
  one(c2, ".cond-task[data-card=\"gather\"]").click();
  one(c2, ".cond-store[data-store=\"wood\"]").click();   // cap 40: under 10, until 20
  addRule(c2).click();
  quarterThenUp("wood", 40, sentOrders(w.decided)?.[0]?.when);
});

// ---------------------------------------------------------------- 5: changing task clears what it doesn't answer

await check("5 another task clears a store it doesn't make", () => {
  const cond = newRule(rig(viewWith()));
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  expect("store chosen", pressed(cond).sort(), ["gather", "wood"]);
  one(cond, ".cond-task[data-card=\"tend\"]").click();
  expect("wood cleared, the new task chosen", pressed(cond), ["tend"]);
  expect("Add rule off again", addRule(cond).disabled, true);
});

await check("5 another task clears a chip it doesn't make", () => {
  const v = viewWith((x) => withStore(x, "energy"));
  const cond = newRule(rig(v));
  one(cond, ".cond-task[data-card=\"rest\"]").click();
  one(cond, ".cond-store[data-chip=\"tired\"]").click();
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  expect("chip cleared", pressed(cond), ["gather"]);
  expect("Add rule off again", addRule(cond).disabled, true);
});

await check("5 a store the new task also makes stays chosen", () => {
  const v = viewWith((x) => withStore(x, "smoked"));
  const made = { ...v, cards: v.cards.map((c) => (c.card === "smoke_catch" ? { ...c, cap: null, completions: 0 } : c)) };
  const cond = newRule(rig(made));
  one(cond, ".cond-task[data-card=\"smoke_roots\"]").click();
  one(cond, ".cond-store[data-store=\"smoked\"]").click();
  one(cond, ".cond-task[data-card=\"smoke_catch\"]").click();
  expect("smoked still chosen", pressed(cond).includes("smoked"), true);
  expect("Add rule still on", addRule(cond).disabled, false);
});

// ---------------------------------------------------------------- 6: Add rule on hands / other lane

await check("6 hands task: a rule running its solo mix; an equal saved one is reused", () => {
  const r = rig(viewWith());
  const cond = newRule(r);
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  addRule(cond).click();
  expect("only set_orders", r.decided.map((d) => d.kind), ["set_orders"]);
  expect("runs the saved solo mix", sentOrders(r.decided)?.[0]?.then, { kind: "switch_mix", mix_id: "Gather by hand" });
});

await check("6 hands task with no saved solo mix: one named by its label is saved first", () => {
  const content: Content = { ...fixtureContent, store_infos: fixtureContent.store_infos.map((s) => (s.store === "wood" ? { ...s, made_by: ["gather", "woodcutting"] } : s)) };
  const r = rig(viewWith(), new Catalog(content));
  const cond = newRule(r);
  one(cond, ".cond-task[data-card=\"woodcutting\"]").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  addRule(cond).click();
  expect("save the mix, then the rule", r.decided.map((d) => d.kind), ["save_mix", "set_orders"]);
  const saved = r.decided[0];
  expect("a solo mix named by the label", saved?.kind === "save_mix" ? saved.mix : null, solo("Cut wood", "woodcutting"));
  expect("the rule runs it", sentOrders(r.decided)?.[0]?.then, { kind: "switch_mix", mix_id: "Cut wood" });
});

await check("6 a task on another lane saves a tap_card rule", () => {
  const r = rig(viewWith());
  const cond = newRule(r);
  one(cond, ".cond-task[data-card=\"shelter\"]").click();
  one(cond, ".cond-more").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  addRule(cond).click();
  expect("no mix saved", r.decided.map((d) => d.kind), ["set_orders"]);
  expect("tap_card", sentOrders(r.decided)?.[0]?.then, { kind: "tap_card", card: "shelter" });
});

// ---------------------------------------------------------------- 7: More options

await check("7 More options hides itself and shows the saved mixes (not a listed task's solo)", () => {
  const r = rig(viewWith((v) => v, [], [solo("Sit on stool", "stool")]));
  const cond = newRule(r);
  expect("More options is offered", [one(cond, ".cond-more").hidden, one(cond, ".cond-more").textContent], [false, "More options"]);
  one(cond, ".cond-more").click();
  expect("it hides itself", one(cond, ".cond-more").hidden, true);
  const mixes = q(cond, ".cond-mix").map((b) => b.textContent);
  expect("player's mix and an unlisted task's solo shown", [...mixes].sort(), ["Morning <b>fire</b> & wood", "Sit on stool"].sort());
  for (const solos of ["Gather by hand", "Rest by the fire", "Rest"]) {
    if (mixes.includes(solos)) throw new Error(`solo mix of a listed task shown: ${solos}`);
  }
});

await check("7 More options: When shows every chip the save has shown and every store of two items", () => {
  const v = viewWith((x) => ({ ...withStore(x, "energy"), chips: [], chips_seen: ["cold", "tired"] }));
  const cond = newRule(rig(v));
  one(cond, ".cond-more").click();
  const ids = whenIds(cond);
  expect("the tired chip, shown before and off now", ids.includes("tired"), true);
  expect("the cold chip, though no task makes warmth", ids.includes("cold"), true);
  expect("not a chip the save has never shown", ids.includes("warm"), false);
  for (const s of ["wood", "stone", "energy"]) {
    if (!ids.includes(s)) throw new Error(`store ${s} missing from When: ${JSON.stringify(ids)}`);
  }
});

await check("7 More options: levels (folded) and the rate fact come back", () => {
  const cond = newRule(rig(viewWith()));
  one(cond, ".cond-task[data-card=\"gather\"]").click();
  one(cond, ".cond-more").click();
  one(cond, ".cond-store[data-store=\"wood\"]").click();
  expect("levels row present, body folded", [one(cond, ".cond-levels").hidden, one(cond, ".cond-fold").hidden, one(cond, ".cond-fold-body").hidden], [false, false, true]);
  expect("the rate fact is no longer hidden", one(cond, ".cond-fact").hidden, false);
});

// ---------------------------------------------------------------- 8: editing an existing rule

await check("8 editing a store rule opens the full editor", () => {
  const rules: Order[] = [{ when: store("wood", 10, 20), then: { kind: "switch_mix", mix_id: "Gather by hand" } }];
  const v = viewWith((x) => x, rules);
  const r = rig(v);
  one(r.root, ".rules-list .rule-cond", 0).click();
  const cond = one(r.root, ".cond");
  expect("More options not offered", one(cond, ".cond-more").hidden, true);
  expect("mixes shown", q(cond, ".cond-mix").length > 0, true);
  expect("levels shown", one(cond, ".cond-levels").hidden, false);
  expect("When row shown", one(cond, ".cond-stores").hidden, false);
});

await check("8 editing a chip's rule shows only Do, the sentence and Remove", () => {
  const rules: Order[] = [{ when: chipWhen("tired"), then: { kind: "switch_mix", mix_id: "Rest" } }];
  const r = rig(viewWith((x) => x, rules));
  one(r.root, ".rules-list .rule-cond", 0).click();
  const cond = one(r.root, ".cond");
  expect("no When, no levels, no More options, no rate",
    [one(cond, ".cond-stores").hidden, one(cond, ".cond-levels").hidden, one(cond, ".cond-more").hidden, one(cond, ".cond-fact").shown()], [true, true, true, ""]);
  expect("Do is shown", q(cond, ".cond-task").length > 0 || q(cond, ".cond-mix").length > 0, true);
  expect("Remove is there", one(cond, ".cond-actions .danger").hidden, false);
  expect("the sentence", flat(one(cond, ".cond-sentence").shown()), "While tired → Rest");
  expect("no number anywhere", /\d/.test(cond.shown()), false);
});

// ---------------------------------------------------------------- 9: the Rules tab has no mix chips

await check("9 no mix chips; a slot is set only through its picker", () => {
  const rules: Order[] = [{ when: store("wood", 10, 20), then: { kind: "switch_mix", mix_id: "Gather by hand" } }];
  const r = rig(viewWith((x) => x, rules));
  expect("no mix chips", q(r.root, ".mix-chip").length, 0);
  expect("no picker until the slot is tapped", q(r.root, ".rule-picker").length, 0);
  one(r.root, ".rule-slot", 0).click();
  const picks = q(r.root, ".rule-picker .selector-run");
  if (picks.length === 0) throw new Error("the slot opened no picker");
  picks.find((b) => b.textContent.endsWith("Rest"))!.click();
  expect("the pick re-points the rule", sentOrders(r.decided)?.[0]?.then, { kind: "switch_mix", mix_id: "Rest" });
});

// ---------------------------------------------------------------- 10: saving in the mix editor never switches

function editorRig(view: View): { editor: MixEditor; root: FakeEl; decided: Decision[] } {
  const { ctx, got } = testContext();
  ctx.actions.dryRun = () => Promise.resolve(view);   // the forecast of any edit: the view itself
  const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
  const root = mounted(editor.root);
  editor.update(view);
  return { editor, root, decided: got.decided };
}
function nameIt(root: FakeEl, name: string): void {
  const input = one(root, "input");
  input.value = name;
  input.dispatchEvent(new FakeEvent("input"));
}
const button = (root: FakeEl, text: string): FakeEl => {
  const b = q(root, "button").find((x) => flat(x.textContent) === text && !x.hidden);
  if (!b) throw new Error(`no visible "${text}" button; buttons: ${JSON.stringify(q(root, "button").map((x) => [x.textContent, x.hidden]))}`);
  return b;
};
const noSwitch = (label: string, ds: Decision[]): void => {
  if (ds.length === 0) throw new Error(`${label}: nothing was decided`);
  if (ds.some((d) => d.kind === "switch_mix")) throw new Error(`${label}: sent switch_mix: ${JSON.stringify(ds.map((d) => d.kind))}`);
};

await check("10 a new mix is saved without switching", async () => {
  const v = viewWith();
  const e = editorRig(v);
  e.editor.showNew(v);
  nameIt(e.root, "Night");
  { const b = button(e.root, "Gather by hand"); b.dispatchEvent(pointer("pointerdown", 5, 5)); b.dispatchEvent(pointer("pointerup", 5, 5)); b.click(); }
  await settle();
  button(e.root, "Save").click();
  await settle();
  noSwitch("new mix", e.decided);
  expect("saved", e.decided.some((d) => d.kind === "save_mix"), true);
});

await check("10 Save as new is saved without switching", async () => {
  const v = viewWith();
  const e = editorRig(v);
  e.editor.show(v, v.active_mix_id);
  nameIt(e.root, "Copy of mine");
  button(e.root, "Save as new").click();
  await settle();
  noSwitch("save as new", e.decided);
  expect("saved under the new name", e.decided.some((d) => d.kind === "save_mix" && d.mix.id === "Copy of mine"), true);
});

await check("10 editing another mix is saved without switching", async () => {
  const v = viewWith();
  const e = editorRig(v);
  e.editor.show(v, "Rest by the fire");
  button(e.root, "Save").click();
  await settle();
  noSwitch("another mix", e.decided);
  const running = editorRig(v);   // the mix a rule is running: still not the player's own
  running.editor.show(v, v.running_mix_id);
  button(running.root, "Save").click();
  await settle();
  noSwitch("the rule-run mix", running.decided);
});

await check("10 renaming the player's own mix keeps it the player's own", async () => {
  const v = viewWith();
  const e = editorRig(v);
  e.editor.show(v, v.active_mix_id);
  nameIt(e.root, "Day");
  button(e.root, "Save").click();
  await settle();
  const sw = e.decided.find((d) => d.kind === "switch_mix");
  expect("switch to the new name", sw && sw.kind === "switch_mix" ? sw.mix_id : null, "Day");
  expect("the old one deleted", e.decided.some((d) => d.kind === "delete_mix"), true);
});

// ---------------------------------------------------------------- 11: Mixes list

function listRows(view: View): { name: string; text: string; run: string }[] {
  const { ctx } = testContext();
  const sel = new MixSelector(ctx);
  sel.show(view);
  const root = mounted(sel.root);
  return q(root, ".selector-row").map((row) => ({
    name: one(row, ".selector-name").textContent, text: flat(row.shown()), run: flat(q(row, ".selector-run")[0]?.shown() ?? ""),
  }));
}

await check("11 a rule is running: its row says ● running, every other runnable row says Run", () => {
  const v = viewWith((x) => x, [tiredRule]);
  expect("a rule runs Rest", v.running_mix_id, "Rest");
  const rows = listRows(v);
  const running = rows.find((r) => r.name === "Rest")!;
  if (!running.text.includes("●") || !running.text.includes("running")) throw new Error(`running row: ${JSON.stringify(running)}`);
  for (const r of rows.filter((x) => x.name !== "Rest" && x.name !== v.active_mix_id && !v.greyed_mix_ids.includes(x.name))) {
    if (!r.run.endsWith("Run")) throw new Error(`${r.name} says: ${r.run}`);
    if (r.text.includes("●")) throw new Error(`${r.name} carries the running dot`);
  }
});

await check("11 the player's own mix running: ● and how long it runs; others Run", () => {
  const v = viewWith((x) => ({ ...x, running_mix_id: x.active_mix_id }));
  const rows = listRows(v);
  const own = rows.find((r) => r.name === v.active_mix_id)!;
  if (!own.text.includes("●") || !/runs/.test(own.text) || own.text.includes("running")) throw new Error(`own row: ${JSON.stringify(own)}`);
  for (const r of rows.filter((x) => x.name !== v.active_mix_id)) {
    if (!r.run.endsWith("Run")) throw new Error(`${r.name} says: ${r.run}`);
  }
  const open = listRows({ ...v, runs_out_at: null }).find((r) => r.name === v.active_mix_id)!;
  if (!open.text.includes("runs as set")) throw new Error(`no end time: ${JSON.stringify(open)}`);
});

// ---------------------------------------------------------------- 12: strip

await check("12 strip: Mixes ▾ button and the running mix's name", () => {
  const { ctx } = testContext();
  const hands = new Hands(ctx);
  const root = mounted(hands.root);
  const v = viewWith((x) => x, [tiredRule]);
  hands.update(v);
  hands.tick(100);
  if (!q(root, "button").some((b) => flat(b.textContent) === "Mixes ▾")) {
    throw new Error(`buttons: ${JSON.stringify(q(root, "button").map((b) => b.textContent))}`);
  }
  expect("a rule runs Rest", one(root, ".hands-mix-name").textContent, "Rest");
  const own = viewWith((x) => ({ ...x, running_mix_id: x.active_mix_id }));
  hands.update(own);
  expect("the player's own", one(root, ".hands-mix-name").textContent, own.active_mix_id);
});

for (const f of failures) console.log(`FAIL ${f}`);
if (failures.length > 0) throw new Error(`${failures.length} contract check(s) failed`);
