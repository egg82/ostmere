// A card that arrives while another tab is open marks the Tasks tab with the quiet new dot (ui/screen.ts), and opening
// Tasks clears it. The panel stays where the player left it: Add rule's lesson waits on the Rules tab.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const base = fixtureStep("restrule", AT);
const arriving: Card = {
  card: "take_stock", completions: 0, cap: 1, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null,
  completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20, needs: [],
};
const withCard: Step = { ...base, view: { ...base.view, cards: [...base.view.cards, arriving] } };

function rig(): { screen: Screen; tabs: HTMLElement[]; dot: () => boolean } {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(base);
  const tabs = [...screen.root.querySelectorAll<HTMLElement>(".tabs .tab")];
  return { screen, tabs, dot: () => tabs[0]?.querySelector(":scope > .new-dot") != null };
}

{
  const { screen, tabs, dot } = rig();
  tabs[2]?.click();   // Rules
  screen.show(withCard);
  expect("a card arrives on another tab: Tasks is dotted", dot(), true);
  tabs[0]?.click();
  expect("opening Tasks clears the dot", dot(), false);
}
{
  const { screen, dot } = rig();
  screen.show(withCard);
  expect("a card arrives on the open Tasks tab: no dot", dot(), false);
}
