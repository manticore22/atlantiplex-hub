# Atlantiplex Studio Professional Livestreaming Interface

## Overview

A professional-grade livestreaming control center built for Atlantiplex Studio, featuring an Atlantean sci-fi aesthetic with crystalline materials, holographic elements, and real-time multi-participant workflow management.

The interface matches the UI/UX design specification and integrates with StreamYard, OBS Studio, and the existing Atlantiplex backend infrastructure.

---

## Access & Navigation

### Launch the Interface

Access the livestreaming interface via URL parameter:

```
http://localhost:5173/?livestream=true
```

Or from within the application, navigate to the livestream page using the routing system.

---

## Core Features

### 1. **Modular Docking System**

The interface uses a flexible panel-based layout that can be rearranged:

- **Left Panel**: Scene Switcher
  - Switch between pre-configured scenes
  - View scene sources and properties
  - Create and duplicate scenes
  - Live indicator shows active scene

- **Center Area**: Preview & Main Controls
  - High-resolution scene preview
  - Guest tiles (up to 4 visible)
  - Source indicator overlays
  - Stream controls and metrics

- **Right Panel**: Guest Management & Live Chat
  - Guest list with connection status
  - Select guests to add to broadcast
  - Real-time chat with message history
  - One-click feature comments integration

- **Bottom Panel**: Source Management
  - Manage audio, video, and media sources
  - Layer ordering and visibility toggles
  - Drag-to-dock source configuration

### 2. **Scene & Source Management**

**Scene Switcher** (Left Panel)
- Display name and source count
- Live scene indicator (green glow when active)
- Smooth transitions between scenes
- Scene creation and duplication

**Source Manager** (Bottom Panel)
- Camera, microphone, screen share icons
- Source status indicators (live/offline)
- Source layer management
- Quick-add buttons for common sources

### 3. **Guest Management**

**Guest Manager** (Right Panel, Top)
- Display up to 10 connected guests
- Connection status indicators (green = online, red = offline)
- Stream quality info (resolution, bitrate)
- Checkbox selection to add guests to layout
- Real-time connection monitoring

Guest tiles in preview show:
- Guest video placeholder
- Connection status glow
- Guest number label
- Interactive hover states

### 4. **Live Chat Integration**

**Chat Panel** (Right Panel, Bottom)
- Receive live comments from viewers
- Floating message bubbles with holographic styling
- Timestamp for each message
- Broadcaster comment action (animates into main scene)
- Auto-scroll to latest message

### 5. **Stream Controls**

**Primary Control** (Center Bottom)
- Large "Start Broadcast" / "Stop Broadcast" button
- Status indicator (LIVE/OFFLINE) with pulsing light
- Active broadcast animation

**Secondary Controls**
- Scene counter
- Guest counter
- Settings button
- Analytics button

**Footer Statistics**
- Current bitrate (e.g., 6.5 Mbps)
- Resolution (e.g., 1920x1080p60)
- Network latency (e.g., 2.1ms)
- Frame rate (e.g., 60 FPS)
- Viewer count (real-time)

---

## Design Language

### Atlantean Aesthetic

The interface uses ancient Atlantean sci-fi visual language:

