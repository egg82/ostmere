// The Feedback sheet (src/ui/feedback.ts): Send waits for words, a kept send thanks and closes, one that is not kept says
// to try later and keeps the words, Not now keeps a draft, and the screen puts the button in the panel's foot and sends what
// the player wrote.
import { FakeEvent, fakeDocument, install, type FakeEl } from "./fake-dom";
import { testContext } from "./context";
import { dayOneStep } from "../fixtures/dayone";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { Keeps } from "../src/game/keeps";
import { FeedbackSheet } from "../src/ui/feedback";
import { Screen } from "../src/ui/screen";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const catalog = new Catalog(fixtureContent);
const text = (key: string): string => catalog.text.get(key);
const later = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 5));

function found(selector: string): FakeEl {
  const node = fakeDocument.querySelector(selector);
  if (!node) throw new Error(`nothing on the page matches ${selector}`);
  return node;
}

/** The sheet's controls, looked up on the fake page. */
function controls() {
  return {
    open: found("button.feedback-open"), dialog: found("dialog.feedback-sheet"), field: found("textarea"),
    send: found("button.primary"), cancel: found("button.quiet"), result: found("p.feedback-result"), note: found("p.feedback-note"),
  };
}

function write(field: FakeEl, words: string): void {
  field.value = words;
  field.dispatchEvent(new FakeEvent("input"));
}

function rig(kept = true) {
  const { ctx, got } = testContext(undefined, catalog);
  ctx.actions.sendFeedback = (words) => { got.feedback.push(words); return Promise.resolve(kept); };
  const sheet = new FeedbackSheet(ctx, 0);
  const holder = document.createElement("div");
  holder.append(sheet.button, sheet.root);
  document.body.replaceChildren(holder);
  return { ...controls(), got };
}

{  // the words on the sheet are the content's
  const r = rig();
  expect("the button", r.open.textContent, text("ui.feedback.open"));
  expect("the note says what travels with the words", r.note.textContent, text("ui.feedback.note"));
  expect("Send", r.send.textContent, text("ui.feedback.send"));
  expect("Not now", r.cancel.textContent, text("ui.feedback.cancel"));
}
{  // Send waits for words; a kept send thanks, clears the field, and closes
  const r = rig();
  r.open.click();
  expect("opening shows the sheet", r.dialog.open, true);
  expect("no words, no Send", r.send.disabled, true);
  write(r.field, "   \n ");
  expect("spaces are no words", r.send.disabled, true);
  write(r.field, "  the third tap felt wrong \n");
  expect("words enable Send", r.send.disabled, false);
  r.send.click();
  expect("a second press while sending sends nothing more", r.send.disabled, true);
  r.send.click();
  await later();
  expect("the words go trimmed, once", r.got.feedback, ["the third tap felt wrong"]);
  expect("a thank-you", r.result.textContent, text("ui.feedback.thanks"));
  expect("the field is cleared", r.field.value, "");
  expect("and the sheet closes", r.dialog.open, false);
  r.open.click();
  expect("opened again it is clean", [r.result.textContent, r.send.disabled], ["", true]);
}
{  // not kept (limited, or no answer): says to try later, keeps the words and the sheet
  const r = rig(false);
  r.open.click();
  write(r.field, "words");
  r.send.click();
  await later();
  expect("try later", r.result.textContent, text("ui.feedback.later"));
  expect("the words stay", r.field.value, "words");
  expect("the sheet stays", r.dialog.open, true);
  expect("Send is there to try again", r.send.disabled, false);
}
{  // Not now closes and keeps the draft; the backdrop does the same
  const r = rig();
  r.open.click();
  write(r.field, "half a thought");
  r.cancel.click();
  expect("Not now closes", r.dialog.open, false);
  r.open.click();
  expect("the draft is still there", [r.field.value, r.send.disabled], ["half a thought", false]);
  r.dialog.click();
  expect("the backdrop closes", r.dialog.open, false);
  expect("and sent nothing", r.got.feedback, []);
}
{  // on the screen: at the panel's foot, and what the player writes reaches the page's sender
  const sent: string[] = [];
  const screen = new Screen(catalog, () => undefined, () => Promise.resolve(null), new Keeps(), (words) => { sent.push(words); return Promise.resolve(true); });
  document.body.replaceChildren(screen.root);
  screen.show(dayOneStep("returned", 100));
  expect("the Feedback button sits in the panel's foot", found(".panel-foot").children.map((n) => n.className), ["feedback-open"]);
  expect("and not with the chips beside the Log", found(".scene-head").querySelector(".feedback-open"), null);
  const r = controls();
  r.open.click();
  write(r.field, "the screen's words");
  r.send.click();
  await later();
  expect("the screen's sender got them", sent, ["the screen's words"]);
}
