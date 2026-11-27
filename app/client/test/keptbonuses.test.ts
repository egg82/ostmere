// The camp header keeps what changes: the passing states (chips) stay in its row, and the permanent bonuses carried
// (FeatureInfo.label_key) are one control, a count that opens their list (ui/keptbonuses.ts, ui/story.ts).
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Story } from "../src/ui/story/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const second = { feature: "second_keep", hint_key: null, label_key: "feature.second_keep", effect_key: "feature.second_keep.up", change_bp: [2500, -500], feature_card: null };
const bare = { feature: "bare_keep", hint_key: null, label_key: "feature.bare_keep", effect_key: null, change_bp: [], feature_card: null };
const catalog = new Catalog({
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, { key: "feature.second_keep", text: "Second" }, { key: "feature.second_keep.up", text: "{pct} gap strength, {pct_b} stakes" }, { key: "feature.bare_keep", text: "Bare" }],
  feature_infos: [...fixtureContent.feature_infos, second, bare],
} satisfies Content);
const mid = fixtureStep("mid", 100).view;
const has = (v: View, ...ids: string[]): View => ({ ...v, unlocked: [...v.unlocked, ...ids.map((id) => ({ category: "feature" as const, id }))] });
const chips = (s: Story): string[] => Array.from(s.head.querySelectorAll(".chip"), (n) => (n as HTMLElement).dataset["tone"] ?? "?");
const control = (s: Story): HTMLElement | null => s.head.querySelector(".kept-button") as HTMLElement | null;
const lines = (s: Story): string[][] => Array.from(s.head.querySelectorAll(".kept-list li"), (li) => Array.from(li.querySelectorAll("span"), (n) => n.textContent ?? ""));
const kept = (s: Story): string[] => Array.from(s.head.querySelectorAll(".kept-list li"), (n) => (n as HTMLElement).dataset["keep"] ?? "?");

{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(has(mid, "dusk_ramp", "second_keep"), null);
  expect("a passing state is a chip in the header", chips(story), ["cold"]);
  expect("a permanent bonus is no chip", story.head.querySelector(".chip.keep"), null);
  expect("both bonuses sit behind the one control", kept(story), ["dusk_ramp", "second_keep"]);
  expect("the count matches the list", control(story)?.textContent, "Bonuses · 2");
  expect("the list starts shut", (story.head.querySelector(".kept-list") as HTMLElement).hidden, true);
  control(story)?.click();
  expect("a tap opens it", [(story.head.querySelector(".kept-list") as HTMLElement).hidden, control(story)?.getAttribute("aria-expanded")], [false, "true"]);
  expect("each line names the bonus and what it does, figured from the served change", lines(story), [["Dusk", "+10% gap strength"], ["Second", "+25% gap strength, -5% stakes"]]);
  story.update(has(mid, "dusk_ramp"), null);
  expect("the count follows the view", control(story)?.textContent, "Bonuses · 1");
}

{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(mid, null);
  expect("no bonus carried: no control shown", (story.head.querySelector(".kept") as HTMLElement).hidden, true);
  expect("the passing state is still a chip", chips(story), ["cold"]);
}

{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(has(mid, "bare_keep"), null);
  expect("a bonus with no effect served is its name alone", lines(story), [["Bare"]]);
}
