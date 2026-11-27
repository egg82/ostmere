// A person's time as the town draws it (townstrip.ts): a bar split into the cards that hold a share and the
// idle rest, each part as wide as its share, and under it a key naming each part with its share, so a narrow part's name
// is never cut off on a phone. While a one-off holds the person's lane, the bar is that card alone (heldSplit), as the hands
// strip draws a tap (handsheld.ts).
import type { View } from "../../api/types";
import { UI } from "../../game/text";
import { personOf } from "../../game/town";
import { el } from "../dom";
import type { PartContext } from "../part";

export interface Part { text: string; bp: number; hue: number; idle: boolean }

export function splitOf(parts: Part[]): { bar: HTMLElement; key: HTMLElement } {
  const bar = el("div", "town-shares");
  const key = el("div", "town-key");
  for (const p of parts) {
    const seg = el("span", `town-seg hue-${p.hue}${p.idle ? " idle" : ""}`);
    seg.style.flexGrow = String(p.bp);
    bar.append(seg);
    key.append(el("span", `town-key-item hue-${p.hue}${p.idle ? " idle" : ""}`, p.text));
  }
  return { bar, key };
}

/** The person's split as parts: each card that holds a share, then the idle rest. `who`: the lane whose label names the idle
 * part, the group's own member while a group is one person's. */
export function splitParts(ctx: PartContext, view: View, lane: string, who = lane): Part[] {
  const { catalog } = ctx;
  const person = personOf(catalog, view, lane);
  const parts: Part[] = person.shares.map((s) => ({ text: `${catalog.cardLabel(s.card)} ${catalog.format.share(s.bp)}`, bp: s.bp, hue: catalog.rank(s.card) % 6, idle: false }));
  if (person.idleBp > 0) parts.push({ text: `${catalog.text.fill(UI.townIdle, { person: catalog.laneLabel(who, view) })} ${catalog.format.share(person.idleBp)}`, bp: person.idleBp, hue: 5, idle: true });
  return parts;
}

/** "then {split}": what the person goes back to once the tap holding their lane lands, their shares (idle when they
 * have none). */
export function thenSplit(ctx: PartContext, view: View, lane: string, who = lane): string {
  return ctx.catalog.text.fill(UI.handsThen, { mix: splitWords(ctx, view, lane, who) });
}

/** The split in words: the cards that hold a share, each with it (all of the parts when none does). */
export function splitWords(ctx: PartContext, view: View, lane: string, who = lane): string {
  const parts = splitParts(ctx, view, lane, who);
  const working = parts.filter((p) => !p.idle);
  return (working.length > 0 ? working : parts).map((p) => p.text).join(", ");
}
