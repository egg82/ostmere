// The opening's slower reveal, as a contract (docs/design/opening-screen.md): a thing is drawn when it first means
// something, and stays once drawn. Written blind, from the contract alone, through the parts' public surface: a chip
// waits for its offered_after; the Camp bar waits for its first level (arriving, then its level burst, only when that
// level is crossed live); the strip's mix row opens with a name and a bar, and Edit, Mixes and runs each come when
// they first mean something; a ledger line is drawn for the reasons it has to be and then stays, its store kept once
// for the account; the Rules tab glows only for a rule seen on, with the tab never opened.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent, Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, LedgerLine, Step, Unlock, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Hands } from "../src/ui/hands";
import { Ledger } from "../src/ui/ledger";
import { Screen } from "../src/ui/screen";
import { LADDER } from "../src/ui/ladder";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

const LEVEL = LADDER.level.pulse ?? "";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const mid = fixtureStep("mid", AT);

/** The one node mounted on the page: a real-typed root seen as the fake element it is. */
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

/** Drawn: neither the node nor anything above it up to `top` is hidden. */
function drawn(node: FakeEl, top: FakeEl): boolean {
  for (let n: FakeEl | null = node; n; n = n.parent) {
    if (n.hidden) return false;
    if (n === top) return true;
  }
  return true;
}
const drawnTexts = (top: FakeEl, selector: string): string[] => top.querySelectorAll(selector).filter((n) => drawn(n, top)).map((n) => n.textContent);

function screenOf(cat: Catalog, keeps: Keeps = new Keeps()): { screen: Screen; top: FakeEl } {
  const screen = new Screen(cat, () => undefined, () => Promise.resolve(null), keeps);
  return { screen, top: mounted(screen.root) };
}
const stepWith = (view: View): Step => ({ ...mid, view });
const unlockOf = (category: Unlock["category"], id: string): Unlock => ({ category, id });

// ---- 2. A chip waits for its offered_after; one with none is drawn as soon as it is on.
{
  const gated = new Catalog({
    ...fixtureContent,
    chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "cold" ? { ...c, offered_after: unlockOf("card", "not_yet") } : c)),
  });
  const cold = gated.label(gated.chips.get("cold")?.label_key);
  const warm = gated.label(gated.chips.get("warm")?.label_key);
  const both: View = { ...mid.view, chips: ["cold", "warm"] };
  const chips = (top: FakeEl): string[] => drawnTexts(top, ".chip");
  const has = (top: FakeEl, label: string): boolean => chips(top).some((t) => t.includes(label));

  const { screen, top } = screenOf(gated);
  screen.show(stepWith(both));
  screen.tick(AT);
  expect("chip: on but its offered_after is not unlocked: not drawn", has(top, cold), false);
  expect("chip: with no offered_after, drawn as soon as it is on", has(top, warm), true);

  screen.show(stepWith({ ...both, at: AT + 1, unlocked: [...both.unlocked, unlockOf("card", "not_yet")] }));
  screen.tick(AT + 1);
  expect("chip: once unlocked, drawn", has(top, cold), true);
  expect("chip: and the other stays", has(top, warm), true);

  const off = screenOf(gated);
  off.screen.show(stepWith({ ...both, chips: ["warm"], unlocked: [...both.unlocked, unlockOf("card", "not_yet")] }));
  off.screen.tick(AT);
  expect("chip: unlocked but not on: not drawn", has(off.top, cold), false);
}

