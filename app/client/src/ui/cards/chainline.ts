// A working's reach on its face (contract/spells.txt, "SPELLS"): "reaches up to 3" under its tap, the number a button
// that opens the reach's sources, the base first, as a strength's do (ledger/strength.ts). Drawn from View.chains as
// served: the page never works out a reach, a due count or a chain's length.
import type { Chain, View } from "../../api/types";
import type { Catalog } from "../../game/page/catalog";
import { UI } from "../../game/page/text";
import { el, tapFeedback } from "../dom";
import { strengthItems } from "../ledger/strength";

const GAP = "\u0001";   // where the number goes in the words

export class ChainLine {
  readonly root = el("div", "fight chain");
  private readonly words = el("span", "chain-up-to");
  private readonly entries = el("ul", "fight-entries");
  private open = false;
  private shown = "";
  private chain: Chain | null = null;

  constructor(private readonly catalog: Catalog, private readonly card: string) {
    this.entries.hidden = true;
    this.root.append(this.words, this.entries);
  }

  /** Shown while the view serves this card's chain; else hidden. */
  sync(view: View): void {
    const chain = view.chains.find((c) => c.card === this.card);
    this.root.hidden = chain === undefined;
    if (chain === undefined) return;
    this.chain = chain;
    const key = JSON.stringify(chain.up_to);
    if (key === this.shown) return;
    this.shown = key;
    const parts = this.catalog.text.fill(UI.chainUpTo, { n: GAP }).split(/(\u0001)/).filter((p) => p !== "");
    this.words.replaceChildren(...parts.map((p) => (p === GAP ? this.button(chain) : p)));
    this.drawEntries();
  }

  private button(chain: Chain): HTMLButtonElement {
    const b = el("button", "fight-strength", String(chain.up_to.value));
    b.type = "button";
    b.setAttribute("aria-expanded", String(this.open));
    b.addEventListener("click", () => {
      tapFeedback();
      this.open = !this.open;
      b.setAttribute("aria-expanded", String(this.open));
      this.drawEntries();
    });
    return b;
  }

  private drawEntries(): void {
    this.entries.hidden = !this.open || this.chain === null;
    if (this.entries.hidden || this.chain === null) return;
    const owner = this.catalog.label(this.catalog.cards.get(this.card)?.label_key);
    this.entries.replaceChildren(...strengthItems(this.catalog, this.chain.up_to, owner, UI.chainBase));
  }
}
