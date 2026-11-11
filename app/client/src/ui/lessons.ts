// The lesson runner (game/lessons.ts holds the lessons as data). A lesson starts when its trigger is on show and it
// may; then each step's control takes the one glow, with its line in a small note beside it, fixed to the viewport so
// nothing in the layout moves. When a step starts and its control, or what it keeps `clear`, is out of sight (off the
// window on a phone's long page, under a pinned strip, past a scrolling sheet's edge), the control is scrolled to the
// middle of what the pinned scene and hands strip leave of the window, at once under reduced motion. The step on show is game/lessons.stepOnShow's: a step ends on a tap of its control
// (or, for a "read" step, a tap on the note, which says "Got it"; never a timer, since a player may look away for a
// while), and a step whose control is not on show waits; once nothing of the lesson is on show (trigger, last finished
// step, next step) for HELD_MS, it is abandoned, so the next lesson can run and this one starts over the next time it may.
// Skip, at every step, ends it; skipped or done, it is kept in the save and never comes again in it. Nothing is modal: every control stays
// live under the note, and a lesson interrupted by a reload simply starts over the next time it may.
import type { View } from "../api/types";
import { LESSONS, mayStart, outrankedBy, stepOnShow, stepsFor, type Lesson, type Subject } from "../game/lessons";
import { UI } from "../game/text";
import { ACTED, bringIntoView, el, setText, tapFeedback } from "./dom";
import type { Part, PartContext } from "./part";

const GAP_PX = 8;
const GUTTER_PX = 16;
/** How long a lesson waits with nothing of it on show (its trigger, its last finished step's control, its next step's)
 * before it ends as skipped: a server round trip (Add rule's row arriving) is quicker, and a closed editor or a tab left
 * never comes back by itself. While the last finished step's control is on show (the Rules row), it waits without limit. */
export const HELD_MS = 30_000;
/** The control is there to be tapped: in the page, not hidden, not held back by the reveal, not off, with a size. */
export function onShow(node: Element | null): node is HTMLElement {
  if (!node || !node.isConnected || node.closest("[hidden], .held")) return false;
  if ((node as HTMLButtonElement).disabled) return false;
  const r = node.getBoundingClientRect();
  return r.width > 0 && r.height > 0;
}

function find(root: Pick<ParentNode, "querySelectorAll">, selector: string): HTMLElement | null {
  for (const n of Array.from(root.querySelectorAll(selector))) if (onShow(n)) return n;
  return null;
}

/** What is at the middle of `node`, under the note (which moves to it next), is `node` or inside it: it can be seen there.
 * Anything else (the window's edge, a pinned strip, a sheet's edge) is in the way; the browser's own nearest scroll
 * knows nothing of pinned parts. */
function inSight(doc: Pick<Document, "elementsFromPoint">, node: Element, note: Element): boolean {
  const r = node.getBoundingClientRect();
  const hit = doc.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2).find((n) => !note.contains(n));
  return hit !== undefined && node.contains(hit);
}

/** The subject a trigger carries in its data attributes. */
function subjectOf(node: HTMLElement): Subject {
  return Object.fromEntries(Object.entries(node.dataset).filter((e): e is [string, string] => e[1] !== undefined));
}

interface Spot { left: number; top: number }

/** `shown`: the last step brought into view, so a step scrolls the page once, not again when the player scrolls away. */
interface Running { lesson: Lesson; at: number[]; subject: Subject; reached: number; step: number | null; since: number; target: HTMLElement | null; longest: number; heldSince: number | null; shown: number }

export class Lessons implements Part {
  readonly root = el("aside", "lesson-note");
  private readonly line = el("p", "lesson-line");
  private readonly tag = el("span", "lesson-tag");
  private readonly skip = el("button", "lesson-skip");
  private readonly next = el("button", "lesson-next");
  private view: View | null = null;
  private run: Running | null = null;

