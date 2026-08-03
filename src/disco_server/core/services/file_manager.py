import os

from werkzeug.datastructures import FileStorage


def save(file: FileStorage, path: str) -> None:
    """Save an uploaded file to the given path."""
    file.save(path)


def remove(path: str) -> None:
    """Remove the file at the given path."""
    os.remove(path)
