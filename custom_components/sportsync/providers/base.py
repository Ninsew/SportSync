"""Base provider class for SportSync."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import logging
import re
from typing import TYPE_CHECKING

from ..const import SPORT_KEYWORDS

if TYPE_CHECKING:
    from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


@dataclass
class SportEvent:
    """A sport broadcast event."""

    id: str
    title: str
    sport: str
    channel: str
    start_time: datetime
    source: str
    league: str | None = None
    end_time: datetime | None = None
    home_team: str | None = None
    away_team: str | None = None
    is_live: bool = False
    channel_logo: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "sport": self.sport,
            "league": self.league,
            "channel": self.channel,
            "channel_logo": self.channel_logo,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "is_live": self.is_live,
            "source": self.source,
        }

    def matches_favorites(
        self,
        sports: list[str] | None = None,
        teams: list[str] | None = None,
        leagues: list[str] | None = None,
    ) -> bool:
        """Check if event matches favorite criteria."""
        if not sports and not teams and not leagues:
            return False

        # Match sport
        if sports and self.sport in sports:
            return True

        # Match team (case-insensitive, partial match)
        if teams:
            title_lower = self.title.lower()
            for team in teams:
                team_lower = team.lower()
                if team_lower in title_lower:
                    return True
                if self.home_team and team_lower in self.home_team.lower():
                    return True
                if self.away_team and team_lower in self.away_team.lower():
                    return True

        # Match league
        if leagues and self.league:
            league_lower = self.league.lower()
            for league in leagues:
                if league.lower() in league_lower:
                    return True

        return False


class SportProvider(ABC):
    """Abstract base class for sport TV guide providers."""

    name: str = "base"
    base_url: str = ""

    def __init__(self, session: ClientSession) -> None:
        """Initialize provider."""
        self.session = session
        self.last_fetch: datetime | None = None
        self.last_error: str | None = None

    @abstractmethod
    async def async_fetch_events(self, date: datetime | None = None) -> list[SportEvent]:
        """Fetch events for a date. Override in subclasses."""
        pass

    async def _async_fetch_html(self, url: str) -> str | None:
        """Fetch HTML from URL."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
        }

        try:
            async with self.session.get(
                url, headers=headers, timeout=30
            ) as response:
                if response.status == 200:
                    self.last_fetch = datetime.now()
                    self.last_error = None
                    return await response.text()
                else:
                    self.last_error = f"HTTP {response.status}"
                    _LOGGER.warning("Failed to fetch %s: %s", url, self.last_error)
                    return None
        except Exception as err:
            self.last_error = str(err)
            _LOGGER.error("Error fetching %s: %s", url, err)
            return None

    def _generate_id(self, *parts: str) -> str:
        """Generate unique event ID."""
        content = "|".join(str(p) for p in parts if p)
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _detect_sport(self, text: str) -> str:
        """Detect sport type from text."""
        text_lower = text.lower()

        # Sort keywords by length (longest first) to match specific terms before generic ones
        # This ensures "skidskytte" matches before "vm", "champions league" before "league" etc.
        sorted_keywords = sorted(SPORT_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True)

        for keyword, sport in sorted_keywords:
            if keyword in text_lower:
                return sport
        return "other"

    def _extract_teams(self, title: str) -> tuple[str | None, str | None]:
        """Extract team names from title like 'Team A - Team B'."""
        separators = [" - ", " – ", " — ", " vs ", " mot ", " v "]
        for sep in separators:
            if sep in title:
                parts = title.split(sep, 1)
                if len(parts) == 2:
                    home = re.sub(r"\s*\([^)]*\)\s*$", "", parts[0].strip())
                    away = re.sub(r"\s*\([^)]*\)\s*$", "", parts[1].strip())
                    return home, away
        return None, None

    def _parse_time(self, time_str: str, date: datetime | None = None) -> datetime | None:
        """Parse time string to datetime."""
        if date is None:
            date = datetime.now()

        time_str = time_str.replace(".", ":").strip()

        # Try HH:MM format
        match = re.match(r"(\d{1,2}):(\d{2})", time_str)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            return date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        return None
