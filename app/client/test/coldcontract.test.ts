// Blind contract tests, written from the contract alone (not the implementation), ported to the story strip: the strip
// shows the newest line once read, a step's lines each stay until their reading time, the Chronicle button gets a dot for a
// line that left unseen, and the lone first card is `first untapped`. The CSS items read src/game.css.
import { readFileSync } from "node:fs";
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import type { FakeEl } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Card, LogLine, View } from "../src/api/types";
import { readingMs } from "../src/game/reading";
import { NewMarks } from "../src/game/marks";
import { Cards } from "../src/ui/cards";
import { PHONE } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";
import { Story } from "../src/ui/story";
import { el } from "../src/ui/dom";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { fixtureContent } from "../fixtures/content";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// ---- environment: a clock, a phone switch, and window listeners the page may use for touches ----
let now = 0;
let phone = false;
type Listener = (e: FakeEvent) => void;
const windowListeners: { type: string; f: Listener }[] = [];
Object.assign(globalThis, {
  performance: { now: () => now },
  window: {
    addEventListener: (type: string, f: Listener) => { windowListeners.push({ type, f }); },
    removeEventListener: () => undefined,
    matchMedia: (query: string) => ({ matches: query === PHONE ? phone : false, addEventListener: () => undefined }),
    setTimeout, clearTimeout, innerWidth: 400, innerHeight: 800,
  },
});