// ---- 3. The Camp bar: hidden at level 0, drawn from level 1; arrival then its level burst only when crossed live.
{
  const flat = (items: number): LedgerLine => ({
    store: "camp", segment: { start: AT, start_value: items * Q, rate: 0, limit: null }, net_per_hour: 0, contributions: [],
    empties_at: null, fills_at: null, falling: false, covered: false, starved: false, cap: 1000 * Q,
  });
  const at = (items: number, t = AT): View => ({ ...mid.view, at: t, ledger: mid.view.ledger.map((l) => (l.store === "camp" ? flat(items) : l)) });
  const first = fixtureContent.camp?.camp_levels[0];
  if (!first) throw new Error("fixture: no camp level");
  const below = at(Math.floor(first.at / Q) - 10);
  const reached = at(Math.ceil(first.at / Q) + 10);
  const campOf = (top: FakeEl): FakeEl | undefined => top.querySelectorAll(".camp").find((n) => drawn(n, top));

  const closed = screenOf(catalog);
  closed.screen.show(stepWith(below));
  closed.screen.tick(AT);
  expect("camp: level 0: hidden", campOf(closed.top) !== undefined, false);

  // Crossing from 0 to 1 live: it is drawn, arrives, and then flourishes.
  const live = screenOf(catalog);
  live.screen.show(stepWith(below));
  live.screen.tick(AT);
  live.screen.show(stepWith({ ...reached, at: AT + 1 }));
  const seen: { arrive: boolean; flourish: boolean }[] = [];
  for (let k = 0; k < 600; k += 1) {
    live.screen.tick(AT + 1 + k / 10);
    const n = campOf(live.top);
    seen.push({ arrive: n?.classList.contains("arrive") ?? false, flourish: n?.classList.contains(LEVEL) ?? false });
  }
  expect("camp: crossing live: drawn", campOf(live.top) !== undefined, true);
  expect("camp: crossing live: it arrives", seen.some((s) => s.arrive), true);
  expect("camp: crossing live: then a flourish", seen.some((s) => s.flourish), true);
  const firstFlourish = seen.findIndex((s) => s.flourish);
  const firstArrive = seen.findIndex((s) => s.arrive);
  expect("camp: the arrival comes first", firstArrive >= 0 && firstArrive <= firstFlourish, true);

  // A page opened already at level 1: drawn, with neither.
  const opened = screenOf(catalog);
  opened.screen.show(stepWith(reached));
  const quiet: boolean[] = [];
  for (let k = 0; k < 600; k += 1) {
    opened.screen.tick(AT + k / 10);
    const n = campOf(opened.top);
    quiet.push(n?.classList.contains("arrive") === true || n?.classList.contains(LEVEL) === true);
  }
  expect("camp: opened at level 1: drawn", campOf(opened.top) !== undefined, true);
  expect("camp: opened at level 1: no arrival, no flourish", quiet.some((q) => q), false);
}

// ---- 4. The strip's mix row: name and bar always; Edit, Mixes and runs each when they first mean something, then they stay.
{
  const mixId = mid.view.active_mix_id;
  const first = mid.view.cards.filter((c) => c.card === "gather" || c.card === "tend");
  const unlockedWithoutLedger = mid.view.unlocked.filter((u) => !(u.category === "feature" && u.id === "ledger"));
  const quiet: View = {
    ...mid.view, cards: first, greyed_mix_ids: [], mixes: mid.view.mixes.slice(0, 1), unlocked: unlockedWithoutLedger, running_mix_id: mixId,
  };
  const gather = first.find((c) => c.card === "gather");
  if (!gather || mixId === null) throw new Error("fixture: no gather card or running mix");
  const extra = (id: string): Card => ({ ...gather, card: id, share_bp: 0, run: null, by: null });
  const extraOf = (id: string): Card => mid.view.cards.find((c) => c.card === id) ?? extra(id);

  function strip(view: View): { part: Hands; top: FakeEl } {
    const part = new Hands(testContext().ctx);
    const top = mounted(part.root);
    part.update(view);
    part.tick(AT);
    return { part, top };
  }
  interface Row { name: boolean; bar: boolean; edit: boolean; mixes: boolean; runs: boolean }
  function row(top: FakeEl): Row {
    const text = top.shown();
    return {
      name: drawnTexts(top, ".hands-mix-name").some((t) => t.length > 0),
      bar: top.querySelectorAll(".share-bar").some((n) => drawn(n, top)),
      edit: top.querySelectorAll(".hands-edit").some((n) => drawn(n, top) && n.textContent.includes("Edit")),
      mixes: text.includes("Mixes"),
      runs: drawnTexts(top, ".hands-runs").some((t) => t.startsWith("runs")),
    };
  }
  const bare: Row = { name: true, bar: true, edit: false, mixes: true, runs: false };

  const a = strip(quiet);
  expect("strip: bare, the name and the bar only", row(a.top), bare);

  /** Updating through `later` shows `want` in the row; going back to `quiet` keeps it. */
  function opens(label: string, later: View, want: Partial<Row>): void {
    const s = strip(quiet);
    s.part.update(later);
    s.part.tick(AT + 1);
    expect(`strip: ${label}`, row(s.top), { ...bare, ...want });
    s.part.update(quiet);
    s.part.tick(AT + 2);
    expect(`strip: ${label}, and it stays`, row(s.top), { ...bare, ...want });
  }
  opens("a greyed mix brings Edit", { ...quiet, greyed_mix_ids: [mixId] }, { edit: true });
  opens("an action card outside the first mix brings Edit", { ...quiet, cards: [...first, extraOf("woodcutting")] }, { edit: true });
  opens("the ledger unlocked brings runs", { ...quiet, unlocked: [...quiet.unlocked, unlockOf("feature", "ledger")] }, { runs: true });

  // What does not bring Edit: a craft, a narrative, a bench action, a first-mix card.
  for (const id of ["stool", "look", "shelter"]) {
    const card = mid.view.cards.find((c) => c.card === id);
    if (!card) throw new Error(`fixture: no ${id} card`);
    const s = strip({ ...quiet, cards: [...first, card] });
    expect(`strip: ${id} in play does not bring Edit`, row(s.top).edit, false);
  }
  expect("strip: the first saved mix brings Mixes", row(strip(quiet).top).mixes, true);
  expect("strip: without the ledger, no runs", row(strip(quiet).top).runs, false);
}

