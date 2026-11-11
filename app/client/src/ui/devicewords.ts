// The sheet's second part: recovery words. Made on the player's tap (new words, on a second tap that says the old
// ones stop working), shown once (wordsform.ts).
import { UI } from "../game/text";
import { el, setText } from "./dom";
import { wordsForm } from "./wordsform";
import type { DevicesContext } from "./devices";

export class WordsPart {
  readonly root = el("section", "devices-part devices-words");
  private readonly make = el("button", "quiet");
  private readonly ask = el("p", "devices-note");
  private readonly shown = el("div", "devices-shown");
  private readonly note = el("p", "devices-note");
  private asking = false;

  constructor(private readonly ctx: DevicesContext, private hasWords: boolean) {
    const t = ctx.text;
    this.root.append(el("h3", "devices-heading", t.get(UI.wordsHeading)), el("p", "devices-lead", t.get(UI.wordsLead)),
      this.shown, this.ask, this.make, this.note);
    this.make.type = "button";
    this.make.addEventListener("click", () => void this.tapped());
    this.reset();
  }

  /** Back to the tap that makes words (the sheet reopened). */
  reset(): void {
    this.asking = false;
    this.shown.replaceChildren();
    this.ask.hidden = true;
    setText(this.ask, this.ctx.text.get(UI.wordsReplaceAsk));
    this.make.hidden = false;
    setText(this.make, this.ctx.text.get(this.hasWords ? UI.wordsRemake : UI.wordsMake));
    setText(this.note, "");
  }

  private async tapped(): Promise<void> {
    if (this.hasWords && !this.asking) {
      this.asking = true;
      this.ask.hidden = false;
      return;
    }
    this.make.disabled = true;
    try {
      const made = await this.ctx.api.makeWords();
      this.hasWords = true;
      this.show(made.words, made.label);
    } catch (e) {
      setText(this.note, this.ctx.refusalLine(e));
    } finally {
      this.make.disabled = false;
    }
  }

  private show(words: string, label: string): void {
    this.ask.hidden = true;
    this.make.hidden = true;
    const form = wordsForm(this.ctx.text, words, label, this.note);
    this.shown.replaceChildren(form.form);
    form.save.focus();
  }
}
