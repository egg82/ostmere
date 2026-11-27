// The hands strip: one row that says what the hands are doing (docs/design/opening-screen/hands-strip.md, "The hands strip"). It
// takes no room until the first mix's offer (game/shown.ts), then comes in through the arrival queue; until then each
// card's own bar says what the hands do. Once drawn it stays. The mix row opens
// bare, its bar and name; Edit, Mixes ▾ and "runs …" each come when they first mean something, then stay. On a phone only
// the bar and the name ("Main ▾", the way to the Mixes list) stay pinned; the row of controls under them scrolls with the
// cards (`rows`).
// Tapping: the card's name (its bar stays on the card). Idle: "idle". The first-mix offer: its cards and one button.
// A running mix: its split bar (under it, while a card of the mix is stopped, the split that runs now: runningnow.ts), name, how long it runs, Edit; grey when it holds a
// retired or completed card, shown as the grey bar, "stopped · {card} done" naming that card, and Edit. The bar shows what the hands do now
// (game/holder.ts, ui/handsheld.ts): while a tap holds them, that card as the whole bar with its time left, the name slot
// saying "then {mix}"; else a rule's mix while its condition holds, or a goal stint's mix, either with "until …", where it
// lets go, where "runs …" would be, and "then {mix}" after it; else the player's own. "until …" (or
// "while …") is a button: it opens the Rules tab, where Lately says what the rules did. Once a mix exists "Mixes ▾" opens the Mixes list, the
// running mix's name beside it as plain text; with none running but mixes or rules saved, a plain button in the meta slot opens the list (or, with
// only rules, the Rules tab). Under the mix row, a card the mix can take, offered once (mixoffer.ts), and a chip's rule
// offer once it is due (chipoffer.ts); what someone asks is the Asks list's (asks.ts). When the running
// mix greys (a task in it retired or completed), Edit takes the glow until the editor is opened. While the queue holds a
// tap, "next: {task}" sits in whichever row is showing.
import type { Mix, View } from "../../api/types";
import { apportion, firstMixOffer, runningMix, withShares } from "../../game/mix";
import { handsRule, ruleRunning } from "../../game/orders";
import { editShown, mixesShown, runsShown, stripShown } from "../../game/shown";
import { nextCard } from "../../game/queue";
import { handsHolder, type Holder } from "../../game/holder";
import { spentNote } from "../../game/spent";
import { FIRST_MIX, guided } from "../../game/lessons";
import { UI } from "../../game/text";
import { ChipOffer } from "../story/chipoffer";
import { LaneRows } from "../town/lanerows";
import { PHONE } from "../layout";
import { RunningNow } from "../mixes/runningnow";
import { GlowWhile } from "../feedback/fresh";
import { markStopped, markSwitch } from "./handsmarks";
import { letGo, tapBar, thenWords } from "./handsheld";
import { el, setText, tapFeedback } from "../dom";
import type { Part, PartContext } from "../part";
import { ShareBar, type SegmentSpec } from "../mixes/sharebar";

export function segmentSpecs(ctx: PartContext, mix: Mix, view: View | null): SegmentSpec[] {
  const { catalog } = ctx;
  return mix.components.map((c) => c.kind === "card_share"
    ? { key: `c:${c.card}`, label: catalog.cardLabel(c.card), hue: catalog.rank(c.card), struck: view !== null && !view.cards.some((v) => v.card === c.card) }
    : { key: `m:${c.mix_id}`, label: c.mix_id, hue: 5 });
}

/** The strip's bar for a mix: a retired or completed card the mix still holds is not drawn, and its share goes to the
 * cards left in proportion (the engine keeps it in the greyed mix; the strip shows what is left of it). */
function stripBar(specs: SegmentSpec[], shares: number[], total: number): { specs: SegmentSpec[]; shares: number[] } {
  const live = specs.map((s, i) => i).filter((i) => specs[i]?.struck !== true);
  return { specs: live.map((i) => specs[i] as SegmentSpec), shares: apportion(live.map((i) => shares[i] ?? 0), total) };
}