  constructor(private readonly ctx: Pick<PartContext, "catalog" | "glow" | "keeps">, private readonly host: Pick<HTMLElement, "append">,
    private readonly changed: () => void = () => undefined, private readonly doc: Pick<Document, "querySelectorAll" | "addEventListener" | "elementsFromPoint"> = document,
    private readonly now: () => number = () => performance.now()) {
    const { catalog } = ctx;
    this.skip.type = "button";
    setText(this.tag, catalog.text.get(UI.lessonTag));
    setText(this.skip, catalog.text.get(UI.lessonSkip));
    this.skip.addEventListener("click", () => { tapFeedback(); this.lap(); this.end(true); });
    this.next.type = "button";
    setText(this.next, catalog.text.get(UI.lessonNext));
    this.root.addEventListener("click", (e) => this.read(e.target));
    this.root.append(this.tag, this.skip, this.line, this.next);
    this.root.hidden = true;
    host.append(this.root);
    for (const type of ["click", ACTED]) this.doc.addEventListener(type, (e) => this.touched(e.target), true);
  }

  update(view: View): void {
    this.view = view;
  }

  /** The lesson under way (started, not yet done or skipped), or null. */
  get current(): string | null {
    return this.run?.lesson.id ?? null;
  }

  /** The lesson under way that holds a guided rule offer back (game/lessons.ts, ruleWaits): `current`, but not one that
   * yields and has not been touched. */
  get holding(): string | null {
    const run = this.run;
    return run && !(run.lesson.yields && run.reached < 0) ? run.lesson.id : null;
  }

  /** What the lesson under way started on, or null. */
  get subject(): Subject | null {
    return this.run?.subject ?? null;
  }

  /** Every frame (the game time it is handed is not a reading clock: the page's own clock is). */
  tick(): void {
    const t = this.now();
    const view = this.view;
    if (!view) return;
    if (this.run && !this.ctx.keeps.lessonsOn()) this.abandon(this.run);   // turned off: nothing kept, so it starts over once they are on
    if (this.run && this.run.reached < 0 && outrankedBy(this.run.lesson, view, this.ctx.keeps, (sel) => find(this.doc, sel) !== null)) this.abandon(this.run);
    if (!this.run) {
      this.run = this.start(view, t);
      if (this.run) this.changed();   // another guided offer now waits (game/lessons.ts, ruleWaits)
    }
    const run = this.run;
    if (!run) return;
    if (run.reached < 0 && !find(this.doc, run.lesson.trigger)) { this.abandon(run); return; }   // its trigger went (Dismiss) before the first touch
    this.refresh(run, t);
    if (this.heldOut(run, t)) { this.abandon(run); return; }
    if (this.run && run.target) this.place(run.target);
  }

  /** Nothing of the lesson can move or be seen, for HELD_MS: its trigger has gone, and neither the last finished step's
   * control (whose line stays while the next waits) nor the next step's is on show. */
  private heldOut(run: Running, t: number): boolean {
    const on = (i: number): boolean => { const s = run.lesson.steps[i]; return s !== undefined && find(this.doc, s.target(run.subject)) !== null; };
    const held = !on(run.reached) && !on(run.reached + 1) && !find(this.doc, run.lesson.trigger);
    run.heldSince = held ? run.heldSince ?? t : null;
    return run.heldSince !== null && t - run.heldSince >= HELD_MS;
  }

  /** The lesson goes with nothing kept (its trigger left before a touch, or nothing of it stayed on show), and starts over at
   * the next time it may. */
  private abandon(run: Running): void {
    if (run.target) this.ctx.glow.clear(run.target);
    this.run = null;
    this.root.hidden = true;
    this.changed();   // an offer that waited on this one comes back (game/lessons.ts, ruleWaits)
  }

