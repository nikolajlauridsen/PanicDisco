#include "disco_client.h"

#include <HTTPClient.h>

DiscoClient::DiscoClient(const char* baseUrl) : baseUrl_(baseUrl) {}

int DiscoClient::panicStart()
{
    return post("/panic/start");
}

int DiscoClient::panicStop()
{
    return post("/panic/stop");
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
