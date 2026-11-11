// The "Another device" sheet's first part: a transfer code, large, with its QR code on a light tile and how long it
// still works; once it has expired, a way to make a new one. A code is made when the sheet opens for it.
import type { TransferCode } from "../api/types";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { DevicesContext } from "./devices";
import { qrSvg } from "./qr";

export class CodePart {
  readonly root = el("section", "devices-part devices-code");
  private readonly code = el("p", "devices-code-text");
  private readonly tile = el("div", "qr-tile");
  private readonly note = el("p", "devices-note");
  private readonly again = el("button", "quiet");
  private endsAt = 0;
  private timer: number | null = null;

  constructor(private readonly ctx: DevicesContext) {
    this.root.append(el("p", "devices-lead", ctx.text.get(UI.codeLead)), this.code, this.tile, this.note, this.again);
    this.again.type = "button";
    this.again.textContent = ctx.text.get(UI.codeNew);
    this.again.addEventListener("click", () => void this.make());
    this.again.hidden = true;
  }

  async make(): Promise<void> {
    this.stop();
    this.again.hidden = true;
    let made: TransferCode;
    try {
      made = await this.ctx.api.makeCode();
    } catch (e) {
      this.failed(e);
      return;
    }
    setText(this.code, made.transfer_code);
    this.tile.replaceChildren(qrSvg(made.qr, made.transfer_code));
    this.tile.hidden = false;
    this.endsAt = performance.now() + made.expires_in_s * 1000;
    this.tick();
    this.timer = window.setInterval(() => this.tick(), 1000);
  }

  /** The sheet closed: no countdown runs unseen. */
  stop(): void {
    if (this.timer !== null) window.clearInterval(this.timer);
    this.timer = null;
  }

  private tick(): void {
    const left = Math.ceil((this.endsAt - performance.now()) / 1000);
    if (left > 0) {
      setText(this.note, this.ctx.text.fill(UI.codeNote, { d: this.ctx.format.duration(left) }));
      return;
    }
    this.stop();
    setText(this.code, "");
    this.tile.replaceChildren();
    this.tile.hidden = true;
    setText(this.note, this.ctx.text.get(UI.codeGone));
    this.again.hidden = false;
  }

  private failed(e: unknown): void {
    setText(this.code, "");
    this.tile.hidden = true;
    setText(this.note, this.ctx.refusalLine(e));
    this.again.hidden = false;
  }
}
