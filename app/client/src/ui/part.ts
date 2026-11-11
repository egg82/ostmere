// What every part of the game screen is: redrawn from each new View, and sampled every frame in between.
import type { Condition, Decision, LogLine, Repeats, RuleRun, View } from "../api/types";
import type { Catalog } from "../game/catalog";
import type { Keeps } from "../game/keeps";
import type { Subject } from "../game/lessons";
import type { HandStreak } from "../game/stall";
import type { OrderFires } from "./fires";
import type { Glow } from "./fresh";
import type { LaneTarget } from "./laneedit";
import type { Arrivals } from "./reveal";

/** What the Rules tab opens on: its list (null), a rule's condition editor, a new rule's, or a lane's task editor. */
export type RuleTarget = number | "new" | null | LaneTarget;

export interface Part {
  readonly root: HTMLElement;
  update(view: View, prev: View | null): void;
  tick(t: number): void;
}

/** What a part may do besides draw. */
export interface Actions {
  decide(decision: Decision): void;
  /** The view after these decisions, not kept (Session.dryRun). */
  dryRun(decisions: Decision[]): Promise<View | null>;
  /** Open the mix editor on a saved mix (null: the running one). */
  editMix(mixId: string | null): void;
  /** Open the editor on a new mix; with a rule's index, saving points that rule at it. */
  newMix(forRule: number | null): void;
  /** Open the Mixes list. */
  openSelector(): void;
  /** Open the Rules tab; with a rule's index, on that rule's condition editor; with "new", on a new rule's, which
   * starts at the offered condition's levels when one is given; with a lane, on that lane's task editor (laneedit.ts). */
  openRules(rule: RuleTarget, offered?: Condition): void;
  /** A rule offer was accepted; its element, for the flight to the Rules tab. */
  orderSent(card: HTMLElement): void;
  /** Light up the ledger lines these cards feed or draw on (null: none), while a share is dragged. */
  highlight(cards: string[] | null): void;
  /** A tester's words to the server: whether they were kept. */
  sendFeedback(text: string): Promise<boolean>;
}

export interface PartContext {
  catalog: Catalog;
  actions: Actions;
  /** Cards an order started that are still running (their cards wear a marker). */
  fires: OrderFires;
  glow: Glow;
  /** The player's recent hand-starts, for the stall offer. */
  streak: HandStreak;
  /** Where a part sends what it draws new: shown at once, or in turn on a return (reveal.ts). */
  arrivals: Arrivals;
  /** The end is recorded and its lines have been read (this page session): TheEnd.behind. */
  endBehind(): boolean;
  /** What the server keeps for the page that is not game state (a rule seen, the Rules tab opened). */
  keeps: Keeps;
  /** What the player keeps doing by hand, from the latest Step (CONTRACT.txt, "Repeats"). */
  repeats(): Repeats;
  /** What the rules did lately, from the latest Step (CONTRACT.txt, "Rule runs"). */
  ruleRuns(): RuleRun[];
  /** The latest Step's lines: what an arrival announced by one of them waits behind (an offer's row). */
  lines(): LogLine[];
  /** The save being played: what the log's fight labels are drawn from. */
  saveId(): number;
  /** The lesson under way (ui/lessons.ts), or null: offers that would crowd it wait. */
  lesson(): string | null;
  /** What the lesson under way started on (its trigger's data attributes), or null: another offer like it waits. */
  lessonSubject(): Subject | null;
}
