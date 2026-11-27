"""The content's places on the world map (contract/map.txt, "MAP")."""
from ...rules.expand import convert as authored
from ...rules.schema import Opening
from .. import convert
from .map_models import PlaceInfo, Stamp


def place_infos(o: Opening) -> list[PlaceInfo]:
    return [PlaceInfo(place=p.id, stamp=Stamp(p.stamp), east=p.at[0], north=p.at[1],
                      reveal=convert.unlock(authored.unlock(p.reveal)), label_key=p.label_key,
                      labelled_after=None if p.labelled_after is None else convert.unlock(authored.unlock(p.labelled_after)),
                      over=p.over) for p in o.places]
