// The story strip shows as many of the newest lines as fit whole in its room (docs/design/opening-screen.md, "One column
// of attention"): the last N in order, a new line pushing out the oldest; the Chronicle is dotted only when a line that
// showed with no touch after it leaves the strip entirely. A room not laid out holds just the newest.
import { FakeEl, FakeEvent, fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { fitting } from "../src/ui/stripfit";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

// The pure count: spans oldest first, stacked with a 4-unit gap.
const stack = (heights: number[]) => {
  let top = 0;
  return heights.map((h) => { const s = { top, bottom: top + h }; top += h + 4; return s; });
};
expect("room for two of three", fitting(stack([20, 20, 20]), 44), 2);
expect("a gap counts: 43 holds one", fitting(stack([20, 20, 20]), 43), 1);
expect("room for all", fitting(stack([20, 20, 20]), 200), 3);
expect("the newest always shows, however tall", fitting(stack([20, 90]), 50), 1);
expect("a room not laid out holds the newest only", fitting(stack([0, 0, 0]), 0), 1);
expect("no lines, none", fitting([], 50), 0);

let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });
Object.assign(window, { matchMedia: () => ({ matches: false, addEventListener: () => {} }) });

const { ctx } = testContext();
const story = new Story(ctx);
document.body.append(story.head, story.root, story.book.tab);
const text = (key: string): string => ctx.catalog.text.get(key);
const strip = (): string[] => Array.from(story.root.querySelector("ol.lines")?.children ?? [], (n) => n.textContent ?? "");
const dotted = (): boolean => story.book.tab.querySelector(".new-dot") !== null;

// A layout the fake DOM lacks: every line 20 high, 4 apart, newest last; a room of 68 holds three.
// The page's types say DOM nodes; under install() they are FakeEls, which carry a settable rect.
const isFake = (n: unknown): n is FakeEl => n instanceof FakeEl;
const room = story.root.querySelector("div.strip-room");
if (!isFake(room)) throw new Error("no room");
const rect = (top: number, height: number) => ({ left: 0, top, width: 0, height, right: 0, bottom: top + height });
room.rect = rect(0, 68);
const lay = (): void => {
  Array.from(story.root.querySelector("ol.lines")?.children ?? []).forEach((n, i) => { if (isFake(n)) n.rect = rect(i * 24, 20); });
};
const arrive = (key: string): void => {
  story.appendKeys([key], true, true);
  lay();
  story.tick(0);
  now += 10;
};

arrive("line.1");
arrive("line.2");
arrive("line.3");
expect("room for three: all three show, oldest first", strip(), ["line.1", "line.2", "line.3"].map(text));
expect("nothing has left: no dot", dotted(), false);
arrive("line.4");
expect("a new line pushes out the oldest", strip(), ["line.2", "line.3", "line.4"].map(text));
expect("an unseen line left: Book is dotted", dotted(), true);
fakeDocument.querySelector("button[data-tab=\"book\"]")?.dispatchEvent(new FakeEvent("pointerdown"));
fakeDocument.body.dispatchEvent(new FakeEvent("pointerdown"));
expect("touching clears the dot", dotted(), false);

// A touch after the lines showed: the one pushed out was seen, so no dot.
now += 10;
arrive("line.1");
fakeDocument.body.dispatchEvent(new FakeEvent("pointerdown"));
now += 10;
arrive("line.2");
expect("the window moves on", strip(), ["line.4", "line.1", "line.2"].map(text));
expect("a line pushed out after a touch since it showed leaves no dot", dotted(), false);

// The room narrows to two lines' worth: the oldest goes with the next tick.
room.rect = rect(0, 44);
story.tick(0);
expect("less room, fewer lines", strip(), ["line.1", "line.2"].map(text));
