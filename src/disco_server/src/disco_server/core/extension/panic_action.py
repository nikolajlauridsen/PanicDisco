from abc import ABC, abstractmethod


class PanicAction(ABC):
    """Extension point for the panic button.

    Implement `start`/`stop` to hook custom behavior (starting playback, driving
    GPIO for lights, etc.) into the panic button, then register an instance
    via `disco_server.services.add_panic_action`. `Panic` runs every
    registered action when the button is triggered.
    """

    @abstractmethod
    def start(self) -> None:
        """Perform this action's panic behavior."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Revert this action's panic behavior."""
        pass