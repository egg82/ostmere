// Dragging in the Rules tab (docs/design/opening-screen.md, "The Rules tab"): a rule's ≡ to another place among the
// rules drawn with it (the hands' rules, or the town's). Pointer drag (mouse, pen or touch): a ghost follows
// the pointer and the drop lands where it is let go; a press that moves less than DRAG_PX stays a tap (the node's click).
import type { View } from "../api/types";

/** How far a press moves before it is a drag rather than a tap. */
const DRAG_PX = 6;

/** The dragged rule's index. */
export type Dragged = { rule: number };

/** The tab a drag runs in. */
export interface DragHost {
  readonly root: HTMLElement;
  view(): View | null;
  /** The rules drawn together with rule `rule`, in order: the places it can be dropped. */
  group(view: View, rule: number): number[];
  /** Let go on `target`, a rule's row. */
  dropped(what: Dragged, target: HTMLElement): void;
  /** The drag is over, dropped or not: the tab redraws. */
  ended(): void;
}

interface Drag {
  pointer: number;
  x: number;
  y: number;
  ghost: HTMLElement | null;
  what: Dragged;
  target: Element | null;
}

export class RuleDrag {
  private drag: Drag | null = null;

  constructor(private readonly host: DragHost) {}

  /** A press is being dragged (or may become a drag). */
  get active(): boolean {
    return this.drag !== null;
  }

  /** Makes `node` draggable as `what`. */
  attach(node: HTMLElement, what: () => Dragged): void {
    node.addEventListener("pointerdown", (e) => {
      if (e.button !== 0 || (node as HTMLButtonElement).disabled) return;
      this.drag = { pointer: e.pointerId, x: e.clientX, y: e.clientY, ghost: null, what: what(), target: null };
      try { node.setPointerCapture(e.pointerId); } catch { /* a synthetic pointer: moves still arrive on the node */ }
    });
    node.addEventListener("pointermove", (e) => {
      const drag = this.drag;
      if (!drag || drag.pointer !== e.pointerId) return;
      if (!drag.ghost) {
        if (Math.hypot(e.clientX - drag.x, e.clientY - drag.y) < DRAG_PX) return;
        drag.ghost = this.lift(this.host.root.querySelector<HTMLElement>(`.rules-row[data-rule="${drag.what.rule}"]`) ?? node);
      }
      drag.ghost.style.transform = `translate(${e.clientX - drag.x}px, ${e.clientY - drag.y}px)`;
      this.aim(drag, e.clientY);
    });
    const end = (e: PointerEvent, drop: boolean): void => {
      const drag = this.drag;
      if (!drag || drag.pointer !== e.pointerId) return;
      this.drag = null;
      if (!drag.ghost) return;   // a tap: its click follows
      const { root } = this.host;
      drag.ghost.remove();
      root.classList.remove("dragging");
      for (const n of root.querySelectorAll(".drop-before, .drop-after, .lifted")) n.classList.remove("drop-before", "drop-after", "lifted");
      node.addEventListener("click", (c) => { c.stopImmediatePropagation(); c.preventDefault(); }, { capture: true, once: true });   // not a tap
      const target = drag.target as HTMLElement | null;
      if (drop && target && this.host.view()) this.host.dropped(drag.what, target);
      this.host.ended();
    };
    node.addEventListener("pointerup", (e) => end(e, true));
    node.addEventListener("pointercancel", (e) => end(e, false));
  }

  /** The ghost: a copy of what is dragged, over the page, following the pointer. */
  private lift(shown: HTMLElement): HTMLElement {
    const rect = shown.getBoundingClientRect();
    const ghost = shown.cloneNode(true) as HTMLElement;
    ghost.classList.add("drag-ghost");
    Object.assign(ghost.style, { left: `${rect.left}px`, top: `${rect.top}px`, width: `${rect.width}px` });
    document.body.append(ghost);
    shown.classList.add("lifted");
    this.host.root.classList.add("dragging");
    return ghost;
  }

  /** Marks where a drop at height y would land: a place between rules. */
  private aim(drag: Drag, y: number): void {
    const view = this.host.view();
    const { root } = this.host;
    if (!view) return;
    for (const n of root.querySelectorAll(".drop-before, .drop-after")) n.classList.remove("drop-before", "drop-after");
    drag.target = null;
    const group = this.host.group(view, drag.what.rule);
    const rows = [...root.querySelectorAll<HTMLElement>(".rules-row[data-rule]")].filter((r) => group.includes(Number(r.dataset.rule)));
    if (rows.length === 0) return;
    const at = rows.find((r) => y < r.getBoundingClientRect().bottom) ?? rows[rows.length - 1]!;
    const from = group.indexOf(drag.what.rule), to = group.indexOf(Number(at.dataset.rule));
    if (from === to || to < 0) return;
    at.classList.add(to > from ? "drop-after" : "drop-before");
    drag.target = at;
  }
}
