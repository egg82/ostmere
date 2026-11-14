// What a long absence brings back (docs/design/opening-screen.md, "Coming back"; decisions.md, "Day and night run on
// the story's clock"): every story line that landed while the player was away plays, in order, each alone on the band
// for its reading time; a tap moves on to the next, and Escape or a tap on the band shows the rest at once. A chip's
// on-line, which comes once per save, goes to the chronicle only; its off-lines, which can come every cycle while away,
// collapse to the chip's last change in the chronicle, as does a repeat task's line. The case is day one's fourth visit
// (run2, V4): beats H7 and B3 and Camp level 6 land after the tired chip's first showing. Keys are the content's; the
// texts here are placeholders.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { Content, LogLine, Step } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { readingMs } from "../src/game/reading";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function check(label: string, block: () => void): void {
  try { block(); } catch (e) { throw new Error(`${label}: ${(e as Error).message}`); }
}

const BEATS = ["l_prints_1", "l_prints_2", "l_b3_1", "l_b3_2", "l_b3_3", "l_b3_4", "l_camp_6"];
const placeholder = (key: string): string => `[fixture] ${key.replace(/_/g, " ")} placeholder line.`;
const content: Content = {
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, ...[...BEATS, "l_tired", "l_rest_done"].map((key) => ({ key, text: placeholder(key) }))],
  line_infos: [...fixtureContent.line_infos, ...BEATS.map((key) => ({ key, kind: "story" as const, cause: null, person: false, mention: null })), { key: "l_tired", kind: "body" as const, cause: null, person: false, mention: null }, { key: "l_rest_done", kind: "tap" as const, cause: null, person: false, mention: null }],
  chip_infos: fixtureContent.chip_infos.map((c) => (c.chip === "tired" ? { ...c, on_line_key: "l_tired" } : c)),
};
const catalog = new Catalog(content);
const text = (key: string): string => catalog.text.get(key);
const visible = (screen: Screen): string[] => [...screen.root.querySelectorAll("ol.lines > li")].filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");
const logged = (screen: Screen): string[] => {
  (document.querySelector("button[data-tab=\"book\"]") as HTMLButtonElement).click();
  return [...document.querySelectorAll(".chron-all .v-body .chron-text")].map((n) => n.textContent ?? "");
};

/** V4's lines in the order they landed: the tired chip's on-line before the beats. */
function v4(): LogLine[] {
  const keys = ["l_tired", ...BEATS];
  return keys.map((key, i) => ({ at: 3000 + i * 10, seq: 0, key, card: null }));
}

function returned(lines: LogLine[], chips: string[]): Screen {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const landed: Step = { ...dayOneStep("landed", 4000), lines };
  screen.show({ ...landed, view: { ...landed.view, chips } }, true);
  return screen;
}

/** Ticks the screen at `ms` on the page's clock. */
function at(screen: Screen, ms: number): void {
  const real = performance.now;
  performance.now = () => ms;
  try { screen.tick(4000); } finally { performance.now = real; }
}

// Every beat plays, in order, each alone for its reading time.
check("every beat plays in order", () => {
  const screen = returned(v4(), ["tired"]);
  let t = performance.now();   // the reveal started during returned(): each beat is due by now plus the ones before it
  BEATS.forEach((key, i) => {
    at(screen, t + 50);
    const shown = visible(screen);
    expect(`beat ${i + 1} is the newest line`, shown[shown.length - 1], text(key));
    expect(`beat ${i + 1} alone: nothing after it yet`, shown.filter((s) => BEATS.slice(i + 1).map(text).includes(s)), []);
    t += readingMs(text(key));
  });
  expect("no chip line on the band", visible(screen).filter((s) => s === text("l_tired")), []);
  expect("the band keeps three", visible(screen).length <= 3, true);
});

// The tired chip, on now: its on-line in the chronicle only.
check("a chip's on-line goes to the chronicle", () => {
  const screen = returned(v4(), ["tired"]);
  const log = logged(screen);
  expect("one tired line in the chronicle", log.filter((s) => s === text("l_tired")).length, 1);
  expect("the beats in the chronicle, in order", log.filter((s) => BEATS.map(text).includes(s)), BEATS.map(text));
});

