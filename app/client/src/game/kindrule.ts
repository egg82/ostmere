// The answer rule (CONTRACT.txt, "Offers"): one rule per offer kind, "answer this way whenever someone asks it again".
// The page offers to build it only once an offer of the kind has been answered, and names each role by the label of
// the answer that offer gave under it. Reads the view and the content only.
import type { View } from "../api/types";
import type { Catalog } from "./catalog";

/** One button of the builder: a role of the kind, worded by the answer an answered offer of the kind gave under it. */
export interface RoleChoice { role: string; label_key: string }

/** The kinds the builder is offered for, in content order: those with an offer answered in the view. */
export function answeredKinds(catalog: Catalog, view: View): string[] {
  const kinds: string[] = [];
  for (const o of view.offers) {
    const kind = catalog.offers.get(o.offer)?.kind ?? null;
    if (o.answer !== null && kind !== null && !kinds.includes(kind)) kinds.push(kind);
  }
  return kinds;
}

/** The last offer of `kind` answered in the view (content order), or null. */
function lastAnswered(catalog: Catalog, view: View, kind: string): string | null {
  return view.offers.filter((o) => o.answer !== null && catalog.offers.get(o.offer)?.kind === kind).at(-1)?.offer ?? null;
}

/** The builder's text: the question of the kind's last answered offer. */
export function kindText(catalog: Catalog, view: View, kind: string): string {
  return catalog.label(catalog.offers.get(lastAnswered(catalog, view, kind) ?? "")?.text_key);
}

/** The label of the answer the kind's last answered offer was given. */
export function givenLabelKey(catalog: Catalog, view: View, kind: string): string | undefined {
  const offer = lastAnswered(catalog, view, kind);
  const given = view.offers.find((o) => o.offer === offer)?.answer;
  return catalog.offers.get(offer ?? "")?.answers.find((a) => a.answer === given)?.label_key;
}

/** The kind's roles with the labels of its last answered offer's answers, in that offer's answer order. */
export function roleChoices(catalog: Catalog, view: View, kind: string): RoleChoice[] {
  const answers = catalog.offers.get(lastAnswered(catalog, view, kind) ?? "")?.answers ?? [];
  return answers.flatMap((a) => (a.role === null ? [] : [{ role: a.role, label_key: a.label_key }]));
}

/** The label of `role` in any offer of `kind` (the first in content order), for the words of a rule set without the page. */
export function roleLabelKey(catalog: Catalog, kind: string, role: string): string | undefined {
  for (const info of catalog.content.offer_infos) {
    if (info.kind !== kind) continue;
    const found = info.answers.find((a) => a.role === role);
    if (found) return found.label_key;
  }
  return undefined;
}

/** The index of the rule answering `kind`, or -1. */
export function kindRuleAt(view: View, kind: string): number {
  return view.orders.findIndex((o) => o.then.kind === "answer_kind" && o.then.offer_kind === kind);
}