  /** The step on show now, drawn when it changed or when its control was redrawn under it (the editor redraws its rows
   * after a preview): the note follows the new control, and a read step keeps the time it has had. */
  private refresh(run: Running, t: number): void {
    this.unfold(run);
    const step = stepOnShow(run.lesson, run.subject, run.reached, (sel) => find(this.doc, sel) !== null);
    const redrawn = step === run.step && run.target !== null && !run.target.isConnected;
    if (step !== run.step || redrawn) this.show(run, step, redrawn ? run.since : t);
    if (step !== null && !redrawn && run.target && run.shown !== step) {
      run.shown = step;
      const clear = run.lesson.steps[step]?.clear;
      const seen = [run.target, ...(clear ? Array.from(this.doc.querySelectorAll(clear)) : [])];
      if (!seen.every((n) => inSight(this.doc, n, this.root))) bringIntoView(this.doc, run.target);
    }
  }

  /** The next step's control sits in a folded part (the editor's Add list): the fold is told to open. */
  private unfold(run: Running): void {
    const next = run.lesson.steps[run.reached + 1];
    if (!next) return;
    for (const n of Array.from(this.doc.querySelectorAll(next.target(run.subject)))) n.closest(".folded")?.dispatchEvent(new Event("unfold"));
  }

  /** The first lesson that may start and whose trigger is on show. */
  private start(view: View, t: number): Running | null {
    const { keeps } = this.ctx;
    for (const lesson of LESSONS) {
      if (!mayStart(lesson, view, keeps)) continue;
      const trigger = find(this.doc, lesson.trigger);
      if (trigger) return { ...stepsFor(lesson, keeps, subjectOf(trigger)), subject: subjectOf(trigger), reached: -1, step: null, since: t, target: null, longest: 0, heldSince: null, shown: -1 };
    }
    return null;
  }

  private show(run: Running, step: number | null, t: number): void {
    if (run.target) this.ctx.glow.clear(run.target);
    run.step = step;
    run.since = t;
    run.target = step === null ? null : find(this.doc, run.lesson.steps[step]!.target(run.subject));
    this.root.hidden = run.target === null;
    const reads = step !== null && step >= 0 && run.lesson.steps[step]?.ends === "read";
    this.next.hidden = !reads;
    this.root.classList.toggle("reads", reads);
    if (!run.target || step === null) return;
    this.seat(run.target);
    setText(this.line, run.lesson.steps[step]!.line(this.ctx.catalog, run.subject));
    this.ctx.glow.clear();   // the lesson's step is the one obvious next thing
    this.ctx.glow.offer(run.target);
  }

  /** The note lives in the page; for a control inside a sheet it lives in that sheet's own layer, which a modal sheet
   * would otherwise cover (a sheet's lesson: the journal's). */
  private seat(target: HTMLElement): void {
    const home: Pick<HTMLElement, "append"> = target.closest("dialog") ?? this.host;
    if (this.root.parentElement !== home) home.append(this.root);
  }

  /** A tap on the step's control (or inside it) ends that step. A read step never holds a tap back: one on the control of
   * a step after it, with only read steps between, ends them all (the player tapped Save while the bar's line was up). */
  private touched(target: EventTarget | null): void {
    const run = this.run;
    const at = target as Element | null;
    if (!run || run.step === null || run.step < 0 || typeof at?.closest !== "function" || this.root.contains(at)) return;
    for (let i = run.step; i < run.lesson.steps.length; i += 1) {
      const step = run.lesson.steps[i]!;
      if (at.closest(step.target(run.subject))) { this.finish(run, i); return; }
      if (step.ends !== "read") return;
    }
  }

  /** A tap on the note ends the read step on show; Skip is its own button. */
  private read(target: EventTarget | null): void {
    const run = this.run;
    const at = target as Element | null;
    if (!run || run.step === null || run.step < 0 || run.lesson.steps[run.step]?.ends !== "read" || this.skip.contains(at as Node)) return;
    tapFeedback();
    this.finish(run, run.step);
  }

  /** The step on show ends now: how long it was there counts toward the longest wait. */
  private lap(): void {
    const run = this.run;
    if (run?.target && run.step !== null && run.step >= 0) run.longest = Math.max(run.longest, this.now() - run.since);
  }

  private finish(run: Running, step: number): void {
    this.lap();
    run.reached = Math.max(run.reached, step);
    if (run.reached >= run.lesson.steps.length - 1) this.end(false);
    else run.step = -1;   // drawn afresh next frame
  }

