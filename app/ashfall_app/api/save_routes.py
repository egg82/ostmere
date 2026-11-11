"""The account and save endpoints (CONTRACT.txt, ENDPOINTS). Each asks the Saves and Accounts systems (services.py)
and answers in the wire models; what a system raises becomes the contract's error (answered)."""
from collections.abc import Generator
from contextlib import contextmanager

from fastapi import APIRouter, Request

from .. import engine as e
from .. import services
from ..accounts.interface import About, AccountsUnavailable, Limited
from ..saves.interface import (
    KEPT_DAYS, MAX_SAVES, Behind, DecisionsLimited, Info, Invalid, LastSave, NewGamesLimited, NotFound, Stale,
    TooManySaves, Unavailable,
)
from . import session
from .errors import (
    catching_up, invalid_decision, last_save, no_account, not_found, rate_limited, stale, too_many_saves, unavailable,
)
from .error_models import ApiError
from .models import ForecastAnswer, Step, View
from .saves_models import (
    Account, AccountPresentation, AccountSettings, DecisionRequest, DryRunRequest, Me, NewSave, Opened, PastLine,
    SaveId, SaveInfo, SavePresentation,
)
from .lessonlog import log_new_ends
from .limits import MAX_LIST
from .service import Game

_SAVE_ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ApiError, "description": "no_account"},
    404: {"model": ApiError, "description": "not_found"},
    422: {"model": ApiError, "description": "invalid_decision (a request that does not fit the models included)"},
    503: {"model": ApiError, "description": "save_unavailable (Retry-After)"},
}
_DECIDE_ERRORS: dict[int | str, dict[str, object]] = {
    **_SAVE_ERRORS,
    409: {"model": ApiError, "description": "stale, with the save now as `step`; catching_up, with the save as left"},
}
_APPLY_ERRORS: dict[int | str, dict[str, object]] = {
    **_DECIDE_ERRORS,
    429: {"model": ApiError, "description": "rate_limited (Retry-After): too many decisions on the save just now"},
}
_FORECAST_ERRORS: dict[int | str, dict[str, object]] = {
    **_SAVE_ERRORS,
    409: {"model": ApiError, "description": "catching_up, with the save as stored as `step`"},
}


_NEW_ERRORS: dict[int | str, dict[str, object]] = {
    409: {"model": ApiError, "description": "too_many_saves"},
    429: {"model": ApiError, "description": "rate_limited (Retry-After on an account's new games)"},
    503: _SAVE_ERRORS[503],
}


def save_info(info: Info) -> SaveInfo:
    return SaveInfo(save_id=info.save_id, number=info.number, decisions=info.decisions, game_time=info.game_time,
                    ended_at=info.ended_at, started_at=info.started_at, played_at=info.played_at,
                    camp_level=info.camp_level)


def account_presentation(stored: dict[str, object]) -> AccountPresentation:
    return AccountPresentation.model_validate({k: v for k, v in stored.items() if k in AccountPresentation.model_fields})


def save_presentation(stored: dict[str, object]) -> SavePresentation:
    return SavePresentation.model_validate({k: v for k, v in stored.items() if k in SavePresentation.model_fields})


def account(about: About) -> Account:
    return Account(presentation=account_presentation(about.presentation),
                   settings=AccountSettings(lessons=about.lessons), has_words=about.has_words,
                   words_due=about.words_due)


@contextmanager
def answered(game: Game) -> Generator[None]:
    """A system's refusal as the contract's error."""
    try:
        yield
    except NotFound as ex:
        raise not_found(str(ex)) from ex
    except Stale as ex:
        raise stale(game.step(ex.played)) from ex
    except Behind as ex:
        raise catching_up(game.step(ex.played)) from ex
    except (Invalid, e.InvalidVerbError) as ex:
        raise invalid_decision(str(ex)) from ex
    except (Unavailable, AccountsUnavailable) as ex:
        raise unavailable(str(ex)) from ex
    except Limited as ex:
        raise rate_limited() from ex
    except NewGamesLimited as ex:
        raise rate_limited("too many new games on this account just now", ex.retry_after_s) from ex
    except DecisionsLimited as ex:
        raise rate_limited("too many decisions on this save just now", ex.retry_after_s) from ex
    except TooManySaves as ex:
        raise too_many_saves(MAX_SAVES) from ex
    except LastSave as ex:
        raise last_save() from ex


