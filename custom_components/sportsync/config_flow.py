"""Config flow for SportSync integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_FAVORITE_SPORTS,
    CONF_FAVORITE_TEAMS,
    CONF_FAVORITE_LEAGUES,
    CONF_FAVORITE_TITLES,
    CONF_FAVORITE_CHANNELS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


def parse_comma_list(value: str) -> list[str]:
    """Parse comma-separated string to list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class SportSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SportSync."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="SportSync",
                data={},
                options={
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                    CONF_FAVORITE_SPORTS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_SPORTS, "")
                    ),
                    CONF_FAVORITE_TEAMS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_TEAMS, "")
                    ),
                    CONF_FAVORITE_LEAGUES: parse_comma_list(
                        user_input.get(CONF_FAVORITE_LEAGUES, "")
                    ),
                    CONF_FAVORITE_TITLES: parse_comma_list(
                        user_input.get(CONF_FAVORITE_TITLES, "")
                    ),
                    CONF_FAVORITE_CHANNELS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_CHANNELS, "")
                    ),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=300, max=86400),
                    ),
                    vol.Optional(CONF_FAVORITE_SPORTS, default=""): str,
                    vol.Optional(CONF_FAVORITE_TEAMS, default=""): str,
                    vol.Optional(CONF_FAVORITE_LEAGUES, default=""): str,
                    vol.Optional(CONF_FAVORITE_TITLES, default=""): str,
                    vol.Optional(CONF_FAVORITE_CHANNELS, default=""): str,
                }
            ),
            description_placeholders={
                "default_interval": str(DEFAULT_SCAN_INTERVAL // 60),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SportSyncOptionsFlow:
        """Get the options flow for this handler."""
        return SportSyncOptionsFlow(config_entry)


class SportSyncOptionsFlow(config_entries.OptionsFlow):
    """Handle SportSync options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                    CONF_FAVORITE_SPORTS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_SPORTS, "")
                    ),
                    CONF_FAVORITE_TEAMS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_TEAMS, "")
                    ),
                    CONF_FAVORITE_LEAGUES: parse_comma_list(
                        user_input.get(CONF_FAVORITE_LEAGUES, "")
                    ),
                    CONF_FAVORITE_TITLES: parse_comma_list(
                        user_input.get(CONF_FAVORITE_TITLES, "")
                    ),
                    CONF_FAVORITE_CHANNELS: parse_comma_list(
                        user_input.get(CONF_FAVORITE_CHANNELS, "")
                    ),
                },
            )

        # Current values
        current_sports = self.config_entry.options.get(CONF_FAVORITE_SPORTS, [])
        current_teams = self.config_entry.options.get(CONF_FAVORITE_TEAMS, [])
        current_leagues = self.config_entry.options.get(CONF_FAVORITE_LEAGUES, [])
        current_titles = self.config_entry.options.get(CONF_FAVORITE_TITLES, [])
        current_channels = self.config_entry.options.get(CONF_FAVORITE_CHANNELS, [])
        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=300, max=86400),
                    ),
                    vol.Optional(
                        CONF_FAVORITE_SPORTS,
                        default=", ".join(current_sports),
                    ): str,
                    vol.Optional(
                        CONF_FAVORITE_TEAMS,
                        default=", ".join(current_teams),
                    ): str,
                    vol.Optional(
                        CONF_FAVORITE_LEAGUES,
                        default=", ".join(current_leagues),
                    ): str,
                    vol.Optional(
                        CONF_FAVORITE_TITLES,
                        default=", ".join(current_titles),
                    ): str,
                    vol.Optional(
                        CONF_FAVORITE_CHANNELS,
                        default=", ".join(current_channels),
                    ): str,
                }
            ),
        )
