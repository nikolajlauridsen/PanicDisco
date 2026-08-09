from disco_server.core.extension.panic_action import PanicAction


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
                action.execute()
            except Exception:
                # Swallow silently, we always want all extensions to run.
                # TODO: Add logging and log error.
                pass