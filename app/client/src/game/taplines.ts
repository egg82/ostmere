// Which story lines the player's own taps wrote (docs/design/opening-screen.md, "Cards"): those go on the card as well
// as the band. The server names the card that wrote a line however it was run (LogLine.card); only the page knows a
// tap was the player's rather than a rule's, so it remembers the cards it tapped until each tap ends (a failed tap ends
// at once).
import type { LogLine, View } from "../api/types";

const tapped = (view: View | null, card: string): boolean =>
  view?.cards.some((c) => c.card === card && c.by === "tap") ?? false;

export class TapLines {
  private readonly mine = new Set<string>();

  /** The player tapped this card (a tap_card decision is on its way). */
  tap(card: string): void {
    this.mine.add(card);
  }

  /** The card a line goes on: the one that wrote it, when the player's tap of it did; null: the band only. */
  cardOf(line: LogLine): string | null {
    return line.card !== null && this.mine.has(line.card) ? line.card : null;
  }

  /** After a step's lines are placed: a tap that has ended (tapped before, not now, or the step's failed tap) is
   * forgotten. */
  observe(view: View, prev: View | null, failed: string | null): void {
    for (const card of [...this.mine]) if (card === failed || (tapped(prev, card) && !tapped(view, card))) this.mine.delete(card);
  }
}

/** A failed tap's line is not stacked: a line of the card whose tap just failed (Step.failed_tap), identical to the
 * line before it, is dropped (`last`: the key of the line before the first). Story lines are never dropped. */
export function withoutRepeatedFails(lines: LogLine[], failed: string | null, last: string | undefined): LogLine[] {
  return lines.filter((line) => {
    const repeat = failed !== null && line.card === failed && line.key === last;
    last = line.key;
    return !repeat;
  });
}
