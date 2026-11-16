"""The writer with no API key: the default Services answers every job with its authored stand-in, one logfmt line per
call that names the kind, outcome and duration and never the text."""
import pytest

from ashfall_app import logs
from ashfall_app.services import Services
from ashfall_app.writer.interface import JobKind
from ashfall_app.writer.service import Registry, UnknownKind, Writer

REACTION = JobKind("soul.reaction")
STAND_IN = "She says nothing about the fire."


def lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return [ln for ln in capsys.readouterr().out.splitlines() if ln]


def test_default_services_return_the_stand_in_and_log_one_line(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    writer = Services().writer
    writer.registry.add(REACTION)
    assert writer.write("soul.reaction", STAND_IN) == STAND_IN
    (line,) = lines(capsys)
    assert "event=writer.call" in line and "kind=soul.reaction outcome=ok client=NullClient ms=" in line
    assert "fire" not in line and "nothing" not in line


def test_an_unregistered_kind_is_refused():
    with pytest.raises(UnknownKind):
        Writer().write("nobody.registered.this", STAND_IN)


def test_a_kind_registers_once():
    with pytest.raises(ValueError):
        Registry((REACTION, REACTION))


class Broken:
    def write(self, kind: JobKind, stand_in: str) -> str:
        raise RuntimeError("secret-prompt-content")


def test_a_failing_client_answers_the_stand_in_and_logs_the_failure(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    writer = Writer(Registry((REACTION,)), Broken())
    assert writer.write("soul.reaction", STAND_IN) == STAND_IN
    (line,) = lines(capsys)
    assert "level=warning" in line and "outcome=failed" in line and "exc=RuntimeError" in line
    assert "secret-prompt-content" not in line
