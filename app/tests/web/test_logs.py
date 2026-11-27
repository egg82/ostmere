"""logs.py: logfmt lines, the access line without client addresses or probes, exceptions without their message."""
import logging

import pytest

from ashfall_app import logs

log = logging.getLogger("ashfall.test")


def lines(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return [ln for ln in capsys.readouterr().out.splitlines() if ln]


def test_a_line_is_logfmt_with_quoted_values(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    logs.info(log, "thing.done", count=3, label="two words", ok=True, skipped=None)
    (line,) = lines(capsys)
    assert line.startswith("ts=") and " level=info logger=ashfall.test event=thing.done " in line
    assert line.endswith('count=3 label="two words" ok=true')


def test_an_exception_is_its_type_and_frames_never_its_message(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    try:
        raise ValueError("secret-row-content")
    except ValueError:
        log.error("boom", extra={"fields": {}}, exc_info=True)
    (line,) = lines(capsys)
    assert "exc=ValueError" in line and "test_logs.py" in line and "secret-row-content" not in line


def test_setup_is_idempotent(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    logs.setup()
    logs.info(log, "once")
    assert len(lines(capsys)) == 1


def _access(path: str) -> logging.LogRecord:
    return logging.LogRecord("uvicorn.access", logging.INFO, "", 0, '%s - "%s %s HTTP/%s" %d',
                             ("203.0.113.9:5000", "GET", path, "1.1", 200), None)


def test_the_access_line_drops_probes_the_address_and_the_query(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    logging.getLogger("uvicorn.access").handle(_access("/healthz"))
    logging.getLogger("uvicorn.access").handle(_access("/webz"))
    logging.getLogger("uvicorn.access").handle(_access("/api/content?x=secret"))
    (line,) = lines(capsys)
    assert "event=http.request method=GET path=/api/content status=200" in line
    assert "203.0.113.9" not in line and "secret" not in line


def test_a_control_character_in_a_value_is_escaped_and_the_line_stays_one_line(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    logs.info(log, "thing.done", a="x\x1b]52;c;AAAA\x07y", b="p\x7fq\x9br\ts", c="café ☃")
    (line,) = lines(capsys)
    assert 'a="x\\x1b]52;c;AAAA\\x07y"' in line and 'b="p\\x7fq\\x9br\\ts"' in line, line
    assert "café ☃" in line
    assert not any(not ch.isprintable() for ch in line)
