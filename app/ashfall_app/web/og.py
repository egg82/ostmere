"""The link-preview card's address: the site's canonical URL and the card on the assets volume, which tools/ogcard.py
makes and the seed job puts there. The card is linked with the hash of its bytes in `?h=` (like a scene layer), so a
re-made card is a new URL; a chat app caches a preview by URL."""

from ..old_host import NEW_ORIGIN

SITE_URL = f"{NEW_ORIGIN}/"
CARD_PATH = "art/og/ostmere.png"
IMAGE_PLACEHOLDER = "{{og_image}}"   # in static/index.html


def card_url(hash_prefix: str | None) -> str:
    """The card's absolute URL; `hash_prefix` is the file's content hash, None while the volume has no card (it is
    seeded by hand, and the page must still serve)."""
    url = f"{NEW_ORIGIN}/assets/{CARD_PATH}"
    return f"{url}?h={hash_prefix}" if hash_prefix else url
