// The desktop frame (docs/design/redesign.md, "Desktop frame"; ui/tabs.ts, ui/partseat.ts, ui/townview.ts): a left rail
// holds the tabs, Tasks · Town · Rules · Book, then the skills, and the panel's foot; the ledger sits under the art. The
// town's people and lanes are the Town tab's alone, never the main screen's. Town keeps its slot unseen until it has a
// row, and a row arriving while another tab is open dots it, but not on the first view.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { LOW_UNDER_SCENE, RAIL } from "../src/ui/layout";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { matchMedia: (q: string) => ({ matches: q === RAIL || q === LOW_UNDER_SCENE, addEventListener: () => {} }) });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const one = (sel: string): FakeEl => {
  const n = fakeDocument.body.querySelector(sel);
  if (!n) throw new Error(`no ${sel}`);
  return n;
};
const fresh = (): Screen => {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  return screen;
};
const town = (): FakeEl => one(".tabs [data-tab=\"town\"]");
const dotted = (b: FakeEl): boolean => b.querySelector(".new-dot") !== null;

{
  fresh().show(fixtureStep("full", 100));
  const rail = one(".rail");
  expect("the rail's tabs, in order", rail.querySelector(".tabs")?.children.map((b) => b.dataset.tab), ["cards", "town", "rules", "book"]);
  expect("the skills and the foot are the rail's", [rail.querySelector(".skills") !== null, rail.querySelector(".panel-foot") !== null], [true, true]);
  expect("the ledger sits under the art", one(".low").querySelector(".ledger") !== null, true);
  expect("no one in the town yet: Town keeps its slot unseen", town().style.visibility, "hidden");
}
{
  fresh().show(townStep("town"));
  expect("people: Town shows", town().style.visibility, "");
  expect("the first view dots nothing", dotted(town()), false);
  const panel = one(".panel");
  const outside = [...panel.querySelectorAll(".town-person"), ...panel.querySelectorAll(".lane-row")].filter((n) => n.closest(".town-tab") === null);
  expect("no one's jobs on the main screen", outside.length, 0);
  expect("the town's people are the Town tab's", one(".town-tab").querySelectorAll(".town-people .town-person").length, 2);
  town().click();
  expect("Town on: the view shows, the cards do not", [one(".town-tab").hidden, one(".deck").hidden], [false, true]);
  expect("the screen knows Town is on (the view takes the middle and the right)", one(".game").dataset.tab, "town");
}
{
  const screen = fresh();
  screen.show(townStep("townone"));
  expect("one person: no dot on the first view", dotted(town()), false);
  screen.show(townStep("town"));
  expect("a second arrives while Tasks is open: Town is dotted", dotted(town()), true);
  town().click();
  expect("opening Town clears it", dotted(town()), false);
}
