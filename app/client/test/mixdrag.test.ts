// The mix editor's forecast (ui/editor.ts, "after" totals) while a divider is being dragged: the numbers follow the
// drag and are still there after the finger lifts, and a new view arriving mid-drag does not wipe them.
import { fakeDocument, FakeEl, install, pointer } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { MixEditor } from "../src/ui/editor";
import type { PartContext } from "../src/ui/part";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const wait = (ms: number): Promise<void> => new Promise((done) => setTimeout(done, ms));
const q = (root: FakeEl, sel: string): FakeEl[] => root.querySelectorAll(sel);

const step = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const woodRow = (per_hour: number) => ({ store: "wood", per_hour, heading: "steady" as const, at: null, mixed: false });
const base: View = { ...step, store_rows: [woodRow(0)] };
const MIX = "Morning <b>fire</b> & wood";   // gather 60%, tend 40%

/** The engine's answer to a dry run, stood in: wood's rate follows the first card's share. */
function answer(decisions: Decision[]): View {
  const saved = decisions.find((d) => d.kind === "save_mix");
  const first = saved?.kind === "save_mix" ? saved.mix.components[0]?.share_bp ?? 0 : 0;
  return { ...base, store_rows: [woodRow(first - 6000)] };
}

const { ctx } = testContext();
ctx.actions.dryRun = (ds) => Promise.resolve(answer(ds));
const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
document.body.replaceChildren(editor.root);
const root = fakeDocument.body.firstElementChild;
if (!root) throw new Error("nothing mounted");
editor.update(base);
editor.show(base, MIX);
await wait(200);
const bar = q(root, ".share-track")[0];
if (!bar) throw new Error("no bar");
bar.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
const after = (): string[] => q(root, ".totals-after").map((n) => n.textContent);

const divider = q(root, ".share-divider")[0];
if (!divider) throw new Error("no divider");
expect("nothing differs before the drag", after(), []);
divider.dispatchEvent(pointer("pointerdown", 600, 10));
let last: string[] = [];
for (const x of [590, 580, 570, 560, 550, 540, 530, 520, 510, 500]) {
  divider.dispatchEvent(pointer("pointermove", x, 10));
  await wait(30);   // a finger never rests as long as the preview delay
  last = after();
}
expect("numbers show while the divider moves without pausing", last.length > 0, true);
editor.update(base);   // the page's next view arrives mid-drag
expect("a new view mid-drag keeps them", after().length > 0, true);
const later: View = { ...base, at: base.at + 60, store_rows: base.store_rows.map((r) => ({ ...r })) };
editor.update(later);
expect("a later view (a step landing) keeps them", after().length > 0, true);
for (const x of [330, 310]) { divider.dispatchEvent(pointer("pointermove", x, 10)); editor.update({ ...later, at: later.at + x }); }
expect("views arriving between moves keep them", after().length > 0, true);
divider.dispatchEvent(pointer("pointerup", 350, 10));
await wait(300);
expect("numbers stay after release", after().length > 0, true);

// A forecast that gets no answer (a pod restarting, a refused request) says so and asks again, never an empty readout.
{
  let up = false;
  const { ctx: c2 } = testContext();
  c2.actions.dryRun = (ds) => Promise.resolve(up ? answer(ds) : null);
  const second = new MixEditor(c2 as PartContext, () => undefined, new NewMarks());
  document.body.replaceChildren(second.root);
  const r2 = fakeDocument.body.firstElementChild;
  if (!r2) throw new Error("nothing mounted");
  second.update(base);
  second.show(base, MIX);
  const track = q(r2, ".share-track")[0];
  const d2 = q(r2, ".share-divider")[0];
  if (!track || !d2) throw new Error("no bar");
  track.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
  d2.dispatchEvent(pointer("pointerdown", 600, 10));
  d2.dispatchEvent(pointer("pointermove", 400, 10));
  d2.dispatchEvent(pointer("pointerup", 400, 10));
  await wait(300);
  expect("a failed forecast says it is unknown", q(r2, ".totals-unknown").length, 1);
  up = true;
  await wait(2300);
  expect("it asks again and the numbers come", [q(r2, ".totals-unknown").length, q(r2, ".totals-after").length > 0], [0, true]);
}
