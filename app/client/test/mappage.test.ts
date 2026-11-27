// The Book's Map page on a real Screen (contract/map.txt, "MAP", acceptance 4 and 7): no button and nothing fetched until a
// place is revealed; then the button, last in the Book's row, the stamps' manifest asked for, the Book's tab dotted for a
// place revealed later, the named places listed with the town first, and a row's tap sending nothing. And the map's
// lesson: on the Map button's first showing, two steps, kept, never again.
import { install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { placesView, withPlaces } from "../fixtures/places";
import { fixtureStep } from "../fixtures/steps";
import { Catalog } from "../src/game/catalog";
import { FIRST_MIX, FIRST_RULE, JOURNAL, JOURNAL_NUMBERS, MAP } from "../src/game/lessons";
import { Glow } from "../src/ui/feedback/fresh";
import { PHONE } from "../src/ui/layout";
import { Lessons } from "../src/ui/lessons/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800, matchMedia: (q: string) => ({ matches: q === PHONE, addEventListener: () => {} }) });
const requests: string[] = [];
Object.assign(globalThis, { fetch: (url: string) => { requests.push(url); return new Promise(() => undefined); } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(withPlaces(fixtureContent));
const QUIET = [FIRST_MIX, FIRST_RULE, JOURNAL, JOURNAL_NUMBERS];

function rig(lessons: string[]) {
  const sent: Flat[] = [];
  const keeps = keepsOf({ ...NEW_FLAT, lessons }, sent);
  const screen = new Screen(catalog, () => { throw new Error("the map decided something"); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  let at = 100;
  const show = (revealed: number): void => { at += 10; const s = fixtureStep("town", at); screen.show({ ...s, view: placesView(s.view, revealed) }); };
  const q = (sel: string): HTMLElement | null => screen.root.querySelector<HTMLElement>(sel);
  const pages = (): string[] => [...screen.root.querySelectorAll<HTMLElement>(".book-page")].filter((b) => !b.hidden).map((b) => b.dataset["page"] ?? "");
  return { screen, keeps, sent, show, q, pages };
}

{  // 4: no place, no page; then the page, last; a later place dots the tab
  const r = rig([...QUIET, MAP]);
  r.show(0);
  expect("no Map button with no place revealed", r.pages().includes("map"), false);
  expect("nothing asked of the stamps", requests.filter((u) => u.includes("/assets/art/map/")), []);
  r.show(1);
  expect("the Map button shows, last in the row", r.pages().at(-1), "map");
  expect("the stamps' manifest is asked for once", requests.filter((u) => u.includes("/assets/art/map/")), ["/assets/art/map/manifest.json"]);
  const tabDot = (): boolean => r.q('.tabs [data-tab="book"] .new-dot') !== null;
  r.q('.tabs [data-tab="book"]')!.click();
  expect("no dot once the Book is opened", tabDot(), false);
  r.show(3);
  expect("a place revealed later dots the Book's tab", tabDot(), true);
  const rows = (): string[] => [...r.screen.root.querySelectorAll<HTMLElement>(".map-row")].map((n) => n.textContent ?? "");
  expect("the named places listed, the town first", rows(), [catalog.townTitle(placesView(fixtureStep("town", 0).view, 0)), "The Old Mill", "Ford of the Long Shallows"]);
  r.q('.book [data-page="map"]')!.click();
  const before = [requests.length, r.sent.length];
  r.q('.map-row[data-place="pl_ford"]')!.click();
  expect("a row's tap marks it", r.q('.map-row[data-place="pl_ford"]')!.getAttribute("aria-pressed"), "true");
  expect("and sends nothing", [requests.length, r.sent.length], before);
  r.show(2);
  expect("an unrevealed place is not listed", rows().includes("Ford of the Long Shallows"), false);
}

{  // 7: the lesson on the Map button's first showing
  const r = rig(QUIET);
  const RECT = { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 };
  const NONE = { left: 0, top: 0, width: 0, height: 0, right: 0, bottom: 0 };
  let clock = 0;
  const shown = (n: HTMLElement): boolean => { for (let x: HTMLElement | null = n; x; x = x.parentElement) if (x.hidden) return false; return true; };
  const runner = new Lessons({ catalog, glow: new Glow(), keeps: r.keeps }, document.body, () => undefined, document, () => clock);
  const line = (): string => (runner.root.hidden ? "" : runner.root.querySelector(".lesson-line")?.textContent ?? "");
  const tick = (t: number): void => {
    for (const sel of ['[data-teach="map"]', ".map-sheet"])
      for (const n of document.querySelectorAll<HTMLElement>(sel)) Object.assign(n, { rect: shown(n) ? RECT : NONE });   // the fake DOM lays nothing out
    clock = t;
    runner.tick();
  };
  r.show(0);
  runner.update(fixtureStep("town", 0).view);
  tick(0);
  expect("no lesson with no Map button", runner.current, null);
  r.show(1);
  r.q('.tabs [data-tab="book"]')!.click();
  tick(1);
  expect("starts on the Map's own button", [runner.current, line()], [MAP, catalog.text.get("ui.lesson.map_open")]);
  r.q('.book [data-page="map"]')!.click();
  tick(2);
  expect("then on the sheet", line(), catalog.text.get("ui.lesson.map_places"));
  runner.root.querySelector<HTMLElement>(".lesson-next")!.click();
  tick(3);
  expect("kept", [runner.current, r.keeps.lessonKept(MAP)], [null, true]);
  tick(60_000);
  expect("never again", runner.current, null);
}
