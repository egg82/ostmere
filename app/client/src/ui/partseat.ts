// Where the ledger, the skills and the finished cards sit, by layout (docs/design/opening-screen.md, "Desktop" and
// "Phone"): on a desktop window tall enough the ledger and skills fill the room under the art, on other wide screens
// they sit at the panel's foot, and the finished cards are the Completed tab's. On a phone the ledger and skills are the
// Town tab's and the finished cards the Book's Done page. `laid` hears each placing (a phone, a tall desktop).
import { LOW_UNDER_SCENE, PHONE } from "./layout";

export interface Seats {
  /** Under the art on a tall desktop. */
  low: HTMLElement;
  /** The panel's foot: the ledger and skills go just before it. */
  foot: HTMLElement;
  /** The Town tab's panel. */
  town: HTMLElement;
  /** The Completed tab's panel, and the Book's Done page. */
  done: { tab: HTMLElement; book: HTMLElement };
}

export function seatParts(state: HTMLElement[], finished: HTMLElement, seats: Seats, laid: (phone: boolean, wide: boolean) => void): void {
  const phone = window.matchMedia(PHONE);
  const wide = window.matchMedia(LOW_UNDER_SCENE);
  const place = (): void => {
    if (phone.matches) seats.town.append(...state);
    else if (wide.matches) seats.low.append(...state);
    else seats.foot.before(...state);
    (phone.matches ? seats.done.book : seats.done.tab).append(finished);
    laid(phone.matches, wide.matches);
  };
  phone.addEventListener("change", place);
  wide.addEventListener("change", place);
  place();
}
