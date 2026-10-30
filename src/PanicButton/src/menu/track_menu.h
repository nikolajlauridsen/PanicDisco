#pragma once

#include "menu.h"
#include "track_entity.h"

class TrackMenu : public Menu
{
  public:
    explicit TrackMenu(std::vector<TrackEntity>& tracks);

    TrackEntity& getSelected() override;

    TrackEntity& get(size_t index) override;

    size_t size() const override;

  private:
    std::vector<TrackEntity>& tracks;
};