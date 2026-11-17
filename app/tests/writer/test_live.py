"""The live writer client, over the real SDK on a fake transport (no network): the text on success, the stand-in and a
logged reason on every failure, no key means the null client, the model comes from config, the key is never logged."""
import json
from collections.abc import Callable, Mapping
from typing import Any

import anthropic
import httpx2
import pytest

from ashfall_app import logs
from ashfall_app.writer import live
from ashfall_app.writer.interface import JobKind, NullClient
from ashfall_app.writer.service import Registry, Writer
from tests.kills import kills

KIND = JobKind("soul.reaction")
OTHER = JobKind("quest.emergent")
STAND_IN = "She says nothing about the fire."
KEY = "sk-ant-planted-key-0123456789"
Handler = Callable[[httpx2.Request], httpx2.Response]


def reply(text: str = "She keeps her eyes on the ash.", stop: str = "end_turn") -> Handler:
    body: dict[str, Any] = {
        "id": "msg_1", "type": "message", "role": "assistant", "model": "m", "stop_reason": stop, "stop_sequence": None,
        "content": [{"type": "text", "text": text}] if text else [],
        "usage": {"input_tokens": 41, "output_tokens": 9, "cache_read_input_tokens": 30}}
    return lambda _: httpx2.Response(200, json=body)


def error(status: int) -> Handler:
    err = {"type": "error", "error": {"type": "api_error", "message": "boom"}}
    return lambda _: httpx2.Response(status, json=err)


def timeout(request: httpx2.Request) -> httpx2.Response:
    raise httpx2.ReadTimeout("slow", request=request)


def writer(handler: Handler, config: live.LiveConfig | None = None) -> Writer:
    sdk = anthropic.Anthropic(api_key=KEY, http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(handler)))
    return Writer(Registry((KIND, OTHER)), live.LiveClient(sdk, config or live.load_config()))


def lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return [ln for ln in capsys.readouterr().out.splitlines() if "event=writer.live" in ln]


@kills(6)
def test_success_returns_the_text_and_logs_one_line_without_the_key_or_the_text(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert writer(reply()).write(KIND.name, STAND_IN) == "She keeps her eyes on the ash."
    (line,) = lines(capsys)
    assert "kind=soul.reaction model=claude-sonnet-5-5" in line and "outcome=ok" in line
    assert "in=41 out=9 cache_read=30" in line and " ms=" in line
    assert KEY not in line and "eyes" not in line and "fire" not in line


@pytest.mark.parametrize("handler,reason", [
    pytest.param(error(500), "api_error", marks=kills(1)),
    pytest.param(timeout, "timeout", marks=kills(2)),
    pytest.param(reply(""), "empty", marks=kills(3)),
    pytest.param(reply("half a li", stop="max_tokens"), "truncated", marks=kills(7)),
    pytest.param(reply("I can't", stop="refusal"), "refused", marks=kills(7)),
])
def test_a_failure_answers_the_stand_in_and_logs_the_reason(
        handler: Handler, reason: str, capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert writer(handler).write(KIND.name, STAND_IN) == STAND_IN
    out = capsys.readouterr().out
    (line,) = [ln for ln in out.splitlines() if "event=writer.live" in ln]
    assert f"outcome={reason}" in line and "level=warning" in line and KEY not in out


@pytest.mark.parametrize("handler", [error(500), error(401), timeout, reply(""), reply("x", stop="max_tokens")])
@kills(1, 2, 3, 7)
def test_the_client_itself_raises_on_every_failure(handler: Handler):
    w = writer(handler)
    with pytest.raises(live.LiveFailure):
        w.client.write(KIND, STAND_IN)


def test_the_status_of_an_api_error_is_logged(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    writer(error(529)).write(KIND.name, STAND_IN)
    assert "status=529" in lines(capsys)[0]


def models_sent(config: live.LiveConfig) -> list[str]:
    seen: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(json.loads(request.content)["model"])
        return reply()(request)

    w = writer(handler, config)
    w.write(KIND.name, STAND_IN)
    w.write(OTHER.name, STAND_IN)
    return seen


@kills(4)
def test_the_model_comes_from_config_per_kind():
    base = live.load_config()
    config = live.LiveConfig({"default": "model-default", OTHER.name: "model-other"}, base.effort, base.max_tokens,
                             base.timeout_s, base.system)
    assert models_sent(config) == ["model-default", "model-other"]


def test_the_shipped_config_names_a_default_model():
    assert live.load_config().models["default"].startswith("claude-")


def test_the_request_carries_the_cached_system_prompt_and_the_line():
    sent: list[dict[str, Any]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        sent.append(json.loads(request.content))
        return reply()(request)

    writer(handler).write(KIND.name, STAND_IN)
    (body,) = sent
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert body["output_config"] == {"effort": live.load_config().effort}
    assert STAND_IN in body["messages"][0]["content"] and "temperature" not in body


@kills(5)
@pytest.mark.parametrize("env", [{}, {live.KEY_VAR: ""}, {live.KEY_VAR: "  "}])
def test_no_key_means_the_null_client(env: Mapping[str, str]):
    assert isinstance(live.build_writer(env).client, NullClient)


def test_a_key_in_the_environment_builds_the_live_client():
    assert isinstance(live.build_writer({live.KEY_VAR: KEY}).client, live.LiveClient)
