// The device's sound switch (audio/mute.ts) as two controls that always agree: a speaker button on the scene's head, and a
// "Sound" checkbox in Settings. Neither is made while only the Null sound is registered (audio/locator.ts).
import { hasSound, refreshSilence } from "../audio/locator";
import type { SoundSwitch } from "../audio/mute";
import { UI, type Text } from "../game/text";
import { el } from "./dom";

export interface SoundControl {
  /** The speaker: named by the state it is in, and a tap flips it. */
  button: HTMLButtonElement;
  /** The Settings row for the same switch. */
  row: HTMLLabelElement;
  /** Draw what the switch holds now (a sheet reopened, a page loaded). */
  show(): void;
}

/** Null while no sound is registered, so the caller draws nothing and leaves no gap. */
export function soundControl(text: Text, mute: SoundSwitch): SoundControl | null {
  if (!hasSound()) return null;
  const button = el("button", "sound-button");
  button.type = "button";
  const input = el("input", "settings-sound");
  input.type = "checkbox";
  const row = el("label", "settings-choice");
  row.append(input, el("span", "", text.get(UI.soundRow)));
  const show = (): void => {
    const on = mute.get();
    const name = text.get(on ? UI.soundOn : UI.soundOff);
    button.setAttribute("aria-label", name);
    button.title = name;
    button.textContent = "♪";
    button.classList.toggle("off", !on);
    input.checked = on;
  };
  const set = (on: boolean): void => { mute.set(on); refreshSilence(); show(); };   // storage that kept nothing shows as on
  button.addEventListener("click", () => set(!mute.get()));
  input.addEventListener("change", () => set(input.checked));
  show();
  return { button, row, show };
}
