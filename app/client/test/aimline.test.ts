// The aim (ui/aim.ts, game/shown.ts currentAim; CONTRACT.txt, "The client may"): the aim's line states the text of
// the last of Content.aim_infos whose `after` view.unlocked holds, from the first view on; a later aim takes its turn
// in the arrival queue; content with no aims leaves the line empty.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Content, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import type { ArrivalKind } from "../src/game/arrivals";
import { el } from "../src/ui/dom";
import { seatHead } from "../src/ui/headseat";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content: Content = {
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, { key: "aim.first", text: "first aim" }, { key: "aim.later", text: "later aim" },
    { key: "aim.never", text: "never aim" }],
  aim_infos: [
    { aim: "first", text_key: "aim.first", after: null },
    { aim: "later", text_key: "aim.later", after: { category: "card", id: "tend" } },
    { aim: "never", text_key: "aim.never", after: { category: "feature", id: "not_in_any_view" } },
  ],
};
const catalog = new Catalog(content);
const mid = fixtureStep("mid", 100).view;
const without = (v: View, id: string): View => ({ ...v, unlocked: v.unlocked.filter((u) => !(u.category === "card" && u.id === id)) });
const withCard = (v: View, id: string): View => ({ ...v, unlocked: [...without(v, id).unlocked, { category: "card", id }] });
const aimOf = (story: Story): string => story.aim.textContent ?? "";

{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(without(mid, "tend"), null);
  expect("the first view: the first aim, whose after is none", aimOf(story), "first aim");
  story.update(withCard(mid, "tend"), null);
  expect("a later aim's after unlocked: that aim, not an earlier one", aimOf(story), "later aim");
}

{
  const story = new Story(testContext(undefined, catalog).ctx);
  story.update(withCard(mid, "tend"), null);
  expect("a page opened past a later aim's after: that aim at once", aimOf(story), "later aim");
}

{
  const { ctx } = testContext(undefined, catalog);
  const waited: ArrivalKind[] = [];
  const runs: Array<() => void> = [];
  ctx.arrivals = { arrive: () => undefined, effect: (_n, kind, run) => { waited.push(kind); runs.push(run); }, line: () => undefined, busy: true };
  const story = new Story(ctx);
  story.update(without(mid, "tend"), null);
  expect("the first aim does not wait for the queue", [aimOf(story), waited.length], ["first aim", 0]);
  story.update(withCard(mid, "tend"), null);
  expect("a new aim waits its turn behind what is waiting", [aimOf(story), waited.length], ["first aim", 1]);
  runs.forEach((r) => r());
  expect("and shows at its turn", aimOf(story), "later aim");
}

{
  const story = new Story(testContext().ctx);
  story.update(mid, null);
  expect("content with no aims: the line stays empty", aimOf(story), "");
}

{
  Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
  const seat = (phone: boolean): string[] => {
    Object.assign(window, { matchMedia: () => ({ matches: phone, addEventListener: () => {} }) });
    const story = new Story(testContext(undefined, catalog).ctx);
    const left = el("div", "left");
    const stage = el("section", "stage");
    const box = el("div", "scene-box");
    const frame = el("div", "scene-frame");
    box.append(frame);
    stage.append(box);
    left.append(stage, el("div", "low"));
    seatHead(el("div"), stage, story.head, story.aim, story.root);
    return [...left.children, "|", ...stage.children, "|", ...frame.children].map((n) => (typeof n === "string" ? n : n.className));
  };
  // nothing sits in the art's frame on either: a head laid on the art covered its top once it grew to three rows
  expect("a desktop: the aim over the art's column, the head in the stage above the art, the strip at its foot", seat(false),
    ["aim", "stage", "strip", "low", "|", "scene-head", "scene-box", "|"]);
  expect("a phone: the head, then the aim, in the pinned stage over the art, the strip under it", seat(true),
    ["stage", "low", "|", "scene-head", "aim", "scene-box", "strip", "|"]);
}
