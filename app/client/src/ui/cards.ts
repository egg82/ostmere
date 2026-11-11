// The card panel (docs/design/opening-screen.md, "Cards"): view.cards in lane groups, each lane a stripe colour, crafts
// together under one heading; a ruled lane's cards are left out (they are that lane's tasks, game/lanes.ts). Every card is drawn the same whether tapped, mixed or idle: title, completions against its
// cap, its needs as have/need (short ones in the ledger's red), its one bar (Card.bar modulo bar_total, whoever runs it),
// Ready iff blocker is null; a card whose lane is busy can't be
// tapped and looks flat, unless it cuts in (Card.cuts_in); an unready one is muted but still answers a tap: a failed tap, which takes no time, pulses the
// card red and marks what stopped it, and says its failed line.
// Slots don't move: a card that leaves view.cards stays in its slot, done, until a new card needs one (the new card takes
// the slot of the card whose completion opened it, so the next step lands under the finger) or until it has been held
// DONE_HOLD_MS and nothing is being touched, when it goes to the Completed tab and the cards after it close up.
// A line the player's tap wrote shows on the card for its reading time, over the meta row, so nothing moves (a failed
// tap's leaves the countdown it is about in view); a card
// that would take the slot of a card still showing one waits in the arrival queue, and takes the slot at its turn.
// A new card given a new slot at its group's end (below the mix's cards, out of sight on a phone) is scrolled into
// view once, unless a finger is on the page or just left it.
import type { Card, View } from "../api/types";
import { sample } from "../game/clock";
import { panelView } from "../game/lanes";
import { keptReadyAt, waitsOnUnseen } from "../game/ready";
import { UI } from "../game/text";
import { CardGroups } from "./cardgroups";
import { makeRow, type Row } from "./cardrow";
import { el, pulse, setText } from "./dom";
import { completionRung, play } from "./ladder";
import { cardHintsNow, hintCard } from "./cardhint";
import type { NewMarks } from "../game/marks";
import { markNew } from "./fresh";
import type { Part, PartContext } from "./part";
import { WaitLine } from "./waitline";
import { WhenReady } from "./whenready";
import { storyMarks } from "../game/story";

/** How long a finished card stays in its slot, so the player sees it finish, before it goes to Completed. */
const DONE_HOLD_MS = 5000;
/** A finished card is not removed within this long of the last press or while one is down: nothing reflows under a finger. */
const QUIET_MS = 1500;

export class Cards implements Part {
  readonly root = el("section", "deck");
  private readonly groups: CardGroups;
  private readonly whenReady: WhenReady;
  private readonly rows = new Map<string, Row>();
  /** Finished cards standing in the slot a waiting card will take, drawn done with their line until it does. */
  private readonly leaving = new Set<Row>();
  private view: View | null = null;
  private story: ReadonlySet<string> = new Set();
  /** The wait line, first in the deck (ui/waitline.ts). */
  private readonly wait: WaitLine;
  private pressed = false;
  /** The first card this update gave a new slot at its group's end. */
  private atEnd: HTMLElement | null = null;
  private lastPress = -Infinity;

  constructor(private readonly ctx: PartContext, private readonly marks: NewMarks, private readonly arrived: () => void = () => undefined) {
    this.wait = new WaitLine(ctx);
    this.root.append(this.wait.root);
    this.groups = new CardGroups(this.root, ctx.catalog);
    this.whenReady = new WhenReady(ctx);
    const press = (down: boolean): void => { this.pressed = down; this.lastPress = performance.now(); };
    document.addEventListener("pointerdown", () => press(true), true);
    for (const type of ["pointerup", "pointercancel"]) document.addEventListener(type, () => press(false), true);
  }

  /** Put a story line on a card on screen, for `ms` once shown; its node (held by the caller's queue), or null when the
   * card is not on screen. The band's copy is the one read aloud. `failed`: the line of a failed tap of the card. */
  say(card: string, text: string, ms: number, failed = false): HTMLElement | null {
    const row = this.rows.get(card);
    if (!row || !row.node.isConnected) return null;
    const node = el("span", "card-line", text);
    node.setAttribute("aria-hidden", "true");
    row.node.append(node);
    row.lines.push({ node, ms, shownAt: 0, failed });   // a second line from one tap waits its turn in the queue
    return node;
  }

  /** A failed tap of this card (Step.failed_tap): the card pulses red, and so does what its blocker names (the need
   * row that shows it, else the countdown); with neither on the card, the card alone. A second tap restarts both. */
  failed(card: string, view: View): void {
    const row = this.rows.get(card);
    if (!row || row.done) return;
    row.node.classList.remove("press");   // one animation per node: the press would replay after the pulse
    pulse(row.node, "tap-failed");
    const blocker = row.card.blocker;
    if (!blocker) return;
    const mark = row.needs.shows(blocker.condition) ?? (keptReadyAt(view, row.card) !== null ? row.foot : null);
    if (mark) pulse(mark, "fail-mark");
  }

