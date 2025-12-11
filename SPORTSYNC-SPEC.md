# SportSync - Home Assistant Addon för Sportsändningar

## Projektöversikt

SportSync är ett Home Assistant addon som samlar sportsändningar från flera svenska sport-TV-guider och visar dem i en snygg Lovelace-kort. Perfekt för att snabbt se vilka matcher och sportsändningar som sänds idag.

---

## Datakällor

### Primära källor (Svenska)
| Källa | URL | Prioritet |
|-------|-----|-----------|
| TVsporten.nu | https://www.tvsporten.nu/ | 1 |
| TVmatchen.nu | https://www.tvmatchen.nu/ | 2 |

### Sekundära källor (Nordiska)
| Källa | URL | Land |
|-------|-----|------|
| TVkampen.no | https://www.tvkampen.no/ | Norge |
| TVtid.dk sport | https://www.tvtid.dk/sport | Danmark |

### Metadata (logotyper, lag-info)
- TheSportsDB API (gratis tier)

---

## Tech Stack

| Komponent | Teknologi |
|-----------|-----------|
| Backend | Python 3.11+ |
| HTTP | aiohttp (async) |
| Parsing | BeautifulSoup4 |
| Caching | In-memory dict + TTL |
| API | FastAPI |
| Container | Docker |
| HA Integration | REST sensor + Lovelace card |

---

## Datamodell

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class SportType(Enum):
    FOOTBALL = "football"
    HOCKEY = "hockey"
    BASKETBALL = "basketball"
    TENNIS = "tennis"
    GOLF = "golf"
    WINTER_SPORTS = "winter_sports"
    MOTORSPORT = "motorsport"
    PADEL = "padel"
    SNOOKER = "snooker"
    HORSE_RACING = "horse_racing"
    OTHER = "other"

@dataclass
class SportEvent:
    id: str                          # Unik identifierare
    title: str                       # Event/match-namn
    sport: SportType                 # Sporttyp
    league: Optional[str]            # Liga/tävling
    start_time: datetime             # Starttid (lokal)
    end_time: Optional[datetime]     # Sluttid (om känd)
    channel: str                     # TV-kanal
    channel_logo: Optional[str]      # URL till kanallogga
    teams: Optional[tuple[str, str]] # (hemmalag, bortalag) för matcher
    is_live: bool                    # Sänds just nu
    source: str                      # Vilken källa datan kommer från
```

---

## API Design

### Endpoints

#### GET /api/v1/schedule
Hämtar dagens sportsändningar.

**Query Parameters:**
| Parameter | Typ | Default | Beskrivning |
|-----------|-----|---------|-------------|
| date | string | today | Datum (YYYY-MM-DD) |
| sport | string | all | Filtrera på sport |
| channel | string | all | Filtrera på kanal |
| favorites_only | bool | false | Endast favoriter |

**Response:**
```json
{
  "meta": {
    "date": "2025-12-11",
    "total_count": 42,
    "last_updated": "2025-12-11T08:00:00Z",
    "sources": {
      "tvsporten": { "status": "ok", "events": 25 },
      "tvmatchen": { "status": "ok", "events": 17 }
    }
  },
  "events": [
    {
      "id": "abc123",
      "title": "Sverige - Schweiz",
      "sport": "hockey",
      "league": "Euro Hockey Tour",
      "start_time": "2025-12-11T19:45:00+01:00",
      "end_time": "2025-12-11T22:00:00+01:00",
      "channel": "Telia",
      "channel_logo": "https://...",
      "teams": ["Sverige", "Schweiz"],
      "is_live": false,
      "source": "tvsporten"
    }
  ]
}
```

#### GET /api/v1/health
Hälsostatus för addon.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "cache_age_seconds": 120,
  "sources": {
    "tvsporten": "ok",
    "tvmatchen": "ok"
  }
}
```

#### GET /api/v1/sports
Lista alla tillgängliga sporter.

#### GET /api/v1/channels
Lista alla kanaler med logotyper.

---

## Home Assistant Integration

### Addon Configuration (config.yaml)

```yaml
name: SportSync
version: "1.0.0"
slug: sportsync
description: "Sport-TV-guide för Home Assistant"
arch:
  - amd64
  - aarch64
  - armv7
url: "https://github.com/<repo>/sportsync"
ports:
  8099/tcp: 8099
options:
  refresh_interval: 1800
  favorite_sports:
    - hockey
    - football
  favorite_teams:
    - "Tre Kronor"
    - "Frölunda"
schema:
  refresh_interval: int
  favorite_sports:
    - str
  favorite_teams:
    - str
```

### REST Sensor Configuration

```yaml
# configuration.yaml
rest:
  - resource: http://localhost:8099/api/v1/schedule
    scan_interval: 1800
    sensor:
      - name: "SportSync Schedule"
        value_template: "{{ value_json.meta.total_count }}"
        json_attributes_path: "$.events"
        json_attributes:
          - events

  - resource: http://localhost:8099/api/v1/schedule?favorites_only=true
    scan_interval: 1800
    sensor:
      - name: "SportSync Favorites"
        value_template: "{{ value_json.meta.total_count }}"
        json_attributes_path: "$.events"
        json_attributes:
          - events
```

