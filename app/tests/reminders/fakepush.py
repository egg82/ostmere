"""A push service on localhost for tests: answers each path with the status its name gives (`/201`, `/410`, `/500`),
`/redirect` with a 302 to another server, and remembers which paths it was asked for."""
import base64
import os
import threading
from collections.abc import Generator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from py_vapid import Vapid01

from ashfall_app.reminders.config import Config


def b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _public(key: ec.EllipticCurvePublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def vapid_config() -> Config:
    v = Vapid01()
    v.generate_keys()
    assert v.private_key is not None and v.public_key is not None
    return Config(b64(_public(v.public_key)), b64(v.private_key.private_numbers().private_value.to_bytes(32)), "mailto:t@example.test")


def subscription_keys() -> tuple[str, str]:
    """(p256dh, auth) of a browser's subscription."""
    return b64(_public(ec.generate_private_key(ec.SECP256R1()).public_key())), b64(os.urandom(16))


class Seen:
    def __init__(self) -> None:
        self.paths: list[str] = []


@contextmanager
def push_service(redirect_to: str = "") -> Generator[tuple[str, Seen], None, None]:
    """(base URL, what it was asked for) while the server runs."""
    seen = Seen()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            seen.paths.append(self.path)
            if self.path.startswith("/redirect"):
                self.send_response(302)
                self.send_header("Location", redirect_to)
            else:
                self.send_response(int(self.path.lstrip("/")[:3]))
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", seen
    finally:
        server.shutdown()
        server.server_close()
        thread.join(5)
