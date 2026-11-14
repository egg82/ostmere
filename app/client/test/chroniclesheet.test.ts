// The chronicle, the Book's first page (ui/chroniclesheet.ts, ui/chapter.ts): newest first, the newest return's "Since you left" chapter
// at the top, never folded, then one stretch per earlier return folded to its counts; a row of filters once two kinds
// have entries, Story first; under Story, the chapter's figures as rows and a stretch's counts of the other filters, each
// opening its filter; each line over its cause.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureStep } from "../fixtures/steps";
import { fixtureContent, Q } from "../fixtures/content";
import type { Chapter, LogLine, Offer } from "../src/api/types";
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
const ASK: Offer = { offer: "ask", answer: null, answers: [{ answer: "wait", card: null, takes_s: null }] };

function opened(lines: LogLine[], now: number, visits: Array<{ left: number; back: number }>, chapter: Chapter | null = null, offers: Offer[] = []): Screen {
  const keeps = new Keeps({ save: { ...NEW_SAVE, visits, chapter } });
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const landed = dayOneStep("landed", now);
  screen.show({ ...landed, view: { ...landed.view, offers }, lines }, true);
  (screen.root.querySelector("button[data-tab=\"book\"]") as HTMLButtonElement).click();
  const heading = screen.root.querySelector(".book-tab .book-head > .view-title");
  expect("the Book's view, under its title", heading?.textContent, text(UI.tabBook));
  return screen;
}

const stretches = (s: Screen): HTMLElement[] => [...s.root.querySelectorAll<HTMLElement>("ol.chron-all > li")];
const chapterOf = (s: Screen): HTMLElement | undefined => stretches(s).find((n) => n.classList.contains("chapter"));
const older = (s: Screen): HTMLElement[] => stretches(s).filter((n) => !n.classList.contains("chapter"));
const titles = (s: Screen): string[] => stretches(s).map((n) => n.querySelector(".v-title, .chapter-title")?.textContent ?? "");
const opens = (n: HTMLElement): boolean => n.querySelector<HTMLDetailsElement>("details")?.open ?? false;
const shown = (n: HTMLElement): string[] => [...n.querySelectorAll<HTMLElement>(".chron-line")]
  .map((p) => `${p.dataset["kind"]}:${p.querySelector(".chron-text")?.textContent}${p.querySelector(".chron-cause") ? ` ↳ ${p.querySelector(".chron-cause")?.textContent}` : ""}`);
const filters = (s: Screen): string[] => [...s.root.querySelectorAll<HTMLElement>(".chron-filters > button")]
  .map((b) => `${b.dataset["filter"]}${b.getAttribute("aria-pressed") === "true" ? "*" : ""}`);
const rows = (n: HTMLElement | undefined): string[] => [...(n?.querySelectorAll<HTMLElement>(".chapter-rows > dt, .chapter-rows > dd") ?? [])].map((r) => r.textContent ?? "");
const tap = (s: Screen, sel: string): void => (s.root.querySelector(sel) as HTMLButtonElement).click();

