/**
 * SportSync Card for Home Assistant
 * A Lovelace card to display sport TV broadcasts
 */

const SPORT_ICONS = {
  football: '⚽',
  hockey: '🏒',
  basketball: '🏀',
  tennis: '🎾',
  golf: '⛳',
  handball: '🤾',
  motorsport: '🏎️',
  cycling: '🚴',
  skiing: '⛷️',
  biathlon: '🎯',
  alpine: '⛷️',
  athletics: '🏃',
  swimming: '🏊',
  boxing: '🥊',
  mma: '🥋',
  american_football: '🏈',
  baseball: '⚾',
  volleyball: '🏐',
  table_tennis: '🏓',
  badminton: '🏸',
  rugby: '🏉',
  horse_racing: '🏇',
  snooker: '🎱',
  darts: '🎯',
  padel: '🎾',
  floorball: '🏑',
  bandy: '🏑',
  curling: '🥌',
  esports: '🎮',
  sailing: '⛵',
  winter_sports: '❄️',
  other: '🏆',
};

const SPORT_NAMES = {
  football: 'Fotboll',
  hockey: 'Ishockey',
  basketball: 'Basket',
  tennis: 'Tennis',
  golf: 'Golf',
  handball: 'Handboll',
  motorsport: 'Motorsport',
  cycling: 'Cykling',
  skiing: 'Skidor',
  biathlon: 'Skidskytte',
  alpine: 'Alpint',
  athletics: 'Friidrott',
  swimming: 'Simning',
  boxing: 'Boxning',
  mma: 'MMA',
  american_football: 'Am. fotboll',
  baseball: 'Baseball',
  volleyball: 'Volleyboll',
  table_tennis: 'Bordtennis',
  badminton: 'Badminton',
  rugby: 'Rugby',
  horse_racing: 'Trav/Galopp',
  snooker: 'Snooker',
  darts: 'Dart',
  padel: 'Padel',
  floorball: 'Innebandy',
  bandy: 'Bandy',
  curling: 'Curling',
  esports: 'E-sport',
  sailing: 'Segling',
  winter_sports: 'Vintersport',
  other: 'Övrigt',
};

class SportSyncCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._activeTab = 'all'; // 'all' or 'favorites'
  }

  setConfig(config) {
    if (!config.entity && !config.entity_all && !config.entity_favorites) {
      throw new Error('You need to define an entity');
    }

    this._config = {
      title: config.title || 'Sport på TV',
      entity_all: config.entity_all || config.entity,
      entity_favorites: config.entity_favorites,
      show_channel_logo: config.show_channel_logo !== false,
      show_live_indicator: config.show_live_indicator !== false,
      show_sport_icon: config.show_sport_icon !== false,
      group_by: config.group_by || 'time', // 'time', 'sport', 'channel'
      max_events: config.max_events || 50,
      show_tabs: config.show_tabs !== false,
      default_tab: config.default_tab || 'all',
      ...config,
    };

    this._activeTab = this._config.default_tab;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 4;
  }

  static getConfigElement() {
    return document.createElement('sportsync-card-editor');
  }

  static getStubConfig() {
    return {
      entity_all: 'sensor.sportsync_alla_sandningar',
      entity_favorites: 'sensor.sportsync_favoriter',
      title: 'Sport på TV',
    };
  }

  render() {
    if (!this._hass || !this._config) return;

    const entityId = this._activeTab === 'favorites'
      ? this._config.entity_favorites
      : this._config.entity_all;

    if (!entityId) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="error">Ingen entity konfigurerad för ${this._activeTab}</div>
        </ha-card>
      `;
      return;
    }

    const entity = this._hass.states[entityId];

    if (!entity) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="error">Entity ${entityId} hittades inte</div>
        </ha-card>
      `;
      return;
    }

    const events = entity.attributes.events || [];
    const limitedEvents = events.slice(0, this._config.max_events);

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getStyles()}
      </style>
      <ha-card>
        <div class="card-header">
          <div class="title">${this._config.title}</div>
          ${this._config.show_tabs && this._config.entity_favorites ? this.renderTabs() : ''}
        </div>
        <div class="card-content">
          ${limitedEvents.length > 0
            ? this.renderEvents(limitedEvents)
            : this.renderEmpty()}
        </div>
      </ha-card>
    `;

    // Add tab click handlers
    if (this._config.show_tabs && this._config.entity_favorites) {
      this.shadowRoot.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
          this._activeTab = e.target.dataset.tab;
          this.render();
        });
      });
    }

    // Add event click handlers for expandable details
    this.shadowRoot.querySelectorAll('.event-item').forEach(item => {
      item.addEventListener('click', () => {
        item.classList.toggle('expanded');
      });
    });
  }

  renderTabs() {
    const allCount = this._hass.states[this._config.entity_all]?.state || 0;
    const favCount = this._hass.states[this._config.entity_favorites]?.state || 0;

    return `
      <div class="tabs">
        <button class="tab ${this._activeTab === 'all' ? 'active' : ''}" data-tab="all">
          Alla (${allCount})
        </button>
        <button class="tab ${this._activeTab === 'favorites' ? 'active' : ''}" data-tab="favorites">
          ⭐ Favoriter (${favCount})
        </button>
      </div>
    `;
  }

  renderEvents(events) {
    if (this._config.group_by === 'sport') {
      return this.renderGroupedBySport(events);
    } else if (this._config.group_by === 'channel') {
      return this.renderGroupedByChannel(events);
    }
    return this.renderByTime(events);
  }

  renderByTime(events) {
    // Sort by start time
    const sorted = [...events].sort((a, b) =>
      new Date(a.start_time) - new Date(b.start_time)
    );

    return `
      <div class="events-list">
        ${sorted.map(e => this.renderEventItem(e)).join('')}
      </div>
    `;
  }

  renderGroupedBySport(events) {
    const groups = {};
    events.forEach(e => {
      const sport = e.sport || 'other';
      if (!groups[sport]) groups[sport] = [];
      groups[sport].push(e);
    });

    // Sort sports by number of events
    const sortedSports = Object.keys(groups).sort(
      (a, b) => groups[b].length - groups[a].length
    );

    return sortedSports.map(sport => `
      <div class="sport-group">
        <div class="group-header">
          ${this._config.show_sport_icon ? `<span class="sport-icon">${SPORT_ICONS[sport] || '🏆'}</span>` : ''}
          <span class="group-title">${SPORT_NAMES[sport] || sport}</span>
          <span class="group-count">(${groups[sport].length})</span>
        </div>
        <div class="events-list">
          ${groups[sport]
            .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
            .map(e => this.renderEventItem(e, false))
            .join('')}
        </div>
      </div>
    `).join('');
  }

  renderGroupedByChannel(events) {
    const groups = {};
    events.forEach(e => {
      const channel = e.channel || 'Okänd';
      if (!groups[channel]) groups[channel] = [];
      groups[channel].push(e);
    });

    const sortedChannels = Object.keys(groups).sort();

    return sortedChannels.map(channel => `
      <div class="channel-group">
        <div class="group-header">
          <span class="group-title">${channel}</span>
          <span class="group-count">(${groups[channel].length})</span>
        </div>
        <div class="events-list">
          ${groups[channel]
            .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
            .map(e => this.renderEventItem(e))
            .join('')}
        </div>
      </div>
    `).join('');
  }

  renderEventItem(event, showSportIcon = true) {
    const startTime = new Date(event.start_time);
    const timeStr = startTime.toLocaleTimeString('sv-SE', {
      hour: '2-digit',
      minute: '2-digit'
    });

    const now = new Date();
    const isLive = event.is_live || (startTime <= now && (!event.end_time || new Date(event.end_time) >= now));
    const isUpcoming = startTime > now && (startTime - now) < 3600000; // Within 1 hour

    return `
      <div class="event-item ${isLive ? 'live' : ''} ${isUpcoming ? 'upcoming' : ''}">
        <div class="event-time">
          ${timeStr}
          ${isLive && this._config.show_live_indicator ? '<span class="live-badge">LIVE</span>' : ''}
        </div>
        <div class="event-info">
          <div class="event-title">
            ${showSportIcon && this._config.show_sport_icon ? `<span class="sport-icon-small">${SPORT_ICONS[event.sport] || ''}</span>` : ''}
            ${event.title}
          </div>
          ${event.league ? `<div class="event-league">${event.league}</div>` : ''}
          <div class="event-channel">${event.channel}</div>
        </div>
        <div class="event-details">
          ${event.home_team && event.away_team ? `
            <div class="teams">
              <span class="home-team">${event.home_team}</span>
              <span class="vs">vs</span>
              <span class="away-team">${event.away_team}</span>
            </div>
          ` : ''}
          <div class="source">Källa: ${event.source}</div>
        </div>
      </div>
    `;
  }

  renderEmpty() {
    const message = this._activeTab === 'favorites'
      ? 'Inga favoritsändningar hittades. Lägg till favoriter i integrationens inställningar.'
      : 'Inga sportsändningar hittades för idag.';

    return `
      <div class="empty-state">
        <div class="empty-icon">📺</div>
        <div class="empty-message">${message}</div>
      </div>
    `;
  }

  getStyles() {
    return `
      :host {
        --primary-color: var(--ha-card-header-color, var(--primary-text-color));
        --secondary-color: var(--secondary-text-color);
        --divider-color: var(--divider-color, #e0e0e0);
        --live-color: #f44336;
        --upcoming-color: #ff9800;
      }

      ha-card {
        overflow: hidden;
      }

      .card-header {
        padding: 16px 16px 8px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .title {
        font-size: 1.2em;
        font-weight: 500;
        color: var(--primary-color);
      }

      .tabs {
        display: flex;
        gap: 8px;
      }

      .tab {
        flex: 1;
        padding: 8px 16px;
        border: none;
        background: var(--divider-color);
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9em;
        transition: all 0.2s ease;
      }

      .tab:hover {
        background: var(--primary-color);
        color: var(--card-background-color, white);
      }

      .tab.active {
        background: var(--primary-color);
        color: var(--card-background-color, white);
      }

      .card-content {
        padding: 0 16px 16px;
        max-height: 500px;
        overflow-y: auto;
      }

      .events-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .sport-group, .channel-group {
        margin-bottom: 16px;
      }

      .group-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        border-bottom: 1px solid var(--divider-color);
        margin-bottom: 8px;
      }

      .sport-icon {
        font-size: 1.2em;
      }

      .group-title {
        font-weight: 500;
        color: var(--primary-color);
      }

      .group-count {
        color: var(--secondary-color);
        font-size: 0.9em;
      }

      .event-item {
        display: grid;
        grid-template-columns: 70px 1fr;
        gap: 12px;
        padding: 12px;
        background: var(--card-background-color, white);
        border-radius: 8px;
        border: 1px solid var(--divider-color);
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .event-item:hover {
        border-color: var(--primary-color);
      }

      .event-item.live {
        border-left: 3px solid var(--live-color);
      }

      .event-item.upcoming {
        border-left: 3px solid var(--upcoming-color);
      }

      .event-time {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        font-size: 1.1em;
      }

      .live-badge {
        background: var(--live-color);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.65em;
        margin-top: 4px;
        animation: pulse 1.5s infinite;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
      }

      .event-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 0;
      }

      .event-title {
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .sport-icon-small {
        font-size: 1em;
        flex-shrink: 0;
      }

      .event-league {
        font-size: 0.85em;
        color: var(--secondary-color);
      }

      .event-channel {
        font-size: 0.85em;
        color: var(--secondary-color);
      }

      .event-details {
        display: none;
        grid-column: 1 / -1;
        padding-top: 12px;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }

      .event-item.expanded .event-details {
        display: block;
      }

      .teams {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
      }

      .home-team, .away-team {
        font-weight: 500;
      }

      .vs {
        color: var(--secondary-color);
        font-size: 0.9em;
      }

      .source {
        font-size: 0.8em;
        color: var(--secondary-color);
      }

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;
      }

      .empty-icon {
        font-size: 3em;
        margin-bottom: 16px;
        opacity: 0.5;
      }

      .empty-message {
        color: var(--secondary-color);
        font-size: 0.95em;
      }

      .error {
        padding: 20px;
        color: var(--error-color, red);
        text-align: center;
      }
    `;
  }
}

// Register the card
customElements.define('sportsync-card', SportSyncCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'sportsync-card',
  name: 'SportSync Card',
  description: 'En Lovelace-kort för att visa sportsändningar på TV',
  preview: true,
});

console.info(
  '%c SPORTSYNC-CARD %c 1.0.0 ',
  'color: white; background: #3498db; font-weight: bold;',
  'color: #3498db; background: white; font-weight: bold;'
);