  /** Done or skipped: kept, so it never comes again; a guided offer goes back to its one-tap form. */
  private end(skipped: boolean): void {
    const run = this.run;
    if (!run) return;
    if (run.target) this.ctx.glow.clear(run.target);
    const last = run.lesson.steps.length - 1;
    const step = skipped ? Math.min(Math.max(run.step ?? 0, run.reached + 1, 0), last) : last;
    this.ctx.keeps.keepLesson({ lesson: run.lesson.id, skipped, step: run.at[step] ?? step, longest_wait_s: Math.round(run.longest / 1000) });
    this.run = null;
    this.root.hidden = true;
    this.changed();
  }

  /** The note under its control; else beside it (left, then right); else above it: the first of those inside the
   * window's gutters that covers no sibling of the control, not the card it sits in (then above or below that card), not the panel's tabs
   * and not the next step's control when it is already on show. With none clear, the one that covers least. */
  private place(target: HTMLElement): void {
    if (!onShow(target)) { this.root.hidden = true; return; }
    this.root.hidden = false;
    const r = target.getBoundingClientRect();
    const w = this.root.offsetWidth;
    const h = this.root.offsetHeight;
    const vw = window.innerWidth;
    const across = Math.max(GUTTER_PX, Math.min(r.left, vw - w - GUTTER_PX));
    const middle = r.top + (r.height - h) / 2;
    const spots: Spot[] = [
      { left: across, top: r.bottom + GAP_PX },
      { left: r.left - GAP_PX - w, top: middle },
      { left: r.right + GAP_PX, top: middle },
      { left: across, top: r.top - GAP_PX - h },
    ];
    const card = target.closest<HTMLElement>(".card")?.getBoundingClientRect();   // a control in a card: its title stays in view
    if (card) spots.push({ left: across, top: card.bottom + GAP_PX }, { left: across, top: card.top - GAP_PX - h });
    const fits = (s: Spot): boolean => s.left >= GUTTER_PX && s.left + w <= vw - GUTTER_PX && s.top >= 0 && s.top + h <= window.innerHeight;
    const covered = this.neighbours(target).map((n) => n.getBoundingClientRect());
    const hidden = (s: Spot): number => covered.reduce((sum, c) => sum + Math.max(0, Math.min(s.left + w, c.right) - Math.max(s.left, c.left)) * Math.max(0, Math.min(s.top + h, c.bottom) - Math.max(s.top, c.top)), 0);
    const room = spots.filter(fits);
    const spot = room.find((s) => hidden(s) === 0) ?? room.sort((a, b) => hidden(a) - hidden(b))[0] ?? { left: across, top: Math.max(GUTTER_PX, r.top - GAP_PX - h) };
    this.root.style.left = `${Math.round(spot.left)}px`;
    this.root.style.top = `${Math.round(spot.top)}px`;
  }

  /** What the note must not hide: the control's siblings (the other chips of its row), the panel's tabs, an offer's card
   * names, what the step names as `clear`, and the control the next step points at, so the player sees where to go after
   * this. */
  private neighbours(target: HTMLElement): Element[] {
    const siblings = Array.from(target.parentElement?.children ?? []).filter((n) => n !== target && n !== this.root);
    const owner = target.closest(".card");
    const next = this.nextTarget();
    const clear = this.run && this.run.step !== null ? this.run.lesson.steps[this.run.step]?.clear : undefined;
    const kept = [".tabs", ".offer-names", ...(clear ? [clear] : [])].join(", ");
    return [...siblings, ...(owner ? [owner] : []), ...(next ? [next] : []), ...Array.from(this.doc.querySelectorAll(kept))].filter((n) => n.getBoundingClientRect().width > 0);
  }

  /** The next step's control, when it is on show already; else null. */
  private nextTarget(): HTMLElement | null {
    const run = this.run;
    const next = run && run.step !== null ? run.lesson.steps[run.step + 1] : undefined;
    return run && next ? find(this.doc, next.target(run.subject)) : null;
  }
}
