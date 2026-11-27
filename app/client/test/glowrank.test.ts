// The one glow's rank (ui/feedback/fresh.ts, GlowRank): a story step the content marks (ui/cards/cardglow.ts) takes the glow from the
// shown ask, which keeps its outline; the ask waiting unanswered page session after page session no longer keeps the
// step that moves the story on from ever glowing.
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, Offer, Step } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { Keeps } from "../src/game/account/keeps";
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
const ask: Offer = { offer: "bank", answer: null, answers: [{ answer: "hers", card: null, takes_s: null, shifts: [null] }, { answer: "his", card: null, takes_s: null, shifts: [null] }] };
const waiting = (c: Partial<Card>): Step => ({
  ...base,
  view: { ...base.view, offers: [ask], cards: [...base.view.cards.filter((x) => x.card !== "stand"), { ...stand, ...c }] },
});

function open(first: Step): { screen: Screen; glowing: () => string[] } {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(first);
  const frame = (): void => { clock += 100; screen.tick(AT); };
  frame();
  const glowing = (): string[] => {
    frame();
    return [screen.root.querySelector('[data-card="stand"] .glow') != null ? "stand" : "", screen.root.querySelector(".ask.glow") != null ? "ask" : ""].filter(Boolean);
  };
  return { screen, glowing };
}

{
  const notReady = { blocker: { condition: { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 1, release: 1, value_of_cap: false, release_of_cap: false }, ready_at: null } };
  const { screen, glowing } = open(waiting(notReady));
  expect("with no step ready, the shown ask has the glow", glowing(), ["ask"]);
  screen.show(waiting({}));
  expect("the marked step turning ready takes it from the ask", glowing(), ["stand"]);
}
{
  const { glowing } = open(waiting({}));
  expect("a page opened on an unanswered ask and a ready marked step glows the step", glowing(), ["stand"]);
}
