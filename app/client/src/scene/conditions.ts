// The scene manifest's conditions, read off the Views the page has been handed. Nothing here is a game rule: each
// condition is a field of the view. The manifest's `project:` and `pushes:` names predate cards and are kept as its
// spelling: both read a card's completions, from the card panel or the Completed tab.
import type { View } from "../api/types";
import { sample } from "../game/clock";

export class SceneFacts {
  private view: View | null = null;
  private dark = false;

  observe(view: View): void {
    this.view = view;
  }

  /** The grade the scene now shows is a dusk or a night one (the `dark` condition). */
  setDark(dark: boolean): void {
    this.dark = dark;
  }

  /**
   * always | null          shown from the start
   * project:<id>           the card completed at least once
   * pushes:<id>@<n>        the card completed at least n times
   * running:<id>           a lane is tapping it now
   * mix:<id>               the active mix is running it and it is its turn: the mix's cards run at once, but the
   *                        figure can be in one place, so the cards take turns at the figure, each for its share
   * store:<id>             the store holds at least one item, sampled at t: read off its ledger line, else off
   *                        view.levels (a store the page never lists: the hidden clocks)
   * store:<id>@<n>         the store holds at least n items, sampled at t
   * store:<id>@<a>..<b>    the store holds at least a items and fewer than b: a window of a count-up clock, so a moment
   *                        can start and end on one condition, whatever else is happening to the same person
   * dark                   the grade shown is a dusk or a night one (a manifest grade's `dark`), set by the scene
   * day                    the grade shown is not (`dark`'s opposite: a layer that gives way by day only)
   * end:showing            the end has happened (view.ended_at, which the end lines key on too; it never clears)
   * chip:<id>              the chip is showing
   * feature:<id>           the feature is unlocked
   * action:<id>            the standing action is unlocked (view.standing)
   * answered:<offer>      the offer has been answered, by any answer (view.unlocked, category "answered")
   * answer:<answer>        that answer was the one given (category "answer")
   * joined:<lane>         the lane's person has joined the town (category "joined")
   * left:<lane>           the lane's person has left the town for good (category "left")
   * <a>|<b>|...            any of them holds
   * <a>&<b>&...            all of them hold; binds tighter than |, so a&b|c is (a and b) or c
   */
  holds(condition: string | null | undefined, t: number, quantityPerItem: number): boolean {
    const view = this.view;
    if (!condition || condition === "always") return true;
    if (condition.includes("|")) return condition.split("|").some((c) => this.holds(c, t, quantityPerItem));
    if (condition.includes("&")) return condition.split("&").every((c) => this.holds(c, t, quantityPerItem));
    if (condition === "dark") return this.dark;
    if (condition === "day") return !this.dark;
    if (!view) return false;
    const [kind, rest = ""] = condition.split(":", 2);
    switch (kind) {
      case "project": return this.completions(rest) > 0;
      case "pushes": {
        const [card = "", n = "0"] = rest.split("@", 2);
        return this.completions(card) >= Number(n);
      }
      case "mix": return mixTurn(view, t) === rest;
      case "running": return view.lanes.some((l) => l.running_card === rest);
      case "store": {
        const [store, n = "1"] = rest.split("@", 2);
        const [lo = "1", hi] = n.split("..", 2);
        const segment = (view.ledger.find((l) => l.store === store) ?? view.levels.find((l) => l.store === store))?.segment;
        if (segment === undefined) return false;
        const held = sample(segment, t);
        return held >= Number(lo) * quantityPerItem && (hi === undefined || held < Number(hi) * quantityPerItem);
      }
      case "end": return rest === "showing" && view.ended_at !== null;
      case "chip": return view.chips.includes(rest);
      case "feature": return view.unlocked.some((u) => u.category === "feature" && u.id === rest);
      case "answered":
      case "answer":
      case "joined":
      case "left": return view.unlocked.some((u) => u.category === kind && u.id === rest);
      case "action": return view.standing.some((a) => a.action === rest);
      default: return unknown(condition);
    }
  }

  private completions(card: string): number {
    const view = this.view;
    const found = view?.cards.find((c) => c.card === card) ?? view?.completed.find((c) => c.card === card);
    return found?.completions ?? 0;
  }
}

/** Game seconds one round of turns takes: each running mix card holds the figure for its share of it. */
export const TURN_ROUND_S = 30;

/** The mix card holding the figure at game time t, or null when no card is running by the mix. */
export function mixTurn(view: View, t: number): string | null {
  const running = view.cards.filter((c) => c.by === "mix" && c.share_bp > 0);
  const total = running.reduce((sum, c) => sum + c.share_bp, 0);
  if (total === 0) return null;
  let at = (((t % TURN_ROUND_S) + TURN_ROUND_S) % TURN_ROUND_S) / TURN_ROUND_S * total;
  for (const c of running) {
    if (at < c.share_bp) return c.card;
    at -= c.share_bp;
  }
  return running[running.length - 1]?.card ?? null;
}

const warned = new Set<string>();

function unknown(condition: string): boolean {
  if (!warned.has(condition)) console.warn(`ashfall: scene condition "${condition}" is not one the page knows`);
  warned.add(condition);
  return false;
}
