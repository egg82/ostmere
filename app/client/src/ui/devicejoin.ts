// The sheet's third part: joining this browser to another account, by a code (or its link) or by recovery words. The
// code box is a plain field; the words have a form of their own whose password field a password manager fills. A
// link's code lands in the code box and waits for Join. A device with games of its own is asked whether to move them
// or join without them (MergeAsk), and only its answer sends merge or keep. On 200 the page reloads into GET /api/me,
// after the words of the games it left behind, when it did.
import type { JoinWay, KeptGames } from "../api/types";
import { askLine, joinWith } from "../game/joining";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { DevicesContext } from "./devices";

export class JoinPart {
  readonly root = el("section", "devices-part devices-join");
  readonly code: HTMLInputElement;
  private readonly note = el("p", "devices-note");
  private readonly merging: MergeAsk;

  constructor(private readonly ctx: DevicesContext, user: string, private readonly onKept: (kept: KeptGames) => void) {
    const t = ctx.text;
    this.merging = new MergeAsk(ctx, (typed, way) => this.answer(typed, way));
    const byCode = joinForm(t.get(UI.joinCode), t.get(UI.join), "off", "text");
    this.code = byCode.input;
    this.code.autocapitalize = "characters";
    this.code.spellcheck = false;
    const byWords = joinForm(t.get(UI.joinWords), t.get(UI.join), "current-password", "password", user);
    for (const f of [byCode, byWords]) f.form.addEventListener("submit", (e) => { e.preventDefault(); void this.send(f.input); });
    this.root.append(el("h3", "devices-heading", t.get(UI.joinHeading)), el("p", "devices-lead", t.get(UI.joinLead)),
      byCode.form, byWords.form, this.merging.root, this.note);
  }

  fill(code: string): void {
    this.code.value = code;
    this.merging.hide();
    setText(this.note, "");
    this.code.focus();
  }

  private async send(input: HTMLInputElement): Promise<void> {
    const typed = input.value.trim();
    if (!typed) return;
    this.merging.hide();
    setText(this.note, "");
    const refused = await joinWith(this.ctx.api, typed);
    if (refused?.why === "ask") this.merging.show(typed, refused.wordsReplaced);
    else if (refused !== null) setText(this.note, this.ctx.refusalLine(refused.why, refused.max));
  }

  /** The player chose: the same join again, with merge or keep; on a refusal (the code expired meanwhile, the cap) its
   * line. */
  private async answer(typed: string, way: JoinWay): Promise<void> {
    const refused = await joinWith(this.ctx.api, typed, way, undefined, this.onKept);
    this.merging.hide();
    if (refused !== null) setText(this.note, this.ctx.refusalLine(refused.why, refused.max));
  }
}

/** The question a device with games of its own is asked (confirm_merge): Cancel, Join without moving, or Move my games
 * (the primary one). */
class MergeAsk {
  readonly root = el("div", "devices-ask");
  private typed: string | null = null;
  private readonly answers: HTMLButtonElement[];
  private readonly line = el("p", "devices-note");

  constructor(private readonly ctx: DevicesContext, onAnswer: (typed: string, way: JoinWay) => Promise<void>) {
    const t = ctx.text;
    const move = el("button", "primary", t.get(UI.merge));
    const keep = el("button", "quiet", t.get(UI.keep));
    const no = el("button", "quiet", t.get(UI.mergeCancel));
    this.answers = [move, keep];
    for (const b of [move, keep, no]) b.type = "button";
    for (const [b, way] of [[move, "move"], [keep, "keep"]] as const) {
      b.addEventListener("click", () => {
        if (this.typed === null) return;
        for (const a of this.answers) a.disabled = true;
        void onAnswer(this.typed, way);
      });
    }
    no.addEventListener("click", () => this.hide());
    const actions = el("div", "sheet-actions");
    actions.append(no, keep, move);
    this.root.append(this.line, actions);
    this.root.hidden = true;
  }

  /** `wordsReplaced`: MergeSummary.words_replaced, so the question says this device's words will stop working. */
  show(typed: string, wordsReplaced: boolean): void {
    this.typed = typed;
    setText(this.line, askLine(this.ctx.text, wordsReplaced));
    for (const a of this.answers) a.disabled = false;
    this.root.hidden = false;
    this.answers[0]?.focus();
  }

  hide(): void {
    this.typed = null;
    this.root.hidden = true;
  }
}

interface JoinForm { form: HTMLFormElement; input: HTMLInputElement }

function joinForm(label: string, button: string, autocomplete: string, type: string, user?: string): JoinForm {
  const form = el("form", "devices-joinform");
  if (user !== undefined) {   // the name a saved set of words is filed under, so the password manager offers it
    const name = el("input", "sr");
    name.type = "text";
    name.autocomplete = "username";
    name.value = user;
    name.readOnly = true;
    name.tabIndex = -1;
    name.setAttribute("aria-hidden", "true");
    form.append(name);
  }
  const field = el("label", "devices-field");
  const input = el("input", "devices-input");
  input.type = type;
  input.autocomplete = autocomplete as AutoFill;
  input.maxLength = 200;
  field.append(el("span", "", label), input);
  const go = el("button", "primary", button);
  go.type = "submit";
  form.append(field, go);
  return { form, input };
}
