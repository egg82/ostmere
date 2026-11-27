# Ashfall art sourcing

Sourced (not LLM-drawn) art for the map, the field journal and UI icons. Licences matter little for a personal homelab game; each is noted in one line. "Opened" means the page was fetched; "snippet" means only a search-result summary was seen. Resolution is unstated on most pages, so check a sample file before committing.

Verdict in short: map = Widman PNG pack (free); icons = game-icons.net restricted to one author; **journal sketches = no pack gives one hand across creatures, plants, tools and eldritch things, so commission a set** and use public-domain engravings as a stopgap.

## 1. Hand-inked fantasy map stamps

| Candidate | URL (opened) | Price | Format | Assets | Coherent? | Licence | Fit |
|---|---|---|---|---|---|---|---|
| Widman 2.1 (K.M. Alexander) | https://kmalexander.com/tag/georgio-widman/ | free | ABR + individual PNG pack (2 MB zip); PNG resolution not stated | 500+: 100 mountains, 50 ranges, 50 trees, 50 forests, villages/towns/cities/forts, river crossings, hills with settlements | Yes, one 1680 engraved-map source style | CC0 | Best: real engraved-map symbols read as old ink on parchment. Mountain-heavy. Small 2 MB suggests low resolution; no ruins or compass listed |
| Wuggy's Classic Cartography Set | https://wuggy.itch.io/wuggys-classic-cartography-set | $1.50+ | ABR + 12 MB ImageAssets.zip of PNGs; resolution not stated | 342 (grass, trees, forests, swamps, mountains, houses, castles, bridges) | Yes, one hand | CC BY 4.0 | Good "handmade classic fantasy map" look, a bit softer/cartoonier than engraving |
| Tolkien-inspired Vintage Assets Pack (fantasymapassets.com) | https://fantasymapassets.com/product/tolkien-the-lord-of-the-rings-inspired-vintage-assets-pack-and-other-fantasy-inspirations-complete-pack/ | EUR 13.50 | Transparent PNG, B&W PNG, colour PNG; resolution not stated | 110+ (27 settlements incl. ruined cities and gallows, 7 tree types incl. dead trees, 7 mountain types) | Yes | Commercial use OK, no credit needed | Best theme match (ruins, dead trees, gallows) but only ~110 assets |

Not opened (snippet only): Janssonius 2.0 PNG pack (same author as Widman, free), amanz "fantasy map assets" on itch.io. Nothing found bundles parchment, compass or coastline stamps; parchment texture and compass need a separate source (a public-domain engraved compass rose is the easy route).

Tried 2026-10-11 (`map-test/compose_map.py`): stamps run 23–502 px, fine at phone scale; the engraved mountains, forests and settlements read as real ink. Rivers and routes are still drawn in code and look it.

**Recommendation: Widman 2.1 PNG pack, plus the Tolkien-inspired pack's ruins/dead trees if the Widman set lacks them.** Free, CC0, one coherent engraved style, and hundreds of variants so a growing map doesn't repeat. Verify PNG size before building on it.

## 2. Field-journal ink sketches (make-or-break)

Requirement: dozens of entries in one hand, covering real animals, invented/eldritch creatures, plants, tools and places.

### Packs and public-domain sources

| Candidate | URL (opened) | Price | Format | Assets | Coherent? | Licence | Fit |
|---|---|---|---|---|---|---|---|
| Walthall's Monsters Vol. 1 (Axebane) | https://axebane.itch.io/monsters-fantasy-stock-art-volume-1 | $10+ | 300 DPI PNG | 16 | One artist, hand-inked line art, no gen-AI | Commercial OK, credit required, can't resell | Right technique (old-school ink), but only 16 and all D&D staples (bugbear, gelatinous cube, lich); no plants, tools, places |
| DieselShot Monsters Stock Art Pack (Patrice Long) | https://dieselshot.itch.io/monster-stock-art-pack | $15+ | PNG 2500x3000, 300 dpi, transparent + white versions | 33 files (26 designs) | Page claims nothing about style; technique not stated | Commercial OK, attribution required, void for use with gen-AI | Names like "Frog Whale", "Worm Swarm" suggest original/eldritch designs and horror marketing. Viewing the previews is the only way to judge ink quality |
| Fantasy in Monokrom (Diane Ramic) Vol. 1 | https://diantimony.itch.io/fantasy-in-monokrom-ink-art-by-diane-ramic-vol-1 | $4+ | 67 MB PDF, textless | 140+ pieces | One artist, B&W ink | Personal use only; commercial via her DTRPG listings | Most pieces for the money, includes monsters; extracting from PDF is clumsy and humanoid heroes dominate |
| Odds and Ents Adventuring Sketches | https://oddsandents.itch.io/adventuring-sketches-art-pack | $4.20+ | black transparent PNG | 20 | One artist | Commercial OK, credit requested | Objects only (potions, books, dagger, goggles); "sketchy" iPad style. Usable for the "tools" slice only |
| Old Book Illustrations | https://www.oldbookillustrations.com/ | free | not stated | not stated | Many artists, so not coherent as a set | Terms page returned 404; unverified | Browsable by subject (Animals); genuine period engravings, but each source book is a different hand |
| Gessner Historia animalium woodcuts (Wellcome) | https://wellcomecollection.org/works/hm9n4tvw (from a search result; snippet only) | free | scans | few hundred plates in the source work | One woodcut tradition, still many cutters | Public Domain Mark per snippet | Excellent grimdark texture, includes odd creatures in the wider Gessner/Aldrovandi corpus |

