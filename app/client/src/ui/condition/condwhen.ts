// The condition editor's When row as the draft calls for it (condition.ts, drawWhen).
import type { ChipInfo, View } from "../../api/types";
import type { Catalog } from "../../game/catalog";
import { quickRunning, ruleCards, subjectChoices, whenChoices } from "../../game/ruleoffers";
import type { SubjectRule } from "../../game/subjectrule";
import type { Draft } from "./conditiondraft";
import { whenRow } from "./condrows";
import { quickRunningRows, subjectRows } from "./condsubject";

export interface WhenPicks {
  chip: (c: ChipInfo) => void;
  store: (s: string) => void;
  subject: (r: SubjectRule) => void;
}

/** The When row's elements for `draft`: the chips, stores and subjects offered (the few running cards most relevant,
 * or `full`, every subject); none for a chip's rule being
 * changed or while nothing is offered. */
export function draftWhenRow(catalog: Catalog, view: View, full: boolean, draft: Draft | null, pick: WhenPicks): HTMLElement[] {
  const editing = draft?.index === null || draft?.subject ? null : draft?.rule.store ?? null;
  const offer = whenChoices(catalog, view, full, ruleCards(view, draft?.then ?? null), editing);
  const actions = draft ? [draft.then, ...draft.orElse] : [];
  const subjects = full ? subjectRows(catalog, view, subjectChoices(catalog, view, actions), pick.subject)
    : quickRunningRows(catalog, view, quickRunning(catalog, view, actions, ruleCards(view, draft?.then ?? null)), pick.subject);
  return draft?.chip === true ? [] : whenRow(catalog, offer.chips, offer.stores, pick.chip, pick.store, subjects);
}
