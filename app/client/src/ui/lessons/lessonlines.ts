// A ledger line as a lesson's trigger (ui/ledger/ledger.ts): the cap rule's (game/caphint.ts) and the dry store's
// (game/dryhint.ts) lessons start from the line that is their subject, its data attributes naming what it is about.
import type { DryCue } from "../../game/dryhint";

/** The cap rule's lesson starts from this line while it is the subject: its trigger, with the store it is about. */
export function capLine(box: HTMLElement, store: string, on: boolean): void {
  if (on) Object.assign(box.dataset, { teach: "cap-line", store });
  else if (box.dataset.teach === "cap-line") { delete box.dataset.teach; delete box.dataset.store; }
}

/** The dry store's lesson starts from this line while it is the subject: its trigger, with the stopped card and its maker. */
export function dryLine(box: HTMLElement, cue: DryCue | null): void {
  if (cue) Object.assign(box.dataset, { teach: "dry-line", store: cue.store, card: cue.card, maker: cue.maker });
  else if (box.dataset.teach === "dry-line") { delete box.dataset.teach; delete box.dataset.store; delete box.dataset.card; delete box.dataset.maker; }
}
