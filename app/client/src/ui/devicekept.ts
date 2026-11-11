// The step after a join that left this browser's games on their old account (CONTRACT.txt, "Moving to another
// device", keep). The browser is already the other account's, so this is the one place the old account's recovery words
// can be shown: the words the join made, or, when the account had some, what to do with them. Continue reloads into the
// other account. The sheet is held open on it (devices.ts), as closing it would leave the page drawing games of an
// account this browser has left.
import type { KeptGames } from "../api/types";
import { UI } from "../game/text";
import { el } from "./dom";
import type { DevicesContext } from "./devices";
import { wordsForm } from "./wordsform";

export class KeptPart {
  readonly root = el("section", "devices-part devices-kept");

  constructor(private readonly ctx: DevicesContext, private readonly reload: () => void = () => location.reload()) {
    this.root.hidden = true;
  }

  show(kept: KeptGames): void {
    const t = this.ctx.text;
    const note = el("p", "devices-note");
    const done = el("button", "primary", t.get(UI.keptDone));
    done.type = "button";
    done.addEventListener("click", this.reload);
    const parts: HTMLElement[] = [el("h3", "devices-heading", t.get(UI.keptHeading)),
      el("p", "devices-lead", t.get(kept.words === null ? UI.keptHad : UI.keptNew))];
    if (kept.words !== null) parts.push(wordsForm(t, kept.words, kept.label, note).form, note);
    const actions = el("div", "sheet-actions");
    actions.append(done);
    this.root.replaceChildren(...parts, actions);
    this.root.hidden = false;
    done.focus();
  }
}
