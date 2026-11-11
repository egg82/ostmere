// The stall: a player who keeps starting a card by hand never lets its store fall, so the store's order card (shown
// under a red line) never appears. Two hand-starts of the card in a row offer that card anyway. It is an offer the
// player can ignore, never a gate.
import type { OrderCard } from "../api/types";

export class HandStreak {
  private last: string | null = null;
  private count = 0;

  /** The player started this card by hand. */
  tap(card: string): void {
    this.count = card === this.last ? this.count + 1 : 1;
    this.last = card;
  }

  /** The player's last two hand-starts were this card. */
  twice(card: string): boolean {
    return this.last === card && this.count >= 2;
  }
}

/** Whether the order card starts the card the player has just started by hand twice in a row. */
export function stalled(streak: HandStreak, card: OrderCard): boolean {
  return card.then.kind === "tap_card" && streak.twice(card.then.card);
}
