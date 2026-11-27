// A level on the card it speeds up (game/levelled.ts says which): for LEVEL_MS the card's foot reads "{skill} {n} ·
// {before} → {after}", the old time set apart, on the card's ember wash (game.css, .card.levelled); then its time comes
// back. Colour and words only, so reduced motion shows it the same.
import type { Catalog } from "../../game/page/catalog";
import type { Speedup } from "../../game/cards/levelled";
import { UI } from "../../game/page/text";
import type { Row } from "./cardrow";
import { el } from "../dom";

/** How long the line stays readable on the card. */
export const LEVEL_MS = 2000;
const BEFORE = "\u0001", AFTER = "\u0002";   // where the two times go in the line's words

export function showLevel(catalog: Catalog, row: Row, s: Speedup, nowMs: number): void {
  const [before, after] = catalog.format.spans(s.beforeS, s.afterS);
  const words = catalog.text.fill(UI.cardLevelled, { skill: catalog.skillLabel(s.skill), n: catalog.format.count(s.level), before: BEFORE, after: AFTER });
  const [pre = "", mid = "", post = ""] = words.split(/[\u0001\u0002]/);
  const line = el("span", "card-level");   // one inline run: the foot is a flex box, which would trim each piece's spaces
  line.append(pre, el("s", "", before), mid, el("span", "", after), post);   // each time unbroken where the line wraps
  row.foot.replaceChildren(line);
  row.node.classList.add("levelled");
  row.levelUntil = nowMs + LEVEL_MS;
}

/** True while the line is on the card; past its time it goes, and the foot is the caller's to fill again. */
export function levelShown(row: Row, nowMs: number): boolean {
  if (row.levelUntil === undefined) return false;
  if (nowMs < row.levelUntil) return true;
  row.levelUntil = undefined;
  row.node.classList.remove("levelled");
  row.foot.replaceChildren();
  return false;
}
