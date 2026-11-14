"""Build the preview's scene: graded PNG layers, a manifest the page reads, and one composite per stage to judge by.

    python tools/scene/build.py            # layers + manifest into $ASHFALL_ASSETS/art/scene/, composites into
                                           # $ASHFALL_ASSETS/previews/scene/ (default ~/.local/share/ostmere/assets)
Needs Pillow and the Time Fantasy packs (~/src/time-fantasy, or TIME_FANTASY=...). Deterministic: one seed, no clock.

Output never goes in git or the image (docs/engineering.md): the assets tree is seeded onto the volume the pods
mount, and the page fetches the manifest from /assets/art/scene/manifest.json.
"""
from __future__ import annotations

import hashlib
import random

from PIL import Image, ImageChops

import dayone
import depth
import dayone_poses
import dayeight_layers as d8
import dayeleven_layers as d11
import daytwelve_layers as d12
import dayfour_layers as d4
import daythree_layers as d3
import daytwo_layers as d2
import dayone_world as world
import kit
import night
import props
import trips
from figures import figure
from output import OUT, Entry, Layer, bake, check_conditions, check_depth, write_manifest, write_previews
from parts import (EAVE, EAVE_Y, ROOF_X, at_fire, base, birch, campfire_split, carrying, cleared, damp_heap, dry_stack, fireback, firelight,
                   rack, ruin, seated_at_work, stones_heap, stool, wood_drying)
from place import BY_FIRE, GAP, H, LIE, LIP, LOWEST_HEAD, RIDGE, RUBBLE, SEAT, SLAB, W, WALL_REST
from tints import WOOD

SEED = 7


GATHER = "running:gather_wood|running:woodcutting|mix:gather_wood|mix:woodcutting"
SCAVENGE = "running:scavenge|running:forage|mix:scavenge|mix:forage"
AWAY = f"{GATHER}|{SCAVENGE}|{d3.AWAY_JOBS}|{d4.AWAY_JOBS}"
"""The hands are out working: the figure is at the gap or the rubble, so the resting poses step aside."""
KNAP, ROAST, READ, REST = ("running:knap_edge", "running:roast_roots|running:stew", "running:read_by_fire",
                           "running:rest|mix:rest")
DOING = f"{KNAP}|{ROAST}|{READ}|{REST}"
"""The hands are busy at the fire (or resting at the wall): the idle poses give way to the one pose for the job."""


def on_stool(jobs: str) -> str:
    """Any of `jobs` while the stool stands: each term gets its own `&` (which binds tighter than `|`)."""
    return "|".join(f"{job}&feature:stool" for job in jobs.split("|"))


SNARE, LOOK, SIT_UP = "running:set_snare", "running:look_out", "running:sit_up"
BUILDS = {"lean_to": "running:build_lean_to", "larder": "running:build_larder", "smoke_rack": "running:build_smoke_rack"}
ELSEWHERE = "|".join([SNARE, LOOK, *BUILDS.values(), *d2.HANDS_AWAY, *trips.away(trips.TRIPS), *d3.HANDS_AWAY,
                       *d4.HANDS_AWAY, *d8.HANDS_AWAY, *d11.HANDS_AWAY, *d12.HANDS_AWAY])
"""The hands jobs away from the fire (day one's, then day two's): the seated pose gives way while one runs."""
SMOKING = "running:smoke_catch|running:smoke_roots"
BIRCH = "project:woodcutting|running:n1_cut"


def layers(rng: random.Random) -> list[Layer]:
    """Every layer in draw order. `when` shows it, `until` hides it again (see the manifest's `conditions`)."""
    walls = ruin().getchannel("A")
    return [*_ground_layers(rng, walls), *_player_layers(), *_people_layers(walls), *_light_layers()]


