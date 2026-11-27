// The stores a rule is about (game/relevant.ts): read off the cards' served makes and takes alone, never their names.
// The planted content gives smoking the catch a card one step out on each side, a card that only shares its input,
// a maker it does not know yet, and a card whose name shares a word with a store it has nothing to do with.
import { fixtureContent } from "../fixtures/content";
import type { Content } from "../src/api/types";
import { Catalog } from "../src/game/page/catalog";
import { relevantStores } from "../src/game/condition/relevant";

function expect(label: string, got: unknown, want: unknown): void {
  if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`${label}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
}

const content: Content = structuredClone(fixtureContent);
const base = content.card_infos.find((c) => c.card === "forage")!;
const plant = (card: string, makes: string[], takes: string[]) => content.card_infos.push({ ...base, card, label_key: `card.${card}`, makes, takes });
plant("eat_smoked", ["warmth"], ["smoked"]);   // uses what smoking makes
plant("fish", ["catch"], ["wood"]);            // makes what smoking takes, not in play yet
plant("dry_stones", ["stone"], []);            // "Dry the stones": nothing to do with dry wood
content.store_infos.push({ ...content.store_infos[0]!, store: "dry_wood", label_key: "store.dry_wood", made_by: [] });
content.text_entries.push({ key: "card.dry_stones", text: "Dry the stones" }, { key: "store.dry_wood", text: "dry wood" });
const catalog = new Catalog(content);
expect("control: the planted names share a word", [catalog.cardLabel("dry_stones"), catalog.storeLabel("dry_wood")], ["Dry the stones", "dry wood"]);

const stores = ["wood", "warmth", "stone", "damp_wood", "catch", "smoked", "roots", "dry_wood"];
const known = ["smoke_catch", "smoke_roots", "woodcutting", "forage", "eat_smoked", "dry_stones"];

expect("smoking the catch: what it makes, what it takes (in the stores' order), then one step out",
  relevantStores(catalog, ["smoke_catch"], known, stores), { makes: ["smoked"], takes: ["damp_wood", "catch"], near: ["warmth"] });
expect("a card that only shares an input is not one step out, and a maker not in play brings nothing",
  relevantStores(catalog, ["smoke_catch"], known, stores).near.includes("roots") || relevantStores(catalog, ["smoke_catch"], known, stores).near.includes("wood"), false);
expect("once the maker is in play, what it takes is one step out",
  relevantStores(catalog, ["smoke_catch"], [...known, "fish"], stores).near, ["wood", "warmth"]);
expect("a name never pulls a store in", relevantStores(catalog, ["dry_stones"], known, stores), { makes: ["stone"], takes: [], near: [] });
expect("only offered stores: a store the cards make that is not offered is left out",
  relevantStores(catalog, ["smoke_catch"], known, ["catch", "wood"]), { makes: [], takes: ["catch"], near: [] });
expect("several cards (a mix): each store once, in its first tier; smoking roots makes what eating takes",
  relevantStores(catalog, ["smoke_catch", "eat_smoked"], known, stores), { makes: ["warmth", "smoked"], takes: ["damp_wood", "catch"], near: ["roots"] });
expect("no cards, nothing relevant", relevantStores(catalog, [], known, stores), { makes: [], takes: [], near: [] });