export class Hands implements Part {
  readonly root = el("section", "hands");
  /** A row per lane run by rules, drawn under the strip (the screen places its root). */
  readonly lanes: LaneRows;
  /** A phone's mix controls and chip rule offer, under the pinned strip and scrolling with the cards (the screen places
   * its root); on a wider screen they sit in the strip. */
  readonly rows = el("div", "hands-rows");
  private readonly label = el("span", "hands-label");
  private readonly text = el("span", "hands-text");
  private readonly offer = el("div", "hands-offer");
  private readonly mixRow = el("div", "hands-mix");
  private readonly barRow = el("div", "hands-bar-row");
  private readonly name = el("button", "hands-name");
  private readonly nameText = el("span", "hands-mix-name");
  private readonly plan = el("button", "hands-name hands-plan");
  private readonly runs = el("span", "hands-runs");
  /** Where the running rule or goal stint lets go, as a way into the Rules tab, where Lately says what the rules did. */
  private readonly until = el("button", "hands-rule");
  /** What a rule's or a stint's mix gives the hands back to. */
  private readonly then = el("span", "hands-then");
  private readonly taskRule = el("button", "hands-rule");
  private readonly status = el("span", "hands-status");
  private readonly edit = el("button", "hands-edit");
  private readonly next = el("span", "hands-next");
  private readonly meta = el("div", "hands-meta");
  private readonly handsRow = el("div", "hands-row");
  private readonly bar: ShareBar;
  /** The split that runs now, under the bar while a card of the mix is stopped. */
  private readonly now: RunningNow;
  private readonly ruleOffer: ChipOffer;
  private readonly editGlow: GlowWhile;
  private view: View | null = null;
  private mix: Mix | null = null;
  private holder: Holder = { kind: "own" };
  private offerKey = "";
  /** The strip, and each of the mix row's Edit, Mixes ▾ and "runs …", has been drawn this page session: it stays. */
  private arrived = false;
  private editSeen = false;
  private mixesSeen = false;
  private runsSeen = false;

  constructor(private readonly ctx: PartContext, changed: () => void = () => undefined) {
    const { catalog } = ctx;
    const { text } = catalog;
    setText(this.label, catalog.laneLabel("hands"));
    this.bar = new ShareBar("slim", catalog.content.scales.bp, (bp) => catalog.format.share(bp), {
      moving: (_, d) => this.ctx.actions.highlight(d < 0 ? null : this.neighbours(d)),
      commit: (shares) => {
        this.ctx.actions.highlight(null);
        if (this.mix && !this.view?.greyed_mix_ids.includes(this.mix.id)) this.ctx.actions.decide({ kind: "save_mix", mix: withShares(this.mix, shares) });
      },
    });
    this.name.type = "button";
    this.name.dataset.teach = "mixes";   // a lesson's mark of the way to the list
    this.plan.type = "button";
    this.edit.type = "button";
    setText(this.edit, text.get(UI.edit));
    this.edit.addEventListener("click", () => { tapFeedback(); this.ctx.actions.editMix(null); });
    this.name.addEventListener("click", () => { tapFeedback(); this.ctx.actions.openSelector(); });
    this.plan.addEventListener("click", () => {
      tapFeedback();
      if (this.view?.mixes.length) this.ctx.actions.openSelector();
      else this.ctx.actions.openRules(null);
    });
    for (const b of [this.until, this.taskRule]) {
      b.type = "button";
      b.hidden = true;
      b.dataset.teach = "rule-running";
      b.addEventListener("click", () => { tapFeedback(); this.ctx.actions.openRules(null); });
    }
    this.meta.append(this.name, this.nameText, this.runs, this.until, this.then, this.status, this.edit);
    this.barRow.append(this.bar.root);
    this.mixRow.append(this.barRow, this.meta);
    this.handsRow.append(this.text, this.taskRule, this.plan);
    this.ruleOffer = new ChipOffer(ctx);
    this.lanes = new LaneRows(ctx, changed);
    this.now = new RunningNow(ctx, "hands");
    this.editGlow = new GlowWhile(ctx.glow, this.edit);
    const body = el("div", "hands-body");
    body.append(this.handsRow, this.offer, this.mixRow, this.now.root);
    const phone = window.matchMedia(PHONE);
    const seat = (): void => {
      if (phone.matches) this.barRow.append(this.nameText, this.name);
      else this.meta.prepend(this.name, this.nameText);
      (phone.matches ? this.rows : this.mixRow).append(this.meta);
      (phone.matches ? this.rows : body).append(this.ruleOffer.root);
      if (this.mix) this.drawName(this.mix.id);
    };
    phone.addEventListener("change", seat);
    seat();
    this.root.append(this.label, body);
    this.root.hidden = true;
  }

  update(view: View, prev: View | null = null): void {
    this.view = view;
    if (!this.arrived && stripShown(this.ctx.catalog, view)) {
      this.arrived = true;
      this.root.hidden = false;
      this.ctx.arrivals.arrive(this.root, "feature", "hands");
    }
    this.ruleOffer.update(view);
    this.lanes.update(view, prev);
    this.now.update(view);
    const mix = runningMix(view);
    const offer = mix ? null : firstMixOffer(view, this.ctx.catalog);
    this.text.hidden = mix !== null || offer !== null;
    this.plan.hidden = mix !== null || offer !== null || (view.mixes.length === 0 && view.orders.length === 0);
    setText(this.plan, `${this.ctx.catalog.text.get(view.mixes.length > 0 ? UI.mixesHeading : UI.ordersHeading)} ▾`);
    this.offer.hidden = offer === null;
    this.mixRow.hidden = this.meta.hidden = mix === null;
    this.root.dataset.state = mix ? "mix" : offer ? "offer" : "hands";
    if (offer) this.drawOffer(offer);
    const switchEdit = markSwitch(this.ctx, view, mix !== null, { name: this.name, plan: this.plan, edit: this.edit });
    this.editGlow.update(mix !== null && view.greyed_mix_ids.includes(mix.id));
    this.drawNext(view, mix !== null);
    if (!mix) {
      this.mix = null;
      this.drawHands(view);
      return;
    }
    this.mix = mix;
    this.taskRule.hidden = true;
    this.holder = handsHolder(view);
    const tapped = this.holder.kind === "tap";
    const greyed = view.greyed_mix_ids.includes(mix.id);
    this.drawMeta(view, switchEdit);
    this.drawBar(view.at);
    for (const n of [this.root, this.rows]) {
      n.classList.toggle("greyed", greyed && !tapped);
      n.classList.toggle("tapped", tapped);
    }
    markStopped(this.ctx, mix, view, greyed, this.edit);
    setText(this.status, tapped ? "" : greyed ? this.stopped(mix, view) : spentNote(this.ctx.catalog, view));
    setText(this.then, tapped ? "" : thenWords(this.ctx, view, this.holder));
    this.then.title = this.then.textContent ?? "";
    this.then.hidden = this.then.title === "";
    this.drawName(mix.id);
  }

  /** The bar: a holding tap's card with its time left at `t`, else the running mix's split. */
  private drawBar(t: number): void {
    const { holder: h, mix } = this;
    if (!mix) return;
    const bar = h.kind === "tap" ? tapBar(this.ctx, h.card, h.endsAt, t)
      : stripBar(segmentSpecs(this.ctx, mix, this.view), mix.components.map((c) => c.share_bp), this.ctx.catalog.content.scales.bp);
    this.bar.set(bar.specs, bar.shares);
  }

  /** The running mix's name as text, or while a tap holds the hands "then {mix}"; on a phone, once a mix is saved, it
   * is itself the way to the Mixes list ("Main ▾"), where elsewhere "Mixes ▾" sits before it. */
  private drawName(id: string): void {
    const phone = window.matchMedia(PHONE).matches;
    const label = this.holder.kind === "tap" && this.view ? thenWords(this.ctx, this.view, this.holder) || id : id;
    setText(this.nameText, label);
    this.nameText.title = label;
    setText(this.name, `${phone ? label : this.ctx.catalog.text.get(UI.mixesHeading)} ▾`);
    this.nameText.hidden = phone && this.mixesSeen;
  }

  /** The mix row's controls that have come: Edit (or wherever the switch cue points it), Mixes ▾, "runs …" (tick). */
  private drawMeta(view: View, switchEdit: boolean): void {
    const { catalog } = this.ctx;
    this.editSeen ||= editShown(catalog, view);
    this.mixesSeen ||= mixesShown(view);
    this.runsSeen ||= runsShown(catalog, view);
    this.edit.hidden = !this.editSeen && !switchEdit;
    this.name.hidden = !this.mixesSeen;
  }

