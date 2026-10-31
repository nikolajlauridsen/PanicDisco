#pragma once

#include <vector>

#include "menu.h"
#include "track_entity.h"

/**
 * A Menu over the tracks fetched from the server, one row per TrackEntity
 * with the track name as the label.
 *
 * Unlike ActionMenu there is no select(): what happens on ENTER is up to the
 * caller (see SelectTrackMenuItem), which reads getSelected() and acts on it.
 * The menu does not own the vector, it only holds a reference, so the vector
 * must outlive the menu. Declaring both in the same scope is enough.
 *
 * getSelected()/get() return TrackEntity& (covariant with Menu's MenuItem&)
 * so callers get the id without a cast.
 */
class TrackMenu : public Menu
{
  public:
    /**
     * @param tracks the rows, in display order. Not copied - must stay alive
     *               for as long as the menu is used.
     */
    explicit TrackMenu(std::vector<TrackEntity>& tracks);

    TrackEntity& getSelected() override;

    TrackEntity& get(size_t index) override;

    size_t size() const override;

  private:
    std::vector<TrackEntity>& tracks;
};