def _ground_layers(rng: random.Random, walls: Image.Image) -> list[Layer]:
    """The ruin and the world beyond it, then everything on the ground: heaps, the fire, the builds."""
    ring, laid = campfire_split("camp_campfire_unlit")
    _, lit = campfire_split("camp_campfire_lit")
    made = {"lean_to": dayone.lean_to(), "larder": dayone.larder(WOOD), "smoke_rack": dayone.smoke_rack()}
    backdrop, rim_haze = base(rng)
    return [
        Layer(id="ruin", img=backdrop, when="always"),
        Layer(id="rim_haze", img=rim_haze, when="always"),
        *[Layer(id=f"valley_fog_{i + 1}", img=img, when="project:look_out") for i, img in enumerate(world.valley_fog(walls))],
        *[Layer(id=f"stream_steam_{i + 1}", img=img, when="project:look_out")
          for i, img in enumerate(world.stream_steam(walls))],
        Layer(id="ridge_shape", img=world.ridge_shape(walls), when="feature:morning", until="feature:night_2_sound"),
        *d2.world_layers(walls),
        *d3.world_layers(walls),
        *d4.world_layers(walls),
        *d8.world_layers(walls),
        Layer(id="roof_posts", img=dayone.roof_posts(EAVE_Y, int(LIP) + 2 + EAVE, (ROOF_X[0] + 24, ROOF_X[1] - 14)),
              when="always"),
        Layer(id="cleared", img=cleared(rng), when="pushes:clear_spot@2"),
        Layer(id="prints", img=world.prints(world.PRINTS), when="feature:prints"),
        Layer(id="damp_wood_1", img=damp_heap(0), when="store:damp_wood"),
        Layer(id="damp_wood_2", img=damp_heap(1), when="store:damp_wood@4"),
        Layer(id="damp_wood_3", img=damp_heap(2), when="store:damp_wood@8"),
        Layer(id="stones_1", img=stones_heap(0), when="store:stones"),
        Layer(id="stones_2", img=stones_heap(1), when="store:stones@3"),
        Layer(id="stones_3", img=stones_heap(2), when="store:stones@6"),
        Layer(id="dry_wood_1", img=dry_stack(0), when="store:dry_wood"),
        Layer(id="dry_wood_2", img=dry_stack(1), when="store:dry_wood@4"),
        Layer(id="wood_drying", img=wood_drying(), when="running:lay_to_dry"),
        Layer(id="rack", img=rack(), when="running:lay_to_dry|project:lay_to_dry"),
        Layer(id="fireback", img=fireback(), when="project:build_fireback"),
        Layer(id="ring", img=at_fire(ring), when="project:ring_it"),
        Layer(id="fire_laid", img=at_fire(laid), when="project:ring_it", until="project:strike_fire"),
        *d3.hearth_layers(),
        *d4.hearth_layers(),
        Layer(id="fire_lit", img=at_fire(lit), when="project:strike_fire", ungraded=True),
        Layer(id="stool", img=stool(), when="feature:stool"),
        *d3.under_layers(),
        Layer(id="lean_to", img=made["lean_to"], when="feature:lean_to"),
        Layer(id="larder", img=made["larder"], when="feature:larder"),
        Layer(id="smoke_rack", img=made["smoke_rack"], when="feature:smoke_rack"),
        *[Layer(id=f"{b}_ghost", img=dayone.ghost(made[b]), when=c, until=f"feature:{b}") for b, c in BUILDS.items()],
        *d2.made_layers(),
        *d3.made_layers(),
        *d4.made_layers(),
        *d8.made_layers(),
        *d11.made_layers(),
        *d12.made_layers(),
        *d4.hang_layers(dayone.meat_on_rack()),
    ]


def _player_layers() -> list[Layer]:
    """The player's own poses, day one's."""
    return [
        Layer(id="figure_lying", img=figure("dead", LIE), when="always", until="pushes:stand_up@1"),
        Layer(id="figure_arm", img=figure("status (2)", LIE), when="pushes:stand_up@1", until="pushes:stand_up@2"),
        Layer(id="figure_knees", img=figure("crouch (3)", LIE), when="pushes:stand_up@2", until="pushes:stand_up@3"),
        Layer(id="figure_up", img=figure("hit (1)", (LIE[0], LIE[1] + 2)), when="pushes:stand_up@3",
             until=f"project:strike_fire|{AWAY}|{REST}"),
        Layer(id="figure_by_fire", img=figure("status (1)", BY_FIRE, flip=True),
             when="project:strike_fire", until=f"{AWAY}|{DOING}|feature:stool"),
        Layer(id="figure_on_stool", img=figure("crouch (1)", SEAT, tweak=props.seated),
             when="feature:stool", until=f"{AWAY}|{DOING}|{ELSEWHERE}|{SIT_UP}"),
        Layer(id="figure_knapping", img=figure("crouch (3)", BY_FIRE, flip=True, held=[(props.flint(), 4, -14)]),
             when=KNAP, until=f"{AWAY}|feature:stool"),
        Layer(id="figure_knapping_seated", img=seated_at_work("crouch (3)", (props.flint(), 4, -14)),
             when=on_stool(KNAP), until=AWAY),
        Layer(id="figure_roasting", img=figure("crouch (2)", BY_FIRE, flip=True, held=[(props.root_on_stick(), 8, -24)]),
             when=ROAST, until=f"{AWAY}|feature:stool"),
        Layer(id="figure_roasting_seated", img=seated_at_work("crouch (2)", (props.root_on_stick(rising=True), 4, -40)),
             when=on_stool(ROAST), until=AWAY),
        Layer(id="figure_reading", img=figure("crouch (1)", BY_FIRE, flip=True, held=[(props.book(), 5, -30)]),
             when=READ, until=f"{AWAY}|feature:stool"),
        Layer(id="figure_reading_seated", img=seated_at_work("crouch (1)", (props.book(), 5, -30)),
             when=on_stool(READ), until=AWAY),
        Layer(id="figure_resting", img=figure("status (3)", WALL_REST, flip=True),
             when=REST, until=AWAY),
        Layer(id="figure_gathering", img=carrying(GAP), when=GATHER),
        Layer(id="figure_scavenging", img=figure("crouch (2)", RUBBLE, flip=True), when=SCAVENGE, until=GATHER),
        Layer(id="figure_sitting_up", img=dayone_poses.sitting_up(), when=SIT_UP, until=AWAY),
        Layer(id="figure_looking_out", img=dayone_poses.looking_out(), when=LOOK, until=AWAY),
        *[Layer(id=f"figure_building_{b}", img=dayone_poses.building(b), when=c, until=AWAY) for b, c in BUILDS.items()],
    ]


