# SportSync

En Home Assistant custom integration för att visa sportsändningar på TV.

## Funktioner

- **Svenska sport-TV-guider**: Hämtar data från TVsporten.nu och TVmatchen.nu
- **Favoriter**: Följ dina favoritlag, sporter och ligor
- **Flera sensorer**:
  - Alla sändningar
  - Favoriter
  - Live nu
  - Kommande (nästa 3 timmar)
- **Custom Lovelace-kort**: Snyggt kort med två lägen (alla/favoriter)

## Installation

### HACS (Rekommenderat)

1. Öppna HACS
2. Gå till "Integrations"
3. Klicka på de tre prickarna → "Custom repositories"
4. Lägg till repo-URL med kategori "Integration"
5. Sök efter "SportSync" och installera
6. Starta om Home Assistant
7. Gå till Inställningar → Enheter & Tjänster → Lägg till integration → SportSync

### Manuell installation

1. Kopiera `custom_components/sportsync` till din `config/custom_components/` mapp
2. Starta om Home Assistant
3. Lägg till integrationen via UI

## Lovelace-kort

Se [sportsync-card](./sportsync-card/) för det tillhörande Lovelace-kortet.

## Konfiguration

### Inställningar

I integrationens inställningar kan du konfigurera:

- **Uppdateringsintervall**: Hur ofta data hämtas (standard 30 min)
- **Favoritsporter**: Välj vilka sporter du vill följa
- **Favoritlag**: Ange lagnamn (kommaseparerade)
- **Favoritligor**: Ange ligor (kommaseparerade)

### Sensors

Integrationen skapar följande sensorer:

| Sensor | Beskrivning |
|--------|-------------|
| `sensor.sportsync_alla_sandningar` | Alla sändningar för dagen |
| `sensor.sportsync_favoriter` | Sändningar som matchar dina favoriter |
| `sensor.sportsync_live_nu` | Pågående sändningar |
| `sensor.sportsync_kommande` | Sändningar inom 3 timmar |

### Sensor attribut

Varje sensor har ett `events`-attribut med en lista av sändningar:

```json
{
  "events": [
    {
      "id": "abc123",
      "title": "Sverige - Finland",
      "sport": "hockey",
      "league": "Euro Hockey Tour",
      "channel": "TV4",
      "start_time": "2025-12-11T19:00:00",
      "home_team": "Sverige",
      "away_team": "Finland",
      "is_live": false,
      "source": "tvsporten"
    }
  ]
}
```

## Lägga till fler datakällor

Projektet är byggt med en provider-arkitektur som gör det enkelt att lägga till nya datakällor.

### Skapa en ny provider

1. Skapa en ny fil i `providers/`, t.ex. `tvkampen.py`
2. Ärv från `SportProvider` basklassen
3. Implementera `async_fetch_events()` och parsing-logik
4. Lägg till providern i `providers/__init__.py`

Exempel:

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
        # Din parsing-logik här
        pass
```

## Felsökning

### Inga sändningar visas

1. Kontrollera att integrationen är korrekt installerad
2. Kolla loggarna: `Settings → System → Logs` och sök på "sportsync"
3. Verifiera att providers kan nå källsidorna

### Parsing-problem

Om HTML-strukturen på källsidorna ändras kan parsing sluta fungera. Du kan:

1. Öppna ett issue på GitHub
2. Justera selectors i provider-filerna

## Utveckling

```bash
# Klona repot
git clone <repo-url>
cd sportsync

# Kopiera till HA config
cp -r custom_components/sportsync /path/to/ha/config/custom_components/

# Starta om HA och aktivera debug-loggning
```

Lägg till i `configuration.yaml` för debug-loggning:

```yaml
logger:
  default: info
  logs:
    custom_components.sportsync: debug
```

## Licens

MIT
