// Lessons are kept per save (docs/design/opening-screen.md, "Lessons"): a new save teaches everything again from each
// lesson's own moment, whatever another save of the account kept; a save made before lessons were per save starts with
// none kept, and each lesson's own condition keeps a save that is past it from being taught it again. The account's
// lessons setting turns them all off; on again, a save's lessons go on from what it keeps.
import { fakeDocument, install } from "./fake-dom";
import { fixtureContent } from "../fixtures/content";
import { journalView, NOTE_B, NOTES_A } from "../fixtures/journal";
import { prestigeStep } from "../fixtures/prestige";
import { fixtureStep } from "../fixtures/steps";
import { townStep } from "../fixtures/town";
import type { GameApi } from "../src/api/api";
import type { NewSave, Opened, SavePresentation, View } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { NEW_ACCOUNT, NEW_SAVE, NEW_SETTINGS, type Keeps } from "../src/game/keeps";
import { CAP_RULE, CLOCK, FIRST_MIX, FIRST_RULE, guided, JOURNAL, LESSONS, mayStart, PRESTIGE, TOWN_MIX } from "../src/game/lessons";
import { Session } from "../src/game/session";
import { Glow } from "../src/ui/fresh";
import { Lessons } from "../src/ui/lessons";
import { keepsOf, NEW_FLAT } from "./kept";

install();
Object.assign(window, { innerWidth: 400, innerHeight: 800 });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const noMix: View = { ...fixtureStep("firstmix", 200).view, mixes: [], orders: [], active_mix_id: null };
const EVERY = LESSONS.map((l) => l.id);
const ALL_KEPT: SavePresentation = { ...NEW_SAVE, rule_seen: true, lessons: EVERY, lesson_ends: EVERY.map((lesson) => ({ lesson, skipped: false, step: 0, longest_wait_s: 1 })) };

/** The mix offer on show, as the hands strip draws it under the mix's lesson. */
function mixOffer(): void {
  fakeDocument.body.replaceChildren();
  const n = document.createElement("button");
  Object.assign(n.dataset, { teach: "mix-offer", cards: "stand look" });
  Object.assign(n, { rect: { left: 10, top: 10, width: 80, height: 30, right: 90, bottom: 40 } });
  document.body.append(n);
}

/** The runner over `keeps` on the no-mix view with the mix offer on show: the line of the step it shows ("" for none). */
function runner(keeps: Keeps) {
  mixOffer();
  let clock = 0;
  const lessons = new Lessons({ catalog, glow: new Glow(), keeps }, document.body, () => undefined, document, () => clock);
  lessons.update(noMix);
  const line = (): string => (lessons.root.hidden ? "" : lessons.root.querySelector(".lesson-line")?.textContent ?? "");
  const tick = (): string => { clock += 1; lessons.tick(); return line(); };
  return { lessons, tick };
}
const mixLine = catalog.text.get("ui.lesson.mix_offer");

{  // a new save on an account whose old save kept every lesson walks the mix's lesson again, guided
  const save = { save_id: 3, number: 1, decisions: 0, game_time: 0, ended_at: null, started_at: "2026-11-07T09:00:00Z", played_at: "2026-11-07T09:00:00Z", camp_level: 0 };
  const step = { ...fixtureStep("firstmix", 0), save_id: 3, rules_digest: fixtureContent.rules_digest, lines: [] };
  const none = (): Promise<never> => Promise.reject(new Error("not in this test"));
  let older = false;   // an older pod's open answers no presentation
  const api: GameApi = {
    content: () => Promise.resolve(fixtureContent), me: none, savedView: none, advance: none, forecast: none, decide: none, dryRun: none,
    open: () => Promise.resolve<Opened>(older ? JSON.parse(JSON.stringify({ save, was: step.view, history: [], step })) : { save, was: step.view, history: [], presentation: ALL_KEPT, step }),
    begin: () => Promise.resolve<NewSave>({ save: { ...save, save_id: 4, number: 2 }, presentation: NEW_SAVE, step: { ...step, save_id: 4 } }),
    putMePresentation: none, putMeSettings: none, putSavePresentation: (_id, p) => Promise.resolve(p), sendFeedback: none, makeCode: none,
    makeWords: none, join: none, games: none, deleteGame: none, restoreGame: none, devices: none, removeDevice: none,
  };
  let keeps: Keeps | null = null;
  const session = new Session(api, {
    started(_c, _s, k) { keeps = k; }, stepped() { /* drawn */ }, build() { /* self-update */ }, refused() { /* none */ },
    connected() { /* none */ }, lost() { /* none */ }, limited() { /* none */ }, catchingUp() { /* none */ },
  }, { account: NEW_ACCOUNT, settings: NEW_SETTINGS });
  await session.resume(3);
  const old = keeps as Keeps | null;
  if (!old) throw new Error("the old save never started");
  expect("control: the old save has every lesson kept", [old.lessonKept(FIRST_MIX), guided(FIRST_MIX, noMix, old)], [true, false]);
  expect("control: the old save's runner starts nothing", runner(old).tick(), "");
  older = true;
  await session.resume(3);
  const asked = keeps as Keeps | null;
  if (!asked || asked === old) throw new Error("the save never reopened");
  expect("an older pod's open keeps none, not the save before's", asked.lessonKept(FIRST_MIX), false);
  older = false;
  await session.begin();
  const fresh = keeps as Keeps | null;
  if (!fresh || fresh === old) throw new Error("the new save never started");
  expect("the new save keeps no lesson", [fresh.lessonKept(FIRST_MIX), fresh.ruleSeen()], [false, false]);
  expect("its mix offer is the guided one", guided(FIRST_MIX, noMix, fresh), true);
  expect("and the mix's lesson walks it", runner(fresh).tick(), mixLine);
}

