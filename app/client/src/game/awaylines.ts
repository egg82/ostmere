// Where each line a return brings goes (docs/design/opening-screen.md, "Coming back"): every story line that landed
// while the player was away plays on the band; a chip's on-line, which comes once per save, goes to the chronicle only; its
// off-lines, which can come every cycle while away, collapse to the chip's last change, and that one and a repeat
// task's lines go to the chronicle only too. Which line is which is read from explicit data, never the text: a chip's line
// keys (ChipInfo) with no writing card, and the writing card's cap.
import type { LogLine, View } from "../api/types";
import type { Catalog } from "./catalog";

/** Where one line goes: the band (taking its turn), the chronicle only, or nowhere (a chip's earlier change). */
export type Placement = "band" | "chronicle" | "none";

/** One placement per line, in order: a chip's on-line in the chronicle; its off-lines collapsed to its last change (none
 * when that is not an off-line or the chip shows now), kept for the chronicle only like a repeat task's. */
export function awayLines(catalog: Catalog, lines: LogLine[], view: View, prev: View | null): Placement[] {
  const chips = chipLines(catalog);
  const chipOf = (l: LogLine): { chip: string; on: boolean } | undefined => (l.card === null ? chips.get(l.key) : undefined);
  const last = new Map<string, LogLine>();
  for (const l of lines) {
    const c = chipOf(l);
    if (c) last.set(c.chip, l);
  }
  const repeats = new Set([...view.cards, ...(prev?.cards ?? [])].filter((c) => c.cap === null).map((c) => c.card));
  return lines.map((line) => {
    const c = chipOf(line);
    if (c) return c.on || (last.get(c.chip) === line && !view.chips.includes(c.chip)) ? "chronicle" : "none";
    return line.card !== null && repeats.has(line.card) ? "chronicle" : "band";
  });
}

function chipLines(catalog: Catalog): Map<string, { chip: string; on: boolean }> {
  const found = new Map<string, { chip: string; on: boolean }>();
  for (const c of catalog.content.chip_infos) {
    if (c.on_line_key) found.set(c.on_line_key, { chip: c.chip, on: true });
    if (c.off_line_key) found.set(c.off_line_key, { chip: c.chip, on: false });
  }
  return found;
}
