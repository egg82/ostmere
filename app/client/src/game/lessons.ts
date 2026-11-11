// Lessons (docs/design/opening-screen.md, "Lessons"): a system taught on its real controls the first time it matters,
// one step at a time. A lesson is data: an id, when it may start, the control whose showing starts it (its trigger,
// which carries the lesson's subject in its data attributes), and its steps, each naming the control to highlight
// (a CSS selector, filled from the subject), its line, and whether a touch or a read ends it. The runner
// (ui/lessons.ts), the highlight and the record (Keeps.lessonKept: done or skipped, never again) are written once,
// so a later lesson is one entry below.
import type { OrderCard, View } from "../api/types";
import type { Catalog } from "./catalog";
import type { Keeps } from "./keeps";
import { anyReachesRule } from "./caphint";
import { anySelfFedMix } from "./dryhint";
import { rulesTabDrawn } from "./orders";
import { UI } from "./text";

const WHOLE_BP = 10000;

/** What a lesson is about, read off its trigger's data attributes (`data-cards`, `data-task`, `data-watch`). */
export type Subject = Readonly<Record<string, string>>;

export interface LessonStep {
  /** The control to highlight: a selector, filled from the subject. The first match on show is the one. */
  target: (s: Subject) => string;
  /** The line beside it, filled from the subject. */
  line: (c: Catalog, s: Subject) => string;
  /** "touch": a tap on the target ends it; "read": a tap on the note ends it (a tap on a later step's control too). */
  ends: "touch" | "read";
  /** The step is left out when the lesson with this id ended done (not skipped): it repeats what that one taught. */
  unlessDone?: string;
  /** The step is left out for a subject it does not apply to (a swap the fix has none of). */
  leftOut?: (s: Subject) => boolean;
  /** What the note must not cover besides the target: a selector, such as the numbers a step's line refers to. */
  clear?: string;
}

export interface Lesson {
  id: string;
  /** Whether it may start now (and whether its trigger shows the guided button rather than the one-tap one). */
  may: (view: View, keeps: Keeps) => boolean;
  /** The control whose showing starts it; its data attributes are the subject. */
  trigger: string;
  steps: LessonStep[];
  /** Under way but untouched (nothing of it tapped yet), it gives way to a lesson earlier in the list whose trigger is on
   * show, and holds back no guided rule offer until a touch begins it (`Lessons.holding`): the book's first showing can come
   * just before the offer it is shown with. */
  yields?: true;
}

