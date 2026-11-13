// Content indexed by id, with the text and number formatting that go with it: what every part of the screen
// is handed, so no part reaches into the raw content lists.
import type { CardInfo, ChipInfo, LaneInfo, LineCause, NodeInfo, OfferInfo, OrderCard, Content, SideInfo, SkillInfo, StoreInfo, ThreatInfo, View } from "../api/types";
import { Format } from "./format";
import type { LineKind } from "./chronicle";
import { Text } from "./text";

function byId<T, K extends keyof T>(items: T[], key: K): Map<T[K], T> {
  return new Map(items.map((item) => [item[key], item]));
}

export class Catalog {
  readonly text: Text;
  readonly format: Format;
  readonly stores: Map<string, StoreInfo>;
  readonly cards: Map<string, CardInfo>;
  readonly chips: Map<string, ChipInfo>;
  readonly skills: Map<string, SkillInfo>;
  /** Every skill's prestige track, by node id (SkillPrestige.menu_nodes names them). */
  readonly nodes: Map<string, NodeInfo>;
  readonly lanes: Map<string, LaneInfo>;
  readonly offers: Map<string, OfferInfo>;
  readonly sides: Map<string, SideInfo>;
  readonly threats: Map<string, ThreatInfo>;
  private readonly lineKinds: Map<string, LineKind>;
  private readonly lineCauses: Map<string, LineCause | null>;
  readonly features: Map<string, string | null>;
  /** The store the Camp bar is drawn from; never a ledger line (CONTRACT.txt). */
  readonly campStore: string | null;
  /** The order cards that answer a chip: offered in the hands strip, never under a ledger line (CONTRACT.txt). */
  readonly chipCards: OrderCard[];
  /** Each store's ledger-line order cards, in content order: a later one supersedes an earlier once it is offered. */
  private readonly orderCards = new Map<string, OrderCard[]>();
  private readonly cardOrder: Map<string, number>;

  constructor(readonly content: Content) {
    this.text = new Text(content);
    this.format = new Format(this.text, content.scales);
    this.stores = byId(content.store_infos, "store");
    this.cards = byId(content.card_infos, "card");
    this.chips = byId(content.chip_infos, "chip");
    this.skills = byId(content.skill_infos, "skill");
    this.nodes = byId(content.node_infos, "node");
    this.lanes = byId(content.lane_infos, "lane");
    this.offers = byId(content.offer_infos, "offer");
    this.sides = byId(content.side_infos, "side");
    this.threats = byId(content.threat_infos, "threat");
    this.lineKinds = new Map(content.line_infos.map((l) => [l.key, l.kind]));
    this.lineCauses = new Map(content.line_infos.map((l) => [l.key, l.cause]));
    this.features = new Map(content.feature_infos.map((f) => [f.feature, f.hint_key]));
    for (const c of content.order_cards) if (c.chip === null) this.orderCards.set(c.store, [...this.orderCardsFor(c.store), c]);
    this.chipCards = content.order_cards.filter((c) => c.chip !== null);
    this.cardOrder = new Map(content.card_infos.map((c, i) => [c.card, i]));
    this.campStore = content.camp?.store ?? null;
  }

  /** The ledger line's order cards for a store, in content order; a chip's card is never one. */
  orderCardsFor(store: string): OrderCard[] {
    return this.orderCards.get(store) ?? [];
  }

  /** How the chronicle sets a line: its kind, authored with its text. A key with none is a content the server's checks refused. */
  lineKind(key: string): LineKind {
    const kind = this.lineKinds.get(key);
    if (kind === undefined) throw new Error(`no kind for line ${key}`);
    return kind;
  }

  /** What writes a line, read from where its key is authored (CONTRACT.txt, "Line causes"); null: nothing does. */
  lineCause(key: string): LineCause | null {
    return this.lineCauses.get(key) ?? null;
  }

  label(key: string | null | undefined): string {
    return key ? this.text.get(key) : "";
  }

  storeLabel(store: string): string {
    return this.label(this.stores.get(store)?.label_key);
  }

  /** A store's name where it leads a row (the ledger, the editor's totals): the label with a capital. In a sentence
   * the label stands as the content has it. */
  storeTitle(store: string): string {
    const label = this.storeLabel(store);
    return label.charAt(0).toUpperCase() + label.slice(1);
  }

  cardLabel(card: string): string {
    return this.label(this.cards.get(card)?.label_key);
  }

  sideLabel(side: string): string {
    return this.label(this.sides.get(side)?.label_key);
  }

  threatLabel(threat: string): string {
    return this.label(this.threats.get(threat)?.label_key);
  }

  skillLabel(skill: string): string {
    return this.label(this.skills.get(skill)?.label_key);
  }

  /** A card's or a standing action's label: they share one namespace (CONTRACT.txt). */
  runnerLabel(runner: string): string {
    return this.cards.has(runner) ? this.cardLabel(runner) : this.label(this.content.standing_infos.find((a) => a.action === runner)?.label_key);
  }

  /** A lane's label: the last of its later labels whose unlock `view` holds, else its own (CONTRACT.txt, "A lane run
   * by rules"). */
  laneLabel(lane: string, view?: View): string {
    const info = this.lanes.get(lane);
    const later = view ? info?.later_labels.filter((l) => this.unlocked(view, l.after.category, l.after.id)).at(-1) : undefined;
    return this.label(later?.label_key ?? info?.label_key);
  }

  /** A card on a lane whose task the player's rules set, never their tap. */
  ruled(card: string): boolean {
    return this.lanes.get(this.laneOf(card))?.ruled === true;
  }

  laneOf(card: string): string {
    return this.cards.get(card)?.lane ?? "hands";
  }

  /** CardInfo order: the order the view lists cards in. */
  rank(card: string): number {
    return this.cardOrder.get(card) ?? Number.MAX_SAFE_INTEGER;
  }

  /** Cards the player's mix may hold: those whose lane is the hands (CONTRACT.txt). */
  mixable(card: string): boolean {
    return this.laneOf(card) === "hands";
  }

  /** Whether the view's unlock set holds this id (the view's own say on what exists, CONTRACT.txt). */
  unlocked(view: View, category: View["unlocked"][number]["category"], id: string): boolean {
    return view.unlocked.some((u) => u.category === category && u.id === id);
  }

  /** The card that takes a retiring card's place, when the content names one. */
  replacedBy(card: string): string | null {
    return this.cards.get(card)?.replaced_by ?? null;
  }

  retired(view: View, card: string): boolean {
    return this.unlocked(view, "retired", card);
  }
}
