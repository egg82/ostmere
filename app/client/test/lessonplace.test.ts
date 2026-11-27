// Where the lesson's note stands (ui/lessons/lessons.ts, place): below its control, else beside it, else above it, and never
// over a sibling of the control, the panel's tabs or the next step's control.
import { fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { Glow } from "../src/ui/feedback/fresh";
import { Lessons } from "../src/ui/lessons/lessons";
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

{  // No spot is clear: the note goes where it takes fewer taps from the player, though it covers more of a sibling
  fakeDocument.body.replaceChildren();
  const keeps = keepsOf(NEW_FLAT);
  const lessons = new Lessons({ catalog: new Catalog(fixtureContent), glow: new Glow(), keeps }, document.body, () => undefined, document, () => 0);
  const row = document.createElement("div");
  const offer = document.createElement("button");
  Object.assign(offer.dataset, { teach: "mix-offer", cards: "stand look" });
  Object.assign(offer, { rect: target });
  const chip = document.createElement("div");
  chip.className = "chip";
  Object.assign(chip, { rect: box(150, 270, 40, 20) });
  row.append(offer, chip);
  const tabs = document.createElement("div");
  tabs.className = "tabs";
  Object.assign(tabs, { rect: box(100, 340, 200, 40) });
  const taps = [box(200, 240, 40, 30), box(250, 240, 40, 30)].map((rect) => Object.assign(document.createElement("button"), { rect }));
  document.body.append(row, tabs, ...taps);
  const rects = taps.map((t, i) => [t, [box(200, 240, 40, 30), box(250, 240, 40, 30)][i]!] as const);
  Object.assign(fakeDocument, { elementsFromPoint: (x: number, y: number) => rects.filter(([, r]) => r.left <= x && x <= r.right && r.top <= y && y <= r.bottom).map(([t]) => t) });
  Object.assign(lessons.root, { rect: box(0, 0, 200, 60) });
  lessons.update(noMix);
  lessons.tick();
  expect("above covers less of the chip but two buttons: below", [parseInt(lessons.root.style.left, 10), parseInt(lessons.root.style.top, 10)], [150, 338]);
  delete (fakeDocument as { elementsFromPoint?: unknown }).elementsFromPoint;
}
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

{  // A short window under an open editor: every spot near the control covers something the player taps, so the note docks at a corner that covers none
  Object.assign(window, { innerWidth: 360, innerHeight: 500 });
  const bar = box(16, 150, 328, 50);
  const rows = (...tops: number[]) => tops.map((t) => box(16, t, 328, 44));
  /** The note's rect when the editor's controls stand at `taps`; `bar` is the step's control. */
  const docked = (taps: ReturnType<typeof box>[]): ReturnType<typeof box> => {
    fakeDocument.body.replaceChildren();
    const lessons = new Lessons({ catalog: new Catalog(fixtureContent), glow: new Glow(), keeps: keepsOf(NEW_FLAT) }, document.body, () => undefined, document, () => 0);
    const offer = document.createElement("button");
    Object.assign(offer.dataset, { teach: "mix-offer", cards: "stand look" });
    Object.assign(offer, { rect: bar });
    const buttons = taps.map((rect) => [Object.assign(document.createElement("button"), { rect }), rect] as const);
    document.body.append(offer, ...buttons.map(([b]) => b));
    Object.assign(fakeDocument, { elementsFromPoint: (x: number, y: number) => buttons.filter(([, r]) => r.left <= x && x <= r.right && r.top <= y && y <= r.bottom).map(([b]) => b) });
    Object.assign(lessons.root, { rect: box(0, 0, 200, 60) });
    lessons.update(noMix);
    lessons.tick();
    delete (fakeDocument as { elementsFromPoint?: unknown }).elementsFromPoint;
    const left = parseInt(lessons.root.style.left, 10);
    const top = parseInt(lessons.root.style.top, 10);
    return box(left, top, 200, 60);
  };
  const meets = (a: ReturnType<typeof box>, b: ReturnType<typeof box>): boolean => Math.min(a.right, b.right) > Math.max(a.left, b.left) && Math.min(a.bottom, b.bottom) > Math.max(a.top, b.top);

  const editor = rows(100, 215, 275, 330);   // the editor's name row above the bar, its rows below it
  const note = docked(editor);
  expect("below and above the control each cover a control: the note docks above the editor's first row", [note.left, note.top], [16, 8]);
  expect("and covers none of the editor's controls", editor.some((t) => meets(note, t)), false);
  const nearer = docked([...rows(8), ...rows(100, 215, 275)]);   // the top band holds a control now: the bottom corner is the one left
  expect("the top band taken: the bottom corner", [nearer.left, nearer.top], [16, 432]);
  expect("and covers none of the controls", [...rows(8), ...rows(100, 215, 275)].some((t) => meets(nearer, t)), false);
  const free = docked(rows(100));   // below the bar is clear: the note stays beside its control, no dock
  expect("a clear spot near the control: not docked", [free.left, free.top], [16, 208]);
  Object.assign(window, { innerWidth: 400, innerHeight: 800 });
}