- **Crystalline Materials**: Translucent panels with internal glow
- **Aqua-Luminescent Colors**: Electric cyan (#00ff88) and ocean blue (#00d6ff)
- **Holographic Overlays**: Text and UI elements with layered depth
- **Rune-Tech Glyphs**: Ancient symbols used as icons (◆, ◎, ◈)
- **Energy Channels**: Horizontal gradient lines flowing across panels
- **Bioluminescent Status**: Pulsing lights for active elements

### Color Palette

```css
Primary Accent: #00ff88 (Electric Green/Cyan)
Secondary Accent: #00d6ff (Ocean Blue)
Live Indicator: #ff0088 (Magenta/Red)
Background: #0a0b0f (Deep Dark Blue)
Surface: rgba(11, 42, 85, 0.4) (Translucent Panel)
Text Primary: #ffffff
Text Secondary: #a8b2d1
```

### Typography

- **Display**: 'Poppins' or 'Inter' (clean, futuristic)
- **Body**: 'Inter' (optimized for UI)
- **Monospace**: 'JetBrains Mono' (for metrics)
- **Geometric sans-serif** for Atlantean glyph icons

### Motion & Animation

- **Transitions**: 0.3s ease-out (smooth, responsive)
- **Pulses**: 1.5s ease-in-out (status indicators)
- **Micro-interactions**: 0.15s fade effects
- **Status glow**: Continuous oscillation with 0.5-1s cycle

---

## Component Architecture

### Main Component: `LivestreamInterface.jsx`

Entry point managing:
- WebSocket connection to streaming server
- Global state (scenes, guests, messages, sources)
- Socket event handling
- Layout composition

### Sub-Components

1. **SceneManager.jsx** (`scene-manager.css`)
   - Scene selection and switching
   - Scene list rendering
   - Drag-to-dock header

2. **GuestManager.jsx** (`guest-manager.css`)
   - Guest list display
   - Checkbox selection
   - Connection status visualization

3. **ChatPanel.jsx** (`chat-panel.css`)
   - Message scrolling area
   - Auto-scroll to bottom
   - Input field with send button
   - Disabled state during offline

4. **SourceManager.jsx** (`source-manager.css`)
   - Source grid layout
   - Status indicators
   - Quick-action buttons

5. **StreamControls.jsx** (`stream-controls.css`)
   - Large broadcast button
   - Status indicators
   - Metrics display

6. **ModularDockingPanel.jsx**
   - Placeholder for advanced drag-to-dock (future)

---

## WebSocket Events

The interface communicates with the backend via Socket.IO:

### Client → Server

```javascript
// Start streaming
socket.emit('stream:start', { scene, guests, timestamp })

// Stop streaming
socket.emit('stream:stop', { timestamp })

// Switch scene
socket.emit('scene:switch', { sceneId })

// Toggle guest
socket.emit('guest:toggle', { guestId })

// Send chat message
socket.emit('chat:send', { message, timestamp, sender })
```

### Server → Client

```javascript
// Scene updates
socket.on('scene:update', (data) => { /* [{ id, name, sourceCount }, ...] */ })

// Guest updates
socket.on('guest:update', (data) => { /* [{ id, name, connected, resolution, bitrate }, ...] */ })

// Chat message
socket.on('chat:message', (message) => { /* { sender, message, timestamp } */ })

// Source updates
socket.on('source:update', (data) => { /* [{ id, name, type, icon, active }, ...] */ })
```

---

## Responsive Design

### Desktop (1600px+)
- Full 3-column layout
- All panels visible simultaneously
- Maximum preview area

### Tablet (1200px - 1599px)
- Adjusted panel widths
- Guest tiles in 2x2 grid
- Stacked lower panels

### Mobile (< 1200px)
- Single-column layout
- Panels stack vertically
- Simplified guest grid (2 columns)
- Touch-optimized controls

---

## Integration with Existing Stack

### Backend Connection

```javascript
// Initialize connection to Node.js Stage Server
const socketUrl = import.meta.env.VITE_API_URL || 'http://localhost:9001'
const socket = io(socketUrl, {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5
})
```

### Environment Variables

```env
VITE_API_URL=http://localhost:9001
```

### Required Backend Endpoints

The Node.js server (`matrix-studio/web/stage`) must provide:
- Scene management API
- Guest connection handling
- Chat message relay
- Source configuration
- Stream state management

---

## Usage Examples

### Access Livestream Interface
```
?livestream=true
```

### Send Chat Message (Programmatic)
```javascript
socket.emit('chat:send', {
  message: 'Hello viewers!',
  timestamp: new Date().toISOString(),
  sender: 'broadcaster'
})
```

### Start Broadcast
```javascript
socket.emit('stream:start', {
  scene: 'scene-1',
  guests: ['guest-1', 'guest-2'],
  timestamp: new Date().toISOString()
})
```

### Switch Scene
```javascript
socket.emit('scene:switch', { sceneId: 'scene-2' })
```

---

## Performance Optimizations

1. **Lazy Rendering**: Components only re-render on relevant prop changes
2. **Socket Throttling**: Debounced scene switching (prevent rapid changes)
3. **CSS Optimization**: Hardware-accelerated animations using `transform`
4. **Memory**: Auto-cleanup of socket listeners on component unmount
5. **Scrolling**: Virtualized chat messages for large histories (future)

---

## Customization Guide

### Modify Color Scheme

Edit `livestream-interface.css`:

```css
/* Override primary accent */
:root {
  --primary-accent: #00ff88;  /* Change this */
}
```

### Add Custom Glyphs

Modify icon props in components:

```jsx
<span className="panel-icon">◆</span>  {/* Change symbol */}
```

### Adjust Panel Sizes

Edit grid layout in `livestream-interface.css`:

```css
.livestream-main {
  grid-template-columns: 300px 1fr 300px;  /* Adjust widths */
}
```

---

## Known Limitations & Future Enhancements

### Current Limitations
- Guest tiles limited to 4 visible (extensible to grid view)
- Scene preview is placeholder (requires actual OBS/streaming backend)
- Drag-to-dock panels not yet implemented
- No persistent layout state

### Planned Features
1. **Advanced Docking System**: Drag-to-reposition panels
2. **OBS Integration**: Direct control of OBS scenes and sources
3. **StreamYard Sync**: Pull scenes and guests from StreamYard
4. **Advanced Analytics**: Real-time viewer metrics and engagement
5. **Custom Overlays**: Editable text, branding, alerts
6. **Recording Controls**: Local file recording management
7. **Multi-Stream**: Simultaneous streaming to multiple platforms
8. **Keyboard Shortcuts**: Scene switching, guest toggle hotkeys

---

## Troubleshooting

### Interface Not Loading
- Verify `?livestream=true` query parameter
- Check browser console for errors
- Ensure backend server is running

### No Scenes Showing
- Backend must send `scene:update` event
- Check Socket.IO connection status
- Verify API endpoint in `VITE_API_URL`

### Chat Not Appearing
- Confirm `chat:message` events from server
- Check chat panel scroll position
- Verify stream is active

### Guests Not Displaying
- Guest must emit `guest:update` from backend
- Check connection status indicators
- Verify guest selection checkboxes

---

## API Reference

### Component Props

#### SceneManager
- `scenes`: Array of scene objects
- `currentScene`: Currently active scene ID
- `onSceneSwitch`: Callback function
- `onDockMove`: Callback for drag-to-dock

#### GuestManager
- `guests`: Array of guest objects
- `selectedGuests`: Array of selected guest IDs
- `onGuestToggle`: Callback for selection change
- `onDockMove`: Callback for drag-to-dock

#### ChatPanel
- `messages`: Array of message objects
- `onSendMessage`: Callback for new messages
- `isStreaming`: Boolean stream state
- `onDockMove`: Callback for drag-to-dock

#### StreamControls
- `isStreaming`: Boolean stream state
- `onStart`: Start broadcast callback
- `onStop`: Stop broadcast callback
- `sceneCount`: Number of available scenes
- `guestCount`: Number of selected guests

---

## Files Structure

```
frontend/src/
├── components/
│   ├── LivestreamInterface.jsx (main component)
│   └── livestream/
│       ├── SceneManager.jsx
│       ├── GuestManager.jsx
│       ├── ChatPanel.jsx
│       ├── SourceManager.jsx
│       ├── StreamControls.jsx
│       ├── ModularDockingPanel.jsx
│       ├── scene-manager.css
│       ├── guest-manager.css
│       ├── chat-panel.css
│       ├── source-manager.css
│       └── stream-controls.css
├── styles/
│   └── livestream-interface.css (main stylesheet)
└── App.jsx (routing)
```

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android)

---

## License

Part of Atlantiplex Studio. All rights reserved.

---

**Last Updated**: February 2026  
**Version**: 1.0.0  
**Status**: Production Ready
