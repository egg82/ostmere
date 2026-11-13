// A failed tap (docs/decisions.md, "What can be tapped looks tappable"): when the step answering the player's tap names
// the card (Step.failed_tap), the card pulses red and the thing on it that shows what stopped the tap pulses with it:
// the have/need of a short or pausing store, the skill level, the step, or, for a store the player has never been shown
// or a wait on time, the countdown. Nothing on a card that did not fail; nothing but the card when the card shows no
// such thing. The pulse is a transform and colours only, its numbers tokens on :root, so it moves no layout.
import { readFileSync } from "node:fs";
import { install } from "./fake-dom";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Content, Step, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content: Content = {
  ...fixtureContent,
  card_infos: fixtureContent.card_infos.map((c) => (c.card === "stool" ? { ...c, step_needs: [{ card: "stand", count: 2 }] } : c)),
};
const catalog = new Catalog(content);
const AT = 100;
const still = (v = 0) => ({ start: AT, start_value: v, rate: 0, limit: null });
type Blocker = NonNullable<Card["blocker"]>;
const store = (id: string, value: number): Blocker["condition"] =>
  ({ kind: "at_least", watched: { kind: "store_value", store: id }, value, release: value });
const unready = (card: string, blocker: Blocker, needs: Card["needs"] = []): Card => ({
  card, completions: 0, cap: null, bar: still(), bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null,
  cuts_in: false, spent_store: null, gained: [], tap_s: 20, blocker, needs,
});

const base = fixtureStep("mid", AT);
const cards: Card[] = [
  unready("lean_to", { condition: store("stone", 10 * Q), ready_at: AT + 52 }, [{ store: "stone", quantity: 10 * Q, segment: still(2 * Q), gate: null, makers: [], spent: false }]),
  unready("look", { condition: store("night", 20 * Q), ready_at: AT + 600 }, [{ store: "night", quantity: 20 * Q, segment: still(3 * Q), gate: null, makers: [], spent: false }]),
  unready("hatchet", { condition: { kind: "at_least", watched: { kind: "skill_level", skill: "foraging" }, value: 3, release: 3 }, ready_at: null }),
  unready("stool", { condition: { kind: "at_least", watched: { kind: "card_count", card: "stand" }, value: 2, release: 2 }, ready_at: null }),
  // a Pause: wood holds the input but the card waits for wood to refill to its resume level
  unready("shelter", { condition: store("wood", 30 * Q), ready_at: AT + 900 }, [{ store: "wood", quantity: 6 * Q, segment: still(8 * Q), gate: null, makers: [], spent: false }]),
  unready("rest", { condition: { kind: "after_time", at: AT + 40 }, ready_at: AT + 40 }),
  unready("larder", { condition: store("night", 20 * Q), ready_at: null }, [{ store: "night", quantity: 20 * Q, segment: still(3 * Q), gate: null, makers: [], spent: false }]),
];
const view: View = {
  ...base.view,
  cards,
  completed: [],
  unlocked: [...base.view.unlocked, ...["stone", "wood"].map((id) => ({ category: "store" as const, id }))],
  skills: base.view.skills.map((s) => (s.skill === "foraging" ? { ...s, level: 1 } : s)),
};

const title = (id: string): string => catalog.label(catalog.cards.get(id)?.label_key);
const cardNode = (screen: Screen, id: string): Element => {
  const node = [...screen.root.querySelectorAll(".card")].find((n) => n.querySelector(".card-title")?.textContent === title(id));
  if (!node) throw new Error(`no card ${id}`);
  return node;
};

/** The screen after the step answering a tap of `failed` (null: a step naming no failed tap). */
function shown(failed: string | null): Screen {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show({ ...base, view, lines: [] });
  screen.tick(AT);
  screen.show({ ...base, view, lines: [], failed_tap: failed } as Step);
  screen.tick(AT);
  return screen;
}

/** Which element of the failed card is marked: the need row's kind and text, "foot", or nothing. */
function marked(id: string): { card: boolean; mark: string[] } {
  const screen = shown(id);
  const node = cardNode(screen, id);
  const mark = [...node.querySelectorAll(".fail-mark")].map((m) =>
    m.classList.contains("card-foot") ? "foot" : m.classList.contains("skill") ? "skill" : m.classList.contains("step") ? "step"
      : m.classList.contains("card-need") ? "store" : m.className);
  return { card: node.classList.contains("tap-failed"), mark };
}

