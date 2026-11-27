// One task can take the whole of a mix: a divider beside the idle rest reaches 100% by drag and by arrow key, the task
// keeps 1% while it stays, and a person at 100% (no idle left) can drag down or add a task, which takes its slice from theirs.
import { fakeDocument, type FakeEl, FakeEvent, install, pointer } from "./fake-dom";
import { pageRig } from "./personrig";
import { townStep } from "../fixtures/town";
import type { Decision, Mix, View } from "../src/api/types";
import { ShareBar } from "../src/ui/mixes/sharebar";

install();
Object.assign(globalThis, { ResizeObserver: class { observe(): void { /* no layout here */ } } });

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const BP = 10_000;
const WIDTH = 300;

/** The one node mounted on the page: a real-typed root seen as the fake element it is. */
function mounted(root: HTMLElement): FakeEl {
  document.body.replaceChildren(root);
  const node = fakeDocument.body.firstElementChild;
  if (!node) throw new Error("nothing mounted");
  return node;
}

/** A task and the idle rest (marked idle by its spec, whatever its label), and every share set it commits. */
function bar(task: number): { divider: FakeEl; commits: number[][]; bar: ShareBar } {
  const commits: number[][] = [];
  const b = new ShareBar("large", BP, (bp) => String(bp), { commit: (s) => commits.push(s) });
  b.set([{ key: "a", label: "a", hue: 0 }, { key: "idle", label: "rest", hue: 5, idle: true }], [task, BP - task]);
  const top = mounted(b.root);
  const track = top.querySelector(".share-track");
  const divider = top.querySelector(".share-divider");
  if (!track || !divider) throw new Error("the bar drew no track or divider");
  track.rect = { left: 0, top: 0, width: WIDTH, height: 8, right: WIDTH, bottom: 8 };
  return { divider, commits, bar: b };
}

{  // the task beside idle drags to the end and takes it all
  const { divider, commits } = bar(5000);
  divider.dispatchEvent(new FakeEvent("pointerdown", { pointerId: 1, clientX: WIDTH / 2 }));
  divider.dispatchEvent(new FakeEvent("pointermove", { clientX: WIDTH * 2 }));
  divider.dispatchEvent(new FakeEvent("pointerup"));
  expect("dragged to the end", commits, [[10_000, 0]]);
}
{  // and by arrow key, one percent a press
  const { divider, commits } = bar(9000);
  for (let i = 0; i < 15; i++) divider.dispatchEvent(new FakeEvent("keydown", { key: "ArrowRight" }));
  expect("keys reach the end", commits[commits.length - 1], [10_000, 0]);
  expect("ten presses, then no more", commits.length, 10);
}
{  // the task never drops below 1% while it stays; idle may go back to nothing and return
  const { divider, commits } = bar(10_000);
  divider.dispatchEvent(new FakeEvent("pointerdown", { pointerId: 1, clientX: WIDTH }));
  divider.dispatchEvent(new FakeEvent("pointermove", { clientX: -WIDTH }));
  divider.dispatchEvent(new FakeEvent("pointerup"));
  expect("dragged to the start", commits, [[100, 9900]]);
}

const both = townStep("town").view;   // helper: chop 60%, haul 30%, 10% idle; mason: hew 70%, carve 20%

function opened(view: View) {
  const rig = pageRig(view);
  rig.open(0);
  return rig;
}

/** The town mix with the helper holding chop alone at `chop`. */
function chopAlone(chop: number): View {
  const alone = (m: Mix): Mix => ({ ...m, components: m.components.filter((c) => c.kind !== "card_share" || c.card !== "haul").map((c) => (c.kind === "card_share" && c.card === "chop" ? { ...c, share_bp: chop } : c)) });
  return { ...both, mixes: both.mixes.map((m) => (m.id === "town:main" ? alone(m) : m)) };
}
const shares = (d: Decision | undefined, card: string): number[] => (d?.kind === "save_mix" ? d.mix.components.flatMap((c) => (c.kind === "card_share" && c.card === card ? [c.share_bp] : [])) : []);

{  // a person's one task drags to 100% and the let-go sends it with no idle
  const { page, got } = opened(chopAlone(9000));
  const divider = page.querySelectorAll(".share-divider")[0] as FakeEl;
  divider.dispatchEvent(pointer("pointerdown", 900, 10));
  divider.dispatchEvent(pointer("pointermove", 1000, 10));
  divider.dispatchEvent(pointer("pointerup", 1000, 10));
  expect("the let-go sends 100%", shares(got.decided[0], "chop"), [10_000]);
}
{  // from 100% the task drags down, idle reappearing
  const { page, got } = opened(chopAlone(10_000));
  const dividers = page.querySelectorAll(".share-divider");
  expect("a divider beside the empty idle", dividers.length, 1);
  const divider = dividers[0] as FakeEl;
  divider.dispatchEvent(pointer("pointerdown", 1000, 10));
  divider.dispatchEvent(pointer("pointermove", 400, 10));
  divider.dispatchEvent(pointer("pointerup", 400, 10));
  expect("the task came down", shares(got.decided[0], "chop"), [4000]);
}
{  // from 100% a task can be added; it takes its slice from the one there, as the hands' editor does
  const { face, got } = opened(chopAlone(10_000));
  face("haul").querySelector(".card-tap")?.click();
  expect("an equal slice from the task", [shares(got.decided[0], "chop"), shares(got.decided[0], "haul")], [[5000], [5000]]);
}
