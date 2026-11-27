// A side's strength sheet (docs/design/opening-screen/ledger-and-fights.md, "Fights"): the owner's label, then its entries one row each,
// the base first. A fight panel opens it from a strength figure (fightpanel.ts); a kept bonus's line opens the same sheet
// for its side (bonus.ts).
import type { Strength, View } from "../../api/types";
import type { Catalog } from "../../game/catalog";
import { COMBAT, strengthRows } from "../../game/fights";
import { UI } from "../../game/text";
import { el } from "../dom";

/** A source id as its label: a card, skill, chip, store or feature the content names. Throws on a source none names. */
function sourceName(catalog: Catalog, id: string): string {
  const feature = catalog.content.feature_infos.find((f) => f.feature === id)?.label_key;
  const key = catalog.cards.get(id)?.label_key ?? catalog.skills.get(id)?.label_key ?? catalog.chips.get(id)?.label_key ?? catalog.stores.get(id)?.label_key ?? feature;
  if (!key) throw new Error(`no label for strength source ${id}`);
  return catalog.label(key);
}

/** The sheet's rows: `owner` as its heading, then an entry per source with its amount; the base has no source and is the
 * number. An entry that carries a share (week two's entries held while a card runs) shows it between source and amount. */
export function strengthItems(catalog: Catalog, strength: Strength, owner: string): HTMLElement[] {
  const rows = strengthRows(strength, catalog.content.scales.bp, (id) => sourceName(catalog, id), (bp) => catalog.format.change(bp), (bp) => catalog.format.share(bp));
  return [el("li", "fight-owner", owner), ...rows.map((r) => {
    const li = el("li", "fight-entry");
    li.append(el("span", "fight-source", r.source ?? catalog.text.get(UI.fightBase)), ...(r.share === null ? [] : [el("span", "fight-share", r.share)]), el("span", "fight-amount", r.amount));
    return li;
  })];
}

/** The strength of `side` as the view serves it: while the `combat` feature is on and a fight of that side is served; else null. */
export function sideStrength(catalog: Catalog, view: View, side: string): Strength | null {
  return catalog.unlocked(view, "feature", COMBAT) ? view.fights.find((f) => f.side === side)?.power ?? null : null;
}
