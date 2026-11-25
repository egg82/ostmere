// Where each line a return brings goes (docs/design/opening-screen.md, "Coming back"): every story line that landed
// while the player was away plays on the band; a chip's on-line, which comes once per save, goes to the chronicle only; its
// off-lines, which can come every cycle while away, collapse to the chip's last change, and that one and a repeat
// task's lines go to the chronicle only too. Which line is which is read from explicit data, never the text: a chip's line
// keys (ChipInfo) with no writing card, and the writing card's cap. A save's history restored on a later open places the
// lines that landed inside a kept return (Visit) the same way, as far as history can tell (pastLines).
import type { LogLine, View, Visit } from "../api/types";
import type { Catalog } from "./catalog";
import type { Past } from "./chronicle";

/** Where one line goes: the band (taking its turn), the chronicle only, or nowhere (a chip's earlier change). */
export type Placement = "band" | "chronicle" | "none";

/** One placement per line, in order: a chip's on-line in the chronicle; its off-lines collapsed to its last change (none
 * when that is not an off-line or the chip shows now), kept for the chronicle only like a repeat task's. */
export function awayLines(catalog: Catalog, lines: LogLine[], view: View, prev: View | null): Placement[] {
  const chipped = chipPlaces(catalog, lines, (chip) => view.chips.includes(chip));
  const repeats = new Set([...view.cards, ...(prev?.cards ?? [])].filter((c) => c.cap === null).map((c) => c.card));
  return lines.map((line, i) => chipped[i] ?? (line.card !== null && repeats.has(line.card) ? "chronicle" : "band"));
}

/** One placement per restored line: a line inside a kept return as awayLines placed it, every other line on the band as
 * it was shown live. History keeps no card and no view of the return's end, so a repeat task's line there is on the
 * band, and a chip's last off-line there is kept whether or not the chip showed again by the return's end. */
export function pastLines(catalog: Catalog, past: readonly Past[], visits: readonly Visit[]): Placement[] {
  const placed: Placement[] = past.map(() => "band");
  for (const v of visits) {
    const inside = past.flatMap((p, i) => (p.at > v.left && p.at <= v.back ? [i] : []));
    const chipped = chipPlaces(catalog, inside.map((i) => ({ key: past[i]!.key, card: null })), () => false);
    inside.forEach((i, j) => { placed[i] = chipped[j] ?? "band"; });
  }
  return placed;
}

/** A chip's line's placement (undefined for any other line): its on-line in the chronicle; its off-lines collapsed to
 * its last change, none when that is not an off-line or the chip `showing` now. */
function chipPlaces(catalog: Catalog, lines: readonly Pick<LogLine, "key" | "card">[], showing: (chip: string) => boolean): Array<Placement | undefined> {
  const chips = chipLines(catalog);
  const chipOf = (l: Pick<LogLine, "key" | "card">) => (l.card === null ? chips.get(l.key) : undefined);
  const last = new Map<string, number>();
  lines.forEach((l, i) => { const c = chipOf(l); if (c) last.set(c.chip, i); });
  return lines.map((l, i) => {
    const c = chipOf(l);
    if (!c) return undefined;
    return c.on || (last.get(c.chip) === i && !showing(c.chip)) ? "chronicle" : "none";
  });
}

function chipLines(catalog: Catalog): Map<string, { chip: string; on: boolean }> {
  const found = new Map<string, { chip: string; on: boolean }>();
  for (const c of catalog.content.chip_infos) {
    if (c.on_line_key) found.set(c.on_line_key, { chip: c.chip, on: true });
    for (const k of c.off_line_keys) found.set(k, { chip: c.chip, on: false });
  }
  return found;
}