const cards = (s: Subject): string[] => (s["cards"] ?? "").split(" ").filter((c) => c.length > 0);
const watchLabel = (c: Catalog, s: Subject): string => (s["kind"] === "chip" ? c.label(c.chips.get(s["watch"] ?? "")?.label_key) : c.storeLabel(s["watch"] ?? ""));
/** A value inside a CSS attribute selector's quotes. */
const quoted = (v: string): string => v.replace(/[\\"]/g, "\\$&");
const task = (c: Catalog, s: Subject): string => c.cardLabel(s["task"] ?? "");

export const FIRST_MIX = "first_mix";
export const FIRST_RULE = "first_rule";
export const SECOND_MIX = "second_mix";
export const CAP_RULE = "cap_rule";
export const DRY_STORE = "dry_store";
export const MIX_STOPPED = "mix_stopped";
export const SWITCH_MIX = "switch_mix";
export const CLOCK = "clock";
export const TOWN_MIX = "town_mix";
export const JOURNAL = "journal";
export const JOURNAL_NUMBERS = "journal_numbers";
export const PRESTIGE = "prestige";

export const LESSONS: readonly Lesson[] = [
  {
    id: FIRST_MIX,
    may: (view) => view.mixes.length === 0,
    trigger: `[data-teach="mix-offer"]`,
    steps: [
      { target: () => `[data-teach="mix-offer"]`, line: (c) => c.text.get(UI.lessonMixOffer), ends: "touch" },
      { target: (s) => `.editor .add-card[data-card="${cards(s)[0]}"]`, line: (c, s) => c.text.fill(UI.lessonMixAdd, { card: c.cardLabel(cards(s)[0] ?? "") }), ends: "touch" },
      { target: (s) => `.editor .add-card[data-card="${cards(s)[1]}"]`, line: (c, s) => c.text.fill(UI.lessonMixAddMore, { card: c.cardLabel(cards(s)[1] ?? "") }), ends: "touch" },
      { target: () => `.editor .share-bar`, line: (c) => c.text.get(UI.lessonMixBar), ends: "read" },
      { target: () => `.editor .editor-head .primary`, line: (c) => c.text.get(UI.lessonMixSave), ends: "touch" },
      { target: () => `.hands .hands-mix`, line: (c) => c.text.get(UI.lessonMixRuns), ends: "read" },
      { target: () => `[data-teach="mixes"]`, line: (c) => c.text.get(UI.lessonMixList), ends: "read" },
    ],
  },
  {
    id: FIRST_RULE,
    // after the mix's lesson (or a mix made some other way): a rule is taught in terms of the mix. The player's first rule
    // is a hands rule, which always runs a mix; the orders a story install sets tap a card on a ruled lane
    may: (view, keeps) => !view.orders.some((o) => o.then.kind === "switch_mix") && (keeps.lessonKept(FIRST_MIX) || view.mixes.length > 0),
    trigger: `[data-teach="rule-offer"]`,
    steps: [
      { target: () => `[data-teach="rule-offer"]`, line: (c, s) => c.text.get(c.mixable(s["task"] ?? "") ? UI.lessonRuleHands : UI.lessonRuleLane), ends: "touch" },
      { target: (s) => `.cond .cond-task[data-card="${s["task"]}"]`, line: (c, s) => c.text.fill(UI.lessonRuleDo, { task: task(c, s) }), ends: "touch" },
      { target: (s) => `.cond [data-${s["kind"]}="${s["watch"]}"]`, line: (c, s) => c.text.fill(UI.lessonRuleWhen, { when: watchLabel(c, s) }), ends: "touch" },
      { target: () => `.cond-actions .primary`, line: (c) => c.text.get(UI.lessonRuleAdd), ends: "touch" },
      { target: () => `.rules .rule-cond`, line: (c) => c.text.get(UI.lessonRuleKept), ends: "read", unlessDone: FIRST_MIX },
      { target: () => `[data-teach="rule-running"], [data-teach="rule-on"]`, line: (c, s) => c.text.fill(UI.lessonRuleOn, { task: task(c, s) }), ends: "read" },
    ],
  },
  {
    id: SECOND_MIX,
    // a card the player keeps tapping by hand that their running mix could take (game/hints.ts, secondMixCard; ui/cards.ts
    // marks it), once the first rule's lesson is behind: walked on the Mixes list's own New mix with nothing in it, so the
    // tasks and their shares are the player's pick; saving runs nothing, so it ends on how to switch
    may: (view, keeps) => view.mixes.length > 0 && keeps.lessonKept(FIRST_RULE),
    trigger: `[data-teach="mix-hint"]`,
    steps: [
      { target: (s) => `[data-teach="mix-hint"][data-card="${s["card"]}"]`, line: (c, s) => c.text.fill(UI.lessonSecondHint, { card: c.cardLabel(s["card"] ?? "") }), ends: "read" },
      { target: () => `[data-teach="mixes"]`, line: (c) => c.text.get(UI.lessonSecondOpen), ends: "touch" },
      { target: () => `.selector .selector-new`, line: (c) => c.text.get(UI.lessonSecondNew), ends: "touch" },
      { target: () => `.editor .editor-adds`, line: (c) => c.text.get(UI.lessonSecondAdd), ends: "touch" },
      { target: () => `.editor .share-bar`, line: (c) => c.text.get(UI.lessonSecondBar), ends: "read" },
      { target: () => `.editor .editor-name`, line: (c) => c.text.get(UI.lessonSecondName), ends: "read" },
      { target: () => `.editor .editor-head .primary`, line: (c) => c.text.get(UI.lessonSecondSave), ends: "touch" },
      { target: () => `[data-teach="mixes"]`, line: (c) => c.text.get(UI.lessonSecondRun), ends: "read" },
    ],
  },
  {
    id: CAP_RULE,
    // the first full store the hands fill (game/caphint.ts; ui/ledger.ts marks its line), once writing rules is open (the
    // Rules tab is drawn then, with its New rule): walked
    // on the Rules tab's own New rule with nothing filled in; what the hands do instead is the player's pick, so that step
    // points at the whole row
    // a save that already has a cap rule (on any store) has done what this teaches
    may: (view, keeps) => keeps.ruleSeen() && rulesTabDrawn(view, true) && !anyReachesRule(view),
    trigger: `[data-teach="cap-line"]`,
    steps: [
      { target: (s) => `[data-teach="cap-line"][data-store="${s["store"]}"]`, line: (c, s) => c.text.fill(UI.lessonCapFull, { store: c.storeLabel(s["store"] ?? "") }), ends: "read" },
      { target: () => `.tabs [data-tab="rules"]`, line: (c) => c.text.get(UI.lessonCapRules), ends: "touch" },
      { target: () => `.rules .rules-new`, line: (c) => c.text.get(UI.lessonCapNew), ends: "touch" },
      { target: () => `.cond .cond-more`, line: (c) => c.text.get(UI.lessonCapMore), ends: "touch" },
      { target: (s) => `.cond .cond-store[data-store="${s["store"]}"]`, line: (c, s) => c.text.fill(UI.lessonRuleWhen, { when: c.storeLabel(s["store"] ?? "") }), ends: "touch" },
      { target: () => `.cond .cond-fold`, line: (c) => c.text.get(UI.lessonCapLevels), ends: "touch" },
      { target: () => `.cond .cond-test[data-test="reaches"]`, line: (c, s) => c.text.fill(UI.lessonCapReaches, { store: c.storeLabel(s["store"] ?? "") }), ends: "touch", clear: ".cond .cond-steppers" },
      { target: () => `.cond .cond-mixes`, line: (c) => c.text.get(UI.lessonCapDo), ends: "touch" },
      { target: () => `.cond-actions .primary`, line: (c) => c.text.get(UI.lessonRuleAdd), ends: "touch" },
    ],
  },
  {
    id: DRY_STORE,
    // the first dry store a mix card stopped on that a card in play could refill (game/dryhint.ts; ui/ledger.ts marks its
    // line), once rules are taught: walked on the running mix's own Edit, adding the maker; a rule is the other answer, in
    // one line. A save with a mix that already feeds itself has done what this teaches
    may: (view, keeps) => (keeps.lessonKept(FIRST_RULE) || view.orders.some((o) => o.then.kind === "switch_mix")) && !anySelfFedMix(view),
    trigger: `[data-teach="dry-line"]`,
    steps: [
      { target: (s) => `[data-teach="dry-line"][data-store="${s["store"]}"]`, line: (c, s) => c.text.fill(UI.lessonDryLine, { store: c.storeLabel(s["store"] ?? ""), card: c.cardLabel(s["card"] ?? "") }), ends: "read" },
      { target: () => `.hands-mix .hands-meta .hands-edit`, line: (c, s) => c.text.fill(UI.lessonDryEdit, { task: c.cardLabel(s["maker"] ?? ""), store: c.storeLabel(s["store"] ?? "") }), ends: "touch" },
      { target: (s) => `.editor .add-card[data-card="${s["maker"]}"]`, line: (c, s) => c.text.fill(UI.lessonStoppedAdd, { task: c.cardLabel(s["maker"] ?? "") }), ends: "touch" },
      { target: () => `.editor .editor-head .primary`, line: (c, s) => c.text.fill(UI.lessonDrySave, { card: c.cardLabel(s["card"] ?? ""), task: c.cardLabel(s["maker"] ?? ""), store: c.storeLabel(s["store"] ?? "") }), ends: "touch" },
      { target: () => `.hands .hands-mix`, line: (c) => c.text.get(UI.lessonDryRule), ends: "read" },
    ],
  },
  {
    id: TOWN_MIX,
    // the town's mix, the first time its strip shows (ui/townstrip.ts marks Change): taught on the strip and the town editor's own controls;
    // not while the save's town mix has been split any other way than the game made it (townMixAsMade)
    may: (view) => townMixAsMade(view),
    trigger: `[data-teach="town-change"]`,
    steps: [
      { target: () => `[data-teach="town-change"]`, line: (c) => c.text.get(UI.lessonTownChange), ends: "touch" },
      { target: () => `.town-editor .town-bar`, line: (c) => c.text.get(UI.lessonTownBar), ends: "read" },
      { target: () => `.town-editor .editor-head .primary`, line: (c) => c.text.get(UI.lessonTownSave), ends: "touch" },
      { target: () => `.town .town-people`, line: (c) => c.text.get(UI.lessonTownRuns), ends: "read" },
    ],
  },
  {
    id: MIX_STOPPED,
    // the first running mix to grey over a done card (ui/hands.ts marks its Edit): taught on Edit and the editor's own add button
    // (when the content names the card that takes its place), ✕ and Save; the mark is only on a mix whose ✕ will be live
    may: (view) => view.greyed_mix_ids.length > 0,
    trigger: `[data-teach="mix-stopped"]`,
    steps: [
      { target: () => `[data-teach="mix-stopped"]`, line: (c, s) => c.text.fill(s["with"] === undefined ? UI.lessonStoppedEdit : UI.lessonStoppedEditWith, { card: s["gone"] ?? "", task: s["withLabel"] ?? "" }), ends: "touch" },
      { target: (s) => `.editor .add-card[data-card="${s["with"]}"]`, line: (c, s) => c.text.fill(UI.lessonStoppedAdd, { task: s["withLabel"] ?? "" }), ends: "touch", leftOut: (s) => s["with"] === undefined },
      { target: () => `.editor .editor-entry.struck .entry-remove`, line: (c, s) => c.text.fill(UI.lessonStoppedDrop, { card: s["gone"] ?? "" }), ends: "touch" },
      { target: () => `.editor .editor-head .primary`, line: (c) => c.text.get(UI.lessonStoppedSave), ends: "touch" },
    ],
  },
  {
    id: SWITCH_MIX,
    // after the end, a build waits on a store nothing at work makes (game/teach.ts, switchCue; ui/hands.ts marks the way to the
    // list, or Edit): taught on the real controls, to the saved mix that makes the store, or to adding the card that does
    may: () => true,
    trigger: `[data-switch]`,
    steps: [
      { target: () => `[data-switch]`, line: (c, s) => c.text.fill(s["switch"] === "edit" ? UI.lessonSwitchEdit : UI.lessonSwitchMixes, { build: s["build"] ?? "", store: s["store"] ?? "", mix: s["mix"] ?? "", task: s["task"] ?? "" }), ends: "touch" },
      { target: (s) => `.selector-run[data-mix="${quoted(s["mix"] ?? "")}"]`, line: (c, s) => c.text.fill(UI.lessonSwitchRun, { mix: s["mix"] ?? "" }), ends: "touch", leftOut: (s) => s["switch"] === "edit" },
      { target: (s) => `.editor .add-card[data-card="${s["card"]}"]`, line: (c, s) => c.text.fill(UI.lessonStoppedAdd, { task: s["task"] ?? "" }), ends: "touch", leftOut: (s) => s["switch"] !== "edit" },
      { target: () => `.editor .editor-head .primary`, line: (c, s) => c.text.fill(UI.lessonSwitchSave, { store: s["store"] ?? "" }), ends: "touch", leftOut: (s) => s["switch"] !== "edit" },
    ],
  },
  {
    id: CLOCK,
    // the night's countdown, the moment it first shows (ui/cards.ts marks it): a wait in real time, taught on the clock itself;
    // not in a save past its first night (nightsBegun)
    may: (view) => nightsBegun(view) <= 1,
    trigger: `[data-teach="clock"]`,
    steps: [{ target: () => `[data-teach="clock"]`, line: (c) => c.text.get(UI.lessonClock), ends: "read" }],
  },
  {
    id: JOURNAL,
    // the Journal button, the moment it first shows (ui/journal.ts): its own control, so no Show me; the step after the first runs in its sheet;
    // not in a save with a second page written
    may: (view) => view.unlocked.filter((u) => u.category === "entry").length <= 1,
    trigger: `[data-teach="journal"]`,
    yields: true,
    steps: [
      { target: () => `[data-teach="journal"]`, line: (c) => c.text.get(UI.lessonJournalOpen), ends: "touch" },
      { target: () => `.journal-sheet [data-teach="journal-note"]`, line: (c) => c.text.get(UI.lessonJournalNotes), ends: "read" },
    ],
  },
  {
    id: JOURNAL_NUMBERS,
    // a page's numbers, the first time a page that shows some is open after the journal's lesson: a page with none never waits on it
    may: (_view, keeps) => keeps.lessonKept(JOURNAL),
    trigger: `.journal-sheet .journal-numbers`,
    steps: [{ target: () => `.journal-sheet .journal-numbers`, line: (c) => c.text.get(UI.lessonJournalNumbers), ends: "read" }],
  },
  {
    id: PRESTIGE,
    // the Push past control, which shows only once a skill is at its top (ui/skillrow.ts marks it): taught on the control itself,
    // until a skill of this save has been pushed past (its phase beyond the first)
    may: (view) => !view.skills.some((s) => (s.prestige?.phase ?? 1) > 1),
    trigger: `[data-teach="prestige"]`,
    steps: [{ target: (s) => `[data-teach="prestige"][data-skill="${s["skill"]}"]`, line: (c, s) => c.text.fill(UI.lessonPrestige, { skill: c.skillLabel(s["skill"] ?? "") }), ends: "read" }],
  },
];

/** The save's town mix is as the game made it: each person's whole time on one card (api CONTRACT.txt, "The town's mix"),
 * not split or moved to another task since. */
function townMixAsMade(view: View): boolean {
  const mix = view.mixes.find((m) => m.id === view.running_town_mix_id);
  return mix !== undefined && mix.components.length > 0 && mix.components.every((c) => c.kind === "card_share" && c.share_bp === WHOLE_BP);
}

/** The nights the save has lived into: a night that has begun is a hidden store (a countdown) whose id is both an action
 * and a feature of view.unlocked. */
function nightsBegun(view: View): number {
  const features = new Set(view.unlocked.filter((u) => u.category === "feature").map((u) => u.id));
  return view.unlocked.filter((u) => u.category === "action" && features.has(u.id)).length;
}

/** The lesson as it runs for this player and subject: its steps without those left out by a lesson they ended done
 * (`unlessDone`) or by the subject (`leftOut`), and `at`, each remaining step's index in the full list, which is what the
 * record of how it ended counts in. */
export function stepsFor(lesson: Lesson, keeps: Keeps, subject: Subject): { lesson: Lesson; at: number[] } {
  const at = lesson.steps.flatMap((s, i) => ((s.unlessDone !== undefined && keeps.lessonDone(s.unlessDone)) || s.leftOut?.(subject) ? [] : [i]));
  return { lesson: { ...lesson, steps: at.map((i) => lesson.steps[i]!) }, at };
}

/** The lesson may start now: lessons are on, it is not yet done or skipped in this save, and its own condition holds. */
export function mayStart(lesson: Lesson, view: View, keeps: Keeps): boolean {
  return keeps.lessonsOn() && !keeps.lessonKept(lesson.id) && lesson.may(view, keeps);
}

/** The lesson `id` may start now (mayStart). Its trigger shows the guided button then, in place of the one-tap one. */
export function guided(id: string, view: View, keeps: Keeps): boolean {
  const lesson = LESSONS.find((l) => l.id === id);
  return lesson !== undefined && mayStart(lesson, view, keeps);
}

/** A guided rule offer waits off screen while another lesson is under way (`current`, ui/lessons.ts): one lesson at a
 * time, and its Show me would open its editor with no lesson to walk it. It waits too while the rule's lesson runs on
 * another offer (`subject`, what that lesson started on): one Show me at a time, never a twin, until that one is
 * answered (its lesson ended, or the offer gone). */
export function ruleWaits(card: OrderCard, current: string | null, subject: Subject | null): boolean {
  if (current === null) return false;
  if (current !== FIRST_RULE) return true;
  const own = ruleSubject(card);
  return subject !== null && (own === null || ["task", "watch", "kind"].some((k) => own[k] !== subject[k]));
}

/** A rule offer is built under the rule's lesson (its button reads Show me) while that lesson may start and the offer
 * runs a task the editor can point at; otherwise it is today's one-tap Add rule. */
export function guidedRule(view: View, keeps: Keeps, card: OrderCard): boolean {
  return ruleSubject(card) !== null && guided(FIRST_RULE, view, keeps);
}

/** A rule offer's subject, as its trigger's data attributes: the task it runs and what it watches; null when it
 * runs a mix (nothing on the editor's Do row to point at). */
export function ruleSubject(card: OrderCard): Record<string, string> | null {
  if (card.then.kind !== "tap_card") return null;
  return card.chip !== null ? { task: card.then.card, watch: card.chip, kind: "chip" } : { task: card.then.card, watch: card.store, kind: "store" };
}

/** The lesson earlier in the list than `lesson` that may start and whose trigger is on show: an untouched lesson that
 * `yields` gives way to it. */
export function outrankedBy(lesson: Lesson, view: View, keeps: Keeps, triggerOnShow: (selector: string) => boolean): Lesson | undefined {
  if (!lesson.yields) return undefined;
  return LESSONS.slice(0, LESSONS.findIndex((l) => l.id === lesson.id)).find((l) => mayStart(l, view, keeps) && triggerOnShow(l.trigger));
}

/** The step on show: the furthest one, up to one past the last finished (`reached`), whose target is on show; null
 * when none is. Never more than one ahead, so a step is not skipped because a later control is also in view. */
export function stepOnShow(lesson: Lesson, s: Subject, reached: number, onShow: (selector: string) => boolean): number | null {
  for (let i = Math.min(reached + 1, lesson.steps.length - 1); i >= 0; i -= 1) {
    const step = lesson.steps[i];
    if (step && onShow(step.target(s))) return i;
  }
  return null;
}
