// A dot the player cleared stays cleared (decisions/pacing.md, the quiet dot): across the card finishing and leaving the
// Tasks tab and coming back, across redraws and steps, and across a reload.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const base = fixtureStep("restrule", AT);
const arriving: Card = {
  card: "take_stock", completions: 0, cap: 1, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null,
  completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, speed: 1, needs: [],
};
const without: Step = base;
const withCard: Step = { ...base, view: { ...base.view, cards: [...base.view.cards, arriving] } };
const finished: Step = { ...base, view: { ...base.view, completed: [...base.view.completed, { card: "take_stock", completions: 1 }] } };
const again: Step = { ...withCard, view: { ...withCard.view, cards: withCard.view.cards.map((c) => (c.card === "take_stock" ? { ...c, completions: 1 } : c)) } };

function rig(): { screen: Screen; dot: () => boolean; frame: (ms: number) => void } {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(without);
  const node = (): HTMLElement | null => screen.root.querySelector<HTMLElement>('[data-card="take_stock"]');
  return { screen, dot: () => node()?.querySelector(":scope > .new-dot") != null, frame: (ms) => { clock += ms; screen.tick(AT); } };
}

{
  const { screen, dot, frame } = rig();
  screen.show(withCard);
  expect("a card that arrives is dotted", dot(), true);
  fakeDocument.querySelector('[data-card="take_stock"]')?.dispatchEvent(new FakeEvent("pointerdown"));
  expect("a touch clears it", dot(), false);
  fakeDocument.querySelector('[data-card="take_stock"]')?.dispatchEvent(new FakeEvent("pointerup"));
  screen.show(withCard);
  expect("a redraw leaves it cleared", dot(), false);
  screen.show(finished);
  frame(10000);
  frame(10000);
  expect("the finished card left the tab", screen.root.querySelector('[data-card="take_stock"]') === null, true);
  screen.show(again);
  expect("the card back on the tab after it left is not dotted again", dot(), false);
}
