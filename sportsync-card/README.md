# SportSync Card

Ett Lovelace-kort för Home Assistant som visar sportsändningar på TV.

## Installation via HACS

1. Öppna HACS i Home Assistant
2. Gå till "Frontend"
3. Klicka på de tre prickarna i övre högra hörnet
4. Välj "Custom repositories"
5. Lägg till denna repo-URL med kategori "Lovelace"
6. Installera "SportSync Card"
7. Starta om Home Assistant

## Manuell installation

1. Ladda ner `dist/sportsync-card.js`
2. Kopiera till `config/www/sportsync-card.js`
3. Lägg till resursen i Lovelace:

```yaml
resources:
  - url: /local/sportsync-card.js
    type: module
```

## Användning

### Enkel konfiguration

```yaml
type: custom:sportsync-card
entity_all: sensor.sportsync_alla_sandningar
entity_favorites: sensor.sportsync_favoriter
```

### Full konfiguration

```yaml
type: custom:sportsync-card
title: Sport på TV idag
entity_all: sensor.sportsync_alla_sandningar
entity_favorites: sensor.sportsync_favoriter
show_tabs: true
default_tab: all
group_by: time  # 'time', 'sport', eller 'channel'
max_events: 50
show_sport_icon: true
show_live_indicator: true
show_channel_logo: true
```

## Konfigurationsalternativ

| Alternativ | Typ | Standard | Beskrivning |
|------------|-----|----------|-------------|
| `entity_all` | string | **krävs** | Sensor entity för alla sändningar |
| `entity_favorites` | string | valfri | Sensor entity för favoriter |
| `title` | string | "Sport på TV" | Kortets titel |
| `show_tabs` | boolean | true | Visa flikar för alla/favoriter |
| `default_tab` | string | "all" | Startflik ("all" eller "favorites") |
| `group_by` | string | "time" | Gruppering ("time", "sport", "channel") |
| `max_events` | number | 50 | Max antal event att visa |
| `show_sport_icon` | boolean | true | Visa sportikoner |
| `show_live_indicator` | boolean | true | Visa LIVE-badge |

## Funktioner

- **Två lägen**: Växla mellan alla sändningar och favoriter
- **Gruppering**: Gruppera efter tid, sport eller kanal
- **Live-indikator**: Röd blinkande badge för pågående sändningar
- **Expanderbara detaljer**: Klicka på ett event för mer info
- **Responsiv design**: Fungerar på alla skärmstorlekar