expect("a short store input: its have/need", marked("lean_to"), { card: true, mark: ["store"] });
expect("a store never shown (the night): the countdown", marked("look"), { card: true, mark: ["foot"] });
expect("a skill level: its need row", marked("hatchet"), { card: true, mark: ["skill"] });
expect("a step: its need row", marked("stool"), { card: true, mark: ["step"] });
expect("a Pause on a store: that store's have/need", marked("shelter"), { card: true, mark: ["store"] });
expect("a wait on time: the countdown", marked("rest"), { card: true, mark: ["foot"] });
expect("a store never shown with no countdown: the card alone", marked("larder"), { card: true, mark: [] });

// A refusal is shown by the card and its need alone, never by text: the step answering a refused tap carries no line,
// and the card gains no text and the strip no item. A tap that lands puts its line in the strip and nowhere on the card.
{
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show({ ...base, view, lines: [] });
  screen.tick(AT);
  const strip = (): string[] => [...screen.root.querySelectorAll("ol.lines > li")].map((n) => n.textContent ?? "");
  const node = cardNode(screen, "look");
  const words = node.textContent;
  (node.querySelector(".card-tap") as HTMLButtonElement).click();
  screen.show({ ...base, view, lines: [], failed_tap: "look" } as Step);
  screen.tick(AT);
  expect("a refused tap leaves the card's text as it was", cardNode(screen, "look").textContent, words);
  expect("and puts nothing in the strip", strip(), []);
  expect("the card is red", cardNode(screen, "look").classList.contains("tap-failed"), true);

  const line = fixtureContent.text_entries.find((t) => t.key === "line.3")?.text ?? "";
  screen.show({ ...base, view, lines: [{ at: AT, seq: 0, key: "line.3", card: "look" }], failed_tap: null } as Step);
  screen.tick(AT);
  expect("a tap that lands says its line in the strip", strip(), [line]);
  expect("and not under the card", cardNode(screen, "look").textContent, words);
}

const quiet = shown(null);
expect("no failed tap: no pulse anywhere", quiet.root.querySelectorAll(".tap-failed, .fail-mark").length, 0);
const one = shown("lean_to");
expect("only the failed card pulses", one.root.querySelectorAll(".tap-failed").length, 1);

// The pulse's numbers are tokens in one place, and it moves nothing: transform, colour and shadow only.
const css = readFileSync("src/game.css", "utf8");
const root = css.slice(css.indexOf(":root {"), css.indexOf("}", css.indexOf(":root {")));
expect("its duration is a token", /--fail-ms: 400ms;/.test(root), true);
expect("its scale is a token", /--fail-scale: 1\.12;/.test(root), true);
const frames = (name: string): string => {
  const start = css.indexOf(`@keyframes ${name} {`);
  if (start < 0) throw new Error(`no keyframes ${name}`);
  let depth = 0;
  for (let i = css.indexOf("{", start); i < css.length; i += 1) {
    if (css[i] === "{") depth += 1;
    if (css[i] === "}" && --depth === 0) return css.slice(start, i + 1);
  }
  throw new Error(`unclosed keyframes ${name}`);
};
const props = (block: string): string[] => [...block.matchAll(/([a-z-]+)\s*:/g)].map((m) => m[1] ?? "").filter((p) => p !== "");
for (const name of ["tap-failed", "fail-mark", "fail-flash"]) {
  const used = new Set(props(frames(name).replace(/^@keyframes [^{]*\{/, "")));
  for (const p of used) expect(`${name} animates only transform, colour or shadow (${p})`, ["transform", "color", "box-shadow"].includes(p), true);
}
const reduced = css.slice(css.indexOf("@media (prefers-reduced-motion: reduce) {"));
expect("reduced motion keeps the colour flash", /\.fail-mark[^{]*\{[^}]*animation: fail-flash var\(--fail-ms\)[^}]*!important/.test(reduced), true);
expect("reduced motion keeps the card's red", /\.tap-failed[^{]*\{[^}]*animation: tap-failed var\(--fail-ms\)[^}]*!important/.test(reduced), true);
expect("the colour flash has no scale", /transform/.test(frames("fail-flash")), false);
