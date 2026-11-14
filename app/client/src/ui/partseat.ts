// Where the tabs, the ledger, the skills and the panel's foot sit, by frame (docs/design/opening-screen.md, "Desktop" and
// "Phone"). On a desktop the tabs, the skills and the foot are the left rail's, and the ledger fills the room under the
// art when the window is tall enough, else the panel's foot. On a phone the tabs are the bottom bar (the panel's, fixed
// by game.css) and the ledger and skills are the Town tab's. A landscape phone keeps them all in the panel. `laid` hears
// each placing (a tall desktop).
import { LOW_UNDER_SCENE, PHONE, RAIL } from "./layout";

export interface Parts {
  tabs: HTMLElement;
  ledger: HTMLElement;
  skills: HTMLElement;
  foot: HTMLElement;
}

export interface Seats {
  /** Under the art on a tall desktop. */
  low: HTMLElement;
  /** The desktop's left rail. */
  rail: HTMLElement;
  /** The panel, and its card area, which the tabs sit just before. */
  panel: HTMLElement;
  area: HTMLElement;
  /** The Town tab's panel: the ledger and skills follow the town's own rows there. */
  town: HTMLElement;
}

export function seatParts(parts: Parts, seats: Seats, laid: (wide: boolean) => void): void {
  const queries = [PHONE, RAIL, LOW_UNDER_SCENE].map((q) => window.matchMedia(q));
  const place = (): void => {
    const [phone, rail, wide] = queries.map((q) => q.matches);
    if (rail) seats.rail.append(parts.tabs, parts.skills, parts.foot);
    else seats.panel.insertBefore(parts.tabs, seats.area);
    if (phone) seats.town.append(parts.ledger, parts.skills);
    else if (wide) seats.low.append(parts.ledger);
    else seats.panel.append(parts.ledger);
    if (!rail && !phone) seats.panel.append(parts.skills);
    if (!rail) seats.panel.append(parts.foot);
    laid(wide === true);
  };
  for (const q of queries) q.addEventListener("change", place);
  place();
}
