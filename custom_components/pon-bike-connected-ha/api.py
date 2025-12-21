from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

_LOGGER = logging.getLogger(__name__)

# Swagger base:
# https://data-act.connected.pon.bike/api/v1/...
BASE_URL = "https://data-act.connected.pon.bike/api"


class PonBikeApiError(Exception):
    """Raised when the PON API call fails."""


class PonBikeApi:
    """API wrapper for PON Connected Bikes."""

    def __init__(self, oauth_session: OAuth2Session) -> None:
        self._oauth = oauth_session

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        """Perform an authenticated request via OAuth2Session."""
        url = f"{BASE_URL}{path}"

        # Match Swagger behaviour
        headers = kwargs.pop("headers", {})
        headers.setdefault("accept", "*/*")

        resp = await self._oauth.async_request(
            method,
            url,
            headers=headers,
            **kwargs,
        )

        # Safe debug: confirm Authorization header presence (no token value!)
        auth_present = False
        try:
            auth_present = "Authorization" in resp.request_info.headers
        except Exception:  # noqa: BLE001
            pass

        _LOGGER.debug(
            "PON API %s %s -> %s (auth_header_present=%s)",
            method,
            path,
            resp.status,
            auth_present,
        )

        if resp.status >= 400:
            body = await resp.text()
            raise PonBikeApiError(
                f"HTTP {resp.status} calling {path}: {body[:500]}"
            )

        return await resp.json()

    async def async_get_bikes_info(self) -> Any:
        """Return bikes info (first proof-of-life endpoint)."""
        return await self._request("GET", "/v1/bikes/info")

    async def async_get_last_known_states(self) -> Any:
        """Return last known states per bike (GPS + telemetry)."""
        return await self._request("GET", "/v1/bikes/last-known-states")


