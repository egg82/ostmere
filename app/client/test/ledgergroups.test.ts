// The ledger's groups (docs/design/redesign.md, "Ledger"; ui/ledger.ts): the player's stores under Yours, the threats at
// them under Threats, each label drawn only while its group has a row, and the labels in that order.
import { install } from "./fake-dom";
import { testContext } from "./context";
import { fightsStep } from "../fixtures/fights";
import { fixtureStep } from "../fixtures/steps";
import { Ledger } from "../src/ui/ledger";
import { keepsOf, NEW_FLAT } from "./kept";

install();

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const shown = (part: Ledger): string[] =>
  Array.from(part.root.querySelectorAll(".ledger-group"), (n) => (n as HTMLElement).hidden ? "" : n.textContent ?? "").filter((t) => t !== "");
const fresh = (): Ledger => new Ledger({ ...testContext().ctx, keeps: keepsOf(NEW_FLAT, []) });

{
  const part = fresh();
  part.update(fixtureStep("mid", 100).view, null);
  expect("stores and no threat: Yours alone", shown(part), ["Yours"]);
}

{
  const part = fresh();
  part.update(fightsStep("fightlater", 100).view, null);
  expect("a standing fight too: Yours, then Threats", shown(part), ["Yours", "Threats"]);
  part.setSplit(true);
  part.tick(100);
  expect("a phone with its only line moved above the cards: Threats alone", shown(part), ["Threats"]);
}

{
  const part = fresh();
  part.update({ ...fixtureStep("mid", 100).view, ledger: [] }, null);
  expect("no row in any group: no label", shown(part), []);
}
