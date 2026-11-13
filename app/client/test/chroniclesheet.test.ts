// The chronicle sheet (ui/chroniclesheet.ts): its lines split into stretches, one per return after a long time away,
// the newest open and the older folded to their counts; a row of filters once two kinds have entries, Story first;
// under Story, a stretch's counts of the other filters, each opening its filter; each line over its cause.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent } from "../fixtures/content";
import type { LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps, NEW_SAVE } from "../src/game/keeps";
import { ruleEntries } from "../src/game/rulerows";
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
  (screen.root.querySelector("button.chron-open") as HTMLButtonElement).click();
  const heading = screen.root.querySelector("dialog.chronicle > .panel-heading");
  expect("the sheet's heading", heading?.textContent, text(UI.chronicle));
  return screen;
}

const stretches = (s: Screen): HTMLElement[] => [...s.root.querySelectorAll<HTMLElement>("ol.chron-all > li")];
const titles = (s: Screen): string[] => stretches(s).map((n) => n.querySelector(".v-title")?.textContent ?? "");
const opens = (n: HTMLElement): boolean => n.querySelector<HTMLDetailsElement>("details")?.open ?? false;
const shown = (n: HTMLElement): string[] => [...n.querySelectorAll<HTMLElement>(".v-body > .chron-line")]
  .map((p) => `${p.dataset["kind"]}:${p.querySelector(".chron-text")?.textContent}${p.querySelector(".chron-cause") ? ` ↳ ${p.querySelector(".chron-cause")?.textContent}` : ""}`);
const filters = (s: Screen): string[] => [...s.root.querySelectorAll<HTMLElement>(".chron-filters > button")]
  .map((b) => `${b.dataset["filter"]}${b.getAttribute("aria-pressed") === "true" ? "*" : ""}`);
const tap = (s: Screen, sel: string): void => (s.root.querySelector(sel) as HTMLButtonElement).click();

{
  const s = opened([line("line.1", 1000), line("line.2", 1100), line("line.3", 1800), line("line.6", 1900), line("line.1", 2000)], 2500,
    [{ left: 1100, back: 1700 }]);
  const [early, away] = stretches(s);
  expect("two kinds have entries: the filters, Story chosen, All last", filters(s), ["story*", "finds", "all"]);
  expect("a stretch before the first return, and one per return", titles(s), [text(UI.chronEarlier), "Away 10m"]);
  expect("the older stretch is folded, the newest open", [opens(early!), opens(away!)], [false, true]);
  expect("a folded stretch reads as its counts", early?.querySelector(".v-sum")?.textContent, "Story 2");
  expect("a stretch's counts are by filter, the story's first", away?.querySelector(".v-sum")?.textContent, "Story 2 · Finds 1");
  expect("a return reads against now", away?.querySelector(".v-ago")?.textContent, "13 minutes ago");
  expect("under Story: the story's lines and a tap's, each over its cause", shown(away!),
    [`tap:${text("line.3")} ↳ ${catalog.runnerLabel("stand")}`, `story:${text("line.1")}`]);
  expect("the older stretch's second line carries its cause", shown(early!)[1], `story:${text("line.2")} ↳ time`);
  const counts = [...away!.querySelectorAll<HTMLElement>(".chron-foot > button")].map((b) => b.textContent);
  expect("the stretch ends with the other filters' counts", counts, ["Finds 1"]);
  tap(s, '.chron-foot > button[data-filter="finds"]');
  expect("a count opens its filter", filters(s), ["story", "finds*", "all"]);
  expect("which holds the finds alone", stretches(s).map(shown), [[`find:${text("line.6")} ↳ ${catalog.skillLabel("foraging")} 2`]]);
  tap(s, '.chron-filter[data-filter="all"]');
  expect("All holds every line in order", stretches(s).map(shown).flat().map((x) => x.split(":")[0]), ["story", "story", "tap", "find", "story"]);
  expect("and no counts", s.root.querySelector(".chron-foot"), null);
}
{
  const s = opened([line("line.1", 1000), line("line.2", 1100)], 1700, []);
  expect("with no return kept the whole chronicle is one stretch, now", titles(s), [text(UI.chronNow)]);
  expect("one kind: no filters to choose", s.root.querySelector<HTMLElement>(".chron-filters")?.hidden, true);
  expect("and no counts", stretches(s)[0]?.querySelector(".chron-foot"), null);
}
{
  const s = opened([line("line.1", 1000), line("line.6", 1100)], 1700, [{ left: 5000, back: 5300 }]);
  expect("a return with no line after it opens no stretch", titles(s), [text(UI.chronNow)]);
}
{
  const s = opened([line("line.6", 1000)], 1700, []);
  expect("with no story yet the chronicle opens on the first filter that has one", filters(s), ["finds*", "all"]);
  expect("its lines", stretches(s).map(shown), [[`find:${text("line.6")} ↳ ${catalog.skillLabel("foraging")} 2`]]);
}
{
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  const first = fixtureStep("rulestab", 200_000);
  screen.show(first);
  screen.show({ ...first, view: { ...first.view, at: first.view.at + 100 } });   // the same runs, a later view
  (screen.root.querySelector("button.chron-open") as HTMLButtonElement).click();
  tap(screen, '.chron-filter[data-filter="rules"]');
  const rows = stretches(screen).map(shown).flat();
  expect("what the rules did is under Rules, each start and let-go once however many Steps repeat it",
    rows.length, ruleEntries(catalog, first.rule_runs).length);
  expect("each with the store's level then, where its rule is a store's", rows.filter((r) => r.includes(" ↳ ")).length > 0, true);
}
{
  const s = opened([line("line.1", 1000), line("line.6", 1050), line("line.2", 2000)], 2500, [{ left: 1100, back: 1700 }]);
  expect("under Story the earlier stretch is folded", stretches(s).map(opens), [false, true]);
  tap(s, '.chron-filter[data-filter="finds"]');
  expect("a filter keeps each stretch's own title", titles(s), [text(UI.chronEarlier)]);
  expect("and opens the newest it draws", stretches(s).map(opens), [true]);
  const head = s.root.querySelector<HTMLElement>("ol.chron-all summary")!;
  head.click();
  (head.parentElement as HTMLDetailsElement).open = false;   // the fake DOM's summary does not toggle
  tap(s, '.chron-filter[data-filter="story"]');
  tap(s, '.chron-filter[data-filter="finds"]');
  expect("a stretch folded by hand stays folded", stretches(s).map(opens), [false]);
}
