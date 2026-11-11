// The card panel's lane groups (docs/design/opening-screen.md, "Cards"): one group per lane, the hands first, crafts
// under one heading below their lane's cards; each group keeps its slots in order, so a card never moves under a finger.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";

export interface Group {
  node: HTMLElement;
  list: HTMLElement;
  slots: string[];
}

/** What a slot shows: its card, or the finished card still standing in it until the card's turn to arrive. */
export interface Slotted {
  node: HTMLElement;
  stand?: HTMLElement;
}

export class CardGroups {
  private readonly groups = new Map<string, Group>();

  constructor(private readonly root: HTMLElement, private readonly catalog: Catalog) {}

  /** The card's group has not been made yet. */
  isNew(card: string): boolean {
    return !this.groups.has(this.key(card));
  }

  /** The card's group, made (with its heading) the first time. */
  of(card: string): Group {
    const key = this.key(card);
    let g = this.groups.get(key);
    if (!g) {
      const [lane = "hands", craft] = key.split(":");
      const node = el("div", "lane-group");
      node.dataset.lane = lane;
      const heading = craft ? this.catalog.text.get(UI.craftHeading) : lane === "hands" ? "" : this.catalog.laneLabel(lane);
      if (heading) node.append(el("h3", "lane-tag", heading));
      const list = el("div", "card-list");
      node.append(list);
      g = { node, list, slots: [] };
      this.groups.set(key, g);
    }
    return g;
  }

  /** Groups in lane order (the hands first, their crafts under them), slots in their kept order. */
  layout(rows: Map<string, Slotted>): void {
    const lanes = ["hands", ...this.catalog.lanes.keys()];
    const keys = [...this.groups.keys()].sort((a, b) => {
      const [la = "", ca] = a.split(":");
      const [lb = "", cb] = b.split(":");
      return (lanes.indexOf(la) - lanes.indexOf(lb)) || Number(Boolean(ca)) - Number(Boolean(cb));
    });
    let at = this.root.querySelector(":scope > .lane-group");   // anything before the groups (the wait line) stays first
    for (const key of keys) {
      const g = this.groups.get(key);
      if (!g) continue;
      g.slots = g.slots.filter((id) => rows.has(id));
      g.node.hidden = g.slots.length === 0;
      if (g.node === at) at = at.nextElementSibling;
      else this.root.insertBefore(g.node, at);
      let cursor = g.list.firstElementChild;
      for (const id of g.slots) {   // move only what is out of place: re-inserting restarts animations
        const row = rows.get(id);
        if (row?.stand && !row.stand.isConnected) row.stand = undefined;   // the arrival took the slot
        const node = row?.stand ?? row?.node;
        if (!node) continue;
        if (node === cursor) cursor = cursor.nextElementSibling;
        else g.list.insertBefore(node, cursor);
      }
    }
  }

  private key(card: string): string {
    const info = this.catalog.cards.get(card);
    return `${info?.lane ?? "hands"}${info?.presentation === "craft" ? ":craft" : ""}`;
  }
}