---

## Lovelace Card

### Funktioner
1. **Gruppering** - Per sport eller per tid
2. **Sport-ikoner** - Emoji för varje sport (⚽🏒🏀🎾 etc.)
3. **Kanal-badges** - Med färger
4. **Tid kvar** - Till event börjar

### Interaktioner
- Klicka för att expandera detaljer
- "Lägg till i kalender"-knapp
- Länk till streamingtjänst

### Card YAML

```yaml
type: custom:sportsync-card
entity: sensor.sportsync_schedule
title: Sport på TV idag
group_by: sport  # eller "time"
show_channel_logo: true
show_live_indicator: true
sports_order:
  - hockey
  - football
  - tennis
max_events: 20
```

### Card Implementation (vanilla JS)

```javascript
class SportSyncCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    const entity = this._hass.states[this.config.entity];
    const events = entity.attributes.events || [];
    
    // Render logic here...
  }
}

customElements.define('sportsync-card', SportSyncCard);
```

---

## Provider Base Class

```python
from abc import ABC, abstractmethod
from typing import List
from models import SportEvent

class SportProvider(ABC):
    """Basklass för alla sport-TV-guider"""
    
    name: str
    base_url: str
    
    @abstractmethod
    async def fetch_events(self, date: str = None) -> List[SportEvent]:
        """Hämta alla sportsändningar för ett datum"""
        pass
    
    @abstractmethod
    def parse_html(self, html: str) -> List[SportEvent]:
        """Parsa HTML till SportEvent-objekt"""
        pass
    
    def get_sport_type(self, text: str) -> SportType:
        """Mappa text till SportType enum"""
        mappings = {
            'fotboll': SportType.FOOTBALL,
            'ishockey': SportType.HOCKEY,
            'hockey': SportType.HOCKEY,
            'basket': SportType.BASKETBALL,
            'tennis': SportType.TENNIS,
            'golf': SportType.GOLF,
            'skidor': SportType.WINTER_SPORTS,
            'alpint': SportType.WINTER_SPORTS,
            'padel': SportType.PADEL,
            'snooker': SportType.SNOOKER,
        }
        text_lower = text.lower()
        for key, sport in mappings.items():
            if key in text_lower:
                return sport
        return SportType.OTHER
```

---

## Development Workflow

### Local Development
```bash
# Clone and setup
git clone <repo>
cd sportsync
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Run locally
python -m sportsync

# Run tests
pytest

# Build Docker image
docker build -t sportsync .
docker run -p 8099:8099 sportsync
```

### Testing with Home Assistant
```yaml
# In configuration.yaml
rest:
  - resource: http://localhost:8099/api/v1/schedule
    scan_interval: 1800
    sensor:
      - name: "SportSync Schedule"
        value_template: "{{ value_json.meta.total_count }}"
        json_attributes_path: "$.events"
        json_attributes:
          - events
```

---

## Implementation Priority

### Phase 1: Core (Week 1)
1. Project structure and config
2. SportEvent model
3. TVsporten.nu provider (Sweden)
4. Basic REST API (/schedule, /health)
5. In-memory caching

### Phase 2: HA Integration (Week 2)
1. Dockerfile and addon config
2. REST sensors setup
3. Basic Lovelace card
4. Favorites system

### Phase 3: Expansion (Week 3+)
1. Additional providers (Norway, Denmark)
2. TheSportsDB integration
3. Notifications
4. Advanced card features
5. Calendar integration

---

## Error Handling

- All providers should fail gracefully
- If one source fails, others should still work
- Log errors but don't crash
- Return partial results if some sources fail
- Include source health in API response

---

## Rate Limiting

To be a good citizen:
- Cache aggressively (30 min default)
- Max 1 request per source per 15 minutes
- Respect robots.txt
- Use reasonable User-Agent
- Implement exponential backoff on failures

---

## Projektstruktur

```
sportsync/
├── sportsync/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── tvsporten.py
│   │   └── tvmatchen.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   └── aggregator.py
│   └── utils/
│       ├── __init__.py
│       └── parsing.py
├── lovelace/
│   └── sportsync-card.js
├── tests/
│   ├── __init__.py
│   ├── test_providers.py
│   └── test_api.py
├── Dockerfile
├── config.yaml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Notes for Claude Code

1. **Start with the provider base class** - this is the foundation
2. **TVsporten.nu is the priority** - get this working first
3. **Use async/await throughout** - aiohttp for HTTP, async for all I/O
4. **Type hints everywhere** - makes the code self-documenting
5. **Tests for parsing** - HTML structure may change, tests help catch issues
6. **Keep the Lovelace card simple** - vanilla JS, no build step
7. **Config validation** - use pydantic or similar for config
8. **Logging** - structured logging for debugging

Good luck! 🚀
