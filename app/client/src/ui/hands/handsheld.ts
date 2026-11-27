// The hands strip's words and bar for what holds the hands (game/hands/holder.ts; docs/design/opening-screen/hands-strip.md, "The hands
// strip"): a tap is drawn as one full segment in its card's hue, its legend naming the card and its time left; a rule
// and a goal stint each say where they let go, and every holder names the mix the hands go back to.
import type { View } from "../../api/types";
import type { Holder } from "../../game/hands/holder";
import { mixLabel, ruleRunning } from "../../game/rules/orders";
import { stintRow } from "../../game/mixes/queue";
import { UI } from "../../game/page/text";
import { goalLabel } from "../mixes/goaltimes";
import type { PartContext } from "../part";
import type { SegmentSpec } from "../mixes/sharebar";
import { untilLabel } from "../next/stint";

/** A tap's bar at `t`: the card alone, the whole bar, its time left in the legend while it has an end. */
export function tapBar(ctx: PartContext, card: string, endsAt: number | null, t: number): { specs: SegmentSpec[]; shares: number[] } {
  const { catalog } = ctx;
  const note = endsAt === null ? undefined : catalog.format.duration(endsAt - t);
  return { specs: [{ key: `t:${card}`, label: catalog.cardLabel(card), hue: catalog.rank(card), note }], shares: [catalog.content.scales.bp] };
}

/** Where the holder lets go: the rule's "until …" (also for a rule's tap), the stint's goal; null for the player's mix
 * and a tap no rule makes. */
export function letGo(ctx: PartContext, view: View, holder: Holder): string | null {
  const { catalog } = ctx;
  const order = holder.kind === "rule" || holder.kind === "tap" ? holder.order : null;
  const rule = order === null ? undefined : view.orders[order];
  if (rule) return ruleRunning(catalog, rule);
  const entry = holder.kind === "stint" ? view.queue[holder.entry] : undefined;
  if (!entry) return null;
  const row = stintRow(view, entry.until);
  return catalog.text.fill(UI.handsUntilGoal, { goal: row ? goalLabel(catalog, row) : untilLabel(catalog, entry.until) });
}

/** "then {mix}": the mix the hands go back to, or "" when nothing holds them or nothing else comes back. */
export function thenWords(ctx: PartContext, view: View, holder: Holder): string {
  const back = holder.kind === "own" ? null : holder.then;
  return back === null ? "" : ctx.catalog.text.fill(UI.handsThen, { mix: mixLabel(ctx.catalog, view, back) });
}
