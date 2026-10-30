#pragma once

#include <WString.h>

#include <vector>

#include "track_entity.h"

// Thin HTTP wrapper around disco_server's JSON API - the C++ counterpart of
// the Python disco_client package. One method per endpoint; each returns the
// HTTP status code (or a negative HTTPClient error code if the request never
// got a response, e.g. connection refused). Grouped the same way as the
// server's blueprints so it's obvious where a new endpoint goes.
class DiscoClient
{
  public:
    // Returned instead of an HTTP status when the server answered 200 but the
    // body couldn't be parsed as the expected JSON. Well outside HTTPClient's
    // own error range (-1 .. -11) so the two can't be confused.
    static constexpr int PARSE_ERROR = -100;

    // baseUrl: the API root without a trailing slash, e.g. "http://host:5000/api".
    explicit DiscoClient(const char* baseUrl);

    // /api/panic - runs every registered PanicAction's start()/stop() on the server.
    int panicStart();
    int panicStop();

    // /api/tracks - replaces `tracks` with every track on the server (id + name)
    // on a 200. On any other result `tracks` is left empty and the status (or
    // PARSE_ERROR) says why. Parses the response stream through an ArduinoJson
    // filter, so only id and name are ever held in RAM even if the server's
    // per-track shape grows.
    int getTracks(std::vector<TrackEntity>& tracks);

    // /api/boombox endpoints go here as they're needed.

  private:
    String url(const char* endpoint) const;
    int post(const char* endpoint);

    const char* baseUrl_;
};
