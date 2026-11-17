"""The live client: Claude answers a job through the Anthropic SDK. Any failure raises `LiveFailure`, so the Writer
plays the authored stand-in. One logfmt line per call: kind, model, token counts, duration and outcome, never the key,
the prompt or the text."""

import json
import logging
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, NoReturn

import anthropic

from .. import logs
from .interface import Client, JobKind
from .service import Writer

log = logging.getLogger("ashfall.writer.live")
KEY_VAR = "ANTHROPIC_API_KEY"
_HERE = Path(__file__).parent


class LiveFailure(Exception):
    """The call gave no usable line; `reason` is the logged outcome."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class LiveConfig:
    models: Mapping[str, str]
    """Model id by job kind name; `default` answers a kind with no entry."""
    effort: Literal["low", "medium", "high", "xhigh", "max"]
    max_tokens: int
    timeout_s: float
    system: str

    def model(self, kind: JobKind) -> str:
        return self.models.get(kind.name) or self.models["default"]


def load_config() -> LiveConfig:
    raw: dict[str, Any] = json.loads((_HERE / "live.json").read_text(encoding="utf-8"))
    system = (_HERE / "voice.txt").read_text(encoding="utf-8").strip()
    return LiveConfig(raw["models"], raw["effort"], raw["max_tokens"], raw["timeout_s"], system)


class LiveClient:
    def __init__(self, sdk: anthropic.Anthropic, config: LiveConfig) -> None:
        self.sdk = sdk
        self.config = config

    def write(self, kind: JobKind, stand_in: str) -> str:
        model = self.config.model(kind)
        t0 = time.perf_counter()
        fields: dict[str, object] = {"kind": kind.name, "model": model}
        try:
            msg = self._call(kind, model, stand_in)
        except anthropic.APITimeoutError as e:
            self._fail("timeout", fields, t0, e)
        except anthropic.APIStatusError as e:
            self._fail("api_error", {**fields, "status": e.status_code}, t0, e)
        except anthropic.APIError as e:
            self._fail("api_error", fields, t0, e)
        usage = msg.usage
        fields |= {"in": usage.input_tokens, "out": usage.output_tokens,
                   "cache_read": usage.cache_read_input_tokens or 0}
        text = "".join(b.text for b in msg.content if b.type == "text").strip()
        reason = {"refusal": "refused", "max_tokens": "truncated"}.get(str(msg.stop_reason)) or ("" if text else "empty")
        if reason:
            raise self._failure(reason, fields, t0)
        logs.info(log, "writer.live", outcome="ok", ms=_ms(t0), **fields)
        return text

    def _call(self, kind: JobKind, model: str, stand_in: str) -> anthropic.types.Message:
        c = self.config
        return self.sdk.with_options(timeout=c.timeout_s, max_retries=0).messages.create(
            model=model, max_tokens=c.max_tokens, output_config={"effort": c.effort},
            system=[{"type": "text", "text": c.system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": f"Kind of moment: {kind.name}\nLine: {stand_in}"}])

    def _fail(self, reason: str, fields: dict[str, object], t0: float, cause: Exception) -> NoReturn:
        raise self._failure(reason, fields, t0) from cause

    def _failure(self, reason: str, fields: dict[str, object], t0: float) -> LiveFailure:
        logs.warning(log, "writer.live", outcome=reason, ms=_ms(t0), **fields)
        return LiveFailure(reason)


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def build_writer(env: Mapping[str, str], sdk: anthropic.Anthropic | None = None) -> Writer:
    """The service locator's writer: live only when the key is in `env`, otherwise the Null Object's."""
    key = env.get(KEY_VAR, "").strip()
    if not key:
        return Writer()
    client: Client = LiveClient(sdk or anthropic.Anthropic(api_key=key), load_config())
    return Writer(client=client)
