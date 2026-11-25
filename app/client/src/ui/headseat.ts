// Where the story's parts sit around the art (docs/design/opening-screen.md, "Desktop" and "Phone"). The head (the Camp
// bar and chips): in the stage just above the art, so the art is never under it however many rows it grows. The aim, just above the art: under the head in the stage on a phone, over the art's column on a
// desktop. The story strip, under
// the art: at the stage's foot on a phone (the stage's pinned part), between the stage and the skills and ledger on a desktop.
// On a phone the root also learns the stage's height (--scene-vh, its exact fractional height: offsetHeight rounds, and a panel laid on the rounded value leaves a seam)
// and the strip's (--stage-pin): game.css pins only the strip at the stage's foot, so the head and the art scroll away
// with the page and come back at its top, and lays the panel against the strip.
// On a desktop it learns the head's height (--head-h), which the skills and ledger under the art give up, not the art.
import { PHONE } from "./layout";

export function seatHead(root: HTMLElement, stage: HTMLElement, head: HTMLElement, aim: HTMLElement, strip: HTMLElement): void {
  const phone = window.matchMedia(PHONE);
  const place = (): void => {
    if (phone.matches) {
      stage.prepend(head, aim);
      stage.append(strip);
    } else {
      stage.prepend(head);
      stage.before(aim);
      stage.after(strip);
    }
    measure();
  };
  const measure = (): void => {
    if (phone.matches) {
      root.style.setProperty("--scene-vh", `${stage.getBoundingClientRect().height}px`);
      root.style.setProperty("--stage-pin", `${strip.getBoundingClientRect().height}px`);
      root.style.removeProperty("--head-h");
    } else {
      root.style.setProperty("--head-h", `${head.getBoundingClientRect().height}px`);
      root.style.removeProperty("--scene-vh");
      root.style.removeProperty("--stage-pin");
    }
  };
  phone.addEventListener("change", place);
  const watch = new ResizeObserver(measure);
  watch.observe(stage);
  watch.observe(head);
  watch.observe(strip);
  place();
}
