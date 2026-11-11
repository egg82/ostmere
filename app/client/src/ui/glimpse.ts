// The front page's stage: the game's own Scene (scene/scene.ts) drawn behind the panel, cropped around the fire at a
// whole-number scale, its light following the visitor's hour. With no save to show it is a canned moment of the game
// working (camp-views.ts): the figure alternates between two jobs, and a ledger line ticks. A selected save's own camp
// replaces the canned one while it is selected. The Scene does all the drawing.
import type { Content, View } from "../api/types";
import { el, reducedMotion } from "./dom";
import { hoursNow, daylight } from "../scene/light";
import { UI, type Text } from "../game/text";
import { cannedView } from "./camp-views";
import type { Pictures } from "./pictures";

const JOBS = ["lay_to_dry", "woodcutting"];   // the figure's turns: at the fire, then out to the trees
const TURN_MS = 7000;
const LIGHT_MS = 60_000;
const FIRE: [number, number] = [270, 222];
const HOLD: [number, number] = [0.5, 0.58];   // the fire sits a little below the middle
const STORE = "damp_wood";
const PER_MIN = 11;   // canned: the line climbs this many a minute, shown as a rate
const START = 9;
const CAP = 12;

export interface Stage {
  /** Draw this save's own camp; null goes back to the canned moment. */
  show(view: View | null): void;
}

export function glimpse(box: HTMLElement, chip: HTMLElement, pictures: Pictures | null, text: Text, content: Content): Stage {
  ticking(chip, text, content);
  const scene = pictures?.scene(box);
  if (!pictures || !scene) return { show: () => undefined };
  const q = pictures.quantityPerItem;
  scene.cropTo({ hold: HOLD, focus: FIRE });
  let turn = 0;
  let mine: View | null = null;
  const canned = (): View => cannedView(JOBS[turn % JOBS.length] ?? "", q);
  scene.update(canned());
  let since = performance.now();
  let lightAt = since;
  let last = since;
  const frame = (now: number): void => {
    if (!box.isConnected || document.body.classList.contains("playing")) return;
    if (now - lightAt >= LIGHT_MS) { lightAt = now; scene.setLight(daylight(hoursNow())); }
    if (!mine && now - since >= TURN_MS && !reducedMotion()) {   // still: the first view stays, no cycling
      since = now;
      turn += 1;
      scene.update(canned());
    }
    if (document.visibilityState === "visible") scene.draw(mine ? mine.at : now / 1000, Math.min(0.1, (now - last) / 1000));
    last = now;
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  return { show: (view) => { mine = view; scene.update(view ?? canned()); } };
}

/** The ledger line over the scene: a store's name, its amount climbing, its rate. */
function ticking(chip: HTMLElement, text: Text, content: Content): void {
  const label = content.store_infos.find((i) => i.store === STORE)?.label_key ?? "";
  const amount = el("b", "", String(START));
  chip.replaceChildren(`${text.get(label)} `, amount, el("span", "rate", `+${text.fill(UI.perMinute, { n: String(PER_MIN) })}`));
  let n = START * 60;
  const tick = (): void => {
    if (!chip.isConnected) return;
    n = n >= CAP * 60 ? START * 60 : n + PER_MIN;
    amount.textContent = String(Math.floor(n / 60));
    setTimeout(tick, 1000);
  };
  setTimeout(tick, 1000);
}
