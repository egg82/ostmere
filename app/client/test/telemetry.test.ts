// The leave beacon: one report per leave (a close fires visibilitychange then pagehide), carrying the last card actually tapped.
import { initTelemetry, noteBegin, noteEnd, stepHeaders } from "../src/telemetry";

const handlers = new Map<string, Array<() => void>>();
const on = (name: string, f: () => void): void => { handlers.set(name, [...(handlers.get(name) ?? []), f]); };
const fire = (name: string): void => handlers.get(name)?.forEach((f) => f());
const sent: Array<{ kind: string; last_project: string | null; reached_end: number }> = [];
const doc = { visibilityState: "visible", addEventListener: on, head: { appendChild: () => undefined } };
Object.assign(globalThis, {
  window: { addEventListener: on },
  document: doc,
  fetch: () => Promise.resolve(new Response("", { status: 404 })),
});
Object.defineProperty(globalThis, "navigator", {
  configurable: true,
  value: { sendBeacon: (_url: string, blob: Blob) => { void blob.text().then((t) => sent.push(JSON.parse(t) as never)); return true; } },
});

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}
const settle = () => new Promise((r) => setTimeout(r, 5));

initTelemetry();
noteBegin();
stepHeaders({ kind: "tap_card", card: "gather_wood" });
stepHeaders({ kind: "tap_card", card: "scavenge" });
stepHeaders({ kind: "switch_mix", mix_id: "m" });   // not a card: the last card stays

doc.visibilityState = "hidden";
fire("visibilitychange");
fire("pagehide");
await settle();
check(sent.length === 1, `one report for one close, got ${sent.length}`);
check(sent[0]?.last_project === "scavenge", `the last card tapped, got ${sent[0]?.last_project}`);

doc.visibilityState = "visible";
fire("visibilitychange");
doc.visibilityState = "hidden";
fire("visibilitychange");
await settle();
check(sent.length === 2, `coming back and leaving again reports again, got ${sent.length}`);

// A leave after the end says the end was reached.
check(sent[1]?.reached_end === 0, `reached_end before the end, got ${sent[1]?.reached_end}`);
noteEnd();
doc.visibilityState = "visible";
fire("visibilitychange");
doc.visibilityState = "hidden";
fire("visibilitychange");
await settle();
check(sent.length === 3, `a third leave, got ${sent.length}`);
check(sent[2]?.reached_end === 1, `reached_end after the end, got ${sent[2]?.reached_end}`);
