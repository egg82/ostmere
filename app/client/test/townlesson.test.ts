// The town's lesson (game/lessons.ts, TOWN_MIX), as lessons-as-data on the strip's and the town editor's own controls:
// it starts when the strip's Change shows, walks Change, the person's bar, Save, and the strip once more, and is kept on
// the account when done or skipped, never again. Run against the rendered strip and editor, not stand-in controls.
import { fakeDocument, install } from "./fake-dom";
import { testContext } from "./context";
import { townStep } from "../fixtures/town";
import type { View } from "../src/api/types";
import { LESSONS, TOWN_MIX } from "../src/game/lessons";
import { Glow } from "../src/ui/fresh";
import { LaneRows } from "../src/ui/lanerows";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

/** The town as the game makes it: each person's whole time on one card (the lesson starts only on a town mix still so). */
const asMade = (v: View): View => ({ ...v, mixes: v.mixes.map((m) => (m.id === v.running_town_mix_id ? { ...m, components: m.components.map((c) => (c.kind === "card_share" ? { ...c, share_bp: 10000 } : c)) } : m)) });
const view = asMade(townStep("town").view);
let clock = 0;

function rig(account: Flat = NEW_FLAT) {
  const { ctx, got } = testContext();
  const rows = new LaneRows(ctx);
  fakeDocument.body.replaceChildren();
  document.body.append(rows.root, rows.town.root);
  rows.update(view);
  const sent: Flat[] = [];
  const keeps = keepsOf(account, sent);
  const lessons = new Lessons({ catalog: ctx.catalog, glow: new Glow(), keeps }, document.body, () => undefined, document, () => clock);
  lessons.update(view);
  const text = (key: string): string => ctx.catalog.text.get(key);
  const line = (): string => (lessons.root.hidden ? "" : lessons.root.querySelector(".lesson-line")?.textContent ?? "");
  /** Every control the lesson names, given a size (the fake DOM has no layout). */
  const lay = (): void => {
    for (const sel of [".town-change", ".town-editor .town-bar", ".town-editor .editor-head .primary", ".town .town-people"])
      for (const n of document.querySelectorAll(sel)) Object.assign(n, { rect: { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 } });
  };
  const tick = (t: number): void => { lay(); clock = t; lessons.tick(); };
  const gotIt = (): void => lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();   // a read step ends on a tap of the note
  return { rows, lessons, keeps, sent, line, text, tick, got, gotIt };
}

{  // the lesson is data: its trigger and four steps, each naming a control of the strip or the town editor
  const lesson = LESSONS.find((l) => l.id === TOWN_MIX);
  expect("the lesson exists", lesson?.trigger, '[data-teach="town-change"]');
  expect("its steps", lesson?.steps.map((s) => [s.target({}), s.ends]), [
    ['[data-teach="town-change"]', "touch"], [".town-editor .town-bar", "read"], [".town-editor .editor-head .primary", "touch"], [".town .town-people", "read"]]);
}

{  // walked to the end: done, kept, and it does not start again
  const r = rig();
  r.tick(0);
  expect("starts on the strip's Change", r.line(), r.text("ui.lesson.town_change"));
  document.querySelector<HTMLElement>(".town-change")?.click();   // the real control: opens the town editor too
  r.tick(1);
  expect("the person's bar", r.line(), r.text("ui.lesson.town_bar"));
  r.tick(10 * 60_000);
  expect("a read step waits for a tap on the note", r.line(), r.text("ui.lesson.town_bar"));
  r.gotIt();
  r.tick(10 * 60_000 + 1);
  expect("then Save", r.line(), r.text("ui.lesson.town_save"));
  document.querySelector<HTMLElement>(".town-editor .editor-head .primary")?.click();
  r.tick(10 * 60_000 + 2);
  expect("then the strip", r.line(), r.text("ui.lesson.town_runs"));
  r.gotIt();
  r.tick(10 * 60_000 + 3);
  expect("done: kept in the save", r.sent.at(-1)?.lessons, [TOWN_MIX]);
  const again = rig(r.sent.at(-1));
  again.tick(0);
  expect("never again", again.line(), "");
}

{  // skipped at the first step: kept, never again
  const r = rig();
  r.tick(0);
  r.lessons.root.querySelector<HTMLElement>(".lesson-skip")?.click();
  expect("skipped: kept", r.sent.at(-1)?.lessons, [TOWN_MIX]);
  r.tick(10);
  expect("skipped: the note goes and stays gone", r.line(), "");
}
