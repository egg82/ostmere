// A name typed in the mix editor never reaches a mix that isn't the one being edited (contract/the-towns-mix.txt, "The town's mix",
// "Reserved ids"): a name the game keeps for the town (its town mix's, or any new one beginning as the game's do) is
// refused where it is typed, with one line saying so, and so is a rename onto another saved mix, which Save would
// overwrite. Save as new already refuses a taken name. The view is the engine's own town over the day-two page.
import { fakeDocument, type FakeEl, FakeEvent, install } from "../../fake-dom";
import { testContext } from "../../context";
import { townStep } from "../../../fixtures/town";
import type { View } from "../../../src/api/types";
import { NewMarks } from "../../../src/game/lessons/marks";
import { MixEditor } from "../../../src/ui/mixes/editor";
import type { PartContext } from "../../../src/ui/part";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const view = townStep("town").view;
const own = view.active_mix_id!;
const other = "Gather by hand";

/** The editor open on `from` (a new mix when null) with `typed` as its name: Save's state and the refusal line. */
function typing(v: View, from: string | null, typed: string): { save: boolean; saveNew: boolean | null; refusal: string | null } {
  const { ctx } = testContext();
  ctx.actions.dryRun = () => Promise.resolve(v);
  const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
  document.body.replaceChildren(editor.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  if (from === null) {
    editor.showNew(v);
    root.querySelectorAll(".add-card")[0]!.dispatchEvent(new FakeEvent("click", { detail: 0 }));   // a card, so only the name decides
  } else editor.show(v, from);
  const name = root.querySelector(".editor-label input")!;
  name.value = typed;
  name.dispatchEvent(new FakeEvent("input"));
  const refuse = root.querySelector(".editor-refuse");
  const saveNew = root.querySelectorAll(".editor-foot button")[0];
  return {
    save: root.querySelectorAll(".editor-buttons button")[0]!.disabled,
    saveNew: saveNew && !saveNew.hidden ? saveNew.disabled : null,
    refusal: refuse && !refuse.hidden ? refuse.textContent : null,
  };
}

expect("control: a fresh name saves", typing(view, own, "Evening"), { save: false, saveNew: false, refusal: null });
expect("control: its own name saves", typing(view, own, own).save, false);
expect("control: a new mix with a fresh name saves", typing(view, null, "Evening").save, false);
const reserved = typing(view, own, "town:main");
expect("renamed to the town's mix: refused", [reserved.save, reserved.saveNew], [true, true]);
expect("with a line saying so", reserved.refusal !== null && reserved.refusal.length > 0, true);
expect("a new mix named as the game's: refused", typing(view, null, "town:new").save, true);
const taken = typing(view, own, other);
expect("renamed onto another saved mix: refused", taken.save, true);
expect("with a line saying so", taken.refusal !== null && taken.refusal.length > 0, true);
