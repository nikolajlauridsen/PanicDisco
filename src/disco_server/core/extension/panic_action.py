from abc import ABC, abstractmethod


class PanicAction(ABC):
    """Extension point for the panic button.

    Implement `execute` to hook custom behavior (starting playback, driving
    GPIO for lights, etc.) into the panic button, then register an instance
    via `disco_server.services.add_panic_action`. `Panic` runs every
    registered action when the button is triggered.
    """

    @abstractmethod
    def execute(self) -> None:
        """Perform this action's panic behavior."""
        pass