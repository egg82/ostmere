// A person's split on their page (personpage.ts): the hands' ShareBar over the cards that hold a share of their time, the
// last divider against the idle rest. The town's mix holds every person's shares; this edits one person's and sends the
// mix as it is made, with no Save (contract/the-towns-mix.txt, "The town's mix"; game/town.ts). A card joins or leaves by a tap on its
// face on the page, `toggle`; nothing moves a share from one person to another. While a one-off holds the person's lane the
// bar is that card alone with its time left and "then {split}" under it, as the hands strip draws a tap (handsheld.ts).
// Under it, the stores the person's cards make or cost (storetimes.ts): what each holds of its cap, its rate now and where
// it heads; while a divider is held, now → after from a dry run of the split under the finger, as the hands' editor reads.
import type { Decision, Mix, View } from "../api/types";
import { laneOneOff } from "../game/holder";
import { UI } from "../game/text";
import { crewOf, dropTownCard, given, joinTownCard, soloOf, townEdit, townSaveDecisions, withTownShares } from "../game/town";
import { el, setText } from "./dom";
import { MixPreview } from "./mixpreview";
import { storeRows, touchedBy } from "./storetimes";
import { tapBar } from "./handsheld";
import type { PartContext } from "./part";
import { ShareBar, type SegmentSpec } from "./sharebar";
import { thenSplit } from "./townsplit";

export class PersonMix {
  readonly root = el("section", "person-mix");
  private readonly bar: ShareBar;
  private readonly then = el("span", "hands-then person-then");
  /** A group's page: how many free members each share is of, beside the split. */
  private readonly each = el("span", "hands-then person-each");
  private view: View | null = null;
  private lane = "";
  /** A divider is held: a new view waits for the let-go, so the bar under the finger is not rebuilt. */
  private held = false;
  /** The stores the person's cards make or cost, each with what it holds of its cap, its rate now → after and where it
   * heads (storetimes.ts); the after is a dry run of the split under the finger, none at rest. */
  private readonly stores = el("div", "editor-totals person-stores");
  private dragged: number[] | null = null;
  private after: View | null = null;
  private readonly preview = new MixPreview(() => this.previewDecisions(), (ds) => this.ctx.actions.dryRun(ds), (after) => {
    this.after = this.dragged ? after : null;
    this.drawStores();
  });

  constructor(private readonly ctx: PartContext) {
    const { catalog } = ctx;
    this.bar = new ShareBar("large town-bar", catalog.content.scales.bp, (bp) => catalog.format.share(bp), {
      moving: (shares, d) => {
        this.held = d >= 0;
        this.dragged = this.held ? [...shares] : null;
        if (this.held) this.preview.schedule();
        else this.draw();
      },
      commit: (shares) => {
        this.held = false;
        this.dragged = null;
        this.after = null;
        this.drawStores();
        this.send(withTownShares(catalog, this.edited().mix, this.lane, shares));
      },
    });
    this.then.hidden = true;
    this.root.append(this.bar.root, this.each, this.then, this.stores);
  }

  /** The mix this page edits: the town's, else a new one a save points the town's always rule at; a card the view no
   * longer has is not in it. */
  private edited(): { mix: Mix; isNew: boolean } {
    const view = this.view as View;
    return townEdit(this.ctx.catalog, view, this.ctx.catalog.townTitle(view));
  }

  private send(next: Mix | null): void {
    if (!next || !this.view) return;
    for (const d of townSaveDecisions(this.view, next, this.edited().isNew)) this.ctx.actions.decide(d);
  }

  /** The person's cards that hold a share, with the share, as the mix has them (after `show`). */
  shares(): Map<string, number> {
    return new Map(this.edited().mix.components.flatMap((c) => (c.kind === "card_share" && this.ctx.catalog.laneOf(c.card) === this.lane ? [[c.card, c.share_bp] as const] : [])));
  }

  /** Draws the bar for `lane` as of `view`. */
  show(view: View, lane: string): void {
    this.view = view;
    this.lane = lane;
    if (!this.held) this.draw();
  }

  /** A holding one-off's bar moves on with the clock: its time left. */
  tick(t: number): void {
    const view = this.view;
    const tap = view && laneOneOff(view, this.lane);
    if (tap && !this.held) {
      const bar = tapBar(this.ctx, tap.card, tap.endsAt, t);
      this.bar.set(bar.specs, bar.shares);
    }
  }

  private draw(): void {
    const { catalog } = this.ctx;
    const view = this.view as View;
    const tap = laneOneOff(view, this.lane);
    const pooled = catalog.lanes.get(this.lane)?.pooled === true;
    const crew = pooled ? crewOf(catalog, view, this.lane) : null;
    this.each.hidden = !pooled;
    setText(this.each, !pooled ? "" : crew === null || crew === 0 ? catalog.text.get(UI.townBusy) : catalog.text.fill(UI.townEach, { n: String(crew) }));
    setText(this.then, tap ? thenSplit(this.ctx, view, this.lane) : "");
    this.then.hidden = tap === null;
    if (!this.held) this.drawStores();
    if (tap) {
      this.tick(view.at);
      return;
    }
    const { mix } = this.edited();
    const label = catalog.laneLabel(soloOf(catalog, view, this.lane) ?? this.lane, view);
    const cards = mix.components.flatMap((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === this.lane ? [c] : []));
    const specs: SegmentSpec[] = cards.map((c) => ({ key: c.card, label: catalog.cardLabel(c.card), hue: catalog.rank(c.card) }));
    specs.push({ key: `idle:${this.lane}`, label: catalog.text.fill(UI.townIdle, { person: label }), hue: 5, idle: true });   // always there, so a full person has a divider to drag down
    this.bar.set(specs, [...cards.map((c) => c.share_bp), catalog.content.scales.bp - given(catalog, mix, this.lane)]);
  }

  /** The split under the finger as a dry run sends it; null at rest. */
  private previewDecisions(): Decision[] | null {
    if (!this.dragged || !this.view) return null;
    const { mix, isNew } = this.edited();
    return townSaveDecisions(this.view, withTownShares(this.ctx.catalog, mix, this.lane, this.dragged), isNew);
  }

  private drawStores(): void {
    const view = this.view;
    if (!view) return;
    const { catalog } = this.ctx;
    const touched = touchedBy(catalog, this.shares().keys());
    this.stores.classList.toggle("at-rest", this.after === null);   // no edit under the finger: the now column alone
    this.stores.replaceChildren(...storeRows(catalog, view, this.after ?? view, catalog.text.get(UI.after), touched));
  }

  /** A tap on `card`'s face: it joins the person's time, or leaves it. */
  toggle(card: string): void {
    if (!this.view) return;
    const { mix } = this.edited();
    const held = mix.components.some((c) => c.kind === "card_share" && c.card === card);
    this.send(held ? dropTownCard(mix, card) : joinTownCard(this.ctx.catalog, mix, card));
  }
}
