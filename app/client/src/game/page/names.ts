// The text table with its name slots filled (contract/text-and-numbers.txt, "Text and numbers").
import type { Content } from "../../api/types";

/** The text table with every person's name slot and each find's `{found}` slot filled (contract/text-and-numbers.txt, "Text and
 * numbers", {<lane>}, {found}): the lane's name_key text, lowercased in a line as the lines' voice writes it; the
 * amount a find found, in whole items. Any other slot is left for fill(). */
export function named(content: Content): { table: Map<string, string>; names: Map<string, string>; lines: Set<string> } {
  const raw = new Map(content.text_entries.map((e) => [e.key, e.text]));
  const names = new Map(content.lane_infos.flatMap((l) => (l.name_key ? [[l.lane, raw.get(l.name_key) ?? ""] as const] : [])));
  const lines = new Set(content.line_infos.map((l) => l.key));
  const found = new Map(content.find_infos.map((f) => [f.line_key, String(Math.floor(f.quantity / content.scales.quantity_per_item))]));
  const fillNames = (key: string, text: string): string => text.replace(/\{(\w+)\}/g, (slot, lane: string) => {
    if (lane === "found") return found.get(key) ?? slot;
    const name = names.get(lane);
    if (name === undefined) return slot;
    return lines.has(key) ? name.toLowerCase() : name;
  });
  return { table: new Map([...raw].map(([key, text]) => [key, fillNames(key, text)])), names, lines };
}