  /** A card's node, for the glow. */
  node(card: string): HTMLButtonElement | undefined {
    const row = this.rows.get(card);
    return row && !row.done ? row.tap : undefined;
  }

  update(full: View, before: View | null): void {
    const view = panelView(this.ctx.catalog, full);   // a ruled lane's cards are its tasks, never cards here
    const prev = before && panelView(this.ctx.catalog, before);
    this.view = view;
    this.story = storyMarks(this.ctx.catalog, full).cards;
    this.wait.update(full);
    const live = new Map(view.cards.map((c) => [c.card, c]));
    const landed = new Set<string>();
    for (const [id, row] of this.rows) {
      const now = live.get(id)?.completions ?? view.completed.find((c) => c.card === id)?.completions ?? row.card.completions;
      if (now > row.card.completions) landed.add(id);
      if (!live.has(id) && !row.done) {
        row.done = true;
        row.doneAt = performance.now();
        if (row.lines.length === 0 && prev) {   // finished looks are a change too: at their turn (with a line, at once)
          row.doneShown = false;
          this.ctx.arrivals.effect(row.node, "card", () => { row.doneShown = true; row.node.classList.toggle("done", row.done); });
        }
      }
    }
    for (const card of view.cards) {
      const row = this.rows.get(card.card);
      if (row) row.done = false;
      else this.place(card, landed, prev !== null);
    }
    this.marks.sync(view);   // after placing: a card that arrives already at work never gets a dot
    this.groups.layout(this.rows);
    this.bringIntoView();
    const busy = new Set(view.lanes.filter((l) => l.running_card !== null).map((l) => l.lane));
    const running = new Set(view.lanes.flatMap((l) => (l.running_card ? [l.running_card] : [])));
    const single = this.rows.size === 1;
    const hints = cardHintsNow(this.ctx.catalog, view, this.ctx.keeps, this.ctx.lesson(), this.ctx.repeats().taps);
    for (const row of this.rows.values()) {
      const card = live.get(row.id);
      if (card) {
        const before = row.card;
        row.card = card;
        if (card.completions > before.completions && prev) {
          const rung = completionRung(before.by, row.byOrder === true);   // as it ran until now: the restyle below moves it on
          const pop = (): void => play(row.node, rung);
          if (row.lines.length > 0) pop();   // with its line, on the card the eyes are on
          else this.ctx.arrivals.effect(row.node, "card", pop);
        }
      } else {
        const done = view.completed.find((c) => c.card === row.id);
        if (done) row.card = { ...row.card, completions: done.completions };
      }
      hintCard(row.node, row.id, hints, () => this.ctx.keeps.keepMixOffered(row.id), this.marks.has(row.id));   // a quiet mark, once: the mix could take it
      this.restyle(row, view, { busy, running, single });
    }
    for (const row of this.leaving) {
      if (!row.node.isConnected) {
        this.leaving.delete(row);
        continue;
      }
      const done = view.completed.find((c) => c.card === row.id);
      if (done) row.card = { ...row.card, completions: done.completions };
      this.restyle(row, view, { busy, running, single });
    }
  }

  tick(t: number): void {
    this.wait.tick(t);
    this.sweep();
    for (const row of this.leaving) this.lineTick(row);
    const { format } = this.ctx.catalog;
    for (const row of this.rows.values()) {
      const { card } = row;
      this.lineTick(row);
      if (row.done) continue;
      const span = card.bar_total;
      const v = sample(card.bar, t);
      const done = span > 0 ? (((v % span) + span) % span) / span : 0;
      row.fill.style.transform = `scaleX(${done})`;
      const wait = card.by === "tap" ? card.completes_at : this.view ? keptReadyAt(this.view, card) : null;
      setText(row.foot, wait !== null ? format.duration(wait - t) : card.tap_s !== null ? format.duration(card.tap_s) : "");
      this.markClock(row, wait !== null && this.view !== null && waitsOnUnseen(this.view, card));
      row.needs.tick(card, this.view, t);
    }
  }

  /** The countdown of a card that waits on a store the player was never shown (the night) is the clock's lesson's mark. */
  private markClock(row: Row, clock: boolean): void {
    if (clock) row.foot.dataset["teach"] = "clock";
    else delete row.foot.dataset["teach"];
  }

