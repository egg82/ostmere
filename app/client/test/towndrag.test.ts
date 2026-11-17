// A person's split on their page is set with the hands' share bar (ui/sharebar.ts, ui/personmix.ts): dragging a divider
// trades share between a person's neighbouring parts, the last one against their idle rest, and the let-go sends the mix
// at once, with no Save; the old -/+ step buttons are gone.
import { type FakeEl, install, pointer } from "./fake-dom";
import { pageRig, savedMix, texts } from "./personrig";
import { townStep } from "../fixtures/town";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const both = townStep("town").view;   // helper: chop 60%, haul 30%, 10% idle; mason: hew 70%, carve 20%
const shares = (m: ReturnType<typeof savedMix>): (string | number)[][] => (m?.components ?? []).map((c) => (c.kind === "card_share" ? [c.card, c.share_bp] : []));

{  // dragging a divider changes the person's shares, and the let-go sends them
  const { got, settle, open } = pageRig(both);
  const page = open(0);
  expect("no step buttons", page.querySelectorAll(".town-step, .town-plus, .town-minus").length, 0);
  expect("a divider for each neighbouring pair, the idle rest included", page.querySelectorAll(".share-divider").length, 2);
  const divider = (i: number): FakeEl => page.querySelectorAll(".share-divider")[i] as FakeEl;
  const keyed = (): string[] => texts(page.querySelectorAll(".share-key-item")).map((t) => t.slice(-3).trim());
  divider(0).dispatchEvent(pointer("pointerdown", 600, 10));
  divider(0).dispatchEvent(pointer("pointermove", 500, 10));
  expect("the legend follows mid-drag", keyed(), ["50%", "40%", "10%"]);
  expect("nothing sent until the let-go", got.decided.length, 0);
  divider(0).dispatchEvent(pointer("pointerup", 500, 10));
  expect("the let-go sends the mix, no Save", [got.decided.length, shares(savedMix(got.decided[0]))], [1, [["chop", 5000], ["haul", 4000], ["hew", 7000], ["carve", 2000]]]);
  const next = settle(both);
  divider(1).dispatchEvent(pointer("pointerdown", 900, 10));
  divider(1).dispatchEvent(pointer("pointermove", 950, 10));   // haul takes from the idle rest
  divider(1).dispatchEvent(pointer("pointerup", 950, 10));
  expect("the second drag, on the mix as the first left it", shares(savedMix(got.decided[0])), [["chop", 5000], ["haul", 4500], ["hew", 7000], ["carve", 2000]]);
  expect("the idle rest is what is left", keyed(), ["50%", "45%", "5%"]);
  expect("the other person is untouched", next.mixes.find((m) => m.id === "town:main")?.components.slice(2).map((c) => (c.kind === "card_share" ? c.share_bp : 0)), [7000, 2000]);
}
