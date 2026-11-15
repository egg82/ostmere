// A rule's level is set with a slider (ui/condlevels.ts on ui/valueslider.ts): dragging or touching the track sets the
// level live. A share snaps to five points and reads as its word or percentage; an exact number moves by one up to the
// store's maximum. The arrow keys step it. Each level has its own slider, and a level the rule cannot take is not set.
import { FakeEl, FakeEvent, fakeDocument, install, pointer } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import type { StoreRule } from "../src/game/storerule";
import { Levels } from "../src/ui/condlevels";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const CAP = 40;
const catalog = new Catalog(fixtureContent);

/** The levels mounted on a page, redrawn with each level they report, as the editor does. */
function rig(start: StoreRule): { levels: FakeEl; rule: () => StoreRule } {
  let rule = start;
  const view = new Levels(catalog, () => undefined, (which, level) => {
    rule = which === "n" ? { ...rule, n: level } : { ...rule, m: level };
    view.draw(catalog, rule, CAP, null);
  });
  view.draw(catalog, rule, CAP, null);
  document.body.replaceChildren(view.fold.root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return { levels: node, rule: () => rule };
}

const sliders = (levels: FakeEl, form: string): FakeEl[] => levels.querySelectorAll(`[data-form="${form}"]`);
const track = (s: FakeEl): FakeEl => {
  const t = s.querySelector(".value-track");
  if (!t) throw new Error("no track");
  return t;
};
const handle = (s: FakeEl): FakeEl => {
  const h = s.querySelector('[role="slider"]');
  if (!h) throw new Error("no handle");
  return h;
};
const readout = (levels: FakeEl): string[] => levels.querySelectorAll(".cond-level .cond-value").map((n) => n.textContent);
/** The track `s` laid across 100..100+width, then a pointer at `part` of it. */
const at = (s: FakeEl, width: number, part: number): number => {
  track(s).rect = { left: 100, top: 0, width, height: 44, right: 100 + width, bottom: 44 };
  return 100 + width * part;
};
const press = (s: FakeEl, key: string): void => { handle(s).dispatchEvent(Object.assign(new FakeEvent("keydown"), { key })); };

// A share: the track snaps to five points, live while the pointer moves, and is read in its word or percentage.
{
  const r = rig({ store: "wood", test: "below", n: { share: 2500 }, m: { share: 7500 } });
  const [when] = sliders(r.levels, "share");
  if (!when) throw new Error("no share slider");
  expect("opens on the rule's words", readout(r.levels), ["a quarter", "three quarters"]);
  track(when).dispatchEvent(pointer("pointerdown", at(when, 200, 0.31), 0));
  expect("a touch lands on the nearest five points", [r.rule().n, readout(r.levels)[0]], [{ share: 3000 }, "30%"]);
  track(when).dispatchEvent(pointer("pointermove", at(when, 200, 0.42), 0));
  expect("mid-drag it follows, snapped", [r.rule().n, readout(r.levels)[0]], [{ share: 4000 }, "40%"]);
  track(when).dispatchEvent(pointer("pointermove", at(when, 200, 0.521), 0));
  expect("and reads a named share as its word", [r.rule().n, readout(r.levels)[0]], [{ share: 5000 }, "half"]);
  track(when).dispatchEvent(pointer("pointerup", at(when, 200, 0.521), 0));
  track(when).dispatchEvent(pointer("pointermove", at(when, 200, 0.1), 0));
  expect("after the drop a move does nothing", r.rule().n, { share: 5000 });
  press(when, "ArrowRight");
  press(when, "ArrowRight");
  expect("arrow keys step five points", r.rule().n, { share: 6000 });
  press(when, "ArrowLeft");
  press(when, "Home");
  expect("Home goes to empty", r.rule().n, { share: 0 });
  expect("the handle says where it is", [handle(when).getAttribute("aria-valuenow"), handle(when).getAttribute("aria-valuetext"), handle(when).style["left"]], ["0", "empty", "0%"]);
  track(when).dispatchEvent(pointer("pointerdown", at(when, 200, 0.99), 0));
  expect("a level the rule cannot take (past Until) is not set", r.rule().n, { share: 0 });
}

// An exact number: one at a time between 0 and the store's maximum now.
{
  const r = rig({ store: "wood", test: "below", n: { items: 10 }, m: { items: 20 } });
  const [when, until] = sliders(r.levels, "items");
  if (!when || !until) throw new Error("no exact sliders");
  expect("the number as it reads", readout(r.levels), ["10", "20"]);
  expect("runs to the store's maximum", [handle(until).getAttribute("aria-valuemin"), handle(until).getAttribute("aria-valuemax")], ["0", String(CAP)]);
  track(until).dispatchEvent(pointer("pointerdown", at(until, 400, 29 / CAP), 0));
  expect("a touch lands on a whole number", [r.rule().m, readout(r.levels)[1]], [{ items: 29 }, "29"]);
  track(until).dispatchEvent(pointer("pointermove", at(until, 400, 0.5 + 0.004), 0));
  expect("mid-drag by one", r.rule().m, { items: 20 });
  track(until).dispatchEvent(pointer("pointerup", 0, 0));
  press(when, "ArrowRight");
  expect("an arrow key moves it by one", r.rule().n, { items: 11 });
  press(until, "End");
  expect("End goes to the maximum", r.rule().m, { items: CAP });
  expect("shares show none of this", sliders(r.levels, "share").map((s) => s.hidden), [true, true]);
}
