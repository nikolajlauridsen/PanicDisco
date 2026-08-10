import logging

from disco_server.core.extension.panic_action import PanicAction

logger = logging.getLogger(__name__)


class Panic:
    """Runs every registered `PanicAction` when the panic button is triggered."""

    def __init__(self, actions: list[PanicAction]):
        self.actions = actions

    def panic(self) -> None:
        """Execute every registered action.

        Each action's exceptions are swallowed so one misbehaving action
        (e.g. a flaky GPIO extension) can't stop the others from running.
        """
        for action in self.actions:
            try:
                action.start()
            except Exception as e:
                logger.exception("PanicAction %r failed to start: %s", action, e)

    def stop(self) -> None:
        """Execute every registered stop action.

        Same swallow-and-log behavior as panic(), for the same reason: one
        misbehaving action's stop() can't be allowed to stop the others'.
        """
        for action in self.actions:
            try:
                action.stop()
            except Exception as e:
                logger.exception("PanicAction %r failed to stop: %s", action, e)
