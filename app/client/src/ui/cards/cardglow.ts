import type { View } from "../../api/types";
import type { Catalog } from "../../game/page/catalog";
import { glowTarget } from "../../game/ledger/cues";
import { inUse } from "../../game/lessons/marks";
import type { Glow } from "../feedback/fresh";

/** The glow goes on a card the content marks, the first time it is ready with its lane free, while nothing else
 * has it but the shown ask (which yields it: GlowRank); once per card, and never on one already put to work or done (glowTarget). A card put to work by a mix, a
 * rule or the queue loses it, as a click does (fresh.ts). */
export class CardGlow {
  private readonly glowed = new Set<string>();

  constructor(private readonly catalog: Catalog, private readonly glow: Glow, private readonly node: (card: string) => HTMLElement | undefined) {}

  place(view: View): void {
    for (const card of inUse(view)) {
      const node = this.glowed.has(card) ? this.node(card) : undefined;
      if (node) this.glow.clear(node);
    }
    const card = glowTarget(this.catalog, view, this.glowed);
    const node = card ? this.node(card) : undefined;
    if (card && node && this.glow.offer(node, { outranks: true })) this.glowed.add(card);
  }
}
