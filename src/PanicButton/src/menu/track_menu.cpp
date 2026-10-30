#include "track_menu.h"

TrackMenu::TrackMenu(std::vector<TrackEntity>& tracks) : tracks(tracks)
{
}

TrackEntity& TrackMenu::get(size_t index)
{
    return tracks[index];
}

TrackEntity& TrackMenu::getSelected()
{
    return get(getCursor());
}

size_t TrackMenu::size() const
{
    return tracks.size();
}
