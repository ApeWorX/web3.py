import pytest

from tests.integration.go_ethereum import conftest as geth_conftest


class FakeGethProcess:
    stdin = None
    stdout = None
    stderr = None

    def __init__(self, events):
        self.events = events

    def communicate(self, timeout):
        self.events.append(("communicate", timeout))
        return "", ""


def test_start_geth_process_cleans_up_after_consumer_exception(monkeypatch):
    events = []
    proc = FakeGethProcess(events)

    def fake_check_output(*args, **kwargs):
        events.append(("check_output", args, kwargs))
        return b""

    def fake_popen(*args, **kwargs):
        events.append(("popen", args, kwargs))
        return proc

    def fake_wait_for_port(received_proc):
        assert received_proc is proc
        events.append("wait_for_port")
        return 30303

    def fake_kill_proc_gracefully(received_proc):
        assert received_proc is proc
        events.append("kill_proc_gracefully")

    monkeypatch.setattr(geth_conftest.subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(geth_conftest.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(geth_conftest, "wait_for_port", fake_wait_for_port)
    monkeypatch.setattr(
        geth_conftest,
        "kill_proc_gracefully",
        fake_kill_proc_gracefully,
    )

    fixture_generator = geth_conftest.start_geth_process_and_yield_port.__wrapped__(
        "geth",
        "/tmp/datadir",
        "/tmp/genesis.json",
        ("geth", "--dev"),
    )

    assert next(fixture_generator) == 30303
    with pytest.raises(RuntimeError, match="consumer failed"):
        fixture_generator.throw(RuntimeError("consumer failed"))

    assert "wait_for_port" in events
    assert "kill_proc_gracefully" in events
    assert ("communicate", 5) in events
    assert events.index("kill_proc_gracefully") < events.index(("communicate", 5))
