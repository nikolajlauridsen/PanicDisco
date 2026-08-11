import pytest

from disco_shared.models.track_details import TrackDetails
from disco_shared.models.track_update import TrackUpdate


def test_for_update_carries_over_the_current_fields():
    details = TrackDetails(id=1, name="song1", cue_point=5, path="/music/song1.mp3")

    update = details.for_update()

    assert update == TrackUpdate(name="song1", cue_point=5, path="/music/song1.mp3")


def test_for_update_allows_a_none_cue_point():
    details = TrackDetails(id=1, name="song1", cue_point=None, path="/music/song1.mp3")

    update = details.for_update()

    assert update.cue_point is None


def test_for_update_result_can_be_mutated_independently_of_the_source_details():
    details = TrackDetails(id=1, name="song1", cue_point=5, path="/music/song1.mp3")

    update = details.for_update()
    update.name = "renamed"

    assert details.name == "song1"
    assert update.name == "renamed"
