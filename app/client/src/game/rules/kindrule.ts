// The answer rule (contract/offers.txt, "Offers"): one rule per offer kind, "answer this way whenever someone asks it again".
// The page offers to build it only once an offer of the kind has been answered, and only while an offer of the kind is
// still to be answered (after the last, the rule would wait for an ask that never comes), and names each role by the kind's own
// label for it, written for whoever asks. Reads the view and the content only.
import type { View } from "../../api/types";
import type { Catalog } from "../page/catalog";

/** One button of the builder: a role of the kind, worded by the kind's label for it. */
export interface RoleChoice { role: string; label_key: string | undefined }

/** The kinds the builder is offered for, in content order: those with an offer answered in the view and an offer of the
 * content still to answer (open, or not yet shown). */
export function answeredKinds(catalog: Catalog, view: View): string[] {
  const done = new Set(view.offers.filter((o) => o.answer !== null).map((o) => o.offer));
  const left = new Set(catalog.content.offer_infos.filter((o) => o.kind !== null && !done.has(o.offer)).map((o) => o.kind));
  const kinds: string[] = [];
  for (const o of view.offers) {
    const kind = catalog.offers.get(o.offer)?.kind ?? null;
    if (o.answer !== null && kind !== null && left.has(kind) && !kinds.includes(kind)) kinds.push(kind);
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

/** The kind's roles, in the order its last answered offer lists its answers, each with the kind's label. */
export function roleChoices(catalog: Catalog, view: View, kind: string): RoleChoice[] {
  const answers = catalog.offers.get(lastAnswered(catalog, view, kind) ?? "")?.answers ?? [];
  return answers.flatMap((a) => (a.role === null ? [] : [{ role: a.role, label_key: roleLabelKey(catalog, kind, a.role) }]));
}

/** The kind's own label for `role`: the words of a rule answering every future ask of the kind. */
export function roleLabelKey(catalog: Catalog, kind: string, role: string): string | undefined {
  return catalog.content.offer_kinds.find((k) => k.kind === kind)?.roles.find((r) => r.role === role)?.label_key;
}

/** The index of the rule answering `kind`, or -1. */
export function kindRuleAt(view: View, kind: string): number {
  return view.orders.findIndex((o) => o.then.kind === "answer_kind" && o.then.offer_kind === kind);
}
