// Lessons (game/lessons.ts as data, ui/lessons.ts the runner), from the interface: a lesson starts when its trigger is
// on show and it may; each step's control takes the one glow with its line beside it; a tap on that control, or a read
// step's reading time, moves on; a step whose control is not on show waits; never more than one step ahead; Skip ends
// it at any step; done or skipped, it is kept in the save and never comes back, and its offer is one tap again.
import { fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { CLOCK, FIRST_MIX, FIRST_RULE, guided } from "../src/game/lessons";
import { Glow } from "../src/ui/fresh";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT, type Flat } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const noMix: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
const [a, b] = ["stand", "look"];

/** A control on show: in the page, with a size (the fake DOM's `rect`). */
function control(cls: string, data: Record<string, string>, parent: HTMLElement = document.body): HTMLButtonElement {
  const n = document.createElement("button");
  n.className = cls;
  Object.assign(n.dataset, data);
  Object.assign(n, { rect: { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 } });
  parent.append(n);
  return n;
}
function rig(account: Flat = NEW_FLAT) {
  fakeDocument.body.replaceChildren();
  const sent: Flat[] = [];
  const keeps = keepsOf(account, sent);
  const glow = new Glow();
  let changed = 0;
  const lessons = new Lessons({ catalog, glow, keeps }, document.body, () => { changed += 1; }, document, () => clock);
  const note = lessons.root;
  const line = (): string => (note.hidden ? "" : note.querySelector(".lesson-line")?.textContent ?? "");
  return { lessons, keeps, sent, note, line, changed: () => changed };
}
let clock = 0;
const at = (t: number): void => { clock = t; };
const text = (key: string, slots: Record<string, string> = {}): string => catalog.text.fill(key, slots);

{  // the mix's lesson: trigger, steps in turn, waiting, never two ahead, and done once its last step is read
  const r = rig();
  r.lessons.update(noMix);
  at(0); r.lessons.tick();
  expect("nothing on show: no lesson", r.line(), "");
  expect("guided before it runs", guided(FIRST_MIX, noMix, r.keeps), true);
  const offer = control("offer-both", { teach: "mix-offer", cards: `${a} ${b}` });
  at(1); r.lessons.tick();
  expect("its trigger on show: the first step's line", r.line(), text("ui.lesson.mix_offer"));
  expect("the step's control takes the glow", offer.classList.contains("glow"), true);
  const editor = document.createElement("section");
  editor.className = "editor";
  document.body.append(editor);
  const second = control("add-card", { card: b }, editor);
  at(2); r.lessons.tick();
  expect("a later step's control on show does not skip ahead", r.line(), text("ui.lesson.mix_offer"));
  offer.click();
  const first = control("add-card", { card: a }, editor);
  at(3); r.lessons.tick();
  expect("a tap on its control moves on", r.line(), text("ui.lesson.mix_add", { card: catalog.cardLabel(a) }));
  expect("the glow moved with it", [offer.classList.contains("glow"), first.classList.contains("glow")], [false, true]);
  first.click();
  first.remove();
  at(4); r.lessons.tick();
  expect("then the second card", r.line(), text("ui.lesson.mix_add_more", { card: catalog.cardLabel(b) }));
  second.click();
  at(5); r.lessons.tick();
  expect("the bar not on show: the step waits on the last one on show", r.line(), text("ui.lesson.mix_add_more", { card: catalog.cardLabel(b) }));
  const bar = control("share-bar", {}, editor);
  at(6); r.lessons.tick();
  expect("the bar's line", r.line(), text("ui.lesson.mix_bar"));
  at(6 + 90_000); r.lessons.tick();
  expect("a read step waits for a tap, however long the player looks away", r.line(), text("ui.lesson.mix_bar"));
  r.lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();
  const head = document.createElement("div");
  head.className = "editor-head";
  editor.append(head);
  const save = control("primary", {}, head);
  at(6 + 60_000); r.lessons.tick();
  expect("read: on to Save", r.line(), text("ui.lesson.mix_save"));
  save.click();
  editor.remove();
  bar.remove();
  const strip = document.createElement("section");
  strip.className = "hands";
  document.body.append(strip);
  control("hands-mix", {}, strip);
  at(100_000); r.lessons.tick();
  expect("the strip's bar, last", r.line(), text("ui.lesson.mix_runs"));
  expect("not kept before its last step is read", r.keeps.lessonKept(FIRST_MIX), false);
  r.lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();
  control("hands-name", { teach: "mixes" }, strip);
  at(200_000); r.lessons.tick();
  expect("the strip's Mixes, after the bar's line: where several mixes live", r.line(), text("ui.lesson.mix_list"));
  expect("not kept before its last step is read", r.keeps.lessonKept(FIRST_MIX), false);
  at(300_000); r.lessons.tick();
  expect("the last read step waits for its tap too", r.keeps.lessonKept(FIRST_MIX), false);
  r.lessons.root.querySelector<HTMLElement>(".lesson-next")?.click();
  expect("done: kept in the save", r.sent.at(-1)?.lessons, [FIRST_MIX]);
  expect("done: how it ended, the last step and the longest wait on one", r.sent.at(-1)?.lesson_ends, [{ lesson: FIRST_MIX, skipped: false, step: 6, longest_wait_s: 100 }]);
  expect("done: the note goes", r.line(), "");
  expect("started and done: the screen is told each time, so the offers are redrawn", r.changed(), 2);
  expect("done: no longer guided", guided(FIRST_MIX, noMix, r.keeps), false);
  at(400_000); r.lessons.tick();
  expect("never again", r.line(), "");
}

