"""What the page needs at runtime that is not game state: the build version (sent with client error reports) and the
Umami tracker, if configured. Its own tiny route and models, outside the game API's contract (models.py), so
nothing here is in openapi.json. Umami is off unless both ASHFALL_UMAMI_SCRIPT_URL and ASHFALL_UMAMI_WEBSITE_ID are
set (habits' rule): the page then loads no tracker and sends nothing. `reminders` is null without a well-formed
VAPID public key: the page then says reminders are not available here. A page that finds no `reminders` key at all
is talking to a build from before reminders and offers no row."""
import os
from collections.abc import Mapping

from fastapi import APIRouter
from pydantic import BaseModel

from .reminders import config as reminders


class UmamiConfig(BaseModel):
    script_url: str
    website_id: str


class RemindersConfig(BaseModel):
    public_key: str
    """The VAPID public key, base64url: the applicationServerKey a page subscribes with."""
    after_hours: list[int]
    """The absences a player may pick, in hours, in the order shown."""


class PageConfig(BaseModel):
    version: str
    umami: UmamiConfig | None
    reminders: RemindersConfig | None


def page_config(env: Mapping[str, str]) -> PageConfig:
    script = env.get("ASHFALL_UMAMI_SCRIPT_URL", "").strip()
    site = env.get("ASHFALL_UMAMI_WEBSITE_ID", "").strip()
    umami = UmamiConfig(script_url=script, website_id=site) if script and site else None
    key = reminders.public_key(env)
    offered = None if key is None else RemindersConfig(public_key=key, after_hours=list(reminders.after_hours()))
    return PageConfig(version=env.get("BUILD_VERSION", "dev"), umami=umami, reminders=offered)


def routes() -> APIRouter:
    router = APIRouter()

    @router.get("/page-config.json", response_model=PageConfig, include_in_schema=False)
    def get_page_config() -> PageConfig:
        return page_config(os.environ)

    return router
