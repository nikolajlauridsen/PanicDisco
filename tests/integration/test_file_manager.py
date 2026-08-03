import io

import pytest
from werkzeug.datastructures import FileStorage

from disco_server.core.services import file_manager


def test_save_writes_the_uploaded_file_to_the_given_path(tmp_path):
    destination = tmp_path / "song1.mp3"
    upload = FileStorage(stream=io.BytesIO(b"fake mp3 bytes"), filename="song1.mp3")

    file_manager.save(upload, str(destination))

    assert destination.read_bytes() == b"fake mp3 bytes"


def test_remove_deletes_the_file_at_the_given_path(tmp_path):
    target = tmp_path / "song1.mp3"
    target.write_bytes(b"fake mp3 bytes")

    file_manager.remove(str(target))

    assert not target.exists()


def test_remove_raises_when_the_file_does_not_exist(tmp_path):
    missing = tmp_path / "missing.mp3"

    with pytest.raises(FileNotFoundError):
        file_manager.remove(str(missing))
