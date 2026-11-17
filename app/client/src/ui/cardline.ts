// The newest story line at the top of the card column on a desktop (docs/design/opening-screen.md, "The newest line by
// the cards"): the eye is at the cards, so the line the strip just showed is drawn there too, one line, replaced by the next.
// The strip stays the record and the one place that decides what shows (ui/story.ts hands this the strip's newest shown
// line). A phone draws none. Its room is the tallest story line at the column's width, so no line arriving moves a card.
import type { Catalog } from "../game/catalog";
import { inStrip } from "../game/chronicle";
import { el } from "./dom";
import { PHONE } from "./layout";

/** Every story line's text the strip can show (a day's mention among them), each once. */
export function storyTexts({ content, text }: Catalog): string[] {
  const bands = [...content.people?.came ?? [], ...content.people?.went ?? []].flatMap((b) => b.keys);
  return [...new Set([...content.line_infos.filter((l) => inStrip(l.kind)).map((l) => l.key), ...bands].map((k) => text.get(k)).filter((t) => t))];
}

export class CardLine {
  readonly root = el("p", "card-newest");
  private now = el("span", "");
  private text = "";

  /** `texts`: every story line the content can write, laid out unseen so the row is as tall as the tallest. */
  constructor(texts: readonly string[]) {
    const room = el("span", "card-newest-room");
    room.setAttribute("aria-hidden", "true");
    room.append(...texts.map((t) => el("span", "", t)));
    this.root.append(room, this.now);
  }

  /** The line now (the same text again changes nothing, so its fade does not replay). */
  show(text: string): void {
    if (text === this.text) return;
    this.text = text;
    const next = el("span", "", text);
    this.now.remove();
    this.root.append(next);
    this.now = next;
  }

  /** Seated in `panel` just before `before` on a desktop, and out of the page on a phone. */
  seat(panel: HTMLElement, before: HTMLElement): void {
    const phone = window.matchMedia(PHONE);
    const place = (): void => { if (phone.matches) this.root.remove(); else panel.insertBefore(this.root, before); };
    phone.addEventListener("change", place);
    place();
  }
}
