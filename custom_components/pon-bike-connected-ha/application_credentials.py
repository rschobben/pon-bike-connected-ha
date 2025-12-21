from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2Implementation,
    LocalOAuth2ImplementationWithPkce,
)

from .const import AUTHORIZE_URL, TOKEN_URL

_LOGGER = logging.getLogger(__name__)

PON_SCOPE = "openid offline_access authorization:read"
PON_AUDIENCE = "https://data-act.connected.pon.bike/"


class PonOAuth2Implementation(LocalOAuth2ImplementationWithPkce):
    """PKCE OAuth implementation forcing scope/audience on authorize + audience on token."""

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        # This is what HA uses to append extra query params to /authorize
        return {
            "scope": PON_SCOPE,
            "audience": PON_AUDIENCE,
        }

    async def async_get_token_request_data(self, code: str) -> dict[str, Any]:
        data = await super().async_get_token_request_data(code)
        data["audience"] = PON_AUDIENCE
        _LOGGER.debug("Token request: added audience=%s", PON_AUDIENCE)
        return data

    async def async_refresh_token_request_data(self, refresh_token: str) -> dict[str, Any]:
        data = await super().async_refresh_token_request_data(refresh_token)
        data["audience"] = PON_AUDIENCE
        _LOGGER.debug("Refresh request: added audience=%s", PON_AUDIENCE)
        return data


async def async_get_auth_implementation(
    hass: HomeAssistant,
    auth_domain: str,
    credential: ClientCredential,
) -> AbstractOAuth2Implementation:
    _LOGGER.debug(
        "OAuth impl: client_id=%s authorize_url=%s token_url=%s (client_secret ignored)",
        credential.client_id,
        AUTHORIZE_URL,
        TOKEN_URL,
    )

    return PonOAuth2Implementation(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url=AUTHORIZE_URL,
        token_url=TOKEN_URL,
        client_secret=None,
    )


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    return {"console_url": ""}

