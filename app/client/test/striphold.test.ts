// The story strip holds the newest line whole (docs/design/opening-screen.md, "One column of attention"): a line waiting
// its turn in the arrival queue (held) leaves the shown one in place; once it shows, it replaces it, in order. The strip
// keeps room for every line the content can write (Content.line_infos), each once, unseen and out of the screen
// reader's way, so the tallest sets its height; a line's arrival touches nothing outside the strip's own list.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fixtureContent } from "../fixtures/content";
import { Catalog } from "../src/game/catalog";
import { Story } from "../src/ui/story";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

let now = 0;
Object.assign(globalThis, { performance: { now: () => now } });

const { ctx } = testContext();
const story = new Story(ctx);
const text = (key: string): string => ctx.catalog.text.get(key);
const list = (): Element[] => Array.from(story.root.querySelector("ol.lines")?.children ?? []);
const shown = (): string[] => list().filter((n) => !n.classList.contains("held")).map((n) => n.textContent ?? "");

// The room: every line key's text once, hidden from sight and from screen readers, beside the list in the strip.
{
  const room = story.root.querySelector("div.strip-room");
  expect("the strip keeps a room", room !== null, true);
  expect("the room is out of the screen reader's way", room?.getAttribute("aria-hidden"), "true");
  const want = [...new Set(fixtureContent.line_infos.map((l) => text(l.key)))];
  expect("the room holds every line the content can write, each once", Array.from(room?.children ?? [], (n) => n.textContent), want);
  expect("the room and the list are the strip's own", [...story.root.children].slice(0, 2).map((n) => n.className), ["strip-room", "lines"]);
  const dup = new Catalog({ ...fixtureContent, line_infos: [...fixtureContent.line_infos, { key: "line.1", kind: "story", cause: null }, { key: "no.such.key", kind: "story", cause: null }] });
  const again = new Story(testContext(undefined, dup).ctx);
  expect("a repeated key or one with no text adds nothing", again.root.querySelector("div.strip-room")?.children.length, want.length);
}

// The newest line, whole and alone; a held one waits without moving it.
{
  story.appendKeys(["line.1"]);
  story.tick(0);
  expect("a line shows", shown(), [text("line.1")]);
  const [waiting] = story.appendKeys(["line.2"], true, true);
  waiting?.classList.add("held");   // as the arrival queue holds it (ui/reveal.ts)
  now = 100;
  story.tick(0);
  expect("a held line leaves the shown one in place", shown(), [text("line.1")]);
  waiting?.classList.remove("held");   // its turn
  story.tick(0);
  expect("at its turn it replaces it", shown(), [text("line.2")]);
  const head = story.head.children.length;
  story.appendKeys(["line.3", "line.4"]);
  story.tick(0);
  expect("several at once outside the queue: the newest", shown(), [text("line.4")]);
  expect("the list holds only the newest", list().map((n) => n.textContent), [text("line.4")]);
  expect("a line's arrival touches nothing in the head", story.head.children.length, head);
}
