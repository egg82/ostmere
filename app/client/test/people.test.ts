// People's coming and going in the story (CONTRACT.txt, "PEOPLE"; game/people.ts, ui/story.ts, ui/chapter.ts): a day's
// mention lines are one line, worded from the band for how many they count and drawn by a seeded shuffle bag; a later
// Step on the same day rewords it rather than adding a second; the "Since you left" chapter gathers the lines telling a
// person's joining and the day's mentions into its people section, and has none when nobody came or went.
import { install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps, NEW_SAVE } from "../src/game/keeps";
import { counted, DAY_S, mentionId, mentionKey } from "../src/game/people";
import { UI } from "../src/game/text";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const people = fixtureContent.people;
const ONE = ["came.one.a", "came.one.b"];

{
  const one = counted(null, "joined", "mason", 500);
  expect("a day's first mention is counted at its second", [one.at, one.lanes, one.day], [500, ["mason"], 0]);
  const two = counted(one, "joined", "helper", 900);
  expect("another lane is counted in, the day's first second kept", [two.at, two.lanes], [500, ["mason", "helper"]]);
  expect("a day ends at its last game second", [mentionId("joined", DAY_S - 1), mentionId("joined", DAY_S), mentionId("left", 0)],
    ["joined:0", "joined:1", "left:0"]);
  expect("one person is worded by the first band", ONE.includes(mentionKey(people, 7, one) ?? ""), true);
  expect("two by the band from two", mentionKey(people, 7, two), "came.few");
  expect("a leaving by the went bands", mentionKey(people, 7, counted(null, "left", "mason", 0)), "went.one");
  expect("with no bands, nothing", mentionKey(null, 7, one), null);
  const day = (d: number): string | null => mentionKey(people, 7, { ...one, day: d });
  expect("the same day reads the same every time", day(5), day(5));
  expect("each pair of days takes both of the band's lines, in a seeded order", [0, 2, 4, 6].map((d) => [day(d), day(d + 1)].sort()),
    [ONE, ONE, ONE, ONE]);
  const orders = new Set([0, 2, 4, 6, 8, 10].map((d) => day(d)));
  expect("and which comes first is shuffled, not fixed", orders.size, 2);
}

const line = (key: string, at: number, seq = 0): LogLine => ({ at, seq, key, card: null });

function returned(lines: LogLine[], now: number): Screen {
  const keeps = new Keeps({ save: { ...NEW_SAVE, visits: [{ left: 1100, back: 1700 }], chapter: null } });
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  screen.show({ ...dayOneStep("landed", now), lines }, true);
  (screen.root.querySelector("button[data-tab=\"book\"]") as HTMLButtonElement).click();
  return screen;
}

const chapter = (s: Screen): HTMLElement | null => s.root.querySelector<HTMLElement>("ol.chron-all > li.chapter");
const texts = (n: Element | null | undefined, sel: string): string[] => [...(n?.querySelectorAll(sel) ?? [])].map((x) => x.textContent ?? "");
const section = (s: Screen): HTMLElement | null => chapter(s)?.querySelector<HTMLElement>(".chapter-people") ?? null;
const strip = (s: Screen): string[] => texts(s.root.querySelector("ol.lines"), "li");

{
  const s = returned([line("line.1", 1800), line("line.joins", 1900), line("people.joined.mason", 2000, 1), line("people.joined.helper", 2000, 2)], 2500);
  expect("the people section is labelled", section(s)?.querySelector(".chapter-sec")?.textContent, text(UI.chapterPeople));
  expect("it holds the line telling a person's joining, then the day's one mention, worded for two",
    texts(section(s), ".chron-text"), [text("line.joins"), text("came.few")]);
  expect("which leave the chapter's other lines", texts(chapter(s), ":scope > .chron-line .chron-text"), [text("line.1")]);
  expect("the strip shows the day's mention once", strip(s).filter((t) => t === text("came.few")).length, 1);
  expect("and no mention line by itself", strip(s).includes(""), false);
}
{
  const s = returned([line("people.joined.mason", 2000)], 2500);
  expect("one person is worded by the first band", ONE.map(text).includes(texts(section(s), ".chron-text")[0] ?? ""), true);
  s.show({ ...dayOneStep("landed", 2600), lines: [line("people.joined.helper", 2550)] }, true);
  expect("a later Step on the same day rewords the day's mention, adding none", texts(section(s), ".chron-text"), [text("came.few")]);
  s.show({ ...dayOneStep("landed", DAY_S + 10), lines: [line("people.left.mason", DAY_S + 5)] }, true);
  const all = texts(s.root.querySelector("ol.chron-all"), ".chron-text");
  expect("another day's, or a leaving, is a line of its own", [all.includes(text("came.few")), all.includes(text("went.one"))], [true, true]);
}
{
  const s = returned([line("line.1", 1800), line("line.2", 1900)], 2500);
  expect("a return that brought no one has no people section", section(s), null);
  expect("its lines stay where they were", texts(chapter(s), ":scope > .chron-line .chron-text"), [text("line.1"), text("line.2")]);
}
