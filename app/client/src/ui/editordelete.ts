// The mix editor's Delete (editor.ts): asks once, in place; a mix a rule runs, or nested in another, says so instead.
import type { View } from "../api/types";
import { mixNamedBy } from "../game/mix";
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** What the Delete slot holds for saved mix `from`: a note, the button, or the question with Yes and No. `ask` redraws
 * the slot asking or not; `deleted` follows a Yes. */
export function deleteParts(ctx: PartContext, view: View, from: string, asking: boolean, ask: (on: boolean) => void,
  deleted: () => void): HTMLElement[] {
  const { text } = ctx.catalog;
  const named = mixNamedBy(view, from);
  if (named) return [el("span", "editor-note", text.get(named === "order" ? UI.namedByOrder : UI.nested))];
  if (!asking) {
    const del = el("button", "quiet danger", text.get(UI.deleteMix));
    del.type = "button";
    del.addEventListener("click", () => ask(true));
    return [del];
  }
  const yes = el("button", "quiet danger", text.get(UI.yes));
  const no = el("button", "quiet", text.get(UI.no));
  yes.type = no.type = "button";
  yes.addEventListener("click", () => { tapFeedback(); ctx.actions.decide({ kind: "delete_mix", mix_id: from }); deleted(); });
  no.addEventListener("click", () => ask(false));
  return [el("span", "editor-note", text.get(UI.deleteAsk)), yes, no];
}