// ---- 5. A ledger line is drawn for the reasons it has to be, then stays; its store is kept once, for the account.
{
  const flat = (store: string, over: Partial<LedgerLine> = {}): LedgerLine => ({
    store, segment: { start: AT, start_value: 10 * Q, rate: 0, limit: null }, net_per_hour: 0, contributions: [], empties_at: null, fills_at: null,
    falling: false, covered: false, starved: false, cap: 100 * Q, ...over,
  });
  const falling = (store: string, runner: string, extraRunners: string[] = []): LedgerLine => flat(store, {
    segment: { start: AT, start_value: 50 * Q, rate: -60 * R, limit: 0 }, net_per_hour: -60 * R, falling: true,
    contributions: [runner, ...extraRunners].map((r) => ({ runner: r, per_hour: -30 * R })),
  });
  const rising = (store: string, items: number, cap: number, runner = "gather"): LedgerLine => flat(store, {
    segment: { start: AT, start_value: items * Q, rate: 30 * R, limit: cap * Q }, net_per_hour: 30 * R, contributions: [{ runner, per_hour: 30 * R }], cap: cap * Q,
  });
  const hands = (running: string | null) => ({ lane: "hands", running_card: running, completes_at: null, order: null });
  const withLine = (line: LedgerLine, running: string | null = null, extraUnlocked: Unlock[] = []): View => ({
    ...mid.view, at: AT, ledger: [line], lanes: [hands(running)], orders: [], orders_on: [],
    unlocked: [...mid.view.unlocked, unlockOf("feature", "ledger"), unlockOf("store", line.store), ...extraUnlocked],
  });

  interface Rig { part: Ledger; top: FakeEl; sent: Flat[] }
  function rig(account: Flat = NEW_FLAT): Rig {
    const sent: Flat[] = [];
    const { ctx } = testContext();
    const part = new Ledger({ ...ctx, keeps: keepsOf(account, sent) });
    return { part, top: mounted(part.root), sent };
  }
  const names = (r: Rig): string[] => drawnTexts(r.top, ".line-name");
  function draw(r: Rig, view: View, t = AT): void {
    r.part.update(view, null);
    r.part.tick(t);
  }
  function isDrawn(label: string, view: View, want: boolean, account: Flat = NEW_FLAT): void {
    const r = rig(account);
    draw(r, view);
    const store = view.ledger[0]?.store ?? "";
    expect(`line: ${label}`, names(r).some((n) => n.includes(catalog.storeLabel(store))), want);
  }

  isDrawn("flat, nothing asked: not drawn", withLine(flat("warmth")), false);
  isDrawn("rising and not full: not drawn", withLine(rising("warmth", 20, 100)), false);
  isDrawn("starved: drawn", withLine(flat("warmth", { starved: true })), true);
  isDrawn("falling from a contribution that is not the hands' running card: drawn", withLine(falling("warmth", "tend")), true);
  isDrawn("falling from a contribution that is not the hands' running card, another also running: drawn", withLine(falling("warmth", "tend", ["smoke_catch"]), "tend"), true);
  isDrawn("falling only from the hands' running card: not drawn", withLine(falling("warmth", "tend"), "tend"), false);
  isDrawn("carrying an inline offer: drawn", withLine(rising("catch", 2, 6, "forage"), null, [unlockOf("card", "smoke_catch")]), true);
  isDrawn("the same line with no offer yet: not drawn", withLine(rising("catch", 2, 6, "forage")), false);
  isDrawn("full while fed: drawn", withLine(rising("warmth", 100, 100)), true);
  isDrawn("full but not fed: not drawn", withLine(flat("warmth", { segment: { start: AT, start_value: 100 * Q, rate: 0, limit: null } })), false);
  isDrawn("covered: drawn", withLine(flat("warmth", { covered: true })), true);
  isDrawn("its store already kept: drawn", withLine(flat("warmth")), true, { ...NEW_FLAT, ledger_lines: ["warmth"] });
  isDrawn("another store kept: not drawn", withLine(flat("warmth")), false, { ...NEW_FLAT, ledger_lines: ["stone"] });

  // Once drawn, it stays, and its store is sent once.
  {
    const r = rig();
    draw(r, withLine(flat("warmth")));
    expect("line: before its reason, nothing is kept", [names(r).length, r.sent.length], [0, 0]);
    draw(r, withLine(flat("warmth", { starved: true })), AT + 1);
    expect("line: drawn on its reason", names(r).length, 1);
    expect("line: its store is sent, once", r.sent.map((p) => p.ledger_lines), [["warmth"]]);
    draw(r, withLine(flat("warmth")), AT + 2);
    draw(r, withLine(flat("warmth", { starved: true })), AT + 3);
    draw(r, withLine(flat("warmth")), AT + 4);
    expect("line: once drawn, it stays", names(r).length, 1);
    expect("line: and its store is not sent again", r.sent.map((p) => p.ledger_lines), [["warmth"]]);
  }

  // With empty keeps (a page that has kept nothing), the lines that ask something still show; the rest wait.
  {
    const r = rig();
    const asks = withLine(flat("warmth", { starved: true }));
    draw(r, { ...asks, ledger: [...asks.ledger, flat("stone")] });
    expect("line: empty keeps: the asking line shows, the quiet one waits", names(r).map((n) => n.includes(catalog.storeLabel("warmth"))), [true]);
  }
}

// ---- 6. The Rules tab glows only with a rule, rule_seen, and the tab never opened.
{
  const rule = fixtureStep("covered", AT).view;
  const withRule: View = { ...mid.view, orders: rule.orders, orders_on: rule.orders_on };
  const label = catalog.text.get("ui.heading.orders");
  function glows(view: View, account: Flat): boolean | null {
    const { screen, top } = screenOf(catalog, keepsOf(account));
    screen.show(stepWith(view));
    for (let k = 0; k < 20; k += 1) screen.tick(AT + k);
    const tab = top.querySelectorAll(".tab").find((n) => n.textContent.includes(label));
    return tab ? tab.classList.contains("glow") : null;
  }
  for (const exists of [false, true]) {
    for (const seen of [false, true]) {
      for (const opened of [false, true]) {
        const want = exists && seen && !opened;
        const got = glows(exists ? withRule : mid.view, { ...NEW_FLAT, rule_seen: seen, rules_opened: opened });
        expect(`rules glow: rule ${exists}, seen ${seen}, opened ${opened}: tab found`, got !== null, true);
        expect(`rules glow: rule ${exists}, seen ${seen}, opened ${opened}`, got, want);
      }
    }
  }
}