{
  const s = opened([line("line.1", 1000), line("line.2", 1100), line("line.3", 1800), line("line.6", 1900), line("line.1", 2000)], 2500,
    [{ left: 1100, back: 1700 }]);
  const chapter = chapterOf(s)!;
  const [early] = older(s);
  expect("two kinds have entries: the filters, Story chosen, All last", filters(s), ["story*", "finds", "all"]);
  expect("newest first: the newest return's chapter, then the stretch before the first return", titles(s), [text(UI.chapter), text(UI.chronEarlier)]);
  expect("the chapter says how long the player was away", chapter.querySelector(".v-ago")?.textContent, "10m");
  expect("the older stretch is folded", opens(early!), false);
  expect("a folded stretch reads as its counts", early?.querySelector(".v-sum")?.textContent, "Story 2");
  expect("under Story: the story's lines and a tap's, oldest first, each over its cause", shown(chapter),
    [`tap:${text("line.3")} ↳ ${catalog.runnerLabel("stand")}`, `story:${text("line.1")}`]);
  expect("the older stretch's second line carries its cause", shown(early!)[1], `story:${text("line.2")} ↳ time`);
  expect("no figures kept for this return: no rows, and nothing claimed", [rows(chapter), chapter.querySelector(".chapter-still")], [[], null]);
  const counts = [...chapter.querySelectorAll<HTMLElement>(".chron-foot > button")].map((b) => b.textContent);
  expect("the chapter ends with the other filters' counts", counts, ["Finds 1"]);
  tap(s, '.chron-foot > button[data-filter="finds"]');
  expect("a count opens its filter", filters(s), ["story", "finds*", "all"]);
  expect("which holds the finds alone", stretches(s).map(shown), [[`find:${text("line.6")} ↳ ${catalog.skillLabel("foraging")} 2`]]);
  tap(s, '.chron-filter[data-filter="all"]');
  expect("All holds every line, the newest stretch first", stretches(s).map(shown).flat().map((x) => x.split(":")[0]), ["tap", "find", "story", "story", "story"]);
  expect("and no counts", s.root.querySelector(".chron-foot"), null);
}
{
  const s = opened([line("line.1", 1000), line("line.2", 1500), line("line.1", 3000)], 3200, [{ left: 1200, back: 1400 + 1800 }, { left: 2500, back: 2900 }]);
  expect("each earlier stretch newest first, under the chapter", titles(s), [text(UI.chapter), "Away 33m", text(UI.chronEarlier)]);
}
{
  const s = opened([line("line.1", 1000), line("line.2", 1100)], 1700, []);
  expect("with no return kept the whole chronicle is one stretch, now, and open", [titles(s), stretches(s).map(opens)], [[text(UI.chronNow)], [true]]);
  expect("one kind: no filters to choose", s.root.querySelector<HTMLElement>(".chron-filters")?.hidden, true);
  expect("and no counts", stretches(s)[0]?.querySelector(".chron-foot"), null);
}
{
  const lines = [line("line.1", 1000), line("line.6", 1100)];
  const s = opened(lines, 5400, [{ left: 5000, back: 5300 }]);
  expect("a return with no line after it still opens its chapter, empty", titles(s), [text(UI.chapter), text(UI.chronEarlier)]);
  expect("with no figures kept it claims nothing", chapterOf(s)?.querySelector(".chapter-still"), null);
  const still = opened(lines, 5400, [{ left: 5000, back: 5300 }], { left: 5000, back: 5300, stores: [], levels: [], camp: null, rules: [] });
  expect("with figures kept and nothing in them, it says nothing changed", chapterOf(still)?.querySelector(".chapter-still")?.textContent, text(UI.chapterStill));
  const stale = opened(lines, 5400, [{ left: 5000, back: 5300 }], { left: 10, back: 4000, stores: [], levels: [], camp: null, rules: [] });
  expect("an older return's figures are not this one's", chapterOf(stale)?.querySelector(".chapter-still"), null);
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
  (screen.root.querySelector("button[data-tab=\"book\"]") as HTMLButtonElement).click();
  tap(screen, '.chron-filter[data-filter="rules"]');
  const found = stretches(screen).map(shown).flat();
  expect("what the rules did is under Rules, each start and let-go once however many Steps repeat it",
    found.length, ruleEntries(catalog, first.rule_runs).length);
  expect("each with the store's level then, where its rule is a store's", found.filter((r) => r.includes(" ↳ ")).length > 0, true);
}
{
  const s = opened([line("line.1", 1000), line("line.6", 1050), line("line.2", 2000)], 2500, [{ left: 1100, back: 1700 }]);
  expect("under Story the earlier stretch is folded", older(s).map(opens), [false]);
  tap(s, '.chron-filter[data-filter="finds"]');
  expect("a filter keeps each stretch's own title, and the chapter with none of its lines is not drawn", titles(s), [text(UI.chronEarlier)]);
  expect("and opens the newest it draws", stretches(s).map(opens), [true]);
  const head = s.root.querySelector<HTMLElement>("ol.chron-all summary")!;
  head.click();
  (head.parentElement as HTMLDetailsElement).open = false;   // the fake DOM's summary does not toggle
  tap(s, '.chron-filter[data-filter="story"]');
  tap(s, '.chron-filter[data-filter="finds"]');
  expect("a stretch folded by hand stays folded", stretches(s).map(opens), [false]);
}
{
  const figures: Chapter = { left: 1100, back: 1700, stores: [{ id: "wood", was: 2 * Q, now: 40 * Q }], levels: [{ id: "foraging", was: 1, now: 2 }], camp: null, rules: [] };
  const s = opened([line("line.1", 1800), line("line.7", 1900), line("line.6", 2000)], 2500, [{ left: 1100, back: 1700 }], figures, [ASK]);
  const chapter = chapterOf(s);
  expect("under Story the chapter's figures follow its lines, each row only when it has something", rows(chapter), [
    text(UI.chapterStores), `+38 ${catalog.storeLabel("wood")}`, text(UI.chapterLevels), `${catalog.skillLabel("foraging")} 1 → 2`,
    text(UI.chapterWaiting), "1 ask"]);
  expect("then the counts of the filters no row opens", [...(chapter?.querySelectorAll(".chron-foot > button") ?? [])].map((b) => b.textContent), ["Finds 1"]);
  tap(s, '.chapter-rows button[data-filter="levels"]');
  expect("the levels row's label opens Levels", filters(s).filter((f) => f.endsWith("*")), ["levels*"]);
  expect("where the chapter shows no figures", rows(chapterOf(s)), []);
  tap(s, '.chron-filter[data-filter="story"]');
  tap(s, '.chapter-rows dd[data-section="waiting"] button');
  expect("the waiting count leaves the Book for Tasks to show what waits", [s.root.querySelector<HTMLElement>(".book-tab")?.hidden, s.root.querySelector("button[data-tab=\"cards\"]")?.getAttribute("aria-pressed")], [true, "true"]);
}