  /** Why a greyed mix runs nothing: the first card it holds that is no longer in play, or the greyed mix it nests. */
  private stopped(mix: Mix, view: View): string {
    const { catalog } = this.ctx;
    const gone = mix.components.find((c) => (c.kind === "card_share" ? !view.cards.some((v) => v.card === c.card) : view.greyed_mix_ids.includes(c.mix_id)));
    const name = gone === undefined ? "" : gone.kind === "card_share" ? catalog.cardLabel(gone.card) : gone.mix_id;
    return catalog.text.fill(UI.stopped, { card: name });
  }

  private byRule(order: View["orders"][number]): string {
    return ruleRunning(this.ctx.catalog, order);
  }

  /** The editor was opened (from here or elsewhere): Edit's glow has done its job. */
  editorOpened(): void {
    this.editGlow.used();
  }

  tick(t: number): void {
    this.lanes.tick(t);
    this.editGlow.tick();
    const view = this.view;
    if (!view || !this.mix) return;
    const tapped = this.holder.kind === "tap";
    const live = !tapped && !view.greyed_mix_ids.includes(this.mix.id);
    const where = letGo(this.ctx, view, this.holder);
    this.runs.hidden = where !== null || tapped || !this.runsSeen;
    this.until.hidden = where === null;
    setText(this.until, where ?? "");
    setText(this.runs, live && where === null ? this.ctx.catalog.format.runs(view.runs_out_at, t) : "");
    if (tapped) this.drawBar(t);
  }

  private drawHands(view: View): void {
    const lane = view.lanes.find((l) => l.lane === "hands");
    const running = lane?.running_card ?? null;
    for (const n of [this.root, this.rows]) n.classList.remove("greyed", "yielded");
    this.text.classList.toggle("idle", running === null);
    const index = handsRule(view);
    const rule = view.orders[index];
    setText(this.text, running ? this.ctx.catalog.cardLabel(running) : this.ctx.catalog.text.get(UI.handsIdle));
    this.taskRule.hidden = !rule || this.text.hidden;
    setText(this.taskRule, rule ? `· ${this.byRule(rule)}` : "");
  }

  /** The queue's head, in the row that shows: after the mix's meta, or after what the hands do. */
  private drawNext(view: View, mixShown: boolean): void {
    const card = nextCard(view);
    const { catalog } = this.ctx;
    setText(this.next, card ? catalog.text.fill(UI.handsNext, { card: catalog.cardLabel(card) }) : "");
    this.next.hidden = card === null;
    const row = mixShown ? this.meta : this.handsRow;
    if (this.next.parentElement !== row) row.insertBefore(this.next, mixShown ? this.edit : null);   // Edit stays last
  }

  private drawOffer(ids: string[]): void {
    const guide = guided(FIRST_MIX, this.view!, this.ctx.keeps);   // the mix's lesson: built on the editor, not in one tap
    const key = `${ids.join("|")}|${guide}`;
    if (key === this.offerKey) return;
    this.offerKey = key;
    const { catalog } = this.ctx;
    const names = el("span", "offer-names");
    ids.forEach((id, i) => {
      if (i > 0) names.append(el("span", "offer-plus", "+"));
      names.append(el("span", `offer-name hue-${catalog.rank(id) % 6}`, catalog.cardLabel(id)));
    });
    const both = el("button", guide ? "offer-both lesson-go" : "offer-both", catalog.text.get(guide ? UI.lessonShow : UI.newMix));
    both.type = "button";
    if (guide) Object.assign(both.dataset, { teach: "mix-offer", cards: ids.join(" ") });
    both.addEventListener("click", () => { tapFeedback(); this.ctx.actions.newMix(null); });   // nothing is built: the editor opens, the lesson walks it
    this.offer.replaceChildren(names, both);
    if (!guide) this.ctx.glow.offer(both);   // guided, the lesson places the glow
  }

  private neighbours(divider: number): string[] {
    return (this.mix?.components ?? []).slice(divider, divider + 2).flatMap((c) => (c.kind === "card_share" ? [c.card] : []));
  }
}
