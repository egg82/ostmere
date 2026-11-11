// The mix's lesson on the real editor, pressed the way a mouse, finger or pen presses: the Add row's chip joins on
// pointerup and is redrawn at once, so no click follows it, and the lesson still moves on. A key press (a click with no
// pointer, detail 0) moves it on too, and only one step.
import { FakeEvent, fakeDocument, install, pointer, type FakeEl } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { MixEditor } from "../src/ui/editor";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const noMix: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
const RECT = { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 };

/** The first-mix lesson started from its offer, the editor open on a new mix, the lesson on its first card. */
function rig() {
  fakeDocument.body.replaceChildren();
  const { ctx } = testContext();
  const keeps = keepsOf(NEW_FLAT);
  const lessons = new Lessons({ catalog: ctx.catalog, glow: ctx.glow, keeps }, document.body, () => undefined, document, () => 0);
  const editor = new MixEditor(ctx, () => undefined, new NewMarks());
  document.body.append(editor.root);
  editor.update(noMix);
  editor.showNew(noMix);
  const chips = (): FakeEl[] => fakeDocument.querySelectorAll(".editor .add-card");
  const [a, b] = chips().map((c) => c.dataset["card"] ?? "");
  if (!a || !b) throw new Error("the fixture's first-mix view offers fewer than two cards");
  const offer = fakeDocument.createElement("button");
  Object.assign(offer.dataset, { teach: "mix-offer", cards: `${a} ${b}` });
  offer.rect = RECT;
  fakeDocument.body.append(offer);
  lessons.update(noMix);
  /** A frame: the Add row and the bar on show (the fake DOM lays nothing out), then the runner's tick. */
  const tick = (): void => {
    for (const n of [...chips(), ...fakeDocument.querySelectorAll(".editor .share-bar")]) n.rect = RECT;
    lessons.tick();
  };
  /** What wears the glow: a chip's card, the bar, or the offer. */
  const glowing = (): string => {
    const n = fakeDocument.querySelector(".glow");
    return n === null ? "" : n === offer ? "offer" : n.classList.contains("share-bar") ? "bar" : n.dataset["card"] ?? "?";
  };
  const chip = (card: string): FakeEl => {
    const c = chips().find((n) => n.dataset["card"] === card);
    if (!c) throw new Error(`no chip for ${card}`);
    return c;
  };
  tick();
  offer.click();
  tick();
  return { a, b, tick, glowing, chip };
}

/** A press the way a pointer makes one, with the chip redrawn before a click could follow: none does. */
function press(node: FakeEl): void {
  node.dispatchEvent(pointer("pointerdown", 20, 20));
  node.dispatchEvent(pointer("pointerup", 20, 20));
}

{
  const r = rig();
  expect("the lesson is on the first card", r.glowing(), r.a);
  const first = r.chip(r.a);
  press(first);
  expect("the chip joined and was redrawn", [first.isConnected, r.chip(r.b).isConnected], [false, true]);
  r.tick();
  expect("a pointer press on the first card: the lesson moves on", r.glowing(), r.b);
  press(r.chip(r.b));
  r.tick();
  expect("a pointer press on the second card: on to the bar", r.glowing(), "bar");
}

{
  const r = rig();
  r.chip(r.a).dispatchEvent(new FakeEvent("click", { detail: 0 }));
  r.tick();
  expect("a key press on the first card: the lesson moves on one step", r.glowing(), r.b);
}
console.log("lessonpointer: ok");
