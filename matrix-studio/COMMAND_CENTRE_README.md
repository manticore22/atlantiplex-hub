# Abyssal Bridge - Command & Metrics Centre

## Overview

The **Abyssal Bridge** is the Command & Metrics Centre for Atlantiplex Studio — a sovereign intelligence chamber where data flows like bioluminescent tides and every metric is a creature of the abyss reporting to its keeper.

This is not a dashboard. It is a throne-room of telemetry. A war-table of luminous glyphs. The deep-sea nerve-cluster of the Atlantiplex citadel.

## Features

### 1. The Throne View (Central Display)
- **Program Feed**: Primary stream window with bioluminescent edge glow
- **Preview Feed**: Secondary window for staging scenes and transitions
- **Scene Glyph Bar**: Interactive scene switching interface

### 2. Abyssal Metrics Spine (Right Column)
- **Stream Vitals**: Real-time bitrate, FPS, dropped frames, latency
- **Audience Pulse**: Live viewer count with bioluminescent orb visualization
- **Engagement Velocity**: Messages and reactions per minute
- **Sentiment Tide**: Real-time sentiment analysis visualization
- **Guest Diagnostics**: Individual guest connection quality, CPU load, audio levels

### 3. Abyssal Systems Oracle (Left Column)
- **Server Load Runes**: Animated CPU, GPU, RAM visualization
- **WebRTC Constellation**: Visual map of peer connections
- **API Latency River**: Flowing latency visualization with error sparks
- **Historical Performance**: Collapsible hourly, daily, and weekly charts

### 4. Chronicle of Hands (Bottom Strip)
- Real-time log of all actions (moderator, guest, system)
- Filterable by event type
- Animated entry tiles with timestamps
- Exportable activity history

### 5. Sovereign's Altar (Top Bar)
- Stream start/stop controls
- Recording controls
- Scene switching dropdown
- Overlay trigger buttons
- Chat seal/unseal toggle
- Studio lock/unlock toggle
- Broadcast announcements
- Emergency fallback scene

## Visual Identity

### Color Palette
- **Abyssal Black**: `#02040A` - Deep background
- **Bioluminescent Cyan**: `#00F6FF` - Primary accents
- **Deep-Sea Violet**: `#6A00FF` - System metrics
- **Neon Coral**: `#FF3E7F` - Stream status
- **Matrix Green**: `#00FF8A` - Success states

### Design Elements
- Water ripple background animations
- Bioluminescent particle drift
- Holographic glow effects
- Smooth ritualistic transitions
- Deep-sea caustic light patterns

## Architecture

### Frontend
```
matrix-studio/web/frontend/src/
├── CommandCentre.jsx           # Main component
├── command-centre.css          # Abyssal styling
└── command-centre/
    ├── SovereignAltar.jsx      # Top command bar
    ├── ThroneView.jsx          # Central display
    ├── SystemsOracle.jsx       # Left metrics column
    ├── MetricsSpine.jsx        # Right metrics column
    ├── ChronicleOfHands.jsx    # Bottom activity feed
    └── AbyssalEffects.jsx      # Background effects
```

### Backend
```
matrix-studio/web/backend/
├── command-centre-websocket.js # WebSocket namespace
├── command-centre-api.js       # REST API endpoints
└── auth/
    └── command-centre-auth.js  # Admin authentication
```

## WebSocket Events

### Client → Server
- `request:state` - Request current state
- `request:metrics` - Request metrics
- `request:chronicle` - Request chronicle entries
- `chronicle:filter` - Filter chronicle by type
- `command:stream:start` - Start streaming
- `command:stream:stop` - Stop streaming
- `command:recording:start` - Start recording
- `command:recording:stop` - Stop recording
- `command:scene:switch` - Switch scene
- `command:scene:fallback` - Emergency fallback
- `command:overlay:trigger` - Trigger overlay
- `command:chat:seal` - Seal/unseal chat
- `command:studio:lock` - Lock/unlock studio
- `command:broadcast:announce` - Broadcast message

### Server → Client
- `stream:state` - Stream state update
- `metrics:update` - Metrics update
- `chronicle:entry` - New chronicle entry
- `chronicle:batch` - Batch chronicle entries
- `guests:update` - Guest diagnostics update
- `system:alert` - System alert/warning
- `chat:sealed` - Chat seal status
- `studio:locked` - Studio lock status