  /** A card's line: timed from when it shows, gone after its reading time (a newer one shown replaces it); the meta row
   * is hidden while one is up. */
  private lineTick(row: Row): void {
    const shown = row.lines.filter((l) => !l.node.classList.contains("held"));
    const latest = shown[shown.length - 1];
    for (const l of shown) if (l !== latest) l.node.remove();
    if (latest) {
      const now = performance.now();
      if (latest.shownAt === 0) latest.shownAt = now;
      if (now - latest.shownAt >= latest.ms) latest.node.remove();
    }
    row.lines = row.lines.filter((l) => l.node.isConnected);
    const up = row.lines.filter((l) => !l.node.classList.contains("held"));
    row.node.classList.toggle("saying", up.length > 0);
    row.node.classList.toggle("saying-failed", up.at(-1)?.failed === true);
  }

  /** Finished cards past their hold leave for the Completed tab (the view already lists them there), when no finger is near. */
  private sweep(): void {
    const now = performance.now();
    if (this.pressed || now - this.lastPress < QUIET_MS) return;
    if (this.ctx.arrivals.busy) return;   // a card leaving is a change too: not while something waits its turn
    let left = false;
    for (const [id, row] of this.rows) {
      if (!row.done || now - row.doneAt < DONE_HOLD_MS) continue;
      row.node.remove();
      this.rows.delete(id);
      left = true;
    }
    if (left) this.groups.layout(this.rows);
  }

  private bringIntoView(): void {
    const node = this.atEnd;
    this.atEnd = null;
    if (node && !this.pressed && performance.now() - this.lastPress >= QUIET_MS) node.scrollIntoView?.({ block: "nearest" });
  }

  /** A new card's slot: the done slot of the card that just completed in its group, else any done slot, else a new one. */
  private place(card: Card, landed: Set<string>, inPlay: boolean): void {
    const newGroup = this.groups.isNew(card.card);
    const group = this.groups.of(card.card);
    const done = group.slots.filter((id) => this.rows.get(id)?.done);
    const target = done.find((id) => landed.has(id)) ?? done[0];
    const row = makeRow(this.ctx, this.whenReady, card);
    if (target) {
      const old = this.rows.get(target);
      if (old && old.lines.length > 0 && inPlay) {   // it keeps the slot, showing its line, until this card's turn
        row.stand = old.node;
        this.leaving.add(old);
      } else {
        old?.node.remove();
      }
      this.rows.delete(target);
      group.slots[group.slots.indexOf(target)] = card.card;
    } else {
      group.slots.push(card.card);
      if (inPlay) this.atEnd ??= row.node;
    }
    this.rows.set(card.card, row);
    if (inPlay) {
      this.marks.add(card.card);
      this.arrived();
      markNew(row.node, () => this.marks.clear(card.card));
      this.ctx.arrivals.arrive(row.node, "card", card.card, row.stand);
      const tag = newGroup ? group.node.querySelector<HTMLElement>(":scope > .lane-tag") : null;
      if (tag) this.ctx.arrivals.arrive(tag, "card", card.card);   // a new group's heading comes with its first card
    }
  }

  private restyle(row: Row, view: View, s: { busy: Set<string>; running: Set<string>; single: boolean }): void {
    const { catalog } = this.ctx;
    const { card } = row;
    const info = catalog.cards.get(row.id);
    const lane = info?.lane ?? "hands";
    const isRunning = s.running.has(row.id);
    const laneBusy = s.busy.has(lane) && !card.cuts_in;   // a glowing step or a cure cuts in (Card.cuts_in)
    const retired = row.done && catalog.retired(view, row.id);
    const cl = row.node.classList;
    cl.toggle("story", this.story.has(row.id));   // the story mark (game/story.ts)
    cl.toggle("done", row.done && row.doneShown !== false);
    cl.toggle("retired", retired);
    cl.toggle("ready", !row.done && card.blocker === null);
    cl.toggle("unready", !row.done && card.blocker !== null);
    cl.toggle("busy", !row.done && laneBusy && !isRunning);
    cl.toggle("running", !row.done && isRunning);
    cl.toggle("by-mix", !row.done && card.by === "mix");
    row.byOrder = this.ctx.fires.running.has(row.id);
    cl.toggle("by-order", row.byOrder);
    cl.toggle("first", s.single && !row.done);
    cl.toggle("untapped", s.single && !row.done && card.completions === 0 && card.by === null);
    row.tap.disabled = row.done || laneBusy;
    setText(row.count, retired ? catalog.text.get(UI.retired) : card.cap !== null || card.completions > 0 ? catalog.format.completions(card.completions, card.cap) : "");
    row.needs.draw(row.card, view, row.done);
    row.fight?.sync(view, row.id);
    this.whenReady.sync(row.ready, row.done ? undefined : card, view);
  }
}
