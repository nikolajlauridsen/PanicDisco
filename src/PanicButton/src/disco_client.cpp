#include "disco_client.h"

#include <ArduinoJson.h>
#include <HTTPClient.h>

#include "log.h"

DiscoClient::DiscoClient(const char* baseUrl) : baseUrl_(baseUrl)
{
}

int DiscoClient::panicStart()
{
    return post("/panic/start");
}

int DiscoClient::panicStop()
{
    return post("/panic/stop");
}

int DiscoClient::getTracks(std::vector<TrackEntity>& tracks)
{
    tracks.clear();

    HTTPClient http;
    // ArduinoJson reads straight from the socket via getStream(), which hands
    // back the raw body - it does not undo HTTP/1.1 chunked transfer encoding.
    // Forcing HTTP/1.0 makes the server send a plain Content-Length body.
    http.useHTTP10(true);
    http.begin(url("/tracks"));
    const int status = http.GET();
    if (status != HTTP_CODE_OK)
    {
        http.end();
        return status;
    }

    // The response is an array of TrackEntity objects. A filter with a single
    // element applies to every element of the array; keys not set to true are
    // skipped during parsing rather than stored and dropped afterwards.
    JsonDocument filter;
    filter[0]["id"] = true;
    filter[0]["name"] = true;

    JsonDocument doc;
    const DeserializationError error = deserializeJson(doc, http.getStream(), DeserializationOption::Filter(filter));
    http.end();

    if (error)
    {
        LOG("getTracks: JSON parse failed: %s\n", error.c_str());
        return PARSE_ERROR;
    }

    const JsonArray array = doc.as<JsonArray>();
    if (array.isNull())
    {
        LOG("getTracks: expected a JSON array\n");
        return PARSE_ERROR;
    }

    // The JSON -> TrackEntity mapping is convertFromJson() in track_entity.h.
    tracks.reserve(array.size());
    for (const JsonVariantConst item : array)
    {
        tracks.push_back(item.as<TrackEntity>());
    }
    return status;
}

int DiscoClient::loadTrack(TrackEntity& track)
{
    return put((String("/boombox/load/") + track.id).c_str());
}

String DiscoClient::url(const char* endpoint) const
{
    return String(baseUrl_) + endpoint;
}

int DiscoClient::post(const char* endpoint)
{
    // Built per request rather than kept alive: the device deep-sleeps after a
    // handful of calls, so there's no long-lived state worth keeping.
    HTTPClient http;
    http.begin(url(endpoint));
    const int status = http.POST("");
    http.end();
    return status;
}

int DiscoClient::put(const char* endpoint)
{
    HTTPClient http;
    http.begin(url(endpoint));
    const int status = http.PUT("");
    http.end();
    return status;
}
