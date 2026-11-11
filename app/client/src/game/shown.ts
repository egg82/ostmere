// What of the view the page draws yet (decisions.md, "The screen arrives when it means something";
// docs/design/opening-screen.md). The view says what exists; these say when its part of the screen first means
// something to the player, read off the view and the content only, so a reload draws the same.
import type { AimInfo, LedgerLine, View } from "../api/types";
import type { Catalog } from "./catalog";
import { sample } from "./clock";

/** The chips the band draws: those on whose ChipInfo.offered_after, if any, view.unlocked holds (its cure is on screen). */
export function shownChips(catalog: Catalog, view: View): string[] {
  return view.chips.filter((id) => drawable(catalog, view, id));
}

/** The chips the band has drawn at some time in the save: seen (View.chips_seen), their offered_after held. */
export function seenChips(catalog: Catalog, view: View): string[] {
  return view.chips_seen.filter((id) => drawable(catalog, view, id));
}

function drawable(catalog: Catalog, view: View, id: string): boolean {
  const after = catalog.chips.get(id)?.offered_after ?? null;
  return after === null || catalog.unlocked(view, after.category, after.id);
}

/** The aim the band's top states: the last of Content.aim_infos whose `after` view.unlocked holds (the first has none,
 * so content with aims always has one). */
export function currentAim(catalog: Catalog, view: View): AimInfo | null {
  const set = catalog.content.aim_infos.filter((a) => a.after === null || catalog.unlocked(view, a.after.category, a.after.id));
  return set[set.length - 1] ?? null;
}

/** The hands strip: from the first mix's offer on (its feature unlocked), or once a mix or rule exists. */
export function stripShown(catalog: Catalog, view: View): boolean {
  return catalog.unlocked(view, "feature", catalog.content.first_mix.feature) || view.mixes.length > 0 || view.orders.length > 0;
}

/** The strip's Edit: once a mix greys, or once an action card on the hands is in play that the first mix does not
 * hold (a new task the mix could take). */
export function editShown(catalog: Catalog, view: View): boolean {
  const first = new Set(catalog.content.first_mix.card_ids);
  return view.greyed_mix_ids.length > 0
    || view.cards.some((c) => catalog.cards.get(c.card)?.presentation === "action" && catalog.mixable(c.card) && !first.has(c.card));
}

/** The strip's Mixes ▾: once a mix is saved (the list, and its New mix, are otherwise unreachable). */
export function mixesShown(view: View): boolean {
  return view.mixes.length >= 1;
}

/** The strip's "runs …": a ledger fact, so it comes with the ledger. */
export function runsShown(catalog: Catalog, view: View): boolean {
  return catalog.unlocked(view, "feature", LEDGER_FEATURE);
}

/** The feature that brings the ledger in (with the fire). */
export const LEDGER_FEATURE = "ledger";

/** The store is full and something still feeds it, at `t`. */
export function fullAndFed(line: LedgerLine, t: number): boolean {
  const fed = line.contributions.reduce((a, c) => a + c.per_hour, 0);
  return line.cap > 0 && sample(line.segment, t) >= line.cap && fed > 0;
}

/** The line is red: starved, or falling with nothing covering it. */
export function redLine(line: LedgerLine): boolean {
  return line.starved || (line.falling && !line.covered);
}

/** Something other than the hands' passing tap draws the store down. */
export function drawnDown(line: LedgerLine, view: View): boolean {
  const tapped = view.lanes.find((l) => l.lane === "hands")?.running_card ?? null;
  return line.falling && line.contributions.some((c) => c.per_hour < 0 && c.runner !== tapped);
}

/** A ledger line that asks something: starved, falling with nothing covering it, or carrying an offer (`offered`). */
export function lineAsks(line: LedgerLine, view: View, offered: boolean): boolean {
  return line.starved || (drawnDown(line, view) && !line.covered) || offered;
}

/** A ledger line that joins the ledger now: it asks something, or is falling, full while fed, or covered by a rule. */
export function lineJoins(line: LedgerLine, view: View, offered: boolean): boolean {
  return lineAsks(line, view, offered) || drawnDown(line, view) || fullAndFed(line, view.at) || line.covered;
}