## REST API Endpoints

### Base URL
```
/api/command-centre
```

### Endpoints

#### GET /state
Get complete Command Centre state.

**Response:**
```json
{
  "success": true,
  "data": {
    "stream": { ... },
    "metrics": { ... },
    "chronicle": [ ... ]
  }
}
```

#### GET /metrics
Get current metrics.

#### POST /metrics
Update metrics from external sources.

**Body:**
```json
{
  "bitrate": 4500,
  "fps": 60,
  ...
}
```

#### GET /chronicle
Get chronicle entries.

**Query Parameters:**
- `limit` - Number of entries (default: 50)
- `type` - Filter by type (all, system, moderator, guest, warning)

#### POST /chronicle
Add chronicle entry.

#### POST /guests/join
Log guest join.

#### POST /guests/leave
Log guest leave.

#### POST /moderator-action
Log moderator action.

#### POST /warning
Log system warning.

#### POST /alert
Log system alert.

#### GET /health
Health check.

## Authentication

The Command Centre requires admin-level access. Allowed roles:
- `super_admin`
- `org_owner`
- `org_admin`
- `manticore_controller`

Access is verified via JWT token passed in:
- WebSocket: `socket.handshake.auth.token`
- REST API: `Authorization: Bearer <token>`

## Usage

### Accessing the Command Centre

Navigate to:
```
https://your-domain.com/?command=true
```

Requires admin authentication.

### Integrating with Existing Systems

#### Logging Guest Activity
```javascript
const commandCentre = require('./command-centre-websocket');

// Guest joins
commandCentre.addGuest({
  id: 'guest-123',
  name: 'John Doe',
  connectionQuality: 0.95,
  cpuLoad: 25,
  audioLevel: -12
});

// Guest leaves
commandCentre.removeGuest('guest-123');
```

#### Logging Moderator Actions
```javascript
commandCentre.logModeratorAction('mute', 'user123', 'moderator_name');
```

#### Updating Metrics
```javascript
commandCentre.updateMetrics({
  bitrate: 5000,
  fps: 60,
  liveViewers: 1500
});
```

#### Logging System Alerts
```javascript
commandCentre.logSystemAlert(
  'High CPU Usage',
  'Server CPU usage exceeded 90%',
  'warning' // or 'critical'
);
```

## Integration with Server

### Adding to Existing Node.js Server

```javascript
const { initializeCommandCentre } = require('./command-centre-websocket');
const commandCentreAPI = require('./command-centre-api');

// Initialize WebSocket namespace
const io = require('socket.io')(server);
initializeCommandCentre(io);

// Add REST API routes
app.use('/api/command-centre', commandCentreAPI);
```

## Security Considerations

1. **Role-Based Access**: Only users with admin roles can access
2. **Token Verification**: All connections verified via JWT
3. **No Client-Side Secrets**: Sensitive data never stored client-side
4. **Audit Logging**: All commands logged to chronicle
5. **Encrypted Transmission**: All WebSocket and HTTP traffic encrypted

## Performance

- **WebSocket**: Real-time updates every 2 seconds for metrics
- **Canvas Animations**: GPU-accelerated particle effects
- **Lazy Loading**: Historical charts load on demand
- **Memory Management**: Chronicle limited to 100 entries (configurable)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires WebSocket and Canvas API support.

## Future Enhancements

- [ ] AI-powered anomaly detection
- [ ] Predictive performance analytics
- [ ] Multi-stream support
- [ ] Custom alert thresholds
- [ ] Integration with external monitoring (Grafana, Datadog)
- [ ] Mobile-responsive layout
- [ ] Voice command integration
- [ ] Holographic VR interface (experimental)

## Contributing

When adding features to the Command Centre:

1. Maintain the abyssal aesthetic
2. Use bioluminescent color palette
3. Add animations that feel organic
4. Follow existing component structure
5. Update this documentation
6. Add chronicle logging for new actions

## Support

For issues or questions regarding the Command Centre:
- Check the health endpoint: `/api/command-centre/health`
- Review WebSocket connection status in browser console
- Verify admin role permissions
- Check server logs for authentication errors

---

*The Abyssal Bridge awaits its sovereign.*
