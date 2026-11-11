# Starlette's TestClient imports httpx2 first and falls back to httpx; CI installs httpx only. Without this stub the
# unresolved first import makes TestClient's base class, and so every client.get/post, unknown to pyright.
from httpx import *
from httpx import _client as _client, _types as _types
