from dataclasses import dataclass


@dataclass
class Error:
    error: str
    status_code: int

    def __init__(self, error: str, status_code: int | None = None) -> None:
        self.error = error
        self. status_code = status_code if status_code is not None else 400