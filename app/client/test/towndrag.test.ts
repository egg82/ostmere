// A person's mix in the Camp editor is set with the hands' share bar (ui/sharebar.ts): dragging a divider trades share
// between a person's neighbouring parts, the last one against their idle rest; the old -/+ step buttons are gone, and
// Add is always offered.
import { fakeDocument, type FakeEl, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { Decision, Mix, View } from "../src/api/types";
import { MIN_SHARE_BP } from "../src/game/mix";
import { LaneRows } from "../src/ui/lanerows";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const both = townStep("town").view;   // helper: chop 60%, haul 30%, 10% idle; mason: hew 70%, carve 20%
const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");
const saved = (d: Decision | undefined): Mix | null => (d?.kind === "save_mix" ? d.mix : null);

function opened(view: View) {
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.town.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  rows.update(view);
  root.querySelector(".town-change")?.click();
  const editor = fakeDocument.body.children[1] as FakeEl;
  const person = (i: number): FakeEl => editor.querySelectorAll(".town-person")[i] as FakeEl;
  for (const track of editor.querySelectorAll(".share-track")) track.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
  return { editor, got, person };
}

{  // dragging a divider changes the person's shares, live and on Save; no step buttons
  const { editor, got, person } = opened(both);
  const helper = (): FakeEl => person(0);
  expect("no step buttons", editor.querySelectorAll(".town-step, .town-plus, .town-minus").length, 0);
  expect("a divider for each neighbouring pair, the idle rest included", helper().querySelectorAll(".share-divider").length, 2);
  const divider = (i: number): FakeEl => helper().querySelectorAll(".share-divider")[i] as FakeEl;
  const chopHaul = divider(0);
  chopHaul.dispatchEvent(pointer("pointerdown", 600, 10));
  chopHaul.dispatchEvent(pointer("pointermove", 500, 10));
  expect("the rows follow mid-drag", texts(helper().querySelectorAll(".town-card-share")), ["50%", "40%"]);
  chopHaul.dispatchEvent(pointer("pointerup", 500, 10));
  const haulIdle = divider(1);   // the let-go redrew the person
  haulIdle.dispatchEvent(pointer("pointerdown", 900, 10));
  haulIdle.dispatchEvent(pointer("pointermove", 950, 10));   // haul takes from the idle rest
  haulIdle.dispatchEvent(pointer("pointerup", 950, 10));
  expect("after the let-go", texts(helper().querySelectorAll(".town-card-share")), ["50%", "45%"]);
  expect("the idle rest is what is left", texts(person(0).querySelectorAll(".share-key-item")).map((t) => t.slice(-3).trim()), ["50%", "45%", "5%"]);
  expect("the other person is untouched", texts(person(1).querySelectorAll(".town-card-share")), ["70%", "20%"]);
  editor.querySelector(".editor-head .primary")?.click();
  expect("Save sends the dragged shares", saved(got.decided[0])?.components.map((c) => (c.kind === "card_share" ? [c.card, c.share_bp] : null)),
    [["chop", 5000], ["haul", 4500], ["hew", 7000], ["carve", 2000]]);
}

{  // Add joins with all the idle there is when that is under half (with none, it takes a slice: fullshare.test.ts)
  for (const rest of [300, MIN_SHARE_BP]) {
    const mix = (m: Mix): Mix => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || c.card !== "hew").map((c) => (c.kind === "card_share" && c.card === "carve" ? { ...c, share_bp: 10_000 - rest } : c)) });
    const { editor, person } = opened({ ...both, mixes: both.mixes.map((m) => (m.id === "town:main" ? mix(m) : m)) });
    const add = person(1).querySelector('.town-add[data-card="hew"]') as FakeEl;
    expect(`Add at ${rest} idle`, add.disabled, false);
    add.click();
    expect("the card joins with the idle share", texts(person(1).querySelectorAll(".town-card-share")), [`${rest / 100}%`, `${(10_000 - rest) / 100}%`].reverse());
    expect("still open", editor.hidden, false);
  }
}
