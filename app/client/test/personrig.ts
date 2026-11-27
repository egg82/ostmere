// A person's page on the town fixture (ui/personpage.ts), for the suites about it: the town strip's rows, the page the
// Change of one opens, and the server's side of a decision (a save_mix lands in the view, as the engine keeps it).
import { fakeDocument, type FakeEl } from "./fake-dom";
import { testContext, type Recorded } from "./context";
import type { Catalog } from "../src/game/catalog";
import type { Decision, Mix, View } from "../src/api/types";
import { Glow } from "../src/ui/feedback/fresh";
import { LaneRows } from "../src/ui/town/lanerows";

export interface PageRig {
  rows: LaneRows;
  got: Recorded;
  /** The town strip's root and the page's. */
  root: FakeEl;
  page: FakeEl;
  /** The page the Change of the `i`th person opens; its bar is given a width. */
  open(i: number): FakeEl;
  /** `view` as the server has it after `decisions` (their save_mix taken in), drawn again. */
  settle(view: View, decisions?: Decision[]): View;
  /** A person's task face on the open page. */
  face(card: string): FakeEl;
}

export function pageRig(view: View, catalog?: Catalog, glow = new Glow()): PageRig {
  const { ctx, got } = testContext(glow, catalog);
  const rows = new LaneRows(ctx);
  document.body.replaceChildren(rows.root, rows.page.root);
  const root = fakeDocument.body.firstElementChild as FakeEl;
  const page = fakeDocument.body.children[1] as FakeEl;
  rows.update(view);
  const open = (i: number): FakeEl => {
    root.querySelectorAll(".person-change")[i]?.click();
    for (const track of page.querySelectorAll(".share-track")) track.rect = { left: 0, top: 0, width: 1000, height: 20, right: 1000, bottom: 20 };
    return page;
  };
  const settle = (v: View, decisions: Decision[] = got.decided): View => {
    let next = v;
    for (const d of decisions) {
      if (d.kind === "save_mix") {
        const mix: Mix = d.mix;
        const held = new Map(mix.components.flatMap((c) => (c.kind === "card_share" ? [[c.card, c.share_bp] as const] : [])));
        const was = new Set(next.mixes.find((m) => m.id === mix.id)?.components.flatMap((c) => (c.kind === "card_share" ? [c.card] : [])));
        const cards = next.running_town_mix_id !== mix.id ? next.cards : next.cards.map((c) => ({ ...c, share_bp: held.get(c.card) ?? (was.has(c.card) ? 0 : c.share_bp) }));
        next = { ...next, cards, mixes: next.mixes.some((m) => m.id === mix.id) ? next.mixes.map((m) => (m.id === mix.id ? mix : m)) : [...next.mixes, mix] };
      } else if (d.kind === "set_orders") next = { ...next, orders: d.orders };
    }
    got.decided.length = 0;
    rows.update(next);
    return next;
  };
  const face = (card: string): FakeEl => page.querySelectorAll(".person-cards .card").find((c) => c.dataset.card === card) as FakeEl;
  return { rows, got, root, page, open, settle, face };
}

export const texts = (nodes: FakeEl[]): string[] => nodes.map((n) => n.textContent ?? "");
/** The share a card's face states (empty: it holds none). */
export const shareOf = (face: FakeEl): string => face.querySelector(".card-share")?.textContent ?? "";
export const savedMix = (d: Decision | undefined): Mix | null => (d?.kind === "save_mix" ? d.mix : null);
