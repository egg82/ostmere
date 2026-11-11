// The Log sheet splits its lines into stretches, one per return after a long time away (game/loggroups.ts): the
// newest open and the older folded to their counts, the story's lines full size and the other kinds small under them,
// behind the stretch's tally.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps, NEW_SAVE } from "../src/game/keeps";
import { UI } from "../src/game/text";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const line = (key: string, at: number): LogLine => ({ at, seq: 0, key, card: null });

function opened(lines: LogLine[], now: number, visits: Array<{ left: number; back: number }>): Screen {
  const keeps = new Keeps({ save: { ...NEW_SAVE, visits } });
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  screen.show({ ...dayOneStep("landed", now), lines }, true);
  (screen.root.querySelector("button.log-open") as HTMLButtonElement).click();
  const heading = screen.root.querySelector("dialog.log-sheet > .panel-heading");
  expect("the sheet's heading", heading?.textContent, text(UI.log));
  return screen;
}

const stretches = (s: Screen): HTMLElement[] => [...s.root.querySelectorAll<HTMLElement>("ol.log-all > li")];
const titles = (s: Screen): string[] => stretches(s).map((n) => n.querySelector(".v-title")?.textContent ?? "");
const opens = (n: HTMLElement): boolean => n.querySelector<HTMLDetailsElement>("details")?.open ?? false;
const paragraphs = (n: HTMLElement): string[] => [...n.querySelectorAll(".v-body > p")].map((p) => `${p.className}:${p.textContent}`);

{
  const s = opened([line("line.1", 1000), line("line.2", 1100), line("line.3", 1800), line("line.4", 1900), line("line.1", 2000)], 2500,
    [{ left: 1100, back: 1700 }]);
  const [early, away] = stretches(s);
  expect("a stretch before the first return, and one per return", titles(s), [text(UI.logEarlier), "Away 10m"]);
  expect("the older stretch is folded, the newest open", [opens(early!), opens(away!)], [false, true]);
  expect("the older stretch's lines are story, full size", paragraphs(early!), [`log-story:${text("line.1")}`, `log-story:${text("line.2")}`]);
  expect("a folded stretch reads as its counts", early?.querySelector(".v-sum")?.textContent, "Story 2");
  expect("a stretch's counts lead with its story", away?.querySelector(".v-sum")?.textContent, "Story 1 · Taps 1 · Finds 1");
  expect("a return reads against now", away?.querySelector(".v-ago")?.textContent, "13 minutes ago");
  expect("the newest stretch's story is at full size and the rest small, by kind",
    paragraphs(away!), [`log-small tap:${text("line.3")}`, `log-small find:${text("line.4")}`, `log-story:${text("line.1")}`]);
  expect("the small lines are folded away", [...away!.querySelectorAll<HTMLElement>(".log-small")].map((p) => p.hidden), [true, true]);
  const tally = away!.querySelector<HTMLElement>("button.log-tally")!;
  expect("the tally counts the small kinds", [...tally.querySelectorAll(".log-chip")].map((c) => c.textContent), ["Taps 1", "Finds 1"]);
  tally.click();
  expect("the tally opens the small lines", [...away!.querySelectorAll<HTMLElement>(".log-small")].map((p) => p.hidden), [false, false]);
  expect("and says so", tally.getAttribute("aria-expanded"), "true");
}
{
  const s = opened([line("line.1", 1000), line("line.2", 1100)], 1700, []);
  expect("with no return kept the whole Log is one stretch, now", titles(s), [text(UI.logNow)]);
  expect("it has no tally when every line is story", stretches(s)[0]?.querySelector("button.log-tally"), null);
}
{
  const s = opened([line("line.1", 1000), line("line.4", 1100)], 1700, [{ left: 5000, back: 5300 }]);
  expect("a return with no line after it opens no stretch", titles(s), [text(UI.logNow)]);
}
