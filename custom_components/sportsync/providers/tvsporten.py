"""TVsporten.nu provider for SportSync."""
from __future__ import annotations

from datetime import datetime
import logging
import re

from bs4 import BeautifulSoup

from .base import SportProvider, SportEvent

_LOGGER = logging.getLogger(__name__)


class TVSportenProvider(SportProvider):
    """Provider for tvsporten.nu."""

    name = "tvsporten"
    base_url = "https://www.tvsporten.nu"

    async def async_fetch_events(self, date: datetime | None = None) -> list[SportEvent]:
        """Fetch events from TVsporten.nu."""
        if date is None:
            date = datetime.now()

        # TVsporten.nu uses the base URL for today
        url = self.base_url

        html = await self._async_fetch_html(url)
        if not html:
            return []

        return self._parse_html(html, date)

    def _parse_html(self, html: str, date: datetime) -> list[SportEvent]:
        """Parse TVsporten.nu HTML structure."""
        events: list[SportEvent] = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # TVsporten.nu typical structure:
            # Events are usually in a container with sport sections
            # Each event has time, title/teams, channel, and sport category

            # Strategy 1: Look for common event containers
            # These selectors may need adjustment based on actual site structure

            # Try finding event rows/items
            event_containers = soup.select(
                ".event, .match, .broadcast, .schedule-item, "
                ".tv-event, .sport-event, article, .listing-item, "
                "tr.event-row, .event-card"
            )

            if not event_containers:
                # Fallback: look for table rows with time patterns
                event_containers = soup.find_all(
                    ["tr", "div", "li"],
                    class_=lambda x: x and any(
                        kw in str(x).lower()
                        for kw in ["event", "match", "broadcast", "schedule"]
                    ),
                )

            if not event_containers:
                # Last resort: find all elements containing time patterns
                event_containers = self._find_event_elements(soup)

            for container in event_containers:
                event = self._parse_event_container(container, date)
                if event:
                    events.append(event)

            _LOGGER.debug("TVsporten: parsed %d events", len(events))

        except Exception as err:
            _LOGGER.error("Error parsing TVsporten HTML: %s", err)
            self.last_error = str(err)

        return events

    def _find_event_elements(self, soup: BeautifulSoup) -> list:
        """Find elements that look like event listings."""
        elements = []

        # Look for elements containing time patterns (HH:MM or HH.MM)
        time_pattern = re.compile(r"\b\d{1,2}[.:]\d{2}\b")

        for elem in soup.find_all(["div", "tr", "li", "article"]):
            text = elem.get_text()
            # Must have a time and reasonable length
            if time_pattern.search(text) and 20 < len(text) < 500:
                # Avoid nested duplicates
                if not any(elem in e.descendants for e in elements):
                    elements.append(elem)

        return elements[:100]  # Limit to prevent runaway

    def _parse_event_container(
        self, container, date: datetime
    ) -> SportEvent | None:
        """Parse a single event container."""
        try:
            text = container.get_text(separator=" ", strip=True)

            # Extract time
            time_match = re.search(r"\b(\d{1,2})[.:](\d{2})\b", text)
            if not time_match:
                return None

            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return None

            start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Extract channel - look for common Swedish TV channels
            channel = self._extract_channel(container, text)

            # Extract title/match info
            title = self._extract_title(container, text, time_match.group(0))

            if not title or len(title) < 3:
                return None

            # Detect sport from text
            sport = self._detect_sport(text)

            # Try to extract teams
            home_team, away_team = self._extract_teams(title)

            # Extract league if present
            league = self._extract_league(container, text)

            # Check if live
            is_live = self._check_if_live(container, text)

            event_id = self._generate_id(
                self.name,
                start_time.isoformat(),
                title,
                channel,
            )

            return SportEvent(
                id=event_id,
                title=title,
                sport=sport,
                channel=channel or "Okänd kanal",
                start_time=start_time,
                source=self.name,
                league=league,
                home_team=home_team,
                away_team=away_team,
                is_live=is_live,
            )

        except Exception as err:
            _LOGGER.debug("Error parsing event container: %s", err)
            return None

    def _extract_channel(self, container, text: str) -> str | None:
        """Extract TV channel from container."""
        # Common Swedish sport channels
        channels = [
            "TV4", "TV4+", "TV4 Sport", "TV4 Fakta",
            "SVT1", "SVT2", "SVT24", "SVT",
            "Kanal 5", "Kanal 9", "Kanal 11",
            "Eurosport 1", "Eurosport 2", "Eurosport",
            "Viasat Sport", "Viasat Hockey", "Viasat Fotboll",
            "Viasat Golf", "Viasat Motor", "Viasat",
            "V Sport 1", "V Sport 2", "V Sport Premium", "V Sport",
            "C More Live", "C More Fotboll", "C More Hockey", "C More Sport", "C More",
            "Sportkanalen",
            "Telia", "TV3", "TV3+", "TV6", "TV8", "TV10",
            "Discovery+", "Discovery", "Max",
            "Dplay", "Viafree", "TV4 Play", "SVT Play",
        ]

        text_lower = text.lower()

        # Try to find channel in specific elements first
        channel_elem = container.select_one(
            ".channel, .tv-channel, .broadcaster, .kanal, "
            "[class*='channel'], [class*='kanal']"
        )
        if channel_elem:
            channel_text = channel_elem.get_text(strip=True)
            for ch in channels:
                if ch.lower() in channel_text.lower():
                    return ch

        # Search in full text
        for channel in channels:
            if channel.lower() in text_lower:
                return channel

        return None

    def _extract_title(self, container, text: str, time_str: str) -> str | None:
        """Extract event title."""
        # Try to find title in specific elements
        title_elem = container.select_one(
            ".title, .event-title, .match-title, .teams, "
            "h2, h3, h4, .name, [class*='title'], [class*='match']"
        )
        if title_elem:
            title = title_elem.get_text(strip=True)
            if len(title) > 3:
                return title

        # Fall back to cleaning up the full text
        # Remove time from beginning
        title = re.sub(r"^\s*\d{1,2}[.:]\d{2}\s*", "", text)

        # Remove common channel names at the end
        title = re.sub(
            r"\s*(TV4|SVT\d?|Eurosport\s*\d?|Viasat|V Sport|C More|Kanal \d+).*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Clean up
        title = " ".join(title.split())

        # Take first reasonable chunk
        if len(title) > 100:
            # Try to find a natural break
            for sep in [" - ", " | ", ", ", " – "]:
                if sep in title[:100]:
                    parts = title.split(sep)
                    if len(parts[0]) > 10:
                        title = parts[0] + sep + parts[1] if len(parts) > 1 else parts[0]
                        break
            else:
                title = title[:100]

        return title.strip() if title.strip() else None

    def _extract_league(self, container, text: str) -> str | None:
        """Extract league/competition name."""
        league_elem = container.select_one(
            ".league, .competition, .tournament, .liga, "
            "[class*='league'], [class*='competition']"
        )
        if league_elem:
            return league_elem.get_text(strip=True)

        # Common leagues/competitions to look for
        leagues = [
            "Allsvenskan", "Superettan", "Premier League", "La Liga",
            "Serie A", "Bundesliga", "Ligue 1", "Champions League",
            "Europa League", "Conference League", "SHL", "Hockeyallsvenskan",
            "NHL", "NBA", "NFL", "MLB", "ATP", "WTA",
            "World Cup", "VM", "EM", "OS", "Olympics",
        ]

        for league in leagues:
            if league.lower() in text.lower():
                return league

        return None

    def _check_if_live(self, container, text: str) -> bool:
        """Check if event is currently live."""
        live_indicators = ["live", "direktsändning", "pågår", "nu"]
        text_lower = text.lower()

        for indicator in live_indicators:
            if indicator in text_lower:
                return True

        # Check for live class/attribute
        if container.select_one(".live, .is-live, [class*='live']"):
            return True

        return False
