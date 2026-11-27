// The smallest share is 1%: the hands' share bar (the slim ShareBar) reaches 99/1 by dragging a divider and by its
// arrow-key steps, and a card never goes lower (a card at 0% is the remove control's job).
import { FakeEl, FakeEvent, fakeDocument, install } from "./fake-dom";
import { MIN_SHARE_BP } from "../src/game/mix";
import { ShareBar } from "../src/ui/mixes/sharebar";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const BP = 10_000;
const WIDTH = 300;
const seg = (key: string) => ({ key, label: key, hue: 0 });

/** The one node mounted on the page: a real-typed root seen as the fake element it is. */
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

/** A hands-style bar at 50/50 on a track WIDTH px wide, and every share set it commits. */
function open(): { divider: FakeEl; commits: number[][] } {
  const commits: number[][] = [];
  const bar = new ShareBar("slim", BP, (bp) => String(bp), { commit: (s) => commits.push(s) });
  bar.set([seg("a"), seg("b")], [5000, 5000]);
  const top = mounted(bar.root);
  const track = top.querySelector(".share-track");
  const divider = top.querySelector(".share-divider");
  if (!track || !divider) throw new Error("the bar drew no track or divider");
  track.rect = { left: 0, top: 0, width: WIDTH, height: 8, right: WIDTH, bottom: 8 };
  return { divider, commits };
}

expect("the floor", MIN_SHARE_BP, 100);

// Drag: to the far right end and past it, the card behind keeps 1%.
{
  const { divider, commits } = open();
  divider.dispatchEvent(new FakeEvent("pointerdown", { pointerId: 1, clientX: WIDTH / 2 }));
  divider.dispatchEvent(new FakeEvent("pointermove", { clientX: WIDTH * 2 }));
  divider.dispatchEvent(new FakeEvent("pointerup"));
  expect("dragged to the right end", commits, [[9900, 100]]);
}
// Drag to the left end: the first card keeps 1%.
{
  const { divider, commits } = open();
  divider.dispatchEvent(new FakeEvent("pointerdown", { pointerId: 1, clientX: WIDTH / 2 }));
  divider.dispatchEvent(new FakeEvent("pointermove", { clientX: -WIDTH }));
  divider.dispatchEvent(new FakeEvent("pointerup"));
  expect("dragged to the left end", commits, [[100, 9900]]);
}
// Steps: one percent a press, down to 99/1 and no further.
{
  const { divider, commits } = open();
  const press = (key: string): void => { divider.dispatchEvent(new FakeEvent("keydown", { key })); };
  for (let i = 0; i < 60; i++) press("ArrowRight");
  const last = commits[commits.length - 1];
  expect("steps right stop at 99/1", last, [9900, 100]);
  expect("each step is one percent", commits.length, 49);
  const n = commits.length;
  press("ArrowRight");
  expect("no step past 99/1", commits.length, n);
  expect("the divider reads the share", divider.getAttribute("aria-valuenow"), "99");
  for (let i = 0; i < 120; i++) press("ArrowLeft");
  expect("steps left stop at 1/99", commits[commits.length - 1], [100, 9900]);
}
