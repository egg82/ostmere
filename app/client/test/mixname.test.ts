// The name a new mix opens with (ui/editor.ts showNew): the first mix is ui.mix.default ("Main"), as the first-mix
// offer's one tap names it, whether it comes through the guided lesson or the Mixes list; later ones are ui.mix.new.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { UI } from "../src/game/text";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { NewMarks } from "../src/game/marks";
import { MixEditor } from "../src/ui/editor";
import type { PartContext } from "../src/ui/part";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** The name the editor opens a new mix with on `view`. */
function openedName(view: View): string {
  const { ctx } = testContext();
  const editor = new MixEditor(ctx as PartContext, () => undefined, new NewMarks());
  document.body.replaceChildren(editor.root);
  editor.update(view);
  editor.showNew(view);
  return editor.root.querySelector<HTMLInputElement>("input")?.value ?? "";
}

const none: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
expect("the first mix: the default name", openedName(none), testContext().ctx.catalog.text.get(UI.defaultMix));
expect("a later mix: a new one", openedName(fixtureStep("mid", 100).view), "New mix");
