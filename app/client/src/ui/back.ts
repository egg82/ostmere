// The back gesture: every screen, sheet or editor the player opens is a Layer, and while it is open the page holds one
// history entry for it, so the platform's back (the browser's, or the Android wrapper's, a Trusted Web Activity that
// hands back to the browser's history) arrives as a popstate that closes the top layer. With nothing open there is no
// entry and back leaves the page as the platform does. Layers open and close in any order; the history catches up to
// the stack one step at a time (a traversal is async, and a push issued before it lands would be undone by it).
interface State { ostmere?: number }

const stack: Layer[] = [];
/** The history entries the page holds above its own. */
let depth = 0;
/** A history.back() of ours is in flight: the popstate it brings is not the player's. */
let backing = false;
let listening = false;

export class Layer {
  /** `close` brings the layer's screen down by the player's back; it need not tell the layer. */
  constructor(private readonly close: () => void) {}

  get open(): boolean {
    return stack.includes(this);
  }

  /** The layer's screen is shown (true) or gone (false); says nothing new when it already is. */
  set(on: boolean): void {
    const at = stack.indexOf(this);
    if (on === at >= 0) return;
    if (on) stack.push(this);
    else stack.splice(at, 1);
    catchUp();
  }

  /** The player's back reached this layer. */
  closeByBack(): void {
    this.close();
  }
}

function catchUp(): void {
  if (typeof history === "undefined" || typeof history.pushState !== "function") return;
  if (!listening) {
    listening = true;
    window.addEventListener("popstate", (e) => popped((e as PopStateEvent).state as State | null));
  }
  if (backing) return;
  while (depth < stack.length) history.pushState({ ostmere: ++depth } satisfies State, "");
  if (depth > stack.length) {
    backing = true;
    history.back();
  }
}

function popped(state: State | null): void {
  depth = state?.ostmere ?? 0;
  if (backing) backing = false;
  else for (let n = stack.length - depth; n > 0 && stack.length > 0; n--) stack.pop()!.closeByBack();   // the player's back, or several entries skipped at once
  catchUp();
}

const sheets = new WeakMap<HTMLDialogElement, Layer>();

/** Shows a sheet (a modal dialog) as a layer: back closes it, and so does anything else that closes it. */
export function openSheet(dialog: HTMLDialogElement): void {
  let layer = sheets.get(dialog);
  if (!layer) {
    const made = new Layer(() => dialog.close());
    layer = made;
    sheets.set(dialog, made);
    dialog.addEventListener("close", () => made.set(false));
  }
  dialog.showModal();
  layer.set(true);
}
