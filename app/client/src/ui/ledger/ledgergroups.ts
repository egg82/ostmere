// Stores of one kind of thing (StoreInfo.group_key: the pot's stews) share one ledger row once two or more are drawn: the
// group's label and its total, which a tap opens to show each kind's own line (contract/, "Ledger"). Only the lines
// the ledger keeps with itself are folded: a line drawn with the asks (red, or full while fed) stays where it is seen.
import type { LedgerLine } from "../../api/types";
import { sample } from "../../game/page/clock";
import { el, place, setText, tapFeedback } from "../dom";
import type { PartContext } from "../part";

/** A drawn line and its ledger item. */
export interface Item {
  line: LedgerLine;
  node: HTMLElement;
}

interface Group {
  node: HTMLElement;
  head: HTMLButtonElement;
  amount: HTMLElement;
  body: HTMLElement;
  lines: LedgerLine[];
}

export class LedgerGroups {
  private readonly groups = new Map<string, Group>();
  /** The groups the player opened, kept across redraws. */
  private readonly open = new Set<string>();

  constructor(private readonly ctx: PartContext) {}

  /** `items` in the list's order, each group of two or more drawn as one row at its first member's place. */
  fold(items: readonly Item[]): HTMLElement[] {
    const key = (l: LedgerLine): string | null => this.ctx.catalog.stores.get(l.store)?.group_key ?? null;
    const counts = new Map<string, number>();
    for (const { line } of items) {
      const k = key(line);
      if (k !== null) counts.set(k, (counts.get(k) ?? 0) + 1);
    }
    const out: HTMLElement[] = [];
    const members = new Map<string, HTMLElement[]>();
    for (const { line, node } of items) {
      const k = key(line);
      if (k === null || (counts.get(k) ?? 0) < 2) {
        out.push(node);
        continue;
      }
      const g = this.group(k);
      if (!members.has(k)) {
        members.set(k, []);
        g.lines = [];
        out.push(g.node);
      }
      members.get(k)?.push(node);
      g.lines.push(line);
    }
    for (const [k, g] of this.groups) {
      const nodes = members.get(k);
      if (nodes) {
        place(g.body, nodes);
        g.body.hidden = !this.open.has(k);
        g.head.setAttribute("aria-expanded", String(this.open.has(k)));
      } else {
        g.body.replaceChildren();   // its lines go back to the list (`out`)
        g.node.remove();
        g.lines = [];
      }
    }
    return out;
  }

  /** Each group's total at `t`. */
  tick(t: number): void {
    const { format } = this.ctx.catalog;
    for (const g of this.groups.values()) {
      if (g.lines.length === 0) continue;
      setText(g.amount, format.amount(g.lines.reduce((sum, l) => sum + sample(l.segment, t), 0), g.lines.reduce((sum, l) => sum + l.cap, 0)));
    }
  }

  private group(k: string): Group {
    const had = this.groups.get(k);
    if (had) return had;
    const node = el("div", "ledger-item ledger-fold");
    const head = el("button", "line line-fold");
    head.type = "button";
    const amount = el("span", "line-amount");
    head.append(el("span", "line-name", this.ctx.catalog.label(k)), amount);
    const body = el("div", "ledger-fold-lines");
    head.addEventListener("click", () => {
      tapFeedback();
      if (this.open.has(k)) this.open.delete(k);
      else this.open.add(k);
      body.hidden = !this.open.has(k);
      head.setAttribute("aria-expanded", String(this.open.has(k)));
    });
    node.append(head, body);
    const g: Group = { node, head, amount, body, lines: [] };
    this.groups.set(k, g);
    return g;
  }
}
