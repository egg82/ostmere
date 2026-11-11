// The second mix's lesson (game/lessons.ts, SECOND_MIX; docs/design/opening-screen.md, "Lessons"), on the whole screen: a
// card the player keeps tapping by hand that their running mix could take is the trigger, once the first rule's lesson is
// behind. It walks the Mixes list's own New mix with nothing in it: the tasks and the shares are the player's, Save only
// saves, and the last step shows where switching is. It starts on an account that touched that card's dot in an old save.
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { Decision, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CLOCK, FIRST_MIX, FIRST_RULE, SECOND_MIX } from "../src/game/lessons";
import { Screen } from "../src/ui/screen";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });
Object.assign(window, { innerWidth: 400, innerHeight: 800 });
let clock = 0;
Object.defineProperty(performance, "now", { value: () => clock, configurable: true });   // the lesson's reading clock

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const AT = 100;
const step = fixtureStep("repeattap", AT);   // the running mix, and `look` tapped by hand again and again
const TAUGHT: Flat = { ...NEW_FLAT, rule_seen: true, lessons: [FIRST_MIX, FIRST_RULE] };
/** The live account this was written for, by shape: an old save's lessons (one skipped), rules seen, and the repeated
 * card's dot touched back then. */
const RETURNING: Flat = { ...NEW_FLAT, rule_seen: true, rules_opened: true, mix_offered: ["look"], lessons: [FIRST_MIX, FIRST_RULE, CLOCK],
  lesson_ends: [{ lesson: FIRST_MIX, skipped: false, step: 5, longest_wait_s: 9 }, { lesson: FIRST_RULE, skipped: true, step: 5, longest_wait_s: 14 }, { lesson: CLOCK, skipped: false, step: 0, longest_wait_s: 5 }] };

function rig(view: View, account: Flat) {
  const decided: Decision[] = [];
  const keeps = keepsOf(account);
  const screen = new Screen(catalog, (d) => { decided.push(d); }, () => Promise.resolve(null), keeps);
  document.body.replaceChildren(screen.root);
  screen.show({ ...step, view });
  const lay = (n: Element = document.body): void => {
    Object.assign(n, { rect: { left: 20, top: 300, width: 60, height: 16, right: 80, bottom: 316 } });
    for (const k of Array.from(n.children)) lay(k);
  };
  const frame = (ms = 1): void => { lay(); clock += ms; screen.tick(AT); };
  const trigger = (): HTMLElement | null => document.querySelector<HTMLElement>('[data-teach="mix-hint"]');
  const note = (): string => { const n = document.querySelector<HTMLElement>(".lesson-note"); return n && !n.hidden ? n.querySelector(".lesson-line")?.textContent ?? "" : ""; };
  const tap = (selector: string): void => {
    const n = document.querySelector<HTMLElement>(selector);
    if (!n) throw new Error(`nothing to tap at ${selector}`);
    n.click();
    frame();
  };
  return { screen, decided, frame, trigger, note, tap, keeps };
}
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);
const look = catalog.cardLabel("look");

for (const [who, account] of [["a new account", TAUGHT], ["a returning account", RETURNING]] as const) {  // the walk, on the real controls
  const r = rig(step.view, account);
  r.frame();
  expect(`${who}: the repeated card is the trigger`, r.trigger()?.dataset.card, "look");
  r.frame();
  expect(`${who}: the lesson starts on it`, r.note(), text("ui.lesson.second_hint", { card: look }));
  r.tap(".lesson-next"); r.frame();
  expect(`${who}: then the Mixes list`, r.note(), text("ui.lesson.second_open"));
  r.tap('[data-teach="mixes"]');
  expect(`${who}: then New mix`, r.note(), text("ui.lesson.second_new"));
  r.tap(".selector .selector-new");
  expect(`${who}: then the Add row`, r.note(), text("ui.lesson.second_add"));
  expect(`${who}: the new mix is empty: Save is off`, document.querySelector<HTMLButtonElement>(".editor .editor-head .primary")?.disabled, true);
  fakeDocument.querySelector('.editor .add-card[data-card="look"]')?.dispatchEvent(new FakeEvent("click", { detail: 0 }));   // a key's tap: it joins
  r.frame();
  expect(`${who}: then the bar`, r.note(), text("ui.lesson.second_bar"));
  r.tap(".lesson-next"); r.frame();
  expect(`${who}: then the name`, r.note(), text("ui.lesson.second_name"));
  r.tap(".lesson-next"); r.frame();
  expect(`${who}: then Save`, r.note(), text("ui.lesson.second_save"));
  expect(`${who}: nothing was sent before Save`, r.decided.length, 0);
  r.tap(".editor .editor-head .primary");
  const saved = r.decided.filter((d) => d.kind === "save_mix");
  expect(`${who}: Save saves the player's mix`, saved.length === 1 && saved[0]?.kind === "save_mix" ? saved[0].mix.components.map((c) => (c.kind === "card_share" ? c.card : "")) : null, ["look"]);
  expect(`${who}: and switches nothing`, r.decided.some((d) => d.kind === "switch_mix"), false);
  r.frame();
  expect(`${who}: then where switching is`, r.note(), text("ui.lesson.second_run"));
  r.tap(".lesson-next"); r.frame();
  expect(`${who}: done, and kept`, r.keeps.lessonKept(SECOND_MIX) && r.keeps.lessonDone(SECOND_MIX), true);
  r.screen.show({ ...step, view: step.view });
  r.frame();
  expect(`${who}: the next view takes the trigger off the card`, r.trigger() !== null, false);
}

{  // before the first rule's lesson is behind: the dot only (game/hints.ts), no lesson
  const r = rig(step.view, { ...TAUGHT, lessons: [FIRST_MIX] });
  r.frame(); r.frame();
  expect("no trigger", r.trigger() !== null, false);
  expect("no second-mix lesson", r.note() === text("ui.lesson.second_hint", { card: look }), false);
}

{  // kept: the card keeps its quiet dot, and nothing more
  const r = rig(step.view, { ...TAUGHT, lessons: [...TAUGHT.lessons, SECOND_MIX] });
  r.frame(); r.frame();
  expect("kept: no trigger", r.trigger() !== null, false);
  expect("kept: no lesson", r.note(), "");
  expect("kept: the dot is still there", document.querySelector('.deck .card > .new-dot') !== null, true);
}
