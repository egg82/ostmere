// The side-holder's lesson (game/sidelesson.ts, SIDE_MIX; docs/design/opening-screen/lessons.md, "Lessons"): the first time a fight
// of a side is served while a card that holds that side is in play, the holder's face is the trigger. Two steps: the face, then
// the Mixes control, whose line says both in one mix run together. Never again once done or skipped, and it starts from
// nothing else.
import { install } from "./fake-dom";
import { fightsStep } from "../fixtures/fights";
import { fixtureContent } from "../fixtures/content";
import type { Content, Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { Keeps } from "../src/game/account/keeps";
import { FIRST_MIX, FIRST_RULE, LESSONS, mayStart, SIDE_MIX } from "../src/game/lessons/lessons";
import { sideCue } from "../src/game/lessons/sidelesson";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

function holding(over: Partial<Content["card_infos"][number]> = {}): Catalog {
  return new Catalog({
    ...fixtureContent,
    card_infos: fixtureContent.card_infos.map((c) => (c.card === "poultice" ? { ...c, upside_key: "up.kept", change_bp: [5000], kept: [{ side: "hands", lane: null, amount_bp: 5000, slot: 0 }], ...over } : c)),
    text_entries: [...fixtureContent.text_entries, { key: "up.kept", text: "{pct} strength while kept" }],
  });
}
const catalog = holding();
const AT = 100;
const step = fightsStep("fight", AT);
const view = step.view;
const TAUGHT = { ...NEW_FLAT, rule_seen: true, lessons: [FIRST_MIX, FIRST_RULE] };
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const slots = { card: catalog.cardLabel("poultice"), task: catalog.cardLabel("hunt") };

// the cue, one fact at a time
expect("a fight of its side is served, its card in play", sideCue(catalog, view), { card: "poultice", fight: "hunt" });
expect("combat off", sideCue(catalog, { ...view, unlocked: view.unlocked.filter((u) => u.id !== "combat") }), null);
expect("no fight served", sideCue(catalog, { ...view, fights: [] }), null);
expect("only a fight that runs on its own (no card to mix)", sideCue(catalog, { ...view, fights: view.fights.filter((f) => f.runner === "raiders") }), null);
expect("the fight card not in play", sideCue(catalog, { ...view, cards: view.cards.filter((c) => c.card !== "hunt") }), null);
expect("a card that holds no side", sideCue(holding({ kept: [] }), view), null);
const both = { ...view, mixes: view.mixes.map((m, i) => (i === 0 ? { ...m, components: [...m.components, { kind: "card_share" as const, card: "poultice", share_bp: 1000 }, { kind: "card_share" as const, card: "hunt", share_bp: 1000 }] } : m)) };
expect("a saved mix already holds both", sideCue(catalog, both), null);

const lesson = LESSONS.find((l) => l.id === SIDE_MIX)!;
expect("control: it may start", mayStart(lesson, view, keepsOf(TAUGHT)), true);
expect("no mix at all: the first mix's lesson comes first", mayStart(lesson, { ...view, mixes: [] }, keepsOf(TAUGHT)), false);
expect("lessons off", mayStart(lesson, view, keepsOf(TAUGHT, null, { lessons: false })), false);

function rig(keeps: Keeps, shown: View = view) {
  const decided: Decision[] = [];
  const screen = new Screen(catalog, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...step, view: shown });
  const lay = (n: Element = document.body): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const trigger = (): HTMLElement | null => document.querySelector<HTMLElement>('[data-teach="side-mix"]');
  const note = (): string => { const n = document.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = document.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, trigger, note, tap, keeps };
}

{  // two steps: the holder's face, then the Mixes control; nothing is opened or sent for the player
  const r = rig(keepsOf(TAUGHT));
  r.frame();
  expect("the holder's face is the trigger, naming the fight", [r.trigger()?.dataset.card, r.trigger()?.dataset.fight], ["poultice", "hunt"]);
  r.frame();
  expect("the lesson starts on it", r.note(), text("ui.lesson.side_hold", slots));
  r.tap(".lesson-next"); r.frame();
  expect("then the Mixes control, saying both run together", r.note(), text("ui.lesson.side_open", { card: slots.card }));
  r.tap('[data-teach="mixes"]');
  expect("a touch on it is the end: done, and kept", r.keeps.lessonKept(SIDE_MIX) && r.keeps.lessonDone(SIDE_MIX), true);
  expect("nothing was sent", r.decided.length, 0);
  r.screen.show({ ...step, view });
  r.frame();
  expect("the trigger is gone with it", r.trigger() !== null, false);
}

{  // kept: never again
  const r = rig(keepsOf({ ...TAUGHT, lessons: [...TAUGHT.lessons, SIDE_MIX] }));
  r.frame(); r.frame();
  expect("kept: no trigger, no lesson", [r.trigger() !== null, r.note()], [false, ""]);
}

{  // skipped: kept as skipped, and the trigger goes
  const r = rig(keepsOf(TAUGHT));
  r.frame(); r.frame();
  r.tap(".lesson-note .lesson-skip");
  expect("skipped and kept", r.keeps.lessonKept(SIDE_MIX) && !r.keeps.lessonDone(SIDE_MIX), true);
  r.frame();
  expect("no trigger after the skip", r.trigger() !== null, false);
}

{  // no threat served yet: nothing starts
  const r = rig(keepsOf(TAUGHT), { ...view, fights: [] });
  r.frame(); r.frame();
  expect("no trigger, no lesson", [r.trigger() !== null, r.note()], [false, ""]);
}
