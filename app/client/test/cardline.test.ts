// The newest story line also sits at the top of the card column on a desktop (docs/design/opening-screen.md, "The
// newest line by the cards"): it is the strip's newest shown line, replaced as the next one shows, and drawn from the
// strip's own list. A line still held in the arrival queue is not shown; a line drawn still (a restored page) is not
// news; a phone draws none.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { PHONE } from "../src/ui/layout";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });

const { ctx } = testContext();
const story = new Story(ctx);
const text = (key: string): string => ctx.catalog.text.get(key);
const line = story.cardLine.root;
/** The row's own line: its last child (the first is the unseen room). */
const shownNow = (): string => line.children[line.children.length - 1]?.textContent ?? "";

const seat = (phone: boolean): { panel: HTMLElement; before: HTMLElement } => {
  Object.assign(window, { matchMedia: (q: string) => ({ matches: phone && q === PHONE, addEventListener: () => undefined }) });
  const panel = document.createElement("section");
  const before = document.createElement("div");
  panel.append(before);
  story.cardLine.seat(panel, before);
  return { panel, before };
};

{
  const { panel, before } = seat(false);
  expect("a desktop seats it just before the hands' rows", [...panel.children].map((n) => n.className), ["card-newest", ""]);
  expect("and before is the other child", panel.children[1] === before, true);
}
{
  const { panel } = seat(true);
  expect("a phone draws none", panel.children.length, 1);
  expect("and has none in the page", line.parentElement === null || line.parentElement === undefined, true);
  seat(false);
}

// The room is the strip's room: the same texts, once, so the row is as tall as the tallest line.
{
  const room = line.children[0];
  const strip = story.root.querySelector("div.strip-room");
  expect("the same room texts as the strip's", Array.from(room?.children ?? [], (n) => n.textContent), Array.from(strip?.children ?? [], (n) => n.textContent));
  expect("out of the screen reader's way", room?.getAttribute("aria-hidden"), "true");
}

// Before any line: nothing shown. A line drawn still is not news.
{
  story.tick(0);
  expect("no line yet", shownNow(), "");
  story.appendKeys(["line.5"], false);
  story.tick(0);
  expect("a still line (a restored page) is not drawn", shownNow(), "");
}

// The newest shown line; a held one waits; its turn replaces it.
{
  story.appendKeys(["line.1"]);
  story.tick(0);
  expect("the line shows", shownNow(), text("line.1"));
  const [waiting] = story.appendKeys(["line.2"], true, true);
  waiting?.classList.add("held");
  now = 100;
  story.tick(0);
  expect("a held line leaves it in place", shownNow(), text("line.1"));
  waiting?.classList.remove("held");
  story.tick(0);
  expect("at its turn the next replaces it", shownNow(), text("line.2"));
  expect("one line only", line.children.length, 2);
  expect("it is the strip's newest", shownNow(), story.root.querySelector("ol.lines")?.lastElementChild?.textContent);
  const node = line.children[1];
  story.tick(0);
  expect("a tick with no new line redraws nothing", line.children[1] === node, true);
}

// A find's line goes to the chronicle only: it never reaches the card column.
{
  story.appendKeys(["line.6"]);
  story.tick(0);
  expect("a find's line is not drawn", shownNow(), text("line.2"));
}
