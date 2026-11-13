"""What one request may carry (CONTRACT.txt, "Request limits"). The page reads the ones its editors stop at from Content.limits;
the body's own limit is accounts/body_limit.py's."""

from ..engine import MAX_MIXES as MAX_MIXES

MAX_ORDERS = 64
MAX_QUEUE = 64
MAX_DRY_RUN = 8
MAX_MIX_PARTS = 64
MAX_LIST = 512
MAX_VISITS = 200
"""The returns a save keeps: the chronicle holds this many entries a filter (the page's game/chronicle.ts KEEP), so an older return opens no stretch."""
MAX_NAME = 64
NO_NUL = r"^[^\x00]*$"
"""Postgres text holds no U+0000: a free string a request stores carries this pattern, so it is 422, not a failed write."""
MAX_SAVE_ID = 2**53
MAX_GAME_SECOND = 2**53
"""A game second a request names, within what the page's numbers hold exactly."""
