DOMAIN = "pon_bike_connected_ha"
NAME = "PON Bike Connected"

AUTHORIZE_URL = "https://consumer.login.pon.bike/authorize"
TOKEN_URL = "https://consumer.login.pon.bike/oauth/token"

API_BASE = "https://data-act.connected.pon.bike/api"

DEFAULT_SCAN_INTERVAL = 300

PLATFORMS: list[str] = ["sensor", "device_tracker"]

