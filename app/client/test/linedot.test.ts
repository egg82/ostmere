// A ledger line's quiet dot (decisions/principles.md, the dot rules) clears when the line is touched and stays cleared:
// across views, and across a reload (a Ledger rebuilt over what the account kept).
import { FakeEvent, fakeDocument, install } from "./fake-dom";
import { testContext, TAUGHT } from "./context";
import { Q, R } from "../fixtures/content";
import { fixtureStep } from "../fixtures/steps";
import type { LedgerLine, View } from "../src/api/types";
import { Ledger } from "../src/ui/ledger";
import { keepsOf, type Flat } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AT = 100;
const mid = fixtureStep("mid", AT).view;
const net = -120 * R;
const red: LedgerLine = {   // falling with nothing covering it; the fixture's wood order card answers it
  store: "wood", segment: { start: AT, start_value: 14 * Q, rate: net, limit: 0 }, net_per_hour: net,
  contributions: [{ runner: "tend", per_hour: net }], empties_at: null, fills_at: null, falling: true, covered: false, starved: false, cap: 40 * Q,
};
const view: View = { ...mid, ledger: [red, ...mid.ledger.filter((l) => l.store === "camp")] };

function mount(account: Flat, sent: Flat[] = []): Ledger {
  const part = new Ledger({ ...testContext().ctx, keeps: keepsOf(account, sent) });
  document.body.replaceChildren(part.root);
  return part;
}
const dot = (): boolean => fakeDocument.querySelector(".line > .new-dot") !== null;
const touch = (): void => { fakeDocument.querySelector(".line")?.dispatchEvent(new FakeEvent("pointerdown")); };

{
  const sent: Flat[] = [];
  const part = mount(TAUGHT, sent);
  part.update(view, null);
  expect("a line that asks and can be answered carries the dot", dot(), true);
  touch();
  expect("a touch clears it", dot(), false);
  part.update(view, view);
  expect("the next view leaves it cleared", dot(), false);
  const reloaded = mount(sent.at(-1) ?? TAUGHT);
  reloaded.update(view, null);
  expect("a rebuilt client keeps it cleared", dot(), false);
  const another = mount(TAUGHT);
  another.update(view, null);
  expect("a save that kept nothing still dots the line", dot(), true);
}
