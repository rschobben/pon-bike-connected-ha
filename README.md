# PON Bike (Urban Arrow, Gazelle, Kalkhoff) Home Assistant Integration

A custom **Home Assistant integration** for connected PON bicycles, including **Urban Arrow**, **Gazelle**, **Kalkhoff**, and other PON-connected brands.

This integration connects to the **PON Bike Connected cloud API** and exposes your bike(s) as devices in Home Assistant, including live telemetry and GPS location.

> ⚠️ **Status: Experimental / Early Access**  
> This integration is under active development.  

---

## Personal project disclaimer

This integration is developed **primarily for personal use**.

While it is shared publicly to help others and encourage collaboration:

- Development is driven by personal needs and available time  
- Features may be added, changed, or removed without notice  
- There is **no guarantee of ongoing development or maintenance**  
- Roadmap items are **intentions, not commitments**  

If you rely on this integration for critical automations or dashboards, please be aware that future updates **may or may not happen**.

---

## Features

- OAuth2 (PKCE, public client — no client secret)
- One Home Assistant **device per bike**
- GPS location via `device_tracker`
- Telemetry sensors (currently odometer, module/battery charge)
- Friendly bike naming (nickname + frame number)
- Automatic token refresh (handled by Home Assistant)
- Robust polling coordinator
- Cloud polling (`iot_class: cloud_polling`)

---

## Supported Brands

This integration uses the **PON Bike Connected** platform and is expected to work with:

- **Urban Arrow**
- **Gazelle**
- **Kalkhoff**
- Other PON-connected bikes using the same backend

Availability of sensors depends on what the PON API exposes per brand and model.


---

## Known Limitations / Issues

### ⚠️ Battery statistics (Urban Arrow)

For **Urban Arrow** bikes, the API currently reports:

```
moduleCharge = 100%
```

…regardless of actual battery state.

This appears to be a **PON backend issue**, not an integration bug.  
Until PON exposes correct battery telemetry, Home Assistant will always show 100%.

---

## Installation

The integration required an active "connected" subscription using the Gazelle Connect, Urban Arrow Connected or Kalkhoff Smart Ebike apps (IOS or Android).
Once this is setup the bikes in these apps will be linked to a pon.bike account, after linking some time may be required before the bikes show up.

### Ensure bike visilibty on PON consumer portal (DON'T SKIP, DO THIS FIRST)

1. Create account on https://consumer-account.pon.bike/ 
2. Ensure bike is visibile under "My bikes"

### Create PON developer account and application (DON'T SKIP, DO THIS SECOND)

1. Create a POMN developer account at https://data-act.pon.bike/
  - click login
  - create Sign up

2. Add a New Application
  - Name the Application something like "Home Assistant integration"
  - Add similar description
  - Use following as callback, allowed origin, allowed logut URLs:
    https://my.home-assistant.io/redirect/oauth
  - Use anything as client aliases (for example 1234)
  - Copy the Application ID to the clipboard, you will need it as OAuth Client_ID during the integration setup.

### HACS installation (recommended)

1. ensure you have HACS installed in home assistant
2. Open HACS
3. Add this github repo as custom repository )type: Integration).
4. Install "PON Bike Connected" as an integration from the Custom section.
5. Restart home Assistant


### Manual installation (recommended for now)

1. Copy the integration folder into:
   ```
   custom_components/pon_bike_connected_ha/
   ```
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add integration**
4. Search for **PON Bike Connected**

---

## Configuration

### Application Credentials (Required)

This integration uses Home Assistant’s **Application Credentials** framework.

You will need:
- Your default browser already logged in to https://consumer-account.pon.bike/
- A PON Bike Connected OAuth **client_id** (this is the applcation ID), see above and do that FIRST.
- No client secret (public PKCE client) --> enter something like "dummy"

During setup, Home Assistant will:
- Redirect you to the PON login page
- Authorize access
- Store tokens securely
- Automatically refresh tokens when needed

When you are redirected to the PON consumer portal to authorize the bike make sure you click "add bike" and enable Location, Telemetry and Bike Status(IOT).

The bike should show up as a device in home assistant.

### OAuth details (for reference)
- **Scope** : openid offline_access authorization:read
- **Audience** : https://data-act.connected.pon.bike/
These are handled automatically by the integration.

---

## Entities

### Device

Each bike appears as **one Home Assistant device**, with metadata such as:

- Manufacturer (e.g. Urban Arrow)
- Model (e.g. Family Performance Line Plus)
- Frame number (serial)
- Hardware description (category / type / color / drive unit)

### Sensors

Currently implemented:

- **Odometer** (km, total increasing)
- **Module / battery charge (%)**

### Device Tracker

- GPS location
- Extra attributes:
  - last online timestamp
  - odometer
  - module charge

---

## Update Strategy

- Polling interval: **5 minutes**
- Token refresh handled automatically by Home Assistant
- All API calls via a centralized coordinator

---

## Roadmap

Planned (no guarantees):

- 🔁 Multi-account support
- 📡 MQTT / streaming telemetry (PON has not published endpoint yet)
- 📦 HACS publication
- 📊 Additional telemetry sensors
- 🧼 Entity allow-listing / pruning

---

## Privacy & Security

- OAuth tokens managed by Home Assistant
- No credentials stored in plain text
- All communication via HTTPS
- No data shared outside the official PON API

---

## Disclaimer

This project is:
- **Unofficial**
- **Not affiliated with PON, Urban Arrow, Gazelle, or Kalkhoff**
- Provided **as-is**, without warranty

Use at your own risk.

---

## Acknowledgements

Inspired by the **BMW Cardata Home Assistant integration**.

---

