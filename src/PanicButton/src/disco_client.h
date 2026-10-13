#pragma once

#include <WString.h>

// Thin HTTP wrapper around disco_server's JSON API - the C++ counterpart of
// the Python disco_client package. One method per endpoint; each returns the
// HTTP status code (or a negative HTTPClient error code if the request never
// got a response, e.g. connection refused). Grouped the same way as the
// server's blueprints so it's obvious where a new endpoint goes.
class DiscoClient
{
  public:
    // baseUrl: the API root without a trailing slash, e.g. "http://host:5000/api".
    explicit DiscoClient(const char* baseUrl);

    // /api/panic - runs every registered PanicAction's start()/stop() on the server.
    int panicStart();
    int panicStop();

    // /api/tracks and /api/boombox endpoints go here as they're needed.

  private:
    String url(const char* endpoint) const;
    int post(const char* endpoint);

    const char* baseUrl_;
};