def _people_layers(walls: Image.Image) -> list[Layer]:
    """Lucy's first poses, the birch and the snares, every later day's figures, the beasts, the fog and the smoke."""
    return [
        Layer(id="figure_n1_walking", img=dayone_poses.n1_walking(), when="running:take_stock", until="feature:n1"),
        Layer(id="figure_n1_by_fire", img=dayone_poses.n1_by_fire(), when="feature:n1", until=d2.N1_BUSY),
        Layer(id="birch_log", img=birch(0), when=BIRCH),
        Layer(id="birch_stump", img=birch(1), when=BIRCH),
        *d8.birch_layers(birch(0), birch(1), BIRCH),
        *d12.birch_layers(birch(0), birch(1), BIRCH),
        *[Layer(id=f"snare_{i + 1}", img=dayone.snare(i), when=f"pushes:set_snare@{i + 1}") for i in range(3)],
        Layer(id="figure_snaring", img=dayone_poses.snaring(), when=SNARE, until=AWAY),
        *d2.figure_layers(AWAY, f"{d3.N1_JOBS}|{d4.N1_FAR}"),
        *d3.figure_layers(AWAY),
        *d4.figure_layers(AWAY),
        *d8.figure_layers(AWAY),
        *d11.figure_layers(AWAY),
        *d12.figure_layers(AWAY),
        *d4.creature_layers(),
        *d4.fog_layers(walls),
        Layer(id="smoke_plume", img=world.smoke_plume(ImageChops.lighter(walls, rack().getchannel("A"))), when=SMOKING),
    ]


def _light_layers() -> list[Layer]:
    """The lights over everything, then the ash in the air."""
    return [
        Layer(id="firelight", img=firelight(0.55), when="project:strike_fire", blend="screen", ungraded=True),
        Layer(id="firelight_fireback", img=firelight(0.25), when="project:build_fireback", blend="screen", ungraded=True),
        Layer(id="firelight_dusk", img=firelight(0.7), when="end:showing", until="feature:morning", blend="screen", ungraded=True),
        *d2.light_layers(),
        *d3.light_layers(),
        *d4.light_layers(),
        *d8.light_layers(),
        *d11.light_layers(),
        *d12.light_layers(),
        Layer(id="crack_glow", img=night.crack_glow((W, H), SLAB, 146, SEED), when="end:showing", until="feature:morning", blend="screen"),
        Layer(id="ridge_light", img=night.ridge_light((W, H), RIDGE), when="end:showing", until="feature:morning", blend="screen"),
        Layer(id="ash", img=kit.ash((W, H), 420, (196, 188, 176), SEED), when="always"),
    ]


def write_layers(rng: random.Random) -> list[Entry]:
    OUT.mkdir(parents=True, exist_ok=True)
    out: list[Entry] = []
    bottoms: dict[str, int] = {}
    for layer in layers(rng):
        img = bake(layer)
        box = img.getchannel("A").getbbox() or (0, 0, 1, 1)
        if layer["id"].startswith("figure_") and box[1] < LOWEST_HEAD:
            raise ValueError(f"{layer['id']} reaches y={box[1]}, above the story strip's clearance (y={LOWEST_HEAD})")
        name = f"{layer['id']}.png"
        img.crop(box).save(OUT / name, optimize=True)
        # The content hash makes a changed layer a new URL, so no cached copy of the old art is ever reused.
        src = f"{name}?h={hashlib.sha256((OUT / name).read_bytes()).hexdigest()[:12]}"
        entry = Entry(id=layer["id"], src=src, x=box[0], y=box[1], when=layer["when"])
        if "until" in layer and layer["until"]:
            entry["until"] = layer["until"]
        if "blend" in layer and layer["blend"]:
            entry["blend"] = layer["blend"]
        if "ungraded" in layer and layer["ungraded"]:
            entry["ungraded"] = True
        if layer.get("front"):
            entry["front"] = True
        bottoms[layer["id"]] = box[3]
        out.append(entry)
    return depth.arrange(out, bottoms)


def main() -> None:
    rng = random.Random(SEED)
    entries = write_layers(rng)
    check_conditions(entries)
    check_depth(entries)
    write_manifest(entries)
    write_previews(entries)
    total = sum(p.stat().st_size for p in OUT.iterdir())
    print(f"scene layers={len(entries)} size={W}x{H} bytes={total} out={OUT}")


if __name__ == "__main__":
    main()
