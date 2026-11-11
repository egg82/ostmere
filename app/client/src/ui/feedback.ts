// The Feedback sheet, opened from a quiet button at the panel's foot: a field, a line saying what travels with the words, Send and
// Not now. A send that reaches the server thanks the player and closes the sheet; one that does not says to try
// later and keeps the words. Not now keeps a draft too: it is cleared only by a send.
import { UI } from "../game/text";
import { el, tapFeedback } from "./dom";
import type { PartContext } from "./part";

/** The server's limit on a text (CONTRACT.txt, POST /api/feedback). */
const MAX = 2000;
const THANKS_MS = 1500;

export class FeedbackSheet {
  readonly button = el("button", "feedback-open");
  readonly root = el("dialog", "sheet feedback-sheet");
  private readonly field = el("textarea", "feedback-field");
  private readonly result = el("p", "feedback-result");
  private readonly send = el("button", "primary");
  private sending = false;

  constructor(private readonly ctx: PartContext, private readonly thanksMs = THANKS_MS) {
    const { text } = ctx.catalog;
    this.button.type = "button";
    this.button.textContent = text.get(UI.feedbackOpen);
    this.button.addEventListener("click", () => { tapFeedback(); this.show(); });
    this.field.maxLength = MAX;
    this.field.rows = 6;
    this.field.placeholder = text.get(UI.feedbackPrompt);
    this.field.setAttribute("aria-label", text.get(UI.feedbackPrompt));
    this.field.addEventListener("input", () => this.sync());
    this.result.setAttribute("role", "status");
    this.send.type = "button";
    this.send.textContent = text.get(UI.feedbackSend);
    this.send.addEventListener("click", () => void this.submit());
    const cancel = el("button", "quiet", text.get(UI.feedbackCancel));
    cancel.type = "button";
    cancel.addEventListener("click", () => this.root.close());
    const actions = el("div", "sheet-actions");
    actions.append(cancel, this.send);
    this.root.append(this.field, el("p", "feedback-note", text.get(UI.feedbackNote)), this.result, actions);
    this.root.addEventListener("click", (e) => { if (e.target === this.root) this.root.close(); });
    this.sync();
  }

  private show(): void {
    this.result.textContent = "";
    this.sync();
    this.root.showModal();
  }

  private sync(): void {
    this.send.disabled = this.sending || this.field.value.trim() === "";
  }

  private async submit(): Promise<void> {
    const words = this.field.value.trim();
    if (words === "") return;
    this.sending = true;
    this.result.textContent = "";
    this.sync();
    const kept = await this.ctx.actions.sendFeedback(words);
    this.sending = false;
    if (kept) this.field.value = "";
    this.result.textContent = this.ctx.catalog.text.get(kept ? UI.feedbackThanks : UI.feedbackLater);
    this.sync();
    if (kept) window.setTimeout(() => this.root.close(), this.thanksMs);
  }
}
