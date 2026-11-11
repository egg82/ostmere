// The Rules tab's label comes without its glow (ui/screen.ts; docs/design/opening-screen.md, "Dots and the one glow"):
// it is there once the first rule exists, and takes the glow only once a rule of the save has come on and let go
// (writing rules opens then too), until the tab is first opened.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { UI } from "../src/game/text";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const covered = fixtureStep("covered", AT);
/** The covered camp with its one rule on (`on`) or off, and no lines, so nothing waits its turn. */
const step = (on: boolean, at = AT): Step => ({ ...covered, lines: [], view: { ...covered.view, at, orders_on: covered.view.orders.map(() => on) } });

function screen(account: Flat = NEW_FLAT): { s: Screen; tab: () => HTMLElement } {
  const s = new Screen(catalog, () => undefined, () => Promise.resolve(null), keepsOf(account));
  document.body.replaceChildren(s.root);
  const label = catalog.text.get(UI.ordersHeading);
  const tab = (): HTMLElement => {
    const t = [...s.root.querySelectorAll<HTMLElement>(".tab")].find((n) => n.textContent === label);
    if (!t) throw new Error("no Rules tab");
    return t;
  };
  return { s, tab };
}

{
  expect("the control: a rule exists", covered.view.orders.length > 0, true);
  const { s, tab } = screen();
  s.show(step(false));
  s.tick(AT);
  expect("the label is there with the first rule", tab().style.visibility, "");
  expect("without its glow", tab().classList.contains("glow"), false);
  s.show(step(true, AT + 1));
  s.tick(AT + 1);
  expect("the rule on: still no glow", tab().classList.contains("glow"), false);
  s.show(step(false, AT + 2));
  s.tick(AT + 2);
  expect("on, then let go: the glow", tab().classList.contains("glow"), true);
}

{
  const { s, tab } = screen({ ...NEW_FLAT, rule_seen: true });
  s.show(step(false));
  s.tick(AT);
  expect("a rule seen on and off before (kept): the glow", tab().classList.contains("glow"), true);
}

{
  const bare = fixtureStep("start", AT);
  expect("the control: no rule, nothing queued", [bare.view.orders.length, bare.view.queue.length], [0, 0]);
  const { s, tab } = screen({ ...NEW_FLAT, rule_seen: true, rules_opened: true });
  s.show({ ...bare, lines: [] });
  s.tick(AT);
  expect("a new game's first screen, before its ledger, on an account that has seen rules: no tab yet", tab().style.visibility, "hidden");
}

{
  const { s, tab } = screen({ ...NEW_FLAT, rule_seen: true, rules_opened: true });
  s.show(step(false));
  s.tick(AT);
  expect("the tab opened before: no glow", tab().classList.contains("glow"), false);
}

{  // a save whose record of what its rules did holds a let-go (one no page saw, or one from before rule_seen was per save):
  // writing rules is open in it, so the label takes the glow; a rule the game removed is no let-go
  const order = covered.view.orders[0]!;
  const run = { order, starts: 1, on_at: AT - 50, on_level: 1000, off_at: AT - 10, off_level: 4000, ended: null, made: [] };
  const removed = screen();
  removed.s.show({ ...step(false), rule_runs: [{ ...run, ended: "season" as const }] });
  removed.s.tick(AT);
  expect("control: a removed rule's entry opens nothing", removed.tab().classList.contains("glow"), false);
  const { s, tab } = screen();
  s.show({ ...step(false), rule_runs: [run] });
  s.tick(AT);
  expect("a let-go in the save's rule record: the glow", tab().classList.contains("glow"), true);
}
