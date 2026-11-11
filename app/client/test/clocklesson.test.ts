// The clock's lesson (game/lessons.ts, CLOCK): the night is a wait in real time, taught on its countdown the moment
// that countdown first shows. The countdown is the foot of a card waiting on a store the player was never shown
// (ui/cards.ts marks it); before it, nothing starts; a card waiting on a store in view is no clock.
import { install } from "./fake-dom";
import { fixtureContent, Q } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Card, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { CLOCK } from "../src/game/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const still = { start: AT, start_value: 0, rate: 0, limit: null };
/** A card whose blocker is a countdown on `store` (the engine's ready time 3400 s on). */
const waiting = (id: string, store: string): Card => ({
  card: id, completions: 0, cap: 1, bar: still, bar_total: 20, by: null, completes_at: null, share_bp: 0, run: null, cuts_in: false, spent_store: null, gained: [], tap_s: 20,
  blocker: { condition: { kind: "at_least", watched: { kind: "store_value", store }, value: 20 * Q, release: 20 * Q }, ready_at: AT + 3400 },
  needs: [{ store, quantity: 20 * Q, segment: still, gate: null, makers: [], spent: false }],
});
const base = fixtureStep("restoffer", AT);
const seen = base.view.unlocked.find((u) => u.category === "store")!.id;   // a store in view
const viewWith = (cards: Card[]): View => ({ ...base.view, cards: [...base.view.cards, ...cards], unlocked: base.view.unlocked.filter((u) => u.id !== "night") });

function rig(view: View, keeps = new Keeps()) {
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...base, view });
  const marks = (): HTMLElement[] => [...screen.root.querySelectorAll<HTMLElement>('.card-foot[data-teach="clock"]')];
  const note = (): string => { const n = screen.root.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const laid = (): void => { for (const m of marks()) Object.assign(m, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } }); };
  return { screen, marks, note, laid, keeps };
}

{  // before the countdown: nothing starts, nothing is marked
  const r = rig(viewWith([]));
  r.screen.tick(AT);
  expect("no night card: no mark", r.marks().length, 0);
  expect("no night card: no lesson", r.note(), "");
}

{  // the countdown on a store never shown (the night): it is marked, and the lesson starts on it
  const r = rig(viewWith([waiting("look_out", "night")]));
  r.screen.tick(AT);
  expect("the night's countdown is the clock", r.marks().length, 1);
  r.laid();
  r.screen.tick(AT + 1);
  expect("the lesson's line is on show", r.note(), catalog.text.get("ui.lesson.clock"));
  expect("no lesson kept yet", r.keeps.lessonKept(CLOCK), false);
}

{  // a countdown on a store the player is shown is no clock
  const r = rig(viewWith([waiting("look_out", seen)]));
  r.screen.tick(AT);
  expect("a store in view: no mark", r.marks().length, 0);
}

{  // kept once: a player who skipped or finished it never sees it again
  const keeps = keepsOf({ ...NEW_FLAT, lessons: [CLOCK] });
  const r = rig(viewWith([waiting("look_out", "night")]), keeps);
  r.screen.tick(AT);
  r.laid();
  r.screen.tick(AT + 1);
  expect("already kept: no lesson", r.note(), "");
}
