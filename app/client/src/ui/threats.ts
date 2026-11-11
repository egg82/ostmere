// The ledger's threats group (docs/design/opening-screen.md, "Fights"): a threat that runs on its own at the stores is
// a standing fight, drawn under the stores' lines once the `combat` feature is on: its name, its odds and strengths as
// a card shows them, and how many it has fought and lost. It asks nothing of the player, so it is calm: no alarm hue.
import type { Fight, StandingInfo, View } from "../api/types";
import { COMBAT } from "../game/fights";
import { el, keyed } from "./dom";
import { FightPanel } from "./fightpanel";
import type { PartContext } from "./part";

interface Row {
  node: HTMLElement;
  panel: FightPanel;
}

export class Threats {
  readonly root = el("div", "threats");
  private rows = new Map<string, Row>();

  constructor(private readonly ctx: PartContext) {}

  /** Nothing to show: the feature is off or no standing fight is served. */
  get empty(): boolean {
    return this.rows.size === 0;
  }

  update(view: View, prev: View | null): void {
    const { catalog } = this.ctx;
    const infos = new Map(catalog.content.standing_infos.flatMap((s) => (s.fight ? [[s.action, s] as const] : [])));
    const on = catalog.unlocked(view, "feature", COMBAT);
    const fights = on ? view.fights.filter((f) => infos.has(f.runner)) : [];
    const fresh = new Set(fights.filter((f) => !this.rows.has(f.runner)).map((f) => f.runner));
    this.rows = keyed(this.root, fights, (f) => f.runner, this.rows, (f) => this.make(f, infos.get(f.runner)));
    for (const f of fights) this.rows.get(f.runner)?.panel.draw(f);
    if (prev !== null) for (const id of fresh) { const row = this.rows.get(id); if (row) this.ctx.arrivals.arrive(row.node, "store", `threat:${id}`); }
    this.root.hidden = this.empty;
  }

  private make(fight: Fight, info: StandingInfo | undefined): Row {
    const node = el("div", "threat");
    const panel = new FightPanel(this.ctx.catalog, info?.fight ?? { side: fight.side, threat: fight.threat, loses: [], wounds: [], won_line_keys: [], lost_line_keys: [] }, true);
    node.append(el("span", "threat-name", this.ctx.catalog.label(info?.label_key)), panel.root);
    return { node, panel };
  }
}
