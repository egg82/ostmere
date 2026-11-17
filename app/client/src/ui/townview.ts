// The Town tab's panel, the desktop's Town view (docs/design/redesign.md, "Desktop frame"): the town's people and lanes
// (ui/lanerows.ts: the town strip, then a row per lane run by rules) under the view's title, and on a phone the ledger
// and skills after them (ui/partseat.ts). The rail and the main screen never list anyone's jobs: this is their home.
import type { Catalog } from "../game/catalog";
import { UI } from "../game/text";
import { el } from "./dom";
import { markNew, unmark } from "./fresh";
import type { LaneRows } from "./lanerows";

export class TownView {
  readonly root = el("section", "town-tab");
  /** How many people and lanes are drawn: one more where the player can't see it dots the tab. */
  private rows = 0;
  private fresh = 0;

  constructor(catalog: Catalog, private readonly lanes: LaneRows, private readonly tab: HTMLButtonElement) {
    this.root.append(el("h2", "view-title", catalog.text.get(UI.townTitle)), lanes.root);
  }

  /** Whether the tab shows: once a person or a lane is drawn, or `more` holds (a phone's ledger or skills); until then its
   * slot is kept unseen, so nothing moves. `unseen`: the panel is out of sight and this is not the first view. The tab wears
   * the quiet dot while a person's Change does, coming when more of them do, as a row's arrival dots it (`unseen`). */
  draw(more: boolean, unseen: boolean): boolean {
    const rows = this.lanes.count;
    const shows = rows > 0 || more;
    this.tab.style.visibility = shows ? "" : "hidden";
    if (unseen && rows > this.rows) markNew(this.tab, () => undefined);
    this.rows = rows;
    const fresh = this.lanes.fresh;
    if (fresh === 0) unmark(this.tab);
    else if (fresh > this.fresh && unseen) markNew(this.tab, () => undefined);
    this.fresh = fresh;
    return shows;
  }
}
