// A reordered rule slides to its new place (FLIP): the rows' tops are measured before the move, the list is redrawn in
// its new order, each row that changed place is set back at its old top, then released to slide home on --settle-ms and
// --settle-ease (.slide in game.css, which the reduced-motion block turns into an instant change). Under reduced motion
// nothing is set up at all.
import { reducedMotion } from "./dom";

/** Where each rule that changes place lands: new index -> old index, for rule `index` moved to where rule `to` stands
 * in `group` (the rules drawn together, in order), the ones between shifting one place (game/orders.ts reorderRule). */
export function shiftOf(group: readonly number[], index: number, to: number): Map<number, number> {
  const from = group.indexOf(index), at = group.indexOf(to);
  const moved = new Map<number, number>();
  if (from < 0 || at < 0 || from === at) return moved;
  const order = [...group];
  order.splice(from, 1);
  order.splice(at, 0, index);
  order.forEach((was, n) => { if (was !== group[n]) moved.set(group[n]!, was); });
  return moved;
}

/** Each drawn rule row's top, by its rule index. */
export function rowTops(root: HTMLElement): Map<number, number> {
  const tops = new Map<number, number>();
  for (const row of root.querySelectorAll<HTMLElement>(".rules-row[data-rule]")) tops.set(Number(row.dataset.rule), row.getBoundingClientRect().top);
  return tops;
}

/** The rows now drawn in `root` that moved (`shift`: new index -> old index) leave from the `tops` they had; the lines
 * that hang under a row (why it is off, its menu) go with it. */
export function slide(root: HTMLElement, tops: ReadonlyMap<number, number>, shift: ReadonlyMap<number, number>): void {
  if (reducedMotion()) return;
  const moving: Array<{ nodes: HTMLElement[]; dy: number }> = [];
  for (const row of root.querySelectorAll<HTMLElement>(".rules-row[data-rule]")) {
    const was = shift.get(Number(row.dataset.rule));
    const top = was === undefined ? undefined : tops.get(was);
    if (top === undefined) continue;
    const dy = top - row.getBoundingClientRect().top;
    if (dy === 0) continue;
    const nodes = [row];
    for (let n = row.nextElementSibling as HTMLElement | null; n && !n.classList.contains("rules-row"); n = n.nextElementSibling as HTMLElement | null) nodes.push(n);
    moving.push({ nodes, dy });
  }
  for (const { nodes, dy } of moving) for (const n of nodes) n.style.transform = `translateY(${dy}px)`;
  void root.offsetHeight;
  for (const { nodes } of moving) {
    for (const n of nodes) {
      n.classList.add("slide");
      n.style.transform = "";
      n.addEventListener("transitionend", () => n.classList.remove("slide"), { once: true });
    }
  }
}
