// What a rule's "Or else" offers (docs/design/rule-guards.md, "Or else"; the engine's checks.check_actions): every
// fallback is the same kind of verb as the first action and on its lane (taps) or its layer (mixes), so the editor
// offers nothing else, and none twice. A hands task is offered as a task and saved as its solo mix, so it is on the
// hands' layer with the hands' mixes.
import type { OrderVerb, View } from "../../api/types";
import type { Catalog } from "../page/catalog";
import { chosen, doChoices, type DoChoice } from "./ruleoffers";
import { isTownMix } from "../town/town";

const same = (a: DoChoice | null, b: DoChoice | null): boolean => JSON.stringify(a) === JSON.stringify(b);

/** The verb a choice makes in a draft: a task is a tap (a hands task is saved as its solo mix), a mix its switch. */
export const choiceVerb = (c: DoChoice): OrderVerb => (c.kind === "task" ? { kind: "tap_card", card: c.card } : { kind: "switch_mix", mix_id: c.mix });

/** Where a rule's verb sits: a ruled lane, the hands' layer or the town's; null for an answer or an unknown mix.
 * Verbs on one side may share a rule. */
function side(catalog: Catalog, view: View, verb: OrderVerb): string | null {
  if (verb.kind === "tap_card") return catalog.laneOf(verb.card) === "hands" ? "hands" : `lane:${catalog.laneOf(verb.card)}`;
  const mix = verb.kind === "switch_mix" ? view.mixes.find((m) => m.id === verb.mix_id) : undefined;
  return mix === undefined ? null : isTownMix(catalog, view, mix) ? "town" : "hands";
}

/** The choices a fallback after `then` may be, less `then` and the fallbacks already `held`; none while `then` is
 * unchosen or answers an offer. */
export function elseChoices(catalog: Catalog, view: View, then: OrderVerb | null, held: readonly OrderVerb[]): DoChoice[] {
  const where = then === null ? null : side(catalog, view, then);
  if (then === null || where === null) return [];
  const taken = [then, ...held].map((v) => chosen(catalog, view, v));
  return doChoices(catalog, view, true, then).filter((c) => side(catalog, view, choiceVerb(c)) === where && !taken.some((t) => same(t, c)));
}

/** The fallbacks `held` that still stand after `then` changed: those on its side, not `then` itself, once each. */
export function keepElse(catalog: Catalog, view: View, then: OrderVerb | null, held: readonly OrderVerb[]): OrderVerb[] {
  const where = then === null ? null : side(catalog, view, then);
  const key = (v: OrderVerb | null) => chosen(catalog, view, v);
  return held.filter((v, i) => where !== null && side(catalog, view, v) === where && !same(key(v), key(then)) && held.findIndex((h) => same(key(h), key(v))) === i);
}
