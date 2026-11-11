"""The shipped opening's Ruleset and Game, built once per session so `create_app()` does not build them for every test
(about two thirds of its CPU). A build name changes only the Ruleset's `build` (and so a Game's content tag), so each
build seen gets the shipped rules under its name, once. A test that patches the lock or renames, or patches the opening,
gets its own Ruleset from the real builders."""
from dataclasses import replace

from ashfall_app.api.service import Game
from ashfall_app.opening.lock import load_lock
from ashfall_app.opening.renames import RenameEntry, load_renames
from ashfall_app.opening.schema import Opening
from ashfall_app.saves.interface import Ruleset
from ashfall_app.saves.ruleset import ruleset

BUILD = "dev"


class ShippedRuleset:
    def __init__(self, opening: Opening) -> None:
        self.opening = opening
        self.renames = load_renames()
        self.release = load_lock().release
        self.rs = ruleset(opening, self.renames, BUILD, self.release)
        self._by_build = {BUILD: self.rs}
        self._games = {BUILD: Game(opening, self.rs)}

    def ruleset(self, opening: Opening, renames: list[RenameEntry], build: str, release: int) -> Ruleset:
        if opening is self.opening and renames == self.renames and release == self.release:
            if build not in self._by_build:
                self._by_build[build] = replace(self.rs, build=build)
            return self._by_build[build]
        return ruleset(opening, renames, build, release)

    def make_game(self, opening: Opening, rs: Ruleset) -> Game:
        if opening is self.opening and self._by_build.get(rs.build) is rs:
            if rs.build not in self._games:
                self._games[rs.build] = Game(opening, rs)
            return self._games[rs.build]
        return Game(opening, rs)
