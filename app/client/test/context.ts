// A PartContext for tests that draw a part against the fake DOM (fake-dom.ts, installed first): the real catalog,
// glow, keeps and fires, actions that record what they were asked, and arrivals that show everything at once.
import type { Decision } from "../src/api/types";
import { Catalog } from "../src/game/catalog";
import { FIRST_MIX, FIRST_RULE } from "../src/game/lessons";
import { HandStreak } from "../src/game/stall";
import { OrderFires } from "../src/ui/fires";
import { Glow } from "../src/ui/fresh";
import type { PartContext, RuleTarget } from "../src/ui/part";
import type { Arrivals } from "../src/ui/reveal";
import { fixtureContent } from "../fixtures/content";
import { keepsOf, NEW_FLAT } from "./kept";

/** An account past the first lessons (done or skipped): the offers are today's one-tap ones, which most suites test. */
export const TAUGHT = { ...NEW_FLAT, lessons: [FIRST_MIX, FIRST_RULE] };

export interface Recorded {
  decided: Decision[];
  /** What was flown to the Rules tab (Actions.orderSent). */
  sent: HTMLElement[];
  /** The rules opened (Actions.openRules). */
  opened: RuleTarget[];
  edited: (string | null)[];
  /** What was sent as feedback (Actions.sendFeedback). */
  feedback: string[];
  /** Each Actions.highlight, in order. */
  lit: (string[] | null)[];
}

export function testContext(glow = new Glow(), catalog = new Catalog(fixtureContent)): { ctx: PartContext; got: Recorded } {
  const got: Recorded = { decided: [], sent: [], opened: [], edited: [], feedback: [], lit: [] };
  const arrivals: Arrivals = { arrive: () => undefined, effect: (_node, _kind, run) => run(), line: () => undefined, busy: false };
  const ctx: PartContext = {
    catalog,
    actions: {
      decide: (d) => { got.decided.push(d); }, dryRun: () => Promise.resolve(null), editMix: (id) => { got.edited.push(id); },
      newMix: () => undefined, openSelector: () => undefined, openRules: (rule) => { got.opened.push(rule); },
      orderSent: (node) => { got.sent.push(node); }, highlight: (cards) => { got.lit.push(cards); },
      sendFeedback: (text) => { got.feedback.push(text); return Promise.resolve(true); },
    },
    fires: new OrderFires(), glow, streak: new HandStreak(), arrivals, endBehind: () => true, keeps: keepsOf(TAUGHT),
    repeats: () => ({ taps: [], switches: [] }), ruleRuns: () => [], lines: () => [], saveId: () => 1, lesson: () => null, lessonSubject: () => null,
  };
  return { ctx, got };
}
