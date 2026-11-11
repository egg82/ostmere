// Where the lesson's note stands (ui/lessons.ts, place): below its control, else beside it, else above it, and never
// over a sibling of the control, the panel's tabs or the next step's control.
import { fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Glow } from "../src/ui/fresh";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const noMix: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
const box = (left: number, top: number, w: number, h: number) => ({ left, top, width: w, height: h, right: left + w, bottom: top + h });

/** The note placed for an offer button at `at`, with `others` standing on the page; its [left, top]. */
function placed(at: ReturnType<typeof box>, others: { cls: string; rect: ReturnType<typeof box>; sibling?: boolean }[]): [number, number] {
  fakeDocument.body.replaceChildren();
  const keeps = keepsOf(NEW_FLAT);
  const lessons = new Lessons({ catalog: new Catalog(fixtureContent), glow: new Glow(), keeps }, document.body, () => undefined, document, () => 0);
  const row = document.createElement("div");
  document.body.append(row);
  const offer = document.createElement("button");
  Object.assign(offer.dataset, { teach: "mix-offer", cards: "stand look" });
  Object.assign(offer, { rect: at });
  row.append(offer);
  for (const o of others) {
    const n = document.createElement("div");
    n.className = o.cls;
    Object.assign(n, { rect: o.rect });
    (o.sibling ? row : document.body).append(n);
  }
  Object.assign(lessons.root, { rect: box(0, 0, 200, 60) });
  lessons.update(noMix);
  lessons.tick();
  return [parseInt(lessons.root.style.left, 10), parseInt(lessons.root.style.top, 10)];
}

const target = box(150, 300, 80, 30);
expect("nothing near: below", placed(target, []), [150, 338]);
expect("the tabs under the control: not below, and no room beside: above", placed(target, [{ cls: "tabs", rect: box(100, 335, 200, 30) }]), [150, 232]);
expect("a sibling chip under the control: above", placed(target, [{ cls: "chip", rect: box(150, 340, 60, 30), sibling: true }]), [150, 232]);
const wide = box(250, 300, 80, 30);
expect("the tabs below, room on the left: beside", placed(wide, [{ cls: "tabs", rect: box(100, 350, 300, 30) }]), [42, 285]);
// No spot is clear (no room above, a sibling chip on the left, the tabs a little too near below): the one covering least.
const crowded = box(150, 20, 80, 30);
expect("none clear: the least covered", placed(crowded, [{ cls: "tabs", rect: box(100, 70, 300, 30) }, { cls: "chip", rect: box(20, 10, 120, 50), sibling: true }]), [150, 58]);

{  // the next step's control (the mix lesson's first Add entry) already on show under the control: the note goes above it
  fakeDocument.body.replaceChildren();
  const lessons = new Lessons({ catalog: new Catalog(fixtureContent), glow: new Glow(), keeps: keepsOf(NEW_FLAT) }, document.body, () => undefined, document, () => 0);
  const offer = document.createElement("button");
  Object.assign(offer.dataset, { teach: "mix-offer", cards: "stand look" });
  Object.assign(offer, { rect: target });
  const editor = document.createElement("div");
  editor.className = "editor";
  const add = document.createElement("button");
  add.className = "add-card";
  add.dataset.card = "stand";
  Object.assign(add, { rect: box(150, 345, 80, 30) });
  editor.append(add);
  document.body.append(offer, editor);
  Object.assign(lessons.root, { rect: box(0, 0, 200, 60) });
  lessons.update(noMix);
  lessons.tick();
  expect("the next step's control under it: not below, and no room beside: above", [parseInt(lessons.root.style.left, 10), parseInt(lessons.root.style.top, 10)], [150, 232]);
}