Not verified: Biodiversity Heritage Library, rawpixel and Wikimedia Commons pages were not opened (one Commons URL 404ed, one BHL/rawpixel search returned nothing usable). The Royal Society Aldrovandi dragon plates are "(c) The Royal Society", so not clearly free.

No pack found covers real animals, invented eldritch creatures, plants, tools and places in one hand. The best-matching technique (Walthall) is 16 D&D monsters. Public-domain engravings are free and atmospheric but are many hands, need cut-out and cleanup (paper background to transparent), and will not include an invented Ashfall creature.

### Commissioning a consistent set

Prices below were seen on the cited pages unless marked snippet.

| Artist / marketplace | URL | What it offers | Price seen |
|---|---|---|---|
| uncommoncritter (carrd, opened) | https://uncommoncritter.carrd.co/ | Fantasy creature sketches with hatching; ink wash option | Sketch $90, +$40 greyscale shading; small ink "Gremlin Badge" doodles $20 (lineart) / $30 |
| Creature-specialist artist (snippet from a carrd search result, not opened) | https://skyjynx.carrd.co/ | Creature sketch / render / design sheet | $65 sketch, $165 render, design sheet from $240 |
| Pen-and-ink illustrator (snippet, page not identified or opened) | n/a | Spot art priced by size; says linework is consistent across projects | GBP 40-100 spot, 120-180 half page |
| Dribbble spot illustration services (snippet) | https://dribbble.com/services/search/spot-illustration | Studio-style packages | From about $150-600 per listing; one 4-piece B&W package from $500 |
| Fiverr pen-and-ink category | https://block.fiverr.com/hire/pen-ink-illustration | redirected to the homepage; no prices seen | unknown |

Planning arithmetic (derived, not quoted): 40 entries at $20-90 each is roughly $800-3,600, or $125/piece at the Dribbble-package rate is $5,000. Commissioning the whole set from one artist is what guarantees "one hand, one pen". Cheaper: commission 8-10 anchor pieces (an eldritch creature, a plant, a tool, a place, a wolf) to fix the style, then judge whether the same artist's bulk rate works. Ask for a per-piece rate for a batch, a style test on two of your creatures first, and a usage grant covering game use. Terms were not visible on the uncommoncritter page (its ToS is a separate section).

Stopgap tried 2026-10-11 (`journal-test/ink_engraving.py`): a Gessner hound (Wikimedia Commons, Internet Archive scan) cropped, paper dropped and ink recoloured reads as a real journal sketch at phone size. Commons' Gessner scans are full pages, mostly fish; finding each animal is manual.

Code-drawn test 2026-10-11 (`sketch-test/`, Opus with a render-and-look loop, `notes.md` has its verdict): the journal page furniture (notes, arrows, side studies, a crossed-out first try) works. An invented creature passed as pretty decent. A wolf failed until it was drawn the way a person draws (gesture line, construction masses in measured proportions, contour over them, construction left faint, then noise): `wolf2.png` reads as a wolf and passes as a quick study, still with stiff legs and uniform marks.

**Decided 2026-10-11:** the code-drawn pipeline (`sketch-test/process.md`) is good enough to build on; commissioning is for final art where it slips. The original recommendation follows.

**Recommendation: commission one ink artist for the full set, starting with a 3-5 piece paid test that includes one invented creature.** No sourced pack reaches the coherence and coverage the journal needs. For a zero-cost stopgap, use cleaned Gessner/Old Book engravings for real animals and keep placeholders for invented ones. Cheap interim fill: DieselShot's pack (after viewing previews) for eldritch monsters only.

## 3. UI icons (line/silhouette; Time Fantasy pixel set already owned)

| Candidate | URL (opened) | Price | Format | Assets | Coherent? | Licence | Fit |
|---|---|---|---|---|---|---|---|
| game-icons.net | https://game-icons.net/about.html | free | SVG (PNG only planned), monochrome, recolourable | about 4,180 by author count (Delapouite 2,022, Lorc 1,429, many others) | Mixed: dozens of authors, but Lorc and Delapouite share a similar white-on-black silhouette style | CC BY 3.0, credit authors | Strong fantasy vocabulary (candle, scroll, ore, skull, map) and fits dark UI. Restrict to the two main authors for consistency |
| Lucide | https://lucide.dev/license | free | SVG stroke icons | about 1,800 (snippet count only) | Yes, one design language | ISC | Clean consistent nav icons, but modern/UI-flavoured, not grimdark; no fantasy resource glyphs like ore or candles |
| Phosphor | none opened (snippet only) | free | SVG, 6 weights | 1,200+ base (snippets disagree) | Yes | MIT (snippet) | Same tradeoff as Lucide, more variety |

Not checked: RPG Awesome (search returned nothing).

**Recommendation: game-icons.net, picking every icon from Lorc and Delapouite only,** with credit in an about screen. It is the only option with fantasy-specific candle, ore, scrap and scroll glyphs; the cost is that you must curate by author for coherence. Use Lucide only if you want neutral nav icons.

## Budget used

12 searches and 15 fetches. Several pages were unreachable or unverified (listed above); no files were downloaded and no image quality was inspected, so "fit" judgements are from page descriptions, not looking at the art.
