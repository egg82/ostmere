// Dragging a card from the editor's Add row (ui/editor.ts): a tap joins it, and so does a drop on the bar.

/** A tap joins the card; so does dragging it onto the bar. Dragged anywhere else, nothing happens. */
export function dragIn(e: PointerEvent, node: HTMLElement, bar: HTMLElement, join: () => void): void {
  node.setPointerCapture(e.pointerId);
  const x0 = e.clientX, y0 = e.clientY;
  let moved = false;
  const onMove = (ev: PointerEvent) => {
    const dx = ev.clientX - x0, dy = ev.clientY - y0;
    if (Math.hypot(dx, dy) > 6) moved = true;
    if (moved) node.style.transform = `translate(${dx}px, ${dy}px)`;
  };
  const onUp = (ev: PointerEvent) => {
    node.removeEventListener("pointermove", onMove);
    node.style.transform = "";
    const r = bar.getBoundingClientRect();
    const over = ev.clientX >= r.left && ev.clientX <= r.right && ev.clientY >= r.top - 24 && ev.clientY <= r.bottom + 24;
    if (!moved || over) join();
  };
  node.addEventListener("pointermove", onMove);
  node.addEventListener("pointerup", onUp, { once: true });
  node.addEventListener("pointercancel", () => { node.removeEventListener("pointermove", onMove); node.style.transform = ""; }, { once: true });
}
