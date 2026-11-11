// A chip is drawn once its cure is on screen (ui/story.ts, game/shown.ts; CONTRACT.txt, ChipInfo.offered_after): a
// chip on in the view whose offered_after view.unlocked does not hold is not on the band; once it holds, it is; a chip
// with no offered_after is drawn as soon as it is on. Its cost line follows ChipInfo.cost_key.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog({
  ...fixtureContent,
  chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "cold" ? { ...c, offered_after: { category: "card", id: "tend" } } : c)),
} satisfies Content);
const mid = fixtureStep("mid", 100).view;
const tones = (story: Story): string[] => Array.from(story.head.querySelectorAll(".chip"), (n) => n as HTMLElement)
  .filter((n) => !n.classList.contains("keep")).map((n) => n.dataset["tone"] ?? "");
const without = (v: View, id: string): View => ({ ...v, unlocked: v.unlocked.filter((u) => !(u.category === "card" && u.id === id)) });

{
  expect("the control: cold is on in the view", mid.chips, ["cold"]);
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(without(mid, "tend"), null);
  expect("its cure not yet on screen: not drawn", tones(story), []);
  story.update({ ...mid, unlocked: [...mid.unlocked, { category: "card", id: "tend" }] }, null);
  expect("its cure unlocked: drawn", tones(story), ["cold"]);
}

{
  const story = new Story(testContext().ctx);
  story.update(without(mid, "tend"), null);
  expect("a chip with no offered_after: drawn at once", tones(story), ["cold"]);
}

// A chip that costs something says so under its word, in the content's words (ChipInfo.cost_key); one without a
// cost_key draws its word alone.
{
  const costs = (story: Story): string[] => Array.from(story.head.querySelectorAll(".chip-cost"), (n) => n.textContent ?? "");
  const story = new Story(testContext().ctx);
  story.update(mid, null);
  expect("cold's cost under it", costs(story), ["-20% hands speed"]);
  const free = new Catalog({
    ...fixtureContent,
    chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "cold" ? { ...c, cost_key: null } : c)),
  } satisfies Content);
  const bare = new Story(testContext(undefined, free).ctx);
  bare.update(mid, null);
  expect("the control: no cost_key, no cost line", costs(bare), []);
}
