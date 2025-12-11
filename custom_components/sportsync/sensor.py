"""Sensor platform for SportSync."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_FAVORITE_SPORTS,
    CONF_FAVORITE_TEAMS,
    CONF_FAVORITE_LEAGUES,
    CONF_FAVORITE_TITLES,
    CONF_FAVORITE_CHANNELS,
)
from .coordinator import SportSyncCoordinator, SportSyncData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SportSync sensors."""
    coordinator: SportSyncCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SportSyncAllEventsSensor(coordinator, entry),
        SportSyncFavoritesSensor(coordinator, entry),
        SportSyncLiveSensor(coordinator, entry),
        SportSyncUpcomingSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class SportSyncBaseSensor(CoordinatorEntity[SportSyncCoordinator], SensorEntity):
    """Base class for SportSync sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SportSyncCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "SportSync",
            "manufacturer": "SportSync",
            "model": "Sport TV Guide",
        }

    @property
    def data(self) -> SportSyncData | None:
        """Get coordinator data."""
        return self.coordinator.data


class SportSyncAllEventsSensor(SportSyncBaseSensor):
    """Sensor for all sport events."""

    _attr_icon = "mdi:television-play"
    _attr_translation_key = "all_events"

    def __init__(
        self,
        coordinator: SportSyncCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_all_events"

    @property
    def native_value(self) -> int:
        """Return number of events."""
        if self.data:
            return len(self.data.events)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs: dict[str, Any] = {
            "events": [],
            "last_update": None,
            "provider_status": {},
        }

        if self.data:
            attrs["events"] = self.data.all_events
            attrs["last_update"] = (
                self.data.last_update.isoformat() if self.data.last_update else None
            )
            attrs["provider_status"] = self.data.provider_status

        return attrs


class SportSyncFavoritesSensor(SportSyncBaseSensor):
    """Sensor for favorite sport events."""

    _attr_icon = "mdi:star"
    _attr_translation_key = "favorites"

    def __init__(
        self,
        coordinator: SportSyncCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_favorites"
        self._load_favorites()

    def _load_favorites(self) -> None:
        """Load favorites from config entry options."""
        self._favorite_sports = self._entry.options.get(CONF_FAVORITE_SPORTS, [])
        self._favorite_teams = self._entry.options.get(CONF_FAVORITE_TEAMS, [])
        self._favorite_leagues = self._entry.options.get(CONF_FAVORITE_LEAGUES, [])
        self._favorite_titles = self._entry.options.get(CONF_FAVORITE_TITLES, [])
        self._favorite_channels = self._entry.options.get(CONF_FAVORITE_CHANNELS, [])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinator."""
        self._load_favorites()
        super()._handle_coordinator_update()

    @property
    def native_value(self) -> int:
        """Return number of favorite events."""
        if self.data:
            return len(
                self.data.get_favorites(
                    self._favorite_sports,
                    self._favorite_teams,
                    self._favorite_leagues,
                    self._favorite_titles,
                    self._favorite_channels,
                )
            )
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs: dict[str, Any] = {
            "events": [],
            "favorite_sports": self._favorite_sports,
            "favorite_teams": self._favorite_teams,
            "favorite_leagues": self._favorite_leagues,
            "favorite_titles": self._favorite_titles,
            "favorite_channels": self._favorite_channels,
        }

        if self.data:
            attrs["events"] = self.data.get_favorites(
                self._favorite_sports,
                self._favorite_teams,
                self._favorite_leagues,
                self._favorite_titles,
                self._favorite_channels,
            )

        return attrs


class SportSyncLiveSensor(SportSyncBaseSensor):
    """Sensor for live sport events."""

    _attr_icon = "mdi:broadcast"
    _attr_translation_key = "live"

    def __init__(
        self,
        coordinator: SportSyncCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_live"

    @property
    def native_value(self) -> int:
        """Return number of live events."""
        if self.data:
            return len(self.data.get_live_events())
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs: dict[str, Any] = {"events": []}

        if self.data:
            attrs["events"] = self.data.get_live_events()

        return attrs


class SportSyncUpcomingSensor(SportSyncBaseSensor):
    """Sensor for upcoming sport events."""

    _attr_icon = "mdi:clock-outline"
    _attr_translation_key = "upcoming"

    def __init__(
        self,
        coordinator: SportSyncCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_upcoming"

    @property
    def native_value(self) -> int:
        """Return number of upcoming events (next 3 hours)."""
        if self.data:
            return len(self.data.get_upcoming_events(hours=3))
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        attrs: dict[str, Any] = {"events": [], "hours_ahead": 3}

        if self.data:
            attrs["events"] = self.data.get_upcoming_events(hours=3)

        return attrs
