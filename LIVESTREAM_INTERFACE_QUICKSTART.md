# Livestreaming Interface - Quick Setup Guide

## Installation

The livestreaming interface is now integrated into Atlantiplex Studio frontend. No additional dependencies needed beyond what's already installed.

### Verify Dependencies

```bash
cd AtlantiplexStudio/web/frontend
npm ls socket.io-client react
```

Required packages:
- `socket.io-client` (^4.6.1) ✓ Already installed
- `react` (^18.2.0) ✓ Already installed

## File Checklist

All files have been created. Verify they exist:

```bash
# Main component
AtlantiplexStudio/web/frontend/src/components/LivestreamInterface.jsx

# Sub-components
AtlantiplexStudio/web/frontend/src/components/livestream/
├── SceneManager.jsx
├── GuestManager.jsx
├── ChatPanel.jsx
├── SourceManager.jsx
├── StreamControls.jsx
└── ModularDockingPanel.jsx

# Stylesheets
AtlantiplexStudio/web/frontend/src/styles/
└── livestream-interface.css

# Individual component styles
AtlantiplexStudio/web/frontend/src/components/livestream/
├── scene-manager.css
├── guest-manager.css
├── chat-panel.css
├── source-manager.css
└── stream-controls.css
```

## Launch Instructions

### 1. Start the Backend

```bash
# Terminal 1: Start Node.js Stage Server
cd AtlantiplexStudio/web/stage
npm start

# Terminal 2: Start Python Flask Backend (optional)
cd AtlantiplexStudio
python COMPLETE_WORKING.py
```

### 2. Start the Frontend

```bash
# Terminal 3: Start Vite dev server
cd AtlantiplexStudio/web/frontend
npm run dev
```

### 3. Access the Interface

Open browser to:
```
http://localhost:5173/?livestream=true
```

You should see:
- Header with "Live Broadcasting Control Center" title
- Scene Switcher on left (will show "No scenes available" until backend provides data)
- Large preview area in center
- Guest Manager on right (top)
- Chat Panel on right (bottom)
- Stream Controls below preview
- Performance stats footer

## Backend Integration

The interface expects these Socket.IO events from your Node.js server:

### Setup Server Event Handlers

In `AtlantiplexStudio/web/stage/server.js` (or equivalent), add:

```javascript
const io = require('socket.io')(9001, {
  cors: { origin: '*' }
})

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id)

  // Send initial scene data
  socket.emit('scene:update', [
    { id: 'scene-1', name: 'Main Camera', sourceCount: 2 },
    { id: 'scene-2', name: 'Screen Share', sourceCount: 1 }
  ])

  // Send guest data
  socket.emit('guest:update', [
    { id: 'guest-1', name: 'John Doe', connected: true, resolution: '1080p', bitrate: '3Mbps' },
    { id: 'guest-2', name: 'Jane Smith', connected: false, resolution: '720p', bitrate: '2Mbps' }
  ])

  // Send source data
  socket.emit('source:update', [
    { id: 'src-1', name: 'Camera', type: 'Video', icon: '📷', active: true },
    { id: 'src-2', name: 'Microphone', type: 'Audio', icon: '🎙', active: true }
  ])

  // Handle stream start
  socket.on('stream:start', (data) => {
    console.log('Stream started:', data)
    io.emit('stream:started', data)
  })

  // Handle stream stop
  socket.on('stream:stop', (data) => {
    console.log('Stream stopped:', data)
    io.emit('stream:stopped', data)
  })

  // Handle scene switch
  socket.on('scene:switch', (data) => {
    console.log('Scene switched:', data)
    io.emit('scene:switched', data)
  })

  // Handle guest toggle
  socket.on('guest:toggle', (data) => {
    console.log('Guest toggled:', data)
    io.emit('guest:toggled', data)
  })

  // Handle chat message
  socket.on('chat:send', (data) => {
    console.log('Chat message:', data)
    io.emit('chat:message', data)
  })

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id)
  })
})
```

## Testing the Interface

### Quick Test Checklist

- [ ] Interface loads without errors
- [ ] Scene list populates from backend
- [ ] Guest tiles show connection status
- [ ] Can toggle guests (checkboxes work)
- [ ] "Start Broadcast" button changes to "Stop Broadcast" when clicked
- [ ] Chat message input is enabled when streaming
- [ ] Performance stats display at bottom
- [ ] All panels are interactive and styled correctly

### Send Test Data (Browser Console)

```javascript
// Open DevTools Console and paste:

// Test scene switch
socket.emit('scene:switch', { sceneId: 'scene-2' })

// Test guest toggle
socket.emit('guest:toggle', { guestId: 'guest-1' })

// Test chat message
socket.emit('chat:send', {
  message: 'Test broadcast message',
  timestamp: new Date().toISOString(),
  sender: 'broadcaster'
})
```

## Customization

### Change Primary Color

Edit `livestream-interface.css` line 1 section and modify:

```css
--primary-accent: #00ff88;  /* Electric green */
```

To any hex color you prefer.

### Modify Panel Layout

Edit `livestream-interface.css` grid:

```css
.livestream-main {
  grid-template-columns: 320px 1fr 320px;  /* Left panel width | center | right panel width */
}
```

### Update Atlantean Glyphs

Replace icon symbols in components:

```jsx
// In SceneManager.jsx
<span className="panel-icon">◆</span>  {/* Change to any Unicode symbol */}
```

Available glyphs:
- ◆ ◇ ◈ ◉ ◎ ◐ ◑ ◒ ◓ ⬥ ⬦ ⬧ ⬨ ⬩ △ ▽ ◁ ▷

## Deployment

### Docker Build

The existing Dockerfile handles everything. Just rebuild:

```bash
docker build -f AtlantiplexStudio/web/frontend/Dockerfile.optimized \
  -t atlantiplex-frontend:latest \
  AtlantiplexStudio/web/frontend/
```

### Production Build

```bash
cd AtlantiplexStudio/web/frontend
npm run build
```

Output goes to `dist/` folder, ready for nginx.

## Troubleshooting

### Port Already in Use

If port 5173 is taken:

```bash
npm run dev -- --port 5174
```

Then access: `http://localhost:5174/?livestream=true`

### Socket.IO Connection Failed

Check that backend is running:

```bash
# Should show "Server running on port 9001"
cd AtlantiplexStudio/web/stage && npm start
```

Verify CORS configuration in backend allows frontend origin.

### Styles Not Loading

Clear browser cache:
```
Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
```

Or hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

### Missing Components

If components fail to load, check:

1. All files in `livestream/` folder exist
2. Import paths are correct
3. CSS files are in `styles/` folder
4. No typos in file names (case-sensitive on Linux)

## Next Steps

1. **Integrate OBS**: Add OBS WebSocket plugin for scene control
2. **Add StreamYard**: Pull guest list and integrate feature comments
3. **Analytics**: Connect to backend analytics service
4. **Hotkeys**: Add keyboard shortcuts for scene switching
5. **Recording**: Implement local file recording controls

## Support

For issues or questions, check:
- `LIVESTREAM_INTERFACE_DOCUMENTATION.md` - Full feature documentation
- Browser DevTools Console - Error messages
- Backend logs - Socket.IO connection status

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Ready for Testing
