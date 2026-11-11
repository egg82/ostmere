"""The web pods' server: the page's files (page.py) and nothing else. Every server path goes to the app at the edge
(the HTTPRoute and tunnel patches in the cluster repo), so this process needs no database, no
secret and no init container, and the page still loads while the app or the database is down. Same image,
`python -m ashfall_app.web`."""

import logging
import os

from fastapi import FastAPI, Response
from starlette.middleware.gzip import GZipMiddleware

from .. import logs
from ..build_header import name_every_answer
from ..head import HeadAsGet
from ..old_host import OldHostRedirect
from . import page

# What the edge sends to the app instead of here: every route the app has falls under one (tests/test_web.py). A new
# one is added to the cluster's HTTPRoute and tunnel in the same change.
SERVER_PREFIXES = ("/api/",)
SERVER_EXACT = ("/healthz", "/page-config.json", "/changes", "/openapi.json")


def is_server_path(path: str) -> bool:
    return path in SERVER_EXACT or path.startswith(SERVER_PREFIXES)


def create_app() -> FastAPI:
    logs.setup()
    version = os.environ.get("BUILD_VERSION", "dev")
    logs.info(logging.getLogger("ashfall.web"), "web.start", version=version)
    app = FastAPI(title="Ashfall (page)", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(GZipMiddleware, minimum_size=page.GZIP_MIN)
    app.add_middleware(HeadAsGet)
    app.add_middleware(logs.RequestClock)
    app.add_middleware(OldHostRedirect)   # outermost: the old host never reaches a route
    name_every_answer(app, version, "web")
    page.serve_bundle(app, version)
    page.serve_shell(app, version)

    @app.get("/webz", include_in_schema=False)
    def webz(response: Response) -> None:
        """The web pods' probe: this image's own bundle is there. Reads the image, never the assets volume, so a stalled
        volume cannot mark every pod unready; /healthz is the app's."""
        if not page.bundle_present():
            response.status_code = 503

    return app
