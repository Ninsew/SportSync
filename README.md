# SportSync

A Home Assistant custom integration for displaying sport TV broadcasts.

## Features

- **Swedish Sport TV Guides**: Fetches data from TVsporten.nu and TVmatchen.nu
- **Favorites**: Follow your favorite teams, sports, and leagues
- **Multiple Sensors**:
  - All broadcasts
  - Favorites
  - Live now
  - Upcoming (next 3 hours)
- **Custom Lovelace Card**: Beautiful card with two modes (all/favorites)

## Installation

### HACS (Recommended)

1. Open HACS
2. Go to "Integrations"
3. Click the three dots → "Custom repositories"
4. Add the repo URL with category "Integration"
5. Search for "SportSync" and install
6. Restart Home Assistant
7. Go to Settings → Devices & Services → Add integration → SportSync

### Manual Installation

1. Copy `custom_components/sportsync` to your `config/custom_components/` folder
2. Restart Home Assistant
3. Add the integration via UI

## Lovelace Card

See [sportsync-card](https://github.com/Ninsew/sportsync-card) for the accompanying Lovelace card.

## Configuration

### Settings

In the integration settings you can configure:

- **Update interval**: How often data is fetched (default 30 min)
- **Favorite sports**: Choose which sports to follow
- **Favorite teams**: Enter team names (comma-separated)
- **Favorite leagues**: Enter leagues (comma-separated)
- **Favorite channels**: Enter TV channels (comma-separated)
- **Title keywords**: Keywords to match in event titles (comma-separated)

### Sensors

The integration creates the following sensors:

| Sensor | Description |
|--------|-------------|
| `sensor.sportsync_all_broadcasts` | All broadcasts for the day |
| `sensor.sportsync_favorites` | Broadcasts matching your favorites |
| `sensor.sportsync_live_now` | Currently live broadcasts |
| `sensor.sportsync_upcoming` | Broadcasts within 3 hours |

### Sensor Attributes

Each sensor has an `events` attribute with a list of broadcasts:

```json
{
  "events": [
    {
      "id": "abc123",
      "title": "Sweden - Finland",
      "sport": "hockey",
      "league": "Euro Hockey Tour",
      "channel": "TV4",
      "start_time": "2025-12-11T19:00:00",
      "home_team": "Sweden",
      "away_team": "Finland",
      "is_live": false,
      "source": "tvsporten"
    }
  ]
}
```

## Adding More Data Sources

The project is built with a provider architecture that makes it easy to add new data sources.

### Creating a New Provider

1. Create a new file in `providers/`, e.g., `tvkampen.py`
2. Inherit from the `SportProvider` base class
3. Implement `async_fetch_events()` and parsing logic
4. Add the provider to `providers/__init__.py`

Example:

```python
from .base import SportProvider, SportEvent

class TVKampenProvider(SportProvider):
    name = "tvkampen"
    base_url = "https://www.tvkampen.no"

    async def async_fetch_events(self, date=None):
        html = await self._async_fetch_html(self.base_url)
        if not html:
            return []
        return self._parse_html(html, date or datetime.now())

    def _parse_html(self, html, date):
        # Your parsing logic here
        pass
```

## Troubleshooting

### No Broadcasts Showing

1. Verify the integration is correctly installed
2. Check the logs: `Settings → System → Logs` and search for "sportsync"
3. Verify that providers can reach the source websites

### Parsing Issues

If the HTML structure on source websites changes, parsing may stop working. You can:

1. Open an issue on GitHub
2. Adjust selectors in the provider files

## Development

```bash
# Clone the repo
git clone https://github.com/Ninsew/SportSync.git
cd SportSync

# Copy to HA config
cp -r custom_components/sportsync /path/to/ha/config/custom_components/

# Restart HA and enable debug logging
```

Add to `configuration.yaml` for debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.sportsync: debug
```

## License

MIT
