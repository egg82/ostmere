// The recovery words as the player is shown them, once, inside a username-and-password form so the browser offers to
// save them (habits' showOwnKey): Save submits it, through the Credential Management API where there is one. Copy
// says in `note` when it fails and never puts the words anywhere but here. Shared by the words part (devicewords.ts) and
// the step after a join that left games behind (devicekept.ts).
import { UI, type Text } from "../game/text";
import { el, setText } from "./dom";

export function wordsForm(t: Text, words: string, label: string, note: HTMLElement): { form: HTMLFormElement; save: HTMLButtonElement } {
  const form = el("form", "devices-wordsform");
  form.action = "/";
  form.method = "get";
  const user = hiddenInput("text", "username", label);
  const pass = hiddenInput("password", "new-password", words);
  const list = el("p", "devices-words-list");
  for (const w of words.split("-")) list.append(el("span", "", w));
  const save = el("button", "primary", t.get(UI.wordsSave));
  save.type = "submit";
  const copy = el("button", "quiet", t.get(UI.wordsCopy));
  copy.type = "button";
  copy.addEventListener("click", () => {
    const done = navigator.clipboard ? navigator.clipboard.writeText(words) : Promise.reject(new Error("no clipboard"));
    done.then(() => setText(note, t.get(UI.wordsCopied)), () => setText(note, t.get(UI.wordsCopyFailed)));
  });
  const row = el("div", "sheet-actions");
  row.append(copy, save);
  form.append(user, pass, list, el("p", "devices-note", t.get(UI.wordsNote)), row);
  form.addEventListener("submit", (e) => storeCredential(e, label, words));
  return { form, save };
}

function hiddenInput(type: string, autocomplete: string, value: string): HTMLInputElement {
  const input = el("input", "sr");
  input.type = type;
  input.autocomplete = autocomplete as AutoFill;
  input.value = value;
  input.readOnly = true;
  input.tabIndex = -1;
  input.setAttribute("aria-hidden", "true");
  return input;
}

/** Chrome saves through PasswordCredential and the page stays; elsewhere the form submits to "/", which a password
 * manager notices, and the page reloads into the game. */
function storeCredential(e: SubmitEvent, label: string, words: string): void {
  const PC = (window as Window & { PasswordCredential?: new (d: object) => Credential }).PasswordCredential;
  if (!PC || !navigator.credentials) return;
  e.preventDefault();
  void navigator.credentials.store(new PC({ id: label, password: words, name: label })).catch(() => undefined);
}
