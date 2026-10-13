// Network configuration template.
//
// Copy this file to include/secrets.h and fill in your details. secrets.h is
// gitignored so the real values never end up in the repo; this .example.h is
// the committed, shareable shape of it. Keep the two in sync when adding keys.
#pragma once

// Wi-Fi credentials
#define WIFI_SSID     "your-network-name"
#define WIFI_PASSWORD "your-network-password"

// Static IP for this device - skips DHCP on every wake, which is a noticeable
// chunk of the connect time. Reserve the address in your router.
#define STATIC_IP   192, 168, 1, 12
#define GATEWAY_IP  192, 168, 1, 1
#define SUBNET_MASK 255, 255, 255, 0
#define DNS_IP      192, 168, 1, 1

// disco_server's API root. No trailing slash - endpoints start with one.
#define API_BASE_URL "http://192.168.1.13:5000/api"