// The chip off now (its off-line none): its on-line, the only one the save will send, is still in the chronicle.
check("a chip that ended off keeps its on-line", () => {
  const screen = returned(v4(), []);
  expect("one tired line in the chronicle", logged(screen).filter((s) => s === text("l_tired")).length, 1);
});

// A tap moves on to the next beat at once; Escape shows the rest.
check("a tap advances, Escape skips", () => {
  const screen = returned(v4(), ["tired"]);
  const t0 = performance.now();
  at(screen, t0 + 10);
  expect("the first beat", visible(screen).at(-1), text(BEATS[0]!));
  fakeDocument.body.dispatchEvent(new FakeEvent("click"));
  at(screen, t0 + 20);
  expect("a tap: the second beat", visible(screen).at(-1), text(BEATS[1]!));
  fakeDocument.body.dispatchEvent(new FakeEvent("keydown", { key: "Escape" }));
  at(screen, t0 + 30);
  expect("Escape: the last beat is shown", visible(screen).at(-1), text(BEATS[BEATS.length - 1]!));
});

// A repeat task's line (an uncapped card wrote it) goes to the chronicle, not the band.
check("a repeat task's line takes no turn", () => {
  const lines: LogLine[] = [{ at: 3000, seq: 0, key: "l_rest_done", card: "rest" }, { at: 3010, seq: 1, key: "l_b3_1", card: null }];
  const screen = returned(lines, []);
  const t0 = performance.now();
  at(screen, t0 + 10);
  expect("the beat leads", visible(screen), [text("l_b3_1")]);
  expect("the task's line is in the chronicle", logged(screen).includes(text("l_rest_done")), true);
});

// A chip that went on and then off, and on and off again, while away: its on-line and its last off-line are kept.
check("the on-line and the last off-line", () => {
  const offContent: Content = {
    ...content,
    text_entries: [...content.text_entries, { key: "l_rested", text: placeholder("l_rested") }],
    line_infos: [...content.line_infos, { key: "l_rested", kind: "body" as const, cause: null, person: false, mention: null }],
    chip_infos: content.chip_infos.map((c) => (c.chip === "tired" ? { ...c, on_line_key: "l_tired", off_line_key: "l_rested" } : c)),
  };
  const screen = new Screen(new Catalog(offContent), () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const lines: LogLine[] = ["l_tired", "l_rested", "l_rested"].map((key, i) => ({ at: 3000 + i, seq: 0, key, card: null }));
  const landed = dayOneStep("landed", 4000);
  screen.show({ ...landed, lines, view: { ...landed.view, chips: [] } }, true);
  const log = logged(screen);
  expect("the on-line, then one off-line", log.filter((s) => s === text("l_tired") || s === placeholder("l_rested")),
    [text("l_tired"), placeholder("l_rested")]);
});

// A tap on the band's lines shows every beat still waiting.
check("a tap on the band skips", () => {
  const screen = returned(v4(), ["tired"]);
  const t0 = performance.now();
  at(screen, t0 + 10);
  fakeDocument.querySelector(".lines")?.dispatchEvent(new FakeEvent("click"));
  at(screen, t0 + 20);
  expect("the last beat is shown", visible(screen).at(-1), text(BEATS[BEATS.length - 1]!));
});

// A repeat task that left the view while away (put away, say) is still a repeat task: the view before says so.
check("a repeat task known from the view before", () => {
  const lines: LogLine[] = [{ at: 3000, seq: 0, key: "l_rest_done", card: "rest" }, { at: 3010, seq: 1, key: "l_b3_1", card: null }];
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const landed = dayOneStep("landed", 4000);
  screen.show({ ...landed, lines, view: { ...landed.view, cards: landed.view.cards.filter((c) => c.card !== "rest") } }, true);
  at(screen, performance.now() + 10);
  expect("the beat leads", visible(screen), [text("l_b3_1")]);
});
