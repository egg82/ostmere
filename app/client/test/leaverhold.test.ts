// A person who leaves (CONTRACT.txt, "LEAVES"): the Step that holds the left unlock has already dropped their lane, cards
// and shares, but the page keeps them in its lists until the moment's lines have been shown and dismissed, then drops
// them. A moment with no line drops them at once.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { townStep } from "../fixtures/town";
import type { LogLine, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const before = townStep("town");
const mason = new Set(["hew", "carve"]);
const left = (lines: LogLine[]): Step => {
  const v = before.view;
  return {
    ...before, lines, view: {
      ...v, at: v.at + 10,
      lanes: v.lanes.filter((l) => l.lane !== "mason"), cards: v.cards.filter((c) => !mason.has(c.card)),
      mixes: v.mixes.map((m) => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || !mason.has(c.card)) })),
      unlocked: [...v.unlocked, { category: "left", id: "mason" }],
    },
  };
};

function rig(): Screen {
  const screen = new Screen(new Catalog(fixtureContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  const lists = fakeDocument.querySelector(".lane-rows");
  if (lists) Object.assign(lists.rect, { right: 400, bottom: 100 });   // on screen: out of sight, a change shows at once without waiting its turn
  screen.show(before);
  return screen;
}
const people = (screen: Screen): string[] => [...screen.root.querySelectorAll(".town-person .town-name")].map((n) => n.textContent ?? "");

{
  const screen = rig();
  expect("control: both are in the town", people(screen), ["Helper", "Mason"]);
  screen.show(left([]));
  expect("a moment with no line: gone at once", people(screen), ["Helper"]);
}
{
  const screen = rig();
  screen.show(left([{ at: before.view.at + 10, seq: 0, key: "line.1", card: null }]));
  expect("the moment's line is still waiting: the person stays", people(screen), ["Helper", "Mason"]);
  fakeDocument.body.dispatchEvent(new FakeEvent("keydown", { key: "Escape" }));
  expect("the lines dismissed: the person goes", people(screen), ["Helper"]);
}
