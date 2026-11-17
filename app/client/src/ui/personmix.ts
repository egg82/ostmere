// A person's split on their page (personpage.ts): the hands' ShareBar over the cards that hold a share of their time, the
// last divider against the idle rest. The town's mix holds every person's shares; this edits one person's and sends the
// mix as it is made, with no Save (CONTRACT.txt, "The town's mix"; game/town.ts). A card joins or leaves by a tap on its
// face on the page, `toggle`; nothing moves a share from one person to another.
import type { Mix, View } from "../api/types";
import { UI } from "../game/text";
import { dropTownCard, given, joinTownCard, newTownMix, townMixToEdit, townSaveDecisions, withTownShares } from "../game/town";
import { el } from "./dom";
import type { PartContext } from "./part";
import { ShareBar, type SegmentSpec } from "./sharebar";

export class PersonMix {
  readonly root = el("section", "person-mix");
  private readonly bar: ShareBar;
  private view: View | null = null;
  private lane = "";
  /** A divider is held: a new view waits for the let-go, so the bar under the finger is not rebuilt. */
  private held = false;

  constructor(private readonly ctx: PartContext) {
    const { catalog } = ctx;
    this.bar = new ShareBar("large town-bar", catalog.content.scales.bp, (bp) => catalog.format.share(bp), {
      moving: (_shares, d) => {
        this.held = d >= 0;
        if (!this.held) this.draw();
      },
      commit: (shares) => {
        this.held = false;
        this.send(withTownShares(catalog, this.edited().mix, this.lane, shares));
      },
    });
    this.root.append(this.bar.root);
  }

  /** The mix this page edits: the town's, else a new one a save points the town's always rule at; a card the view no
   * longer has is not in it. */
  private edited(): { mix: Mix; isNew: boolean } {
    const view = this.view as View;
    const found = townMixToEdit(this.ctx.catalog, view);
    const mix = structuredClone(found ?? newTownMix(view, this.ctx.catalog.text.get(UI.townTitle)));
    mix.components = mix.components.filter((c) => c.kind !== "card_share" || view.cards.some((v) => v.card === c.card));
    return { mix, isNew: found === null };
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

  private draw(): void {
    const { catalog } = this.ctx;
    const { mix } = this.edited();
    const label = catalog.laneLabel(this.lane, this.view as View);
    const cards = mix.components.flatMap((c) => (c.kind === "card_share" && catalog.laneOf(c.card) === this.lane ? [c] : []));
    const specs: SegmentSpec[] = cards.map((c) => ({ key: c.card, label: catalog.cardLabel(c.card), hue: catalog.rank(c.card) }));
    specs.push({ key: `idle:${this.lane}`, label: catalog.text.fill(UI.townIdle, { person: label }), hue: 5, idle: true });   // always there, so a full person has a divider to drag down
    this.bar.set(specs, [...cards.map((c) => c.share_bp), catalog.content.scales.bp - given(catalog, mix, this.lane)]);
  }

  /** A tap on `card`'s face: it joins the person's time, or leaves it. */
  toggle(card: string): void {
    if (!this.view) return;
    const { mix } = this.edited();
    const held = mix.components.some((c) => c.kind === "card_share" && c.card === card);
    this.send(held ? dropTownCard(mix, card) : joinTownCard(this.ctx.catalog, mix, card));
  }
}
