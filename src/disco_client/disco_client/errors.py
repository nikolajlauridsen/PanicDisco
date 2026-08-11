class DiscoClientError(Exception):
    """Base exception for all disco_client errors."""


class DiscoAPIError(DiscoClientError):
    """The server returned an error response."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code}: {message}")


class TrackNotFoundError(DiscoAPIError):
    """The requested track does not exist."""


class BoomboxNotLoadedError(DiscoAPIError):
    """No track is currently loaded in the boombox."""
