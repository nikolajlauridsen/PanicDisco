"""Unit tests for Panic, the core service that runs every registered
PanicAction when the panic button is triggered.

Pure unit tests against fake PanicAction implementations, independent of
Flask/the database — same spirit as test_mapper.py.
"""

import logging

from disco_server.core.extension.panic_action import PanicAction
from disco_server.core.services.panic import Panic


class RecordingAction(PanicAction):
    """Fake PanicAction that records whether start/stop were called."""

    def __init__(self):
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


class FailingAction(PanicAction):
    """Fake PanicAction whose start/stop always raise, simulating a flaky extension."""

    def start(self):
        raise RuntimeError("boom")

    def stop(self):
        raise RuntimeError("boom")


def test_panic_starts_every_registered_action():
    actions = [RecordingAction(), RecordingAction()]
    Panic(actions).panic()

    assert all(action.started for action in actions)


def test_panic_with_no_actions_does_not_raise():
    Panic([]).panic()


def test_panic_swallows_an_action_exception_and_still_runs_the_rest():
    good_before = RecordingAction()
    failing = FailingAction()
    good_after = RecordingAction()

    Panic([good_before, failing, good_after]).panic()

    assert good_before.started is True
    assert good_after.started is True


def test_panic_logs_when_an_action_fails_to_start(caplog):
    with caplog.at_level(logging.ERROR):
        Panic([FailingAction()]).panic()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert "boom" in caplog.records[0].getMessage()


def test_panic_does_not_call_stop_on_actions():
    action = RecordingAction()
    Panic([action]).panic()

    assert action.stopped is False


def test_stop_stops_every_registered_action():
    actions = [RecordingAction(), RecordingAction()]
    Panic(actions).stop()

    assert all(action.stopped for action in actions)


def test_stop_with_no_actions_does_not_raise():
    Panic([]).stop()


def test_stop_swallows_an_action_exception_and_still_runs_the_rest():
    good_before = RecordingAction()
    failing = FailingAction()
    good_after = RecordingAction()

    Panic([good_before, failing, good_after]).stop()

    assert good_before.stopped is True
    assert good_after.stopped is True


def test_stop_logs_when_an_action_fails_to_stop(caplog):
    with caplog.at_level(logging.ERROR):
        Panic([FailingAction()]).stop()

    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    assert "boom" in caplog.records[0].getMessage()


def test_stop_does_not_call_start_on_actions():
    action = RecordingAction()
    Panic([action]).stop()

    assert action.started is False
