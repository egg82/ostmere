// A kept bonus's line (CardInfo.kept; docs/decisions/principles.md, "Make what is already there tappable before adding
// words"): the line the card words its bonus with, which leads to the strength it feeds. Once a fight of that side is
// served the line is a button, underlined as the fight's own strengths are, and a tap opens that side's strength sheet
// (strength.ts) under it; until then, and with the `combat` feature off, it is plain text, and says nothing more.
import type { Strength } from "../api/types";
import type { Catalog } from "../game/catalog";
import { el, tapFeedback } from "./dom";
import { strengthItems } from "./strength";

export class Bonus {
  readonly line = el("span", "bonus");
  private readonly sheet = el("ul", "fight-entries");
  private words = "";
  private strength: Strength | null = null;

  /** `side`: the side the bonus feeds; `opened` hears each tap; `open`: the sheet starts open (an editor redraws its rows). */
  constructor(private readonly catalog: Catalog, private readonly side: string, private readonly css: string, private readonly opened: (open: boolean) => void = () => undefined, private open = false) {
    this.sheet.hidden = true;
  }

  /** The line's words, and the side's strength as served now (null: no fight showing for it). The button is kept across
   * views, so a keyboard's focus stays; only the sheet under it is redrawn. */
  draw(words: string, strength: Strength | null): void {
    const was = this.strength !== null;
    const same = words === this.words && was === (strength !== null);
    this.words = words;
    this.strength = strength;
    if (!strength) this.open = false;
    if (!same) this.line.replaceChildren(strength ? this.button() : el("span", this.css, words), this.sheet);
    this.fill();
  }

  /** The same words, the side's strength as served now. */
  sync(strength: Strength | null): void {
    this.draw(this.words, strength);
  }

  /** The sheet, open or shut, from the strength as served. */
  private fill(): void {
    const show = this.open && this.strength !== null;
    this.sheet.hidden = !show;
    this.sheet.replaceChildren(...(show && this.strength ? strengthItems(this.catalog, this.strength, this.catalog.sideLabel(this.side)) : []));
  }

  private button(): HTMLButtonElement {
    const b = el("button", `${this.css} bonus-link`, this.words);
    b.type = "button";
    b.setAttribute("aria-expanded", String(this.open));
    b.addEventListener("click", () => {
      tapFeedback();
      this.open = !this.open;
      this.opened(this.open);
      b.setAttribute("aria-expanded", String(this.open));   // the button stays, so a keyboard's focus does
      this.fill();
    });
    return b;
  }
}