{  // Skip at any step: kept, the offer is one tap again, and it never comes back
  const r = rig();
  r.lessons.update(noMix);
  control("offer-both", { teach: "mix-offer", cards: `${a} ${b}` });
  at(0); r.lessons.tick();
  expect("started", r.line(), text("ui.lesson.mix_offer"));
  at(7000);
  (r.note.querySelector(".lesson-skip") as HTMLButtonElement).click();
  expect("skipped: kept", r.sent.at(-1)?.lessons, [FIRST_MIX]);
  expect("skipped: on step 0, after 7 seconds there", r.sent.at(-1)?.lesson_ends, [{ lesson: FIRST_MIX, skipped: true, step: 0, longest_wait_s: 7 }]);
  expect("skipped: no longer guided (Both again)", guided(FIRST_MIX, noMix, r.keeps), false);
  at(1); r.lessons.tick();
  expect("skipped: never again", r.line(), "");
}

{  // the rule's lesson comes after the mix's: not before it is kept (or a mix exists), and then from its trigger
  const r = rig();
  const view: View = { ...noMix, orders: [] };
  r.lessons.update(view);
  control("primary", { teach: "rule-offer", task: a, watch: "wood", kind: "store" });
  at(0); r.lessons.tick();
  expect("no rule lesson before the mix's", r.line(), "");
  expect("its offer is one tap meanwhile", guided(FIRST_RULE, view, r.keeps), false);
  const later = rig({ ...NEW_FLAT, lessons: [FIRST_MIX] });
  later.lessons.update(view);
  control("primary", { teach: "rule-offer", task: a, watch: "wood", kind: "store" });
  at(0); later.lessons.tick();
  const hands = catalog.mixable(a) ? "ui.lesson.rule_hands" : "ui.lesson.rule_lane";
  expect("after the mix's: the rule's first line, worded by the task's lane", later.line(), text(hands));
  expect("a rule already saved: it may not start", guided(FIRST_RULE, { ...view, orders: fixtureStep("covered", 300).view.orders }, later.keeps), false);
}
{  // the rule's lesson after the mix's: thinner only when the mix's ended done; the record counts in the full list
  const ended = (skipped: boolean): Flat => ({ ...NEW_FLAT, lessons: [FIRST_MIX], lesson_ends: [{ lesson: FIRST_MIX, skipped, step: 5, longest_wait_s: 1 }] });
  const view: View = { ...noMix, orders: [] };
  /** Walks the rule lesson to just after `When`, with the Add rule button and the Rules row both on show. */
  const walk = (account: Flat) => {
    const r = rig(account);
    r.lessons.update(view);
    const offer = control("primary", { teach: "rule-offer", task: a, watch: "wood", kind: "store" });
    at(0); r.lessons.tick();
    offer.click();
    const cond = document.createElement("section");
    cond.className = "cond";
    document.body.append(cond);
    const doTask = control("cond-task", { card: a }, cond);
    at(1); r.lessons.tick();
    doTask.click();
    const when = control("pick", { store: "wood" }, cond);
    at(2); r.lessons.tick();
    when.click();
    const actions = document.createElement("div");
    actions.className = "cond-actions";
    cond.append(actions);
    const addRule = control("primary", {}, actions);
    const rules = document.createElement("section");
    rules.className = "rules";
    document.body.append(rules);
    control("rule-cond", {}, rules);
    at(3); r.lessons.tick();
    return { ...r, addRule, cond, offer };
  };
  const addLine = text("ui.lesson.rule_add");
  const keptLine = text("ui.lesson.rule_kept");
  const onLine = text("ui.lesson.rule_on", { task: catalog.cardLabel(a) });

  const thin = walk(ended(false));
  expect("mix lesson done: Add rule is still guided", thin.line(), addLine);
  thin.addRule.click();
  thin.cond.remove();
  thin.offer.remove();
  at(100_000); thin.lessons.tick();
  expect("mix lesson done: the Rules row is not read", [thin.line() === keptLine, thin.line()], [false, ""]);
  control("x", { teach: "rule-on" });
  at(100_001); thin.lessons.tick();
  expect("mix lesson done: the hand-back is reachable", thin.line(), onLine);
  (thin.note.querySelector(".lesson-next") as HTMLButtonElement).click();
  at(300_000); thin.lessons.tick();
  expect("mix lesson done: ends done on the full list's last index", thin.sent.at(-1)?.lesson_ends?.at(-1)?.step, 5);
  expect("mix lesson done: kept", thin.keeps.lessonKept(FIRST_RULE), true);

  const thinSkip = walk(ended(false));
  control("x", { teach: "rule-on" });
  thinSkip.addRule.click();
  thinSkip.cond.remove();
  thinSkip.offer.remove();
  at(4); thinSkip.lessons.tick();
  (thinSkip.note.querySelector(".lesson-skip") as HTMLButtonElement).click();
  expect("mix lesson done: a skip on the hand-back records the full list's index", thinSkip.sent.at(-1)?.lesson_ends?.at(-1)?.step, 5);

  const full = walk(ended(true));
  expect("mix lesson skipped: the full lesson, Add rule guided", full.line(), addLine);
  full.addRule.click();
  full.cond.remove();
  full.offer.remove();
  at(100_000); full.lessons.tick();
  expect("mix lesson skipped: the Rules row is read", full.line(), keptLine);
  const none = walk({ ...NEW_FLAT, lessons: [FIRST_MIX] });
  expect("no record of how it ended: the full lesson", none.line(), addLine);
}
{  // a read step ends on a tap of the note, never a timer: an hour of looking away leaves it up; Got it is shown on read steps only
  const r = rig({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] });
  r.lessons.update(fixtureStep("firstmix", 200).view);
  const clockTrigger = control("clock", { teach: "clock" });
  at(0); r.lessons.tick();
  expect("the clock's one read step is up", r.line(), text("ui.lesson.clock"));
  const gotIt = r.note.querySelector(".lesson-next") as HTMLButtonElement;
  expect("a read step shows Got it", [gotIt.hidden, gotIt.textContent], [false, text("ui.lesson.next")]);
  at(60 * 60_000); r.lessons.tick();
  expect("an hour on: still up, not kept", [r.line(), r.keeps.lessonKept(CLOCK)], [text("ui.lesson.clock"), false]);
  (r.note.querySelector(".lesson-skip") as HTMLButtonElement).click();
  expect("Skip is not the note's tap: it keeps the lesson skipped", r.sent.at(-1)?.lesson_ends?.at(-1)?.skipped, true);
  const again = rig({ ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] });
  again.lessons.update(fixtureStep("firstmix", 200).view);
  control("clock", { teach: "clock" });
  at(0); again.lessons.tick();
  (again.note.querySelector(".lesson-line") as HTMLElement).click();
  expect("a tap on the note's line ends the step: done", [again.keeps.lessonKept(CLOCK), again.keeps.lessonDone(CLOCK)], [true, true]);
  clockTrigger.remove();
}
{  // the note is the tutorial's, not a game control's: a tag names who is talking, and Skip is its own quiet link that says what it ends
  const r = rig();
  const kids = Array.from(r.note.children);
  expect("the note's tag, Skip, the line, then Got it", kids.map((k) => k.className), ["lesson-tag", "lesson-skip", "lesson-line", "lesson-next"]);
  expect("the tag says tutorial", r.note.querySelector(".lesson-tag")?.textContent, text("ui.lesson.tag"));
  const skip = r.note.querySelector(".lesson-skip") as HTMLElement;
  expect("Skip says it ends the tutorial", skip.textContent, text("ui.lesson.skip"));
  expect("Skip is no game button: not primary, not quiet, not an offer's", ["primary", "quiet", "offer-both"].some((c) => skip.className.includes(c)), false);
}
console.log("lessons: ok");