def add_save_routes(router: APIRouter, game: Game) -> None:
    @router.get("/me", response_model=Me, operation_id="get_me")
    def get_me(request: Request) -> Me:
        """This browser's account and its saves, the most recently played first. Never makes an account."""
        found = session.who(request)
        s = services.of(request)
        about = None if found is None else s.accounts.about(found)
        if found is None or about is None:
            return Me(account=None, saves=[], max_saves=MAX_SAVES, kept_days=KEPT_DAYS)
        return Me(account=account(about), saves=[save_info(i) for i in s.saves.list(found)],
                  max_saves=MAX_SAVES, kept_days=KEPT_DAYS)

    @router.post("/saves", response_model=NewSave, operation_id="new_save", responses=_NEW_ERRORS)
    def new_save(request: Request) -> NewSave:
        """A new save at game time 0; makes the account (and its cookie) when this browser has none. The account's
        other saves are kept."""
        s = services.of(request)
        with answered(game):
            found = session.who(request)
            if found is None:
                made = s.accounts.create(session.address(request), session.label(request))
                session.sign_in(request, made.token)
                found = made.account_id
            info, played = s.saves.create(found)
        return NewSave(save=save_info(info), presentation=SavePresentation(), step=game.step(played))

    @router.post("/saves/{save_id}/open", response_model=Opened, operation_id="open_save", responses=_SAVE_ERRORS)
    def open_save(request: Request, save_id: SaveId) -> Opened:
        """The save as last seen, its last lines, and the save advanced to now."""
        found = session.account(request)
        with answered(game):
            got = services.of(request).saves.open(found, save_id)
        return Opened(save=save_info(got.info), was=game.view(got.was),
                      history=[PastLine(n=p.n, at=p.at, key=p.key) for p in got.history],
                      presentation=save_presentation(got.presentation), step=game.step(got.played))

    @router.post("/saves/{save_id}/advance", response_model=Step, operation_id="advance", responses=_SAVE_ERRORS)
    def advance(request: Request, save_id: SaveId) -> Step:
        """The save advanced to now."""
        found = session.account(request)
        with answered(game):
            return game.step(services.of(request).saves.advance(found, save_id))

    @router.post("/saves/{save_id}/decisions", response_model=Step, operation_id="decide", responses=_APPLY_ERRORS)
    def decide(request: Request, save_id: SaveId, body: DecisionRequest) -> Step:
        """Advance to now, then apply the decision, if the save has had no other since `after`."""
        found = session.account(request)
        with answered(game):
            return game.step(services.of(request).saves.decide(found, save_id, game.verb(body.decision), body.after))

    add_keep_routes(router)
    add_unwritten_routes(router, game)


def add_keep_routes(router: APIRouter) -> None:
    """What the page keeps that is not game state: the account's presentation and settings, and each save's
    presentation."""

    @router.put("/me/presentation", response_model=Account, operation_id="put_account_presentation",
                responses={401: _SAVE_ERRORS[401], 422: _SAVE_ERRORS[422]})
    def put_account_presentation(request: Request, body: AccountPresentation) -> Account:
        """Adds what the page sends to what the account keeps; answers what is kept now."""
        found = session.account(request)
        accounts = services.of(request).accounts
        kept = accounts.keep_presentation(found, body.model_dump(), MAX_LIST)
        about = None if kept is None else accounts.about(found)
        if kept is None or about is None:
            raise no_account()
        return account(about)

    @router.put("/me/settings", response_model=Account, operation_id="put_account_settings",
                responses={401: _SAVE_ERRORS[401], 422: _SAVE_ERRORS[422]})
    def put_account_settings(request: Request, body: AccountSettings) -> Account:
        """Replaces the player's settings for every game of the account; answers the account."""
        found = session.account(request)
        accounts = services.of(request).accounts
        about = accounts.about(found) if accounts.set_lessons(found, body.lessons) else None
        if about is None:
            raise no_account()
        return account(about)

    @router.put("/saves/{save_id}/presentation", response_model=SavePresentation,
                operation_id="put_save_presentation",
                responses={401: _SAVE_ERRORS[401], 404: _SAVE_ERRORS[404], 422: _SAVE_ERRORS[422]})
    def put_save_presentation(request: Request, save_id: SaveId, body: SavePresentation) -> SavePresentation:
        """Adds what the page sends to what the save keeps; answers what is kept now."""
        found = session.account(request)
        kept = services.of(request).accounts.keep_save_presentation(found, save_id, body.model_dump(), MAX_LIST)
        if kept is None:
            raise not_found("no such save")
        log_new_ends(save_id, save_presentation(kept.before).lesson_ends, save_presentation(kept.after).lesson_ends)
        return save_presentation(kept.after)


def add_unwritten_routes(router: APIRouter, game: Game) -> None:
    """The save routes that write nothing."""

    @router.post("/saves/{save_id}/forecast", response_model=ForecastAnswer, operation_id="forecast",
                 responses=_FORECAST_ERRORS)
    def forecast(request: Request, save_id: SaveId) -> ForecastAnswer:
        """What lands from now if the player changes nothing (CONTRACT.txt, "Forecast"). Nothing is written; 409
        catching_up while the save is still behind."""
        found = session.account(request)
        with answered(game):
            saves = services.of(request).saves
            stop = saves.forecast_stop()
            return game.forecast(saves.current(found, save_id, stop), stop)

    @router.get("/saves/{save_id}/view", response_model=View, operation_id="saved_view", responses=_SAVE_ERRORS)
    def saved_view(request: Request, save_id: SaveId) -> View:
        """The save as last written, at its own time: not advanced, nothing written (the front page's picture of each
        save's camp)."""
        found = session.account(request)
        with answered(game):
            return game.view(services.of(request).saves.stored(found, save_id))

    @router.post("/saves/{save_id}/dry-run", response_model=View, operation_id="dry_run", responses=_DECIDE_ERRORS)
    def dry_run(request: Request, save_id: SaveId, body: DryRunRequest) -> View:
        """What the save would show after these decisions, applied in order now. Nothing is written."""
        found = session.account(request)
        with answered(game):
            verbs = tuple(game.verb(d) for d in body.decisions)
            return game.view(services.of(request).saves.dry_run(found, save_id, verbs))
