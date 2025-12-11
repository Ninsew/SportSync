"""TVmatchen.nu provider for SportSync."""
from __future__ import annotations

from datetime import datetime
import logging
import re

from bs4 import BeautifulSoup

from .base import SportProvider, SportEvent

_LOGGER = logging.getLogger(__name__)


class TVMatchenProvider(SportProvider):
    """Provider for tvmatchen.nu."""

    name = "tvmatchen"
    base_url = "https://www.tvmatchen.nu"

    async def async_fetch_events(self, date: datetime | None = None) -> list[SportEvent]:
        """Fetch events from TVmatchen.nu."""
        if date is None:
            date = datetime.now()

        # TVmatchen.nu structure - base URL for today
        url = self.base_url

        html = await self._async_fetch_html(url)
        if not html:
            return []

        return self._parse_html(html, date)

    def _parse_html(self, html: str, date: datetime) -> list[SportEvent]:
        """Parse TVmatchen.nu HTML structure."""
        events: list[SportEvent] = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # TVmatchen.nu typical structure:
            # Usually organized by sport category with match listings

            # Strategy 1: Find sport sections and their matches
            sport_sections = soup.select(
                ".sport-section, .category, .sport-category, "
                "[class*='sport'], section"
            )

            if sport_sections:
                for section in sport_sections:
                    sport_name = self._get_section_sport(section)
                    section_events = self._parse_section_events(section, date, sport_name)
                    events.extend(section_events)

            # Strategy 2: If no sections found, look for individual events
            if not events:
                event_containers = soup.select(
                    ".match, .event, .game, .broadcast, "
                    ".listing-item, .schedule-item, "
                    "tr, li.match-item, article"
                )

                for container in event_containers:
                    event = self._parse_event_container(container, date)
                    if event:
                        events.append(event)

            # Strategy 3: Table-based layout
            if not events:
                tables = soup.select("table")
                for table in tables:
                    rows = table.select("tr")
                    for row in rows:
                        event = self._parse_table_row(row, date)
                        if event:
                            events.append(event)

            _LOGGER.debug("TVmatchen: parsed %d events", len(events))

        except Exception as err:
            _LOGGER.error("Error parsing TVmatchen HTML: %s", err)
            self.last_error = str(err)

        return events

    def _get_section_sport(self, section) -> str | None:
        """Get sport type from section header."""
        # Look for section header
        header = section.select_one("h1, h2, h3, h4, .section-title, .sport-title, .category-title")
        if header:
            header_text = header.get_text(strip=True)
            detected = self._detect_sport(header_text)
            if detected != "other":
                return detected

        # Check section class for sport name
        classes = section.get("class", [])
        if classes:
            class_str = " ".join(classes)
            detected = self._detect_sport(class_str)
            if detected != "other":
                return detected

        # Check data attributes
        for attr in ["data-sport", "data-category", "data-type"]:
            if section.get(attr):
                detected = self._detect_sport(section.get(attr))
                if detected != "other":
                    return detected

        return None

    def _parse_section_events(
        self, section, date: datetime, sport_hint: str | None
    ) -> list[SportEvent]:
        """Parse events within a sport section."""
        events = []

        # Find match/event items within section
        items = section.select(
            ".match, .event, .game, .item, li, tr, "
            "[class*='match'], [class*='event']"
        )

        for item in items:
            event = self._parse_event_container(item, date, sport_hint)
            if event:
                events.append(event)

        return events

    def _parse_event_container(
        self, container, date: datetime, sport_hint: str | None = None
    ) -> SportEvent | None:
        """Parse a single event container."""
        try:
            text = container.get_text(separator=" ", strip=True)

            # Must have reasonable content
            if len(text) < 10:
                return None

            # Extract time
            time_match = re.search(r"\b(\d{1,2})[.:](\d{2})\b", text)
            if not time_match:
                return None

            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                return None

            start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Extract teams/title
            title = self._extract_match_title(container, text)
            if not title or len(title) < 3:
                return None

            # Extract channel
            channel = self._extract_channel(container, text)

            # Extract teams
            home_team, away_team = self._extract_teams(title)

            # Format title with separator if teams were extracted from concatenated names
            title = self._format_title_with_teams(title, home_team, away_team)

            # Get sport: prioritize section hint, then element sport, then detect from text
            sport = sport_hint or self._get_element_sport(container) or self._detect_sport(text)

            # Extract league
            league = self._extract_league(container, text)

            # Check if live
            is_live = "live" in text.lower() or "pågår" in text.lower()

            event_id = self._generate_id(
                self.name,
                start_time.isoformat(),
                title,
                channel or "",
            )

            return SportEvent(
                id=event_id,
                title=title,
                sport=sport,
                channel=channel or "Unknown channel",
                start_time=start_time,
                source=self.name,
                league=league,
                home_team=home_team,
                away_team=away_team,
                is_live=is_live,
            )

        except Exception as err:
            _LOGGER.debug("Error parsing event: %s", err)
            return None

    def _get_element_sport(self, element) -> str | None:
        """Extract sport from element's classes or data attributes."""
        # Check element classes
        classes = element.get("class", [])
        if classes:
            class_str = " ".join(classes)
            detected = self._detect_sport(class_str)
            if detected != "other":
                return detected

        # Check data attributes
        for attr in ["data-sport", "data-category", "data-type"]:
            if element.get(attr):
                detected = self._detect_sport(element.get(attr))
                if detected != "other":
                    return detected

        # Check for sport-specific child element
        sport_elem = element.select_one(
            ".sport, .category, .sport-type, "
            "[class*='sport-'], [class*='category-']"
        )
        if sport_elem:
            detected = self._detect_sport(sport_elem.get_text(strip=True))
            if detected != "other":
                return detected

        return None

    def _parse_table_row(self, row, date: datetime) -> SportEvent | None:
        """Parse a table row as an event."""
        cells = row.select("td")
        if len(cells) < 2:
            return None

        text = row.get_text(separator=" ", strip=True)
        return self._parse_event_container(row, date)

    def _extract_match_title(self, container, text: str) -> str | None:
        """Extract match title (teams)."""
        # Look for team containers
        teams_elem = container.select_one(
            ".teams, .match-teams, .home-away, "
            "[class*='team'], [class*='match']"
        )
        if teams_elem:
            title = teams_elem.get_text(separator=" - ", strip=True)
            if len(title) > 3:
                return title

        # Look for individual team elements
        home = container.select_one(".home, .home-team, .team-home, .team1")
        away = container.select_one(".away, .away-team, .team-away, .team2")
        if home and away:
            return f"{home.get_text(strip=True)} - {away.get_text(strip=True)}"

        # Look for title element
        title_elem = container.select_one(
            ".title, .event-title, .match-title, "
            "h3, h4, .name, strong"
        )
        if title_elem:
            title = title_elem.get_text(strip=True)
            if len(title) > 3:
                return title

        # Extract from full text
        # Remove time
        title = re.sub(r"^\s*\d{1,2}[.:]\d{2}\s*", "", text)
        # Remove channel info at end
        title = re.sub(
            r"\s*(TV4|SVT|Eurosport|Viasat|V Sport|C More|Kanal).*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Clean and truncate
        title = " ".join(title.split())
        if len(title) > 80:
            # Find natural break point
            match = re.match(r"^(.{20,80}?)(?:\s*[-–|,]|\s{2,})", title)
            if match:
                title = match.group(1)
            else:
                title = title[:80]

        return title.strip() if title.strip() else None

    def _extract_channel(self, container, text: str) -> str | None:
        """Extract TV channel."""
        # Channel element
        channel_elem = container.select_one(
            ".channel, .tv-channel, .broadcaster, "
            "td.channel, .kanal, [class*='channel']"
        )
        if channel_elem:
            channel_text = channel_elem.get_text(strip=True)
            if channel_text:
                return channel_text

        # Common channels
        channels = [
            "TV4 Sport", "TV4+", "TV4",
            "SVT1", "SVT2", "SVT",
            "Eurosport 1", "Eurosport 2", "Eurosport",
            "Viasat Sport", "Viasat Hockey", "Viasat Fotboll", "Viasat",
            "V Sport Premium", "V Sport 1", "V Sport 2", "V Sport",
            "C More Live", "C More Fotboll", "C More Hockey", "C More",
            "Kanal 5", "Kanal 9", "TV3", "TV6",
            "Discovery+", "Max",
        ]

        text_lower = text.lower()
        for channel in channels:
            if channel.lower() in text_lower:
                return channel

        return None

    def _extract_league(self, container, text: str) -> str | None:
        """Extract league/competition."""
        league_elem = container.select_one(
            ".league, .competition, .tournament, "
            "[class*='league'], [class*='competition']"
        )
        if league_elem:
            league_text = league_elem.get_text(strip=True)
            # Don't return generic terms that might be misdetected
            if league_text and league_text.lower() not in ["os", "vm", "em"]:
                return league_text

        text_lower = text.lower()

        # Specific league patterns (longer/more specific first)
        specific_leagues = [
            ("champions league", "Champions League"),
            ("europa league", "Europa League"),
            ("conference league", "Conference League"),
            ("premier league", "Premier League"),
            ("premier padel", "Premier Padel Tour"),
            ("la liga", "La Liga"),
            ("serie a", "Serie A"),
            ("bundesliga", "Bundesliga"),
            ("ligue 1", "Ligue 1"),
            ("eredivisie", "Eredivisie"),
            ("allsvenskan", "Allsvenskan"),
            ("superettan", "Superettan"),
            ("hockeyallsvenskan", "Hockeyallsvenskan"),
            ("shl", "SHL"),
            ("nhl", "NHL"),
            ("nba", "NBA"),
            ("nfl", "NFL"),
            ("mlb", "MLB"),
            ("atp", "ATP"),
            ("wta", "WTA"),
            ("world cup", "World Cup"),
            ("världscupen", "Världscupen"),
            ("shoot out", "Shoot Out"),
            # Sport-specific VM/EM
            ("handboll-vm", "Handbolls-VM"),
            ("handbolls-vm", "Handbolls-VM"),
            ("handboll-em", "Handbolls-EM"),
            ("handbolls-em", "Handbolls-EM"),
            ("fotbolls-vm", "Fotbolls-VM"),
            ("fotbolls-em", "Fotbolls-EM"),
            ("ishockey-vm", "Ishockey-VM"),
            ("hockey-vm", "Hockey-VM"),
            ("dart-vm", "Dart-VM"),
        ]

        for pattern, name in specific_leagues:
            if pattern in text_lower:
                return name

        # Don't return generic VM/EM/OS - these are often misdetected
        return None
