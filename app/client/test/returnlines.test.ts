// A planned moment that lands while the player is away plays in full on return (decisions.md, "Day and night run on
// the story's clock"; docs/design/opening-screen/one-thing-at-a-time.md, "Coming back"): the return's lines lead as a live step's do, each
// alone in the story strip for its reading time before what came with it.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { LogLine, Step } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { Keeps } from "../src/game/account/keeps";
import { readingMs } from "../src/game/story/reading";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const shown = (screen: Screen): string[] => [...screen.root.querySelectorAll("ol.lines > li")].filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");

function returned(lines: LogLine[]): { screen: Screen; landed: Step } {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));   // the view the page last showed
  const landed = { ...dayOneStep("landed", 4000), lines };
  screen.show(landed, true);   // the page shown again, hours on
  return { screen, landed };
}

const text = (key: string): string => catalog.text.get(key);
const at = (keys: string[]): LogLine[] => keys.map((key, seq) => ({ at: 3400, seq, key, card: null, opens_beat: false }));

// Two lines on return: the first at once, the second only after the first's reading time.
{
  const t0 = performance.now();
  const { screen } = returned(at(["line.1", "line.2"]));
  screen.tick(4000);
  expect("the first line, alone", shown(screen), [text("line.1")]);
  expect("the strip carries the glow while the first line is held", screen.root.querySelector(".strip")?.classList.contains("glow"), true);
  performance.now = () => t0 + readingMs(text("line.1")) + 50;   // the plain reading time is not enough for a return's first
  screen.tick(4000);
  expect("a return's first line is held past its plain reading time", shown(screen), [text("line.1")]);
  const wait = readingMs(text("line.1"), true);
  const realNow = performance.now;
  performance.now = () => t0 + wait + 50;
  screen.tick(4000);
  expect("after its reading time, the second in its place", shown(screen), [text("line.2")]);
  expect("the glow ends with the hold", screen.root.querySelector(".strip")?.classList.contains("glow"), false);
  performance.now = realNow;
}

// A long absence: every line takes its turn, the first at once (more of this in awaylines.test.ts).
{
  const { screen } = returned(at(["line.1", "line.2", "line.3", "line.4", "line.5"]));
  screen.tick(4000);
  expect("the oldest line first, alone", shown(screen), [text("line.1")]);
}

// A live step's first line is not a return: held for its plain reading time, no glow on the strip.
{
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const t0 = performance.now();
  screen.show({ ...dayOneStep("landed", 4000), lines: at(["line.1", "line.2"]) }, false);
  screen.tick(4000);
  expect("a live step's first line, alone", shown(screen), [text("line.1")]);
  expect("a live step does not light the strip", screen.root.querySelector(".strip")?.classList.contains("glow"), false);
  const realNow = performance.now;
  performance.now = () => t0 + readingMs(text("line.1")) + 50;
  screen.tick(4000);
  expect("a live step's first line is held its plain reading time only", shown(screen), [text("line.2")]);
  performance.now = realNow;
}
