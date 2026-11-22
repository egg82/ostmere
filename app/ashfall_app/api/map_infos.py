"""The content's places on the world map (CONTRACT.txt, "MAP")."""
from ..opening import convert as authored
from ..opening.schema import Opening
from . import convert
from .map_models import PlaceInfo, Stamp


def place_infos(o: Opening) -> list[PlaceInfo]:
    return [PlaceInfo(place=p.id, stamp=Stamp(p.stamp), east=p.at[0], north=p.at[1],
                      reveal=convert.unlock(authored.unlock(p.reveal)), label_key=p.label_key) for p in o.places]
