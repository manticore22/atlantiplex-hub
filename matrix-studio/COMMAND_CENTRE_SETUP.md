# Abyssal Bridge - Quick Setup Guide

## Installation & Setup

### 1. Frontend Components

All frontend files are already created in:
```
matrix-studio/web/frontend/src/
```

The Command Centre is automatically available via the `?command=true` query parameter for admin users.

### 2. Backend Integration

Add to your main `server.js` file:

```javascript
// At the top with other requires
const { initializeCommandCentre } = require('./backend/command-centre-websocket');
const commandCentreAPI = require('./backend/command-centre-api');

// After creating your Socket.io instance
const io = require('socket.io')(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Initialize Command Centre WebSocket
initializeCommandCentre(io);

// Add Command Centre REST API
app.use('/api/command-centre', commandCentreAPI);
```

### 3. Authentication Setup

Ensure your JWT tokens include the user's role:

```javascript
// When generating JWT tokens
const token = jwt.sign({
  sub: user.id,
  username: user.username,
  role: user.role, // Must be: super_admin, org_owner, org_admin, or manticore_controller
  organization_id: user.organization_id
}, JWT_SECRET);
```

### 4. Environment Variables

Add to your `.env` file:

```env
# Command Centre
JWT_SECRET=your-secret-key
COMMAND_CENTRE_ENABLED=true
```

## Testing the Command Centre

### 1. Start Your Server

```bash
npm start
# or
node server.js
```

### 2. Access the Interface

1. Login as an admin user
2. Navigate to: `http://localhost:3000/?command=true`
3. The Abyssal Bridge should appear with:
   - Top: Sovereign's Altar (controls)
   - Left: Systems Oracle (server metrics)
   - Center: Throne View (stream preview)
   - Right: Metrics Spine (stream stats)
   - Bottom: Chronicle of Hands (activity log)

### 3. Verify WebSocket Connection

Open browser console and look for:
```
[AbyssalBridge] Connected to command centre
```

### 4. Test Controls

Try these actions:
- Click scene glyphs to switch scenes
- Toggle recording (circle button)
- Send a broadcast announcement (megaphone button)
- Seal/unseal chat (message button)

## Integration Examples

### From OBS/WebRTC

```javascript
// When guest joins
fetch('/api/command-centre/guests/join', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    id: 'guest-123',
    name: 'John Doe',
    connectionQuality: 0.95,
    cpuLoad: 25,
    audioLevel: -12
  })
});
```

### From Chat Moderation

```javascript
// When moderator mutes user
fetch('/api/command-centre/moderator-action', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    action: 'mute',
    target: 'username123'
  })
});
```

### From Stream Analytics

```javascript
// Update viewer count
fetch('/api/command-centre/metrics', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    liveViewers: 1523,
    engagementVelocity: {
      messagesPerMinute: 45,
      reactionsPerMinute: 120
    }
  })
});
```

## Troubleshooting

### Connection Issues

**Problem**: "Disconnected from command centre"

**Solution**:
1. Check JWT token is valid and not expired
2. Verify user role is in allowed list
3. Check browser console for WebSocket errors
4. Ensure server is running and port is open

### Missing Data

**Problem**: Metrics showing zeros or empty

**Solution**:
1. POST metrics to `/api/command-centre/metrics`
2. Check metrics are being sent from your streaming server
3. Verify WebSocket is connected

### Styling Issues

**Problem**: Layout looks broken

**Solution**:
1. Ensure `command-centre.css` is imported
2. Check browser supports CSS Grid
3. Verify no conflicting CSS from other components

## File Structure Summary

```
matrix-studio/
├── web/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── CommandCentre.jsx
│   │   │   ├── command-centre.css
│   │   │   ├── command-centre/
│   │   │   │   ├── SovereignAltar.jsx
│   │   │   │   ├── ThroneView.jsx
│   │   │   │   ├── SystemsOracle.jsx
│   │   │   │   ├── MetricsSpine.jsx
│   │   │   │   ├── ChronicleOfHands.jsx
│   │   │   │   └── AbyssalEffects.jsx
│   │   │   └── App.jsx (updated)
│   │   └── ...
│   └── backend/
│       ├── command-centre-websocket.js
│       ├── command-centre-api.js
│       └── auth/
│           └── command-centre-auth.js
└── COMMAND_CENTRE_README.md
```

## Next Steps

1. **Customize Metrics**: Modify the metrics update loop in `command-centre-websocket.js` to pull from your actual data sources
2. **Add More Scenes**: Edit the scenes array in `ThroneView.jsx`
3. **Integrate OBS**: Connect OBS WebSocket to control scenes
4. **Add Alerts**: Set up thresholds for automatic alert generation
5. **Mobile View**: Create a mobile-responsive version

---

**The Abyssal Bridge is now ready for its sovereign.**
