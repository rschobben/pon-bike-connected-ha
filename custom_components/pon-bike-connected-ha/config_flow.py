from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN as INTEGRATION_DOMAIN

_LOGGER = logging.getLogger(__name__)

PON_SCOPE = "openid offline_access authorization:read"
PON_AUDIENCE = "https://data-act.connected.pon.bike/"

_UNIQUE_ID = "default"  # single account; multi-bike handled inside the entry


def _sanitize_flow_result(result: Any) -> Any:
    """Return a sanitized copy of a flow result for logging (avoid leaking secrets)."""
    if not isinstance(result, dict):
        return result

    safe = dict(result)

    url = safe.get("url")
    if isinstance(url, str):
        redacted = url
        for key in ("state=", "code_challenge=", "nonce="):
            if key in redacted:
                parts = redacted.split(key, 1)
                prefix = parts[0] + key + "***REDACTED***"
                suffix = ""
                if "&" in parts[1]:
                    suffix = "&" + parts[1].split("&", 1)[1]
                redacted = prefix + suffix
        safe["url"] = redacted

    if "data" in safe:
        safe["data"] = "***REDACTED***"

    return safe


class PonBikeConnectedConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=INTEGRATION_DOMAIN,
):
    """Handle OAuth2 config flow for PON Bike Connected."""

    DOMAIN = INTEGRATION_DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        return _LOGGER

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Initial setup step (single account; multi-bike supported)."""
        await self.async_set_unique_id(_UNIQUE_ID)
        self._abort_if_unique_id_configured()

        result = await self.async_step_pick_implementation(user_input)

        self.logger.debug("pick_implementation result (sanitized): %s", _sanitize_flow_result(result))
        if isinstance(result, dict) and result.get("type") == "external" and "url" in result:
            self.logger.debug("Authorize redirect URL: %s", _sanitize_flow_result({"url": result["url"]})["url"])

        return result

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None):
        """Handle re-authentication requests."""
        self.logger.debug("Starting re-auth flow for PON Bike Connected")

        reauth_entry_id = self.context.get("entry_id")
        if reauth_entry_id:
            self._reauth_entry = self.hass.config_entries.async_get_entry(reauth_entry_id)

        await self.async_set_unique_id(_UNIQUE_ID)

        result = await self.async_step_pick_implementation(None)

        self.logger.debug("reauth pick_implementation result (sanitized): %s", _sanitize_flow_result(result))
        if isinstance(result, dict) and result.get("type") == "external" and "url" in result:
            self.logger.debug("Reauth authorize redirect URL: %s", _sanitize_flow_result({"url": result["url"]})["url"])

        return result

    async def async_get_authorize_data(self) -> dict[str, Any]:
        """Extra parameters for the authorize endpoint."""
        self.logger.debug(
            "Authorize params used: scope=%s audience=%s",
            PON_SCOPE,
            PON_AUDIENCE,
        )
        return {
            "scope": PON_SCOPE,
            "audience": PON_AUDIENCE,
        }

    async def async_oauth_create_entry(self, data: dict[str, Any]):
        """Create the config entry after a successful OAuth flow."""
        impl = getattr(self, "implementation", None) or getattr(self, "_implementation", None)
        client_id = getattr(impl, "client_id", None)

        if client_id:
            title = f"PON Bike account ({client_id})"
        else:
            # Fallback if HA internals change or impl is missing
            title = "PON Bike account"

        return self.async_create_entry(title=title, data=data)

