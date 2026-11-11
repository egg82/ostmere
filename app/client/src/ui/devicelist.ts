// The Another device sheet's last part: the account's browsers (CONTRACT.txt, "Your devices"), asked for afresh each
// time the sheet opens. One row each: its label, a mark on the one asking, when it was last used, and Remove. Removing
// another browser redraws from the answer; removing this one asks first, and once it is done the page starts again
// from GET /api/me (the session is gone, so it lands on the front page).
import { ApiFailure } from "../api/api";
import type { Device, Devices } from "../api/types";
import { dateOf } from "../game/format";
import { UI } from "../game/text";
import { el, setText } from "./dom";
import type { DevicesContext } from "./devices";

export class DeviceList {
  readonly root = el("section", "devices-part devices-list");
  private readonly list = el("ul", "games-list");
  private readonly note = el("p", "devices-note");
  private devices: Devices | null = null;
  private asking: number | null = null;   // the row whose Remove asks once more (this browser's)
  private busy = false;

  constructor(private readonly ctx: DevicesContext, private readonly reload: () => void = () => location.reload()) {
    const t = ctx.text;
    this.note.setAttribute("role", "status");
    this.root.append(el("h3", "devices-heading", t.get(UI.listHeading)), el("p", "devices-lead", t.get(UI.listLead)),
      this.list, this.note);
  }

  /** Back to the plain list, asked for again (the sheet opened). */
  open(): void {
    this.asking = null;
    setText(this.note, "");
    void this.run(() => this.ctx.api.devices());
  }

  /** `signedOut`: the ask removes this browser, so once it is answered the page starts again. */
  private async run(ask: () => Promise<Devices>, signedOut = false): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    this.sync();
    try {
      const answer = await ask();
      if (signedOut) {
        this.reload();
        return;
      }
      this.devices = answer;
      this.asking = null;
      setText(this.note, "");
    } catch (e) {
      setText(this.note, e instanceof ApiFailure && e.code === "not_found" ? "" : this.ctx.text.get(UI.devicesAway));
      if (e instanceof ApiFailure && e.code !== "network") this.devices = await this.ctx.api.devices().catch(() => this.devices);
    } finally {
      this.busy = false;
      this.draw();
    }
  }

  private draw(): void {
    this.list.replaceChildren(...(this.devices?.devices ?? []).map((d) => this.row(d)));
    this.sync();
  }

  private sync(): void {
    for (const b of this.list.querySelectorAll<HTMLButtonElement>("button")) b.disabled = this.busy;
  }

  private row(d: Device): HTMLLIElement {
    const t = this.ctx.text;
    const li = el("li", d.this_device ? "games-row playing" : "games-row");
    const what = el("p", "games-what");
    what.append(el("span", "games-name", d.label));
    if (d.this_device) what.append(el("span", "games-playing", t.get(UI.listThis)));
    li.append(what, el("p", "games-dates", t.fill(UI.listSeen, { seen: dateOf(d.last_seen_at) })));
    const act = el("div", "games-actions");
    if (this.asking === d.device_id) {
      li.append(el("p", "games-ask", t.get(UI.listRemoveAsk)));
      act.append(this.tap("quiet", UI.listRemoveNo, () => { this.asking = null; this.draw(); }),
        this.tap("primary", UI.listRemoveYes, () => this.remove(d)));
    } else {
      act.append(this.tap("quiet", UI.listRemove, () => {
        if (d.this_device) { this.asking = d.device_id; this.draw(); } else this.remove(d);
      }));
    }
    li.append(act);
    return li;
  }

  private remove(d: Device): void {
    void this.run(() => this.ctx.api.removeDevice(d.device_id), d.this_device);
  }

  private tap(className: string, key: string, then: () => void): HTMLButtonElement {
    const b = el("button", className, this.ctx.text.get(key));
    b.type = "button";
    b.addEventListener("click", then);
    return b;
  }
}
