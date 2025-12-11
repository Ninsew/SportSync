"""DataUpdateCoordinator for SportSync."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .providers import PROVIDERS, SportEvent

if TYPE_CHECKING:
    from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class SportSyncData:
    """Container for SportSync data."""

    def __init__(self) -> None:
        """Initialize data container."""
        self.events: list[SportEvent] = []
        self.last_update: datetime | None = None
        self.provider_status: dict[str, dict[str, Any]] = {}

    @property
    def all_events(self) -> list[dict]:
        """Get all events as dicts, sorted by start time."""
        sorted_events = sorted(self.events, key=lambda e: e.start_time)
        return [e.to_dict() for e in sorted_events]

    def get_favorites(
        self,
        sports: list[str] | None = None,
        teams: list[str] | None = None,
        leagues: list[str] | None = None,
        titles: list[str] | None = None,
        channels: list[str] | None = None,
    ) -> list[dict]:
        """Get favorite events as dicts, sorted by start time."""
        favorites = [
            e for e in self.events
            if e.matches_favorites(sports, teams, leagues, titles, channels)
        ]
        sorted_favorites = sorted(favorites, key=lambda e: e.start_time)
        return [e.to_dict() for e in sorted_favorites]

    def get_live_events(self) -> list[dict]:
        """Get currently live events."""
        now = datetime.now()
        live = [
            e for e in self.events
            if e.is_live or (e.start_time <= now and (e.end_time is None or e.end_time >= now))
        ]
        return [e.to_dict() for e in live]

    def get_upcoming_events(self, hours: int = 3) -> list[dict]:
        """Get events starting within the next N hours."""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        upcoming = [
            e for e in self.events
            if now <= e.start_time <= cutoff
        ]
        sorted_upcoming = sorted(upcoming, key=lambda e: e.start_time)
        return [e.to_dict() for e in sorted_upcoming]


class SportSyncCoordinator(DataUpdateCoordinator[SportSyncData]):
    """Coordinator for fetching sport TV data."""

    def __init__(
        self,
        hass: HomeAssistant,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._session: ClientSession = async_get_clientsession(hass)
        self._providers = [provider(self._session) for provider in PROVIDERS]

    async def _async_update_data(self) -> SportSyncData:
        """Fetch data from all providers."""
        data = SportSyncData()

        # Fetch from all providers concurrently
        tasks = [
            self._fetch_provider(provider)
            for provider in self._providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_events: list[SportEvent] = []
        for provider, result in zip(self._providers, results):
            if isinstance(result, Exception):
                _LOGGER.error(
                    "Error fetching from %s: %s",
                    provider.name,
                    result,
                )
                data.provider_status[provider.name] = {
                    "status": "error",
                    "error": str(result),
                    "events_count": 0,
                }
            else:
                events = result or []
                all_events.extend(events)
                data.provider_status[provider.name] = {
                    "status": "ok",
                    "events_count": len(events),
                    "last_fetch": provider.last_fetch.isoformat() if provider.last_fetch else None,
                }

        # Deduplicate events (same time + similar title = duplicate)
        data.events = self._deduplicate_events(all_events)
        data.last_update = datetime.now()

        _LOGGER.debug(
            "SportSync update complete: %d events from %d providers",
            len(data.events),
            len(self._providers),
        )

        return data

    async def _fetch_provider(self, provider) -> list[SportEvent]:
        """Fetch events from a single provider."""
        try:
            return await provider.async_fetch_events()
        except Exception as err:
            _LOGGER.error("Provider %s failed: %s", provider.name, err)
            raise UpdateFailed(f"Provider {provider.name} failed: {err}") from err

    def _deduplicate_events(self, events: list[SportEvent]) -> list[SportEvent]:
        """Remove duplicate events from different providers."""
        seen: dict[str, SportEvent] = {}

        for event in events:
            # Create a key based on start time and normalized title
            title_normalized = event.title.lower().replace(" ", "")[:30]
            key = f"{event.start_time.strftime('%Y%m%d%H%M')}_{title_normalized}"

            if key not in seen:
                seen[key] = event
            else:
                # Keep the one with more information
                existing = seen[key]
                if (event.league and not existing.league) or \
                   (event.home_team and not existing.home_team):
                    seen[key] = event

        return list(seen.values())
