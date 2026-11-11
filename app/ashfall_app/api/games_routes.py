"""Games on one account (CONTRACT.txt, "Games on one account"): the account's saves, live and deleted, and deleting and
restoring one. Each asks the Saves system (services.py); what it raises becomes the contract's error (answered)."""
from fastapi import APIRouter, Request

from .. import services
from ..saves.interface import KEPT_DAYS, MAX_SAVES, Games as GamesHeld
from . import session
from .error_models import ApiError
from .save_routes import answered, save_info
from .saves_models import DeletedSave, Games, SaveId
from .service import Game

_ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ApiError, "description": "no_account"},
    404: {"model": ApiError, "description": "not_found"},
    503: {"model": ApiError, "description": "save_unavailable (Retry-After)"},
}


def games(held: GamesHeld) -> Games:
    return Games(saves=[save_info(i) for i in held.saves],
                 deleted=[DeletedSave(save=save_info(d.info), deleted_at=d.deleted_at, purge_at=d.purge_at)
                          for d in held.deleted],
                 max_saves=MAX_SAVES, kept_days=KEPT_DAYS)


def add_games_routes(router: APIRouter, game: Game) -> None:
    @router.get("/saves", response_model=Games, operation_id="get_games",
                responses={401: _ERRORS[401], 503: _ERRORS[503]})
    def get_games(request: Request) -> Games:
        """The account's live saves, the most recently played first, and its deleted saves still held."""
        found = session.account(request)
        with answered(game):
            return games(services.of(request).saves.games(found))

    @router.post("/saves/{save_id}/delete", response_model=Games, operation_id="delete_save",
                 responses={**_ERRORS, 409: {"model": ApiError, "description": "last_save"}})
    def delete_save(request: Request, save_id: SaveId) -> Games:
        """Deletes a live save that is not the account's only one; it is held for a while and can be restored."""
        found = session.account(request)
        with answered(game):
            return games(services.of(request).saves.delete(found, save_id))

    @router.post("/saves/{save_id}/restore", response_model=Games, operation_id="restore_save",
                 responses={**_ERRORS, 409: {"model": ApiError, "description": "too_many_saves"}})
    def restore_save(request: Request, save_id: SaveId) -> Games:
        """A held deleted save, live again as it was."""
        found = session.account(request)
        with answered(game):
            return games(services.of(request).saves.restore(found, save_id))
