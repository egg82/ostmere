// The self-update's decision: reload only for a new build, at a quiet moment, backing off a build that keeps coming back.
import { BACKOFF_MS, QUIET_MS, counted, decide, type Moment } from "../src/app/selfupdate";

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

const base: Moment = { booted: "a", served: "b", tries: {}, now: 1_000_000, idleMs: QUIET_MS, interacted: true, held: false };

check(decide({ ...base, served: "a" }) === "current", "the same build is current");
check(decide({ ...base, booted: null }) === "current", "nothing known yet is current");
check(decide(base) === "reload", "a new build after a quiet stretch reloads");
check(decide({ ...base, idleMs: QUIET_MS - 1 }) === "wait", "a player still playing is not interrupted");
check(decide({ ...base, idleMs: 0, interacted: false }) === "reload", "an untouched page reloads at once");
check(decide({ ...base, held: true }) === "wait", "an open sheet holds the reload");
const once = counted({}, "b", base.now);
check(decide({ ...base, tries: once }) === "backoff", "a build reloaded for and still served waits");
check(decide({ ...base, tries: once, now: base.now + (BACKOFF_MS[0] ?? 0) }) === "reload", "then tries again");
const all = counted(counted(counted({}, "b", 0), "b", 0), "b", 0);
check(decide({ ...base, tries: all, now: 10 ** 12 }) === "gave-up", "after every backoff it gives up");
let many = {};
for (let i = 0; i < 12; i += 1) many = counted(many, `v${i}`, i);
check(Object.keys(many).length === 8 && "v11" in many && !("v0" in many), "only the eight latest builds are kept");
