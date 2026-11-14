// The story strip's line (docs/design/opening-screen.md, "One column of attention"): it shows the newest line that has
// shown, on a phone and wider alike; a line that leaves the strip with no touch from the player since it showed dots the
// Chronicle button, which clears when the Chronicle is touched. Restored lines never dot it, nor do lines leaving while it is open.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });
const media = (phone: boolean): void => {
  Object.assign(window, { matchMedia: () => ({ matches: phone, addEventListener: () => {} }) });
};

function strip(story: Story): string[] {
  return Array.from(story.root.querySelector("ol.lines")?.children ?? [], (n) => n.textContent ?? "");
}
function logButton(story: Story): HTMLElement {
  return story.book;
}
const dotted = (story: Story): boolean => logButton(story).querySelector(".new-dot") !== null;

function drawn(phone: boolean, at: number): { story: Story; text: (k: string) => string; done: () => void } {
  media(phone);
  now = at;
  const { ctx } = testContext();
  const story = new Story(ctx);
  document.body.append(story.head, story.root, story.book);
  return { story, text: (key) => ctx.catalog.text.get(key), done: () => { story.head.remove(); story.root.remove(); story.book.remove(); } };
}

/** Four lines shown one after another, `gap` ms apart. */
function four(story: Story, gap: number): void {
  for (const key of ["line.1", "line.2", "line.3", "line.4"]) {
    story.appendKeys([key]);
    story.tick(0);
    now += gap;
  }
}

for (const phone of [true, false]) {
  const { story, text, done } = drawn(phone, phone ? 0 : 100_000);
  four(story, 10);
  expect(`${phone ? "phone" : "wider"}: the strip holds the newest line alone`, strip(story), [text("line.4")]);
  expect(`${phone ? "phone" : "wider"}: lines left with no touch since they showed: Book is dotted`, dotted(story), true);
  const log = fakeDocument.querySelector("button[data-tab=\"book\"]");
  if (!log) throw new Error("Book is not on the page");
  log.dispatchEvent(new FakeEvent("pointerdown"));
  expect("touching Book clears its dot", dotted(story), false);
  done();
}

{
  const { story, text, done } = drawn(true, 200_000);
  story.appendKeys(["line.1"]);
  story.tick(0);
  now += 10;
  fakeDocument.body.dispatchEvent(new FakeEvent("pointerdown"));   // touched after line.1 showed
  now += 10;
  story.appendKeys(["line.2"]);
  story.tick(0);
  expect("a line touched after it showed goes", strip(story), [text("line.2")]);
  expect("and leaves no dot", dotted(story), false);
  now += 10;
  story.appendKeys(["line.3"]);
  story.tick(0);
  expect("one that showed after the touch goes untouched: Book is dotted", dotted(story), true);
  done();
}

{
  const { story, text, done } = drawn(true, 300_000);
  story.appendKeys(["line.1", "line.2", "line.3"], false);   // restored: drawn still, never shown live
  story.tick(0);
  expect("restored lines: the newest shows", strip(story), [text("line.3")]);
  expect("restored lines never dot the Chronicle", dotted(story), false);
  done();
}

{
  const { story, done } = drawn(true, 400_000);
  const sheet = story.root.querySelector<HTMLDialogElement>("dialog.chronicle");
  if (!sheet) throw new Error("no chronicle");
  sheet.showModal();
  four(story, 10);
  expect("lines leaving while the chronicle is open: no dot", dotted(story), false);
  done();
}
