"""`python -m ashfall_app.jobs reminders`: the entry point."""
import pytest

from ashfall_app import logs
from ashfall_app.jobs import __main__ as jobs
from ashfall_app.jobs import reminders as job

from tests.reminders.fakepush import vapid_config


def test_with_no_vapid_config_the_job_logs_a_skip_and_exits_zero(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert job.main({}) == 0
    out = capsys.readouterr().out
    assert "event=reminders.skip" in out and "why=no_vapid_config" in out and "reminders.run" not in out


def test_half_a_config_is_no_config(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    assert job.main({"VAPID_PUBLIC_KEY": vapid_config().public_key}) == 0
    assert "event=reminders.skip" in capsys.readouterr().out


def test_keys_without_a_subject_are_no_config(capsys: pytest.CaptureFixture[str]):
    logs.setup()
    cfg = vapid_config()
    assert job.main({"VAPID_PUBLIC_KEY": cfg.public_key, "VAPID_PRIVATE_KEY": cfg.private_key}) == 0
    assert "event=reminders.skip" in capsys.readouterr().out


def test_keys_but_no_database_is_a_usage_error():
    cfg = vapid_config()
    env = {"VAPID_PUBLIC_KEY": cfg.public_key, "VAPID_PRIVATE_KEY": cfg.private_key, "VAPID_SUBJECT": cfg.subject}
    assert job.main(env) == 2


def test_an_unknown_job_name_is_a_usage_error():
    assert jobs.main(["nope"]) == 2
    assert jobs.main([]) == 2


def test_a_job_that_raises_is_logged_with_its_type_and_fails(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    def boom() -> int:
        raise RuntimeError("secret-endpoint-in-a-message")
    monkeypatch.setitem(jobs.JOBS, "reminders", boom)
    assert jobs.main(["reminders"]) == 1
    out = capsys.readouterr().out
    assert "event=job.failed" in out and "exc=RuntimeError" in out and "secret-endpoint" not in out
