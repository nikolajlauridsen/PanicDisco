#pragma once

#include <WString.h>

#include <vector>

#include "track_entity.h"

/**
 * Thin HTTP wrapper around disco_server's JSON API - the C++ counterpart of
 * the Python disco_client package.
 *
 * One method per endpoint, grouped the same way as the server's blueprints
 * (panic, tracks, boombox) so it's obvious where a new endpoint goes. Every
 * method returns an int status:
 *   - >= 100: the HTTP status code the server answered with
 *   - -1 .. -11: an HTTPClient transport error, the request never got a
 *     response (e.g. connection refused, timeout)
 *   - PARSE_ERROR: the server answered 200 but the body wasn't the expected JSON
 *
 * Each call opens and closes its own connection. The device deep-sleeps after
 * a handful of requests, so there's no long-lived connection worth keeping.
 */
class DiscoClient
{
  public:
    /**
     * Returned instead of an HTTP status when the server answered 200 but the
     * body couldn't be parsed as the expected JSON. Well outside HTTPClient's
     * own error range (-1 .. -11) so the two can't be confused.
     */
    static constexpr int PARSE_ERROR = -100;

    /**
     * @param baseUrl the API root without a trailing slash, e.g.
     *                "http://host:5000/api". Not copied - must outlive the client.
     */
    explicit DiscoClient(const char* baseUrl);

    /**
     * POST /api/panic/start - runs every registered PanicAction's start() on
     * the server (by default: starts playback of the loaded track).
     * @return the HTTP status, or a negative error (see class docs).
     */
    int panicStart();

    /**
     * POST /api/panic/stop - runs every registered PanicAction's stop() on the
     * server (by default: stops playback).
     * @return the HTTP status, or a negative error (see class docs).
     */
    int panicStop();

    /**
     * GET /api/tracks - fetches every track on the server as id + name.
     *
     * The response is parsed straight from the socket through an ArduinoJson
     * filter that keeps only id and name, so RAM use doesn't grow if the
     * server adds fields to the per-track shape.
     *
     * @param tracks cleared, then filled with one TrackEntity per track on a
     *               200. Left empty on any other result.
     * @return 200 on success, another HTTP status, a negative HTTPClient
     *         error, or PARSE_ERROR if the body wasn't a JSON array.
     */
    int getTracks(std::vector<TrackEntity>& tracks);

    int loadTrack(TrackEntity& track);

    // /api/boombox endpoints go here as they're needed.

  private:
    String url(const char* endpoint) const;
    int post(const char* endpoint);
    int put(const char* endpoint);

    const char* baseUrl_;
};