/** A touch or key anywhere on the page: to the document, and to any window listener. */
function touch(type: "pointerdown" | "keydown", on: FakeEl = fakeDocument.body): void {
  const e = new FakeEvent(type);
  on.dispatchEvent(e);
  for (const l of windowListeners) if (l.type === type) l.f(e);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const KEYS = ["line.1", "line.2", "line.3", "line.4", "line.5"];

/** The element mounted first on the fake body, typed as the fake's own. */
function mounted(): FakeEl {
  const el = fakeDocument.body.firstElementChild;
  if (!el) throw new Error("nothing mounted");
  return el;
}

function newStory(onPhone: boolean): { story: Story; ui: FakeEl } {
  phone = onPhone;
  now = 0;
  const story = new Story(testContext().ctx);
  const ui = el("div");
  ui.append(story.head, story.root, story.book);
  document.body.replaceChildren(ui);
  return { story, ui: mounted() };
}
const strip = (ui: FakeEl): string[] => Array.from(ui.querySelector("ol.lines")?.children ?? [], (n) => n.textContent ?? "");
const settle = (story: Story): void => { for (let i = 0; i < 12; i += 1) story.tick(0); };
const opener = (root: FakeEl): FakeEl => {
  const b = root.querySelector("button[data-tab=\"book\"]");
  if (!b) throw new Error("no Book button");
  return b;
};
/** A dot is a `.new-dot` element in the story, or the class on the button itself. */
const dotted = (root: FakeEl): boolean =>
  root.querySelectorAll(".new-dot").some((n) => !n.hidden) || opener(root).classList.contains("new-dot");
const longest = Math.max(...KEYS.map((k) => readingMs(text(k))));

// ---- 1. the strip once read ----
for (const onPhone of [true, false]) {
  const { story, ui } = newStory(onPhone);
  story.appendKeys(KEYS);
  now = longest + 1;
  settle(story);
  expect(`${onPhone ? "phone" : "wider"}: the newest alone once all are read`, strip(ui), ["line.5"].map(text));
}

// ---- 2. never removed before its reading time (a live step's lines, through the screen's arrival queue) ----
for (const onPhone of [true, false]) {
  phone = onPhone;
  now = 0;
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  const ui = mounted();
  const shownNow = (): string[] => Array.from(ui.querySelector("ol.lines")?.children ?? [], (n) => n)
    .filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");
  screen.show({ ...fixtureStep("covered", 100), lines: [] });
  const live = ["line.1", "line.2", "line.3"].map((key, seq): LogLine => ({ at: 200, seq, key, card: null }));
  now = 1000;
  screen.show({ ...fixtureStep("covered", 200), lines: live });
  screen.tick(0);
  expect("the step's first line shows", shownNow(), [text("line.1")]);
  now = 1000 + readingMs(text("line.1")) - 1;
  screen.tick(0);
  expect("an unread line stays", shownNow(), [text("line.1")]);
  now = 1000 + readingMs(text("line.1")) + 1;
  screen.tick(0);
  expect("once read, the next takes its place", shownNow(), [text("line.2")]);
}

// ---- 3. the Chronicle dot ----
{
  const { story, ui } = newStory(false);
  story.appendKeys(["line.1"]);
  now = 1000;
  story.appendKeys(["line.4"]);
  now = readingMs(text("line.1"));
  settle(story);
  expect("sanity: a line left the strip", strip(ui).includes(text("line.1")), false);
  expect("a line left with no touch since it showed: the Chronicle button has a dot", dotted(ui), true);

  touch("pointerdown", opener(ui));
  expect("a pointerdown on the button removes the dot", dotted(ui), false);
}
{
  const { story, ui } = newStory(false);
  story.appendKeys(["line.1"]);
  now = 1000;
  story.appendKeys(["line.4"]);
  now = readingMs(text("line.1"));
  settle(story);
  expect("(precondition) dotted again", dotted(ui), true);
  touch("keydown", opener(ui));
  expect("a keydown on the button removes the dot", dotted(ui), false);
}
{
  const { story, ui } = newStory(false);
  story.appendKeys(["line.1"]);
  now = 500;
  touch("pointerdown");
  now = 1000;
  story.appendKeys(["line.4"]);
  now = readingMs(text("line.1"));
  settle(story);
  expect("sanity: a line left after the touch", strip(ui).includes(text("line.1")), false);
  expect("a line that leaves after a pointerdown adds no dot", dotted(ui), false);
}
{
  const { story, ui } = newStory(false);
  story.appendKeys(["line.1"]);
  now = 500;
  touch("keydown");
  now = 1000;
  story.appendKeys(["line.4"]);
  now = readingMs(text("line.1"));
  settle(story);
  expect("a line that leaves after a keydown adds no dot", dotted(ui), false);
}
{
  // The chronicle open while the line leaves.
  const { story, ui } = newStory(false);
  story.appendKeys(["line.1"]);
  opener(ui).click();
  now = 1000;
  story.appendKeys(["line.4"]);
  now = readingMs(text("line.1"));
  settle(story);
  expect("sanity: a line left the strip", strip(ui).includes(text("line.1")), false);
  expect("a line that leaves while the chronicle is open adds no dot", dotted(ui), false);
}
{
  // A line restored on load: the restored line leaves when a live one pushes it out.
  phone = false;
  now = 0;
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  const ui = mounted();
  screen.restore(["line.1", "line.2", "line.3"].map((key) => ({ key, at: 0 })));
  screen.show({ ...fixtureStep("mid", 100), lines: [] });   // a view short of the end: no end line follows
  const lines = (): string[] => Array.from(ui.querySelector("ol.lines")?.children ?? [], (n) => n.textContent ?? "");
  now = 1000;
  const live: LogLine = { at: 200, seq: 50, key: "line.4", card: null };
  screen.show({ ...fixtureStep("mid", 200), lines: [live] });
  now = 100000;
  for (let i = 0; i < 12; i += 1) screen.tick(0);
  expect("sanity: the restored line has left the strip", lines().includes(text("line.1")), false);
  expect("a restored line that leaves adds no dot", dotted(ui), false);
}

// ---- 4. the first card ----
{
  const AT = 100;
  const base: View = fixtureStep("restrule", AT).view;
  const card = (id: string, over: Partial<Card> = {}): Card => ({
    card: id, completions: 0, cap: 1, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null,
    completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, needs: [], ...over,
  });
  const only = (c: Card[], completed: View["completed"] = []): View => ({ ...base, cards: c, completed });
  const classes = (cards: Cards, id: string): string[] => (cards.node(id)?.closest(".card")?.className ?? "").split(" ").filter(Boolean);
  const draw = (v: View): Cards => {
    const { ctx } = testContext();
    const cards = new Cards(ctx, new NewMarks());
    document.body.replaceChildren(cards.root);
    cards.update(v, null);
    return cards;
  };
  const untapped = (c: Cards, id: string): boolean => classes(c, id).includes("untapped");

  const lone = draw(only([card("take_stock")]));
  expect("the only card, 0 completions, by null: first", classes(lone, "take_stock").includes("first"), true);
  expect("the only card, 0 completions, by null: untapped", untapped(lone, "take_stock"), true);

  const next = (from: View, to: View, c: Cards): Cards => { c.update(to, from); return c; };
  const v0 = only([card("take_stock")]);

  const tapped = next(v0, only([card("take_stock", { by: "tap", run: "full" })]), draw(v0));
  expect("running by a tap removes untapped", untapped(tapped, "take_stock"), false);

  const done = next(v0, only([card("take_stock", { completions: 1 })]), draw(v0));
  expect("1+ completions removes untapped", untapped(done, "take_stock"), false);

  const second = next(v0, only([card("take_stock"), card("larder")]), draw(v0));
  expect("a second card on screen removes untapped", untapped(second, "take_stock"), false);

  const drawnTwo = draw(only([card("take_stock"), card("larder")]));
  expect("two cards from the first draw: not untapped", untapped(drawnTwo, "take_stock"), false);
  const drawnDone = draw(only([card("take_stock", { completions: 2 })]));
  expect("1+ completions on first draw: not untapped", untapped(drawnDone, "take_stock"), false);
  const drawnTap = draw(only([card("take_stock", { by: "tap", run: "full" })]));
  expect("run by a tap on first draw: not untapped", untapped(drawnTap, "take_stock"), false);

  // A busy hands lane: a card is flat and can't be tapped, unless it cuts in (Card.cuts_in).
  const hands = { lane: "hands", running_card: "gather", completes_at: AT + 5, order: null };
  const onBusy = (cuts: boolean): Cards => draw({ ...only([card("take_stock", { cuts_in: cuts })]), lanes: [hands] });
  const flat = onBusy(false);
  expect("busy lane: flat", classes(flat, "take_stock").includes("busy"), true);
  expect("busy lane: tap off", flat.node("take_stock")?.disabled, true);
  const cuts = onBusy(true);
  expect("cuts in: not flat", classes(cuts, "take_stock").includes("busy"), false);
  expect("cuts in: tap on", cuts.node("take_stock")?.disabled, false);
}

// ---- 5. CSS ----
{
  const css = readFileSync("src/game.css", "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
  interface Rule { media: string | null; selectors: string[]; decls: Map<string, string> }
  const rules: Rule[] = [];
  /** A selector list split at the commas outside parentheses (so :is(a, b) stays whole). */
  const splitTop = (list: string): string[] => {
    const out: string[] = [];
    let depth = 0;
    let at = 0;
    for (let k = 0; k < list.length; k += 1) {
      if (list[k] === "(") depth += 1;
      else if (list[k] === ")") depth -= 1;
      else if (list[k] === "," && depth === 0) { out.push(list.slice(at, k)); at = k + 1; }
    }
    out.push(list.slice(at));
    return out;
  };
  const block = (src: string, media: string | null): void => {
    let i = 0;
    while (i < src.length) {
      const open = src.indexOf("{", i);
      if (open < 0) break;
      const head = src.slice(i, open).trim();
      let depth = 1;
      let j = open + 1;
      while (j < src.length && depth > 0) { if (src[j] === "{") depth += 1; else if (src[j] === "}") depth -= 1; j += 1; }
      const body = src.slice(open + 1, j - 1);
      if (head.startsWith("@media")) block(body, head.slice(6).trim().replace(/\s+/g, " "));
      else if (!head.startsWith("@")) {
        const decls = new Map<string, string>();
        for (const d of body.split(";")) {
          const c = d.indexOf(":");
          if (c > 0) decls.set(d.slice(0, c).trim(), d.slice(c + 1).trim().replace(/\s+/g, " "));
        }
        rules.push({ media, selectors: splitTop(head).map((s) => s.trim().replace(/\s+/g, " ")), decls });
      }
      i = j;
    }
  };
  block(css, null);

  // A phone media query: the PHONE text, or any query on a width at or under the phone's bounds.
  const normalised = (q: string): string => q.replace(/\s+/g, " ").toLowerCase();
  const isPhone = (m: string | null): boolean => m !== null && (normalised(m) === normalised(PHONE) || /max-width:\s*(639|1023)px/.test(m));
  /** Declarations the phone gets for a selector that ends in `last`, cascaded in source order. */
  const phoneDecls = (last: RegExp): Map<string, string> => {
    const out = new Map<string, string>();
    for (const r of rules) if (isPhone(r.media) && r.selectors.some((s) => last.test(s))) for (const [k, v] of r.decls) out.set(k, v);
    return out;
  };

  expect("phone: the strip in the stage keeps its own height", phoneDecls(/\.stage > \.strip$/).get("flex"), "none");
  expect("phone .lines: no mask", phoneDecls(/(^|[\s.a-z])\.lines$/).get("mask-image"), undefined);

  for (const part of [".card-count", ".card-track", ".card-foot"]) {
    const hits = rules.filter((r) => r.selectors.some((s) => s.includes(".card.first.untapped") && s.includes(part)));
    expect(`.card.first.untapped ${part} has a rule`, hits.length > 0, true);
    expect(`.card.first.untapped ${part} is visibility: hidden`, hits.some((r) => r.decls.get("visibility") === "hidden"), true);
    expect(`.card.first.untapped ${part} is not display: none`, hits.some((r) => r.decls.get("display") === "none"), false);
  }
}
