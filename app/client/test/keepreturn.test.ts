// A save keeps the newest MAX_VISITS returns: the oldest go as new ones are kept, and a merge with the server's answer trims too.
import { MAX_VISITS } from "../src/game/loggroups";
import { Keeps } from "../src/game/keeps";
import { mergeSavePresentation } from "../src/game/presentation";
import { NEW_SAVE } from "../src/game/keeps";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const AWAY = 100_000;
const visit = (n: number) => ({ left: n * AWAY, back: n * AWAY + 5000 });
const run = (n: number) => Array.from({ length: n }, (_, i) => visit(i));

const keeps = new Keeps({ save: { ...NEW_SAVE, visits: run(MAX_VISITS) } });
keeps.keepReturn(MAX_VISITS * AWAY, MAX_VISITS * AWAY + 5000);
expect("the newest are kept, the oldest dropped", keeps.visits(), run(MAX_VISITS + 1).slice(1));

const few = new Keeps({ save: { ...NEW_SAVE, visits: run(2) } });
few.keepReturn(2 * AWAY, 2 * AWAY + 5000);
expect("within the limit all stay", few.visits(), run(3));

const merged = mergeSavePresentation({ ...NEW_SAVE, visits: run(MAX_VISITS) }, { ...NEW_SAVE, visits: [visit(MAX_VISITS)] });
expect("a merge keeps the newest too", merged.visits, run(MAX_VISITS + 1).slice(1));
