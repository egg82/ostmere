// Who a new rule on Camp is for (docs/decisions/mixes.md, "Mine and Camp"): each person whose hands a rule
// can use, by name, as one picker in place of a New rule per kind. With one choice there is nothing to pick. A person is
// offered only while their lane holds a task a rule can do: a rule on Camp does their tasks and no mix.
import type { View } from "../../api/types";
import type { Catalog } from "../../game/catalog";
import { doChoices } from "../../game/ruleoffers";
import { people } from "../../game/town";
import { UI } from "../../game/text";
import { el, tapFeedback } from "../dom";
import type { PartContext } from "../part";

/** A person's lane. */
export interface Who {
  lane: string;
}

export function whoChoices(ctx: PartContext, view: View): Who[] {
  const { catalog } = ctx;
  return people(catalog, view).filter((lane) => laneRulable(catalog, view, lane)).map((lane) => ({ lane }));
}

/** Whether a new rule for `lane` on Camp would offer anything to do. */
export function laneRulable(catalog: Catalog, view: View, lane: string): boolean {
  return doChoices(catalog, view, false, null, "camp", lane).length > 0;
}

export function whoPicker(ctx: PartContext, view: View, pick: (who: Who) => void, close: () => void): HTMLElement[] {
  const { catalog } = ctx;
  const head = el("div", "cond-head");
  const x = el("button", "editor-close", "✕");
  x.type = "button";
  x.setAttribute("aria-label", catalog.text.get(UI.close));
  x.addEventListener("click", close);
  head.append(el("h2", "panel-heading cond-heading", catalog.text.get(UI.ruleNew)), x);
  const row = el("div", "cond-mixes rules-who");
  for (const who of whoChoices(ctx, view)) {
    const b = el("button", "quiet cond-task", catalog.laneLabel(who.lane, view));
    b.type = "button";
    b.addEventListener("click", () => { tapFeedback(); pick(who); });
    row.append(b);
  }
  return [head, row];
}
