// Who a new rule on Camp is for (docs/decisions/mixes.md, "Mine and Camp"): the town and each person whose hands a rule
// can use, by name, as one picker in place of a New rule per kind. With one choice there is nothing to pick.
import type { View } from "../api/types";
import { townCanSwitch, townRules, people } from "../game/town";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** The town (its mixes, once it has a second to switch to and a rule of its own) or a person's lane. */
export interface Who {
  town?: true;
  lane?: string;
}

export function whoChoices(ctx: PartContext, view: View): Who[] {
  const { catalog } = ctx;
  return [...(townRules(catalog, view).length > 0 && townCanSwitch(catalog, view) ? [{ town: true as const }] : []), ...people(catalog, view).map((lane) => ({ lane }))];
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
    const b = el("button", "quiet cond-task", who.town ? catalog.text.get(UI.townTitle) : catalog.laneLabel(who.lane ?? "", view));
    b.type = "button";
    b.addEventListener("click", () => { tapFeedback(); pick(who); });
    row.append(b);
  }
  return [head, row];
}
