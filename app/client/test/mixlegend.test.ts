// No text sits inside a bar (docs/design/redesign.md, "Phone frame"), the Mixes list's small ones included: each row's
// segments are hue alone, and a legend beneath names each task with its share, in the bar's order (ui/selector.ts).
import { fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureStep } from "../fixtures/steps";
import type { PartContext } from "../src/ui/part";
import { MixSelector } from "../src/ui/selector";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const view = fixtureStep("rulestab", 100).view;
const { ctx } = testContext();
const list = new MixSelector(ctx as PartContext);
list.show(view);
document.body.replaceChildren(list.root);
const rows = fakeDocument.body.querySelectorAll(".selector-row");
expect("the fixture lists more than one mix", rows.length > 1, true);
const split = view.mixes.find((m) => m.components.length > 1);
expect("and one of them splits the hands", split !== undefined, true);
for (const [i, mix] of [...view.mixes.filter((m) => m.id === view.active_mix_id), ...view.mixes.filter((m) => m.id !== view.active_mix_id)].entries()) {
  const row = rows[i]!;
  const segs = row.querySelectorAll(".mini-seg");
  expect(`${mix.id}: a segment per task`, segs.length, mix.components.length);
  expect(`${mix.id}: no text in any of them`, Array.from(segs, (s) => s.textContent), mix.components.map(() => ""));
  const want = mix.components.map((c) => `${c.kind === "card_share" ? ctx.catalog.cardLabel(c.card) : c.mix_id} ${ctx.catalog.format.share(c.share_bp)}`);
  expect(`${mix.id}: the legend names each with its share, in order`, Array.from(row.querySelectorAll(".share-key-item"), (n) => n.textContent), want);
}
