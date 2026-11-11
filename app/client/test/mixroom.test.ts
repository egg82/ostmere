// A new mix is not offered once the saves holds Content.limits.max_mixes (api/CONTRACT.txt, "Request limits"): the
// Mixes list and the rule picker say so in one plain line, and the editor will not save a mix under a new name.
import { fakeDocument, FakeEl, FakeEvent, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { MixEditor } from "../src/ui/editor";
import type { PartContext } from "../src/ui/part";
import { MixSelector } from "../src/ui/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const count = (root: FakeEl, sel: string): number => root.querySelectorAll(sel).length;

const { max_mixes } = fixtureContent.limits;
const tab = fixtureStep("rulestab", 100, { orders: [], extra: [] }).view;
const seed = tab.mixes[0]!;
const holding = (n: number): View => ({ ...tab, mixes: Array.from({ length: n }, (_, i) => ({ ...seed, id: `mix ${i}` })) });

const list = (view: View): FakeEl => {
  const s = new MixSelector(testContext().ctx as PartContext);
  s.show(view);
  document.body.replaceChildren(s.root);
  return fakeDocument.body.firstElementChild!;
};
const room = list(holding(max_mixes - 1)), full = list(holding(max_mixes));
expect("list below the bound: New mix", [count(room, ".selector-new"), count(room, ".rules-full")], [1, 0]);
expect("list at the bound: no New mix, one plain line", [count(full, ".selector-new"), count(full, ".rules-full")], [0, 1]);

const editing = (view: View): { save: FakeEl; saveNew: FakeEl } => {
  const { ctx } = testContext();
  ctx.actions.dryRun = () => Promise.resolve(view);
  const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
  document.body.replaceChildren(editor.root);
  const root = fakeDocument.body.firstElementChild!;
  editor.update(view);
  editor.show(view, "mix 0");
  const name = root.querySelector(".editor-label input")!;
  name.value = "a new name";
  name.dispatchEvent(new FakeEvent("input"));
  const buttons = root.querySelectorAll(".editor-buttons button");
  return { save: buttons[0]!, saveNew: root.querySelectorAll(".editor-foot button")[0]! };
};
const below = editing(holding(max_mixes - 1)), at = editing(holding(max_mixes));
expect("editor below the bound: a new name saves", [below.save.disabled, below.saveNew.disabled], [false, false]);
expect("editor at the bound: a new name does not", [at.save.disabled, at.saveNew.disabled], [true, true]);
