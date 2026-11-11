import type { View } from "../api/types";
import type { Catalog } from "../game/catalog";
import { glowTarget } from "../game/cues";
import type { Glow } from "./fresh";

/** The glow goes on a card the content marks, the first time it is ready with its lane free, while nothing else
 * has it; once per card. */
export class CardGlow {
  private readonly glowed = new Set<string>();

  constructor(private readonly catalog: Catalog, private readonly glow: Glow, private readonly node: (card: string) => HTMLElement | undefined) {}

  place(view: View): void {
    const card = glowTarget(this.catalog, view, this.glowed);
    const node = card ? this.node(card) : undefined;
    if (card && node && this.glow.offer(node)) this.glowed.add(card);
  }
}