{  // lessons off: none starts and no offer is guided; on again, the save's own kept state decides
  const off = keepsOf(NEW_FLAT, null, { lessons: false });
  const r = runner(off);
  expect("off: no lesson starts on its trigger", r.tick(), "");
  expect("off: the offer is its one tap", [guided(FIRST_MIX, noMix, off), guided(CAP_RULE, fixtureStep("capfull", 100).view, keepsOf({ rule_seen: true }, null, { lessons: false }))], [false, false]);
  off.keepLessonsOn(true);
  expect("on again: the lesson starts at its moment", r.tick(), mixLine);
  const kept = keepsOf({ lessons: [FIRST_MIX] }, null, { lessons: false });
  kept.keepLessonsOn(true);
  expect("on again: a lesson this save kept stays kept", runner(kept).tick(), "");
}

{  // turned off mid-lesson: the note goes and nothing is kept, so it starts over once lessons are on
  const keeps = keepsOf(NEW_FLAT);
  const r = runner(keeps);
  expect("control: the lesson runs", r.tick(), mixLine);
  keeps.keepLessonsOn(false);
  expect("turned off: the note goes", [r.tick(), r.lessons.current], ["", null]);
  expect("turned off: nothing kept", keeps.lessonKept(FIRST_MIX), false);
  keeps.keepLessonsOn(true);
  expect("on again: it starts over", r.tick(), mixLine);
}

{  // a save already past each lesson, with nothing kept (made before lessons were per save), is not taught it again
  const none = keepsOf(NEW_FLAT);
  const played = fixtureStep("mid", 100).view;
  const handsRule = { when: { kind: "at_most" as const, watched: { kind: "store_value" as const, store: "wood" }, value: 999, release: 3999 }, then: { kind: "switch_mix" as const, mix_id: played.active_mix_id ?? "" } };
  const mid: View = { ...played, orders: [...played.orders, handsRule], orders_on: [...played.orders_on, false], order_states: [...played.order_states, "waiting"] };
  expect("control: the mid save has a mix", played.mixes.length > 0, true);
  expect("control: with no hands rule it may have the first rule's lesson", mayStart(LESSONS.find((l) => l.id === FIRST_RULE)!, played, none), true);
  const lesson = (id: string) => LESSONS.find((l) => l.id === id)!;
  expect("a mid-game save: no first-mix lesson", mayStart(lesson(FIRST_MIX), mid, none), false);
  expect("control: a save with no mix may have it", mayStart(lesson(FIRST_MIX), noMix, none), true);
  expect("a mid-game save with a hands rule: no first-rule lesson", mayStart(lesson(FIRST_RULE), mid, none), false);
  const seen = keepsOf({ rule_seen: true });
  const cap = fixtureStep("capfull", 100).view;
  const reaches = { when: { kind: "at_least" as const, watched: { kind: "store_value" as const, store: "food" }, value: 2000, release: 1000 }, then: { kind: "tap_card" as const, card: "look" } };
  expect("control: the full-store save may have the cap rule's lesson", mayStart(lesson(CAP_RULE), cap, seen), true);
  expect("a save with a cap rule on any store: no cap rule's lesson", mayStart(lesson(CAP_RULE), { ...cap, orders: [...cap.orders, reaches], orders_on: [...cap.orders_on, false], order_states: [...cap.order_states, "waiting"] }, seen), false);
  const pushed = prestigeStep("prestige", 100).view;
  const firstPhase = { ...pushed, skills: pushed.skills.map((s) => (s.prestige ? { ...s, prestige: { ...s.prestige, phase: 1 } } : s)) };
  expect("control: the fixture has a skill pushed past", pushed.skills.some((s) => (s.prestige?.phase ?? 1) > 1), true);
  expect("a save that pushed a skill past: no prestige lesson", mayStart(lesson(PRESTIGE), pushed, none), false);
  expect("control: every skill in its first phase may have it", mayStart(lesson(PRESTIGE), firstPhase, none), true);
  // the story's lessons: a save past the moment each comes at has the lesson's own mark of it
  const onePage = journalView(played, NOTES_A);
  expect("control: the book with one page written may have the journal's lesson", mayStart(lesson(JOURNAL), onePage, none), true);
  expect("a save with a second page written: no journal lesson", mayStart(lesson(JOURNAL), journalView(played, [...NOTES_A, NOTE_B]), none), false);
  const night = (id: string) => [{ category: "action" as const, id }, { category: "feature" as const, id }];
  const first = { ...played, unlocked: [...played.unlocked, ...night("night")] };
  expect("control: a save in its first night may have the clock's lesson", mayStart(lesson(CLOCK), first, none), true);
  expect("a save past its first night: no clock lesson", mayStart(lesson(CLOCK), { ...first, unlocked: [...first.unlocked, ...night("night_2")] }, none), false);
  const split = townStep("town").view;
  const whole = { ...split, mixes: split.mixes.map((m) => (m.id === split.running_town_mix_id ? { ...m, components: m.components.map((c) => (c.kind === "card_share" ? { ...c, share_bp: 10000 } : c)) } : m)) };
  expect("control: a town mix as the game made it may have the town's lesson", mayStart(lesson(TOWN_MIX), whole, none), true);
  expect("a save whose town mix was split: no town lesson", mayStart(lesson(TOWN_MIX), split, none), false);
}
