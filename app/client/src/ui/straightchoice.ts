// A choice the player keeps as a checkbox: "Skip the front page on this device" (app/straight.ts), on the front page and
// in the Games sheet, and "Skip lessons in every game" (the account's lessons setting), in the Games sheet.
import type { Straight } from "../app/straight";
import { UI, type Text } from "../game/text";
import { el } from "./dom";

export interface StraightChoice {
  root: HTMLLabelElement;
  /** Show what is kept now (a sheet reopened, a page loaded). */
  show(): void;
}

/** The checkbox for `choice` (the same shape as Straight: what is kept, and keeping it), labelled `label`. */
export function checkChoice(label: string, choice: Straight, labelClass: string, inputClass: string): StraightChoice {
  const input = el("input", inputClass);
  input.type = "checkbox";
  input.addEventListener("change", () => {
    choice.set(input.checked);
    input.checked = choice.get();   // storage that kept nothing shows as off
  });
  const root = el("label", labelClass);
  root.append(input, el("span", "", label));
  return { root, show: () => { input.checked = choice.get(); } };
}

export function straightChoice(text: Text, straight: Straight, labelClass: string, inputClass: string): StraightChoice {
  return checkChoice(text.get(UI.gameStraight), straight, labelClass, inputClass);
}
