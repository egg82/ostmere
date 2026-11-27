// Each cast role's person, read from the view's unlocked features at each draw (contract/casting.txt, "CASTING"): a role's
// slot is the cast lane's name, lowercased in a line as a lane's slot is, and stays as written while no feature of the role
// is held. The page never guesses a person.
import type { Content } from "../../api/types";

export class Roles {
  private readonly lanes: Map<string, { lane: string; feature: string }[]>;
  private picked = new Map<string, string>();

  constructor(content: Content, private readonly names: Map<string, string>, private readonly lines: Set<string>) {
    this.lanes = new Map(content.cast_infos.map((c) => [c.role, c.lanes]));
  }

  cast(unlocked: readonly { category: string; id: string }[]): void {
    const held = new Set(unlocked.filter((u) => u.category === "feature").map((u) => u.id));
    this.picked = new Map([...this.lanes].flatMap(([role, lanes]) => {
      const lane = lanes.find((l) => held.has(l.feature))?.lane;
      return lane === undefined ? [] : [[role, lane] as const];
    }));
  }

  fill(key: string, text: string): string {
    if (this.picked.size === 0) return text;
    return text.replace(/\{(\w+)\}/g, (slot, role: string) => {
      const name = this.names.get(this.picked.get(role) ?? "");
      if (name === undefined) return slot;
      return this.lines.has(key) ? name.toLowerCase() : name;
    });
  }
}
