// The glow on a marked card (ui/cards/cardglow.ts) is for a card not yet put to work: running it by a mix, a rule or the
// queue takes the glow away and keeps it away, and a page opened on a card already used or done never lights it.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";
import { install } from "./fake-dom";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const base = fixtureStep("restrule", AT);
const stand: Card = {
  card: "stand", completions: 0, cap: null, bar: { start: AT, start_value: 0, rate: 0, limit: null }, bar_total: 20, by: null,
  completes_at: null, share_bp: 0, run: null, blocker: null, cuts_in: false, spent_store: null, full_store: null, gained: [], crew: null, tap_s: 20, speed: 1, needs: [],
};
const stepWith = (over: Partial<Card>, mixes: Step["view"]["mixes"] = []): Step => ({
  ...base,
  view: { ...base.view, mixes, cards: [...base.view.cards.filter((c) => c.card !== "stand"), { ...stand, ...over }] },
});
const idle = stepWith({});
const byMix = stepWith({ by: "mix", run: "full", share_bp: 10000 }, [{ id: "m1", components: [{ kind: "card_share", card: "stand", share_bp: 10000 }] }]);
const done = stepWith({ completions: 1 });

function open(first: Step): { screen: Screen; glows: () => boolean } {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(first);
  const frame = (): void => { clock += 100; screen.tick(AT); };
  frame();
  return { screen, glows: () => { frame(); return screen.root.querySelector('[data-card="stand"] .glow') != null; } };
}

{
  const { screen, glows } = open(idle);
  expect("an unused marked card glows", glows(), true);
  screen.show(byMix);
  expect("running it by a mix takes the glow away", glows(), false);
  screen.show(idle);
  expect("and it does not come back", glows(), false);
}
{
  const { glows } = open(byMix);
  expect("a page opened on a card already in a mix does not glow it", glows(), false);
}
{
  const { glows } = open(done);
  expect("a page opened on a card already done does not glow it", glows(), false);
}
