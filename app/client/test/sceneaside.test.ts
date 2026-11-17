// On a phone the scene steps aside while an editor has the screen (the Rules tab, the mix editor, the town editor, a
// person's page) and returns on Tasks and Book. The screen sets one state, `scene-aside` on its root, that game.css
// turns into a collapsed art (phoneroom.test.ts reads that rule); the speaker's seat, the head, stays. Story lines that
// arrive meanwhile wait their turn in the arrival queue and show once.
import { fakeDocument, type FakeEl, install } from "./fake-dom";
import { townStep } from "../fixtures/town";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import type { Content, LogLine } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { matchMedia: () => ({ matches: true, addEventListener: () => {} }) });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}
const one = (root: FakeEl, sel: string): FakeEl => {
  const n = root.querySelector(sel);
  if (!n) throw new Error(`no ${sel}`);
  return n;
};
const BEATS = ["l_prints_1", "l_prints_2", "l_b3_1"];
const content: Content = {
  ...fixtureContent,
  text_entries: [...fixtureContent.text_entries, ...BEATS.map((key) => ({ key, text: `[fixture] ${key} placeholder line.` }))],
  line_infos: [...fixtureContent.line_infos, ...BEATS.map((key) => ({ key, kind: "story" as const, cause: null, person: false, mention: null }))],
};
const catalog = new Catalog(content);
const text = (key: string): string => catalog.text.get(key);
function fresh(): { screen: Screen; root: FakeEl; aside: () => boolean } {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(townStep("town", {}, 100));
  const root = fakeDocument.body.firstElementChild as FakeEl;
  return { screen, root, aside: () => root.classList.contains("scene-aside") };
}
const tab = (root: FakeEl, name: string): void => one(root, `.tabs [data-tab="${name}"]`).click();

{  // Tasks, Town: the scene stays
  const { root, aside } = fresh();
  expect("Tasks: the scene is there", aside(), false);
  tab(root, "town");
  expect("Town: the scene is there", aside(), false);
}
{  // Rules: aside; Tasks brings it back; the Book's sheet leaves the tab on as it was
  const { root, aside } = fresh();
  tab(root, "rules");
  expect("Rules: the scene is aside", aside(), true);
  tab(root, "book");
  expect("Book's sheet over Rules: still aside, the tab on", aside(), true);
  tab(root, "cards");
  expect("Tasks: the scene returns", aside(), false);
}
{  // the mix editor
  const { root, aside } = fresh();
  const edit = root.querySelectorAll(".hands-edit").find((b) => !b.classList.contains("town-change") && !b.classList.contains("person-change"));
  if (!edit) throw new Error("no mix edit");
  edit.click();
  expect("the mix editor: the scene is aside", aside(), true);
  tab(root, "cards");
  expect("Tasks closes it and the scene returns", aside(), false);
}
{  // a person's page, and the town editor (camp editing)
  const { root, aside } = fresh();
  tab(root, "town");
  one(root, ".person-change").click();
  expect("a person's page: the scene is aside", aside(), true);
  tab(root, "cards");
  expect("Tasks: the scene returns", aside(), false);
  tab(root, "town");
  one(root, ".town-change").click();
  expect("the town editor: the scene is aside", aside(), true);
  tab(root, "book");
  expect("Book keeps the editor's state", aside(), true);
  tab(root, "cards");
  expect("Tasks: the scene returns", aside(), false);
}
{  // beats arriving while the scene is aside take their turns in the queue, each shown once, in order
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps());
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  const root = fakeDocument.body.firstElementChild as FakeEl;
  tab(root, "rules");
  const lines: LogLine[] = BEATS.map((key, i) => ({ at: 3000 + i * 10, seq: 0, key, card: null, opens_beat: false }));
  screen.show({ ...dayOneStep("landed", 4000), lines }, true);
  const visible = (): string[] => root.querySelectorAll("ol.lines > li").filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");
  let waiting = true;   // the queue's own clock is the page's: read it at the time ticked to
  const at = (ms: number): void => {
    const real = performance.now;
    performance.now = () => ms;
    try { screen.tick(4000); waiting = screen.revealing; } finally { performance.now = real; }
  };
  expect("aside, the first beat waits its turn", [root.classList.contains("scene-aside"), screen.revealing], [true, true]);
  const t0 = performance.now();
  at(t0 + 50);
  expect("the first beat plays alone", visible().slice(-1), [text(BEATS[0]!)]);
  at(t0 + 120_000);
  expect("the last beat has played, once", visible().filter((v) => v === text(BEATS[2]!)), [text(BEATS[2]!)]);
  expect("nothing waits", waiting, false);
  const played = visible();
  tab(root, "cards");
  expect("the scene returns and replays nothing", [root.classList.contains("scene-aside"), visible()], [false, played]);
}
