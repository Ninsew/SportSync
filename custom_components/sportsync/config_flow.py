"""Config flow for SportSync integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_FAVORITE_SPORTS,
    CONF_FAVORITE_TEAMS,
    CONF_FAVORITE_LEAGUES,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    SPORT_TYPES,
)


class SportSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SportSync."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Check if already configured
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
                    CONF_FAVORITE_SPORTS: user_input.get(CONF_FAVORITE_SPORTS, []),
                    CONF_FAVORITE_TEAMS: [],
                    CONF_FAVORITE_LEAGUES: [],
                },
            )

        # Build sport options for multiselect
        sport_options = {
            key: f"{data['emoji']} {data['name']}"
            for key, data in SPORT_TYPES.items()
            if key != "other"
        }

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
                    vol.Optional(
                        CONF_FAVORITE_SPORTS,
                        default=[],
                    ): cv.multi_select(sport_options),
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
            # Process teams and leagues (comma-separated strings to lists)
            teams_str = user_input.get(CONF_FAVORITE_TEAMS, "")
            teams = [t.strip() for t in teams_str.split(",") if t.strip()]

            leagues_str = user_input.get(CONF_FAVORITE_LEAGUES, "")
            leagues = [l.strip() for l in leagues_str.split(",") if l.strip()]

            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                    CONF_FAVORITE_SPORTS: user_input.get(CONF_FAVORITE_SPORTS, []),
                    CONF_FAVORITE_TEAMS: teams,
                    CONF_FAVORITE_LEAGUES: leagues,
                },
            )

        # Current values
        current_sports = self.config_entry.options.get(CONF_FAVORITE_SPORTS, [])
        current_teams = self.config_entry.options.get(CONF_FAVORITE_TEAMS, [])
        current_leagues = self.config_entry.options.get(CONF_FAVORITE_LEAGUES, [])
        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Build sport options
        sport_options = {
            key: f"{data['emoji']} {data['name']}"
            for key, data in SPORT_TYPES.items()
            if key != "other"
        }

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
                        default=current_sports,
                    ): cv.multi_select(sport_options),
                    vol.Optional(
                        CONF_FAVORITE_TEAMS,
                        default=", ".join(current_teams),
                    ): str,
                    vol.Optional(
                        CONF_FAVORITE_LEAGUES,
                        default=", ".join(current_leagues),
                    ): str,
                }
            ),
        )
