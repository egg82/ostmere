// A person's time as the town draws it (townstrip.ts, townedit.ts): a bar split into the cards that hold a share and the
// idle rest, each part as wide as its share, and under it a key naming each part with its share, so a narrow part's name
// is never cut off on a phone.
import { el } from "./dom";

export interface Part { text: string; bp: number; hue: number; idle: boolean }

export function splitOf(parts: Part[]): { bar: HTMLElement; key: HTMLElement } {
  const bar = el("div", "town-shares");
  const key = el("div", "town-key");
  for (const p of parts) {
    const seg = el("span", `town-seg hue-${p.hue}${p.idle ? " idle" : ""}`);
    seg.style.flexGrow = String(p.bp);
    bar.append(seg);
    key.append(el("span", `town-key-item hue-${p.hue}${p.idle ? " idle" : ""}`, p.text));
  }
  return { bar, key };
}
