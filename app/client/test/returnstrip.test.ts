// Coming back (docs/design/opening-screen.md, "Coming back"): the replay's first line takes the story strip at its
// first turn, in place of the line the player left on, and the page opens at its top, so no card row hides under the
// pinned strip.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const line = (key: string, seq: number): LogLine => ({ at: 200 + seq, seq, key, card: null });
const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
document.body.replaceChildren(screen.root);
const shown = (): string[] => [...screen.root.querySelectorAll("ol.lines > li")].filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");

screen.show(fixtureStep("mid", 100));
screen.tick(0);
expect("the first view's lines play in turn too: the first, alone", shown(), [text("line.3")]);
for (now = 0; now < 60_000; now += 100) screen.tick(0);   // the first view's lines play out
expect("live: the strip ends on the step's last line", shown(), [text("line.4")]);

screen.root.scrollTop = 300;
screen.show({ ...dayOneStep("landed", 300), lines: [line("line.1", 0), line("line.2", 1)] }, true);
expect("the return: the page opens at its top", screen.root.scrollTop, 0);
now += 16;
screen.tick(0);
expect("the replay's first line takes the strip at once", shown(), [text("line.1")]);
