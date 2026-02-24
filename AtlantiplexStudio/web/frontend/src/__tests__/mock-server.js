/**
 * MOCK STREAMING SERVER - For Testing Livestream Interface
 * Simulates backend with Socket.IO events
 */

const express = require('express')
const http = require('http')
const socketIo = require('socket.io')

const app = express()
const server = http.createServer(app)
const PORT = process.env.TEST_PORT || 9002

const io = socketIo(server, {
  cors: { origin: '*' }
})

// Mock data
const mockScenes = [
  { id: 'scene-1', name: 'Main Camera', sourceCount: 2 },
  { id: 'scene-2', name: 'Screen Share', sourceCount: 1 },
  { id: 'scene-3', name: 'Picture-in-Picture', sourceCount: 3 }
]

const mockGuests = [
  { id: 'guest-1', name: 'John Doe', connected: true, resolution: '1080p', bitrate: '3Mbps' },
  { id: 'guest-2', name: 'Jane Smith', connected: true, resolution: '1080p', bitrate: '3Mbps' },
  { id: 'guest-3', name: 'Bob Johnson', connected: false, resolution: '720p', bitrate: '2Mbps' },
  { id: 'guest-4', name: 'Alice Williams', connected: true, resolution: '1080p', bitrate: '3.5Mbps' }
]

const mockSources = [
  { id: 'src-1', name: 'Camera', type: 'Video', icon: '📷', active: true },
  { id: 'src-2', name: 'Microphone', type: 'Audio', icon: '🎙', active: true },
  { id: 'src-3', name: 'Screen Share', type: 'Video', icon: '📺', active: false },
  { id: 'src-4', name: 'Media Player', type: 'Video', icon: '▶', active: false }
]

const mockMessages = [
  { sender: 'John Doe', message: 'Great stream setup!', timestamp: new Date(Date.now() - 5000).toISOString() },
  { sender: 'Jane Smith', message: 'Audio is clear', timestamp: new Date(Date.now() - 4000).toISOString() },
  { sender: 'System', message: 'Bob Johnson has joined', timestamp: new Date(Date.now() - 3000).toISOString() }
]

// Track stream state
let streamState = {
  isStreaming: false,
  currentScene: 'scene-1',
  selectedGuests: [],
  chatMessages: mockMessages
}

io.on('connection', (socket) => {
  console.log(`✓ Client connected: ${socket.id}`)

  // Send initial data to client
  socket.emit('scene:update', mockScenes)
  socket.emit('guest:update', mockGuests)
  socket.emit('source:update', mockSources)
  socket.emit('chat:message', mockMessages)

  // Handle stream events
  socket.on('stream:start', (data) => {
    console.log('▶ Stream START requested', data)
    streamState.isStreaming = true
    streamState.currentScene = data.scene
    streamState.selectedGuests = data.guests
    
    io.emit('stream:started', {
      timestamp: new Date().toISOString(),
      scene: data.scene,
      guestCount: data.guests.length
    })
    
    socket.emit('chat:message', {
      sender: 'System',
      message: `Stream started on ${mockScenes.find(s => s.id === data.scene)?.name || 'default'}`,
      timestamp: new Date().toISOString()
    })
  })

  socket.on('stream:stop', (data) => {
    console.log('⏹ Stream STOP requested', data)
    streamState.isStreaming = false
    
    io.emit('stream:stopped', {
      timestamp: new Date().toISOString()
    })
    
    socket.emit('chat:message', {
      sender: 'System',
      message: 'Stream ended',
      timestamp: new Date().toISOString()
    })
  })

  // Handle scene switching
  socket.on('scene:switch', (data) => {
    console.log('◆ Scene SWITCH:', data.sceneId)
    streamState.currentScene = data.sceneId
    
    const sceneName = mockScenes.find(s => s.id === data.sceneId)?.name || 'Unknown'
    
    io.emit('scene:switched', {
      sceneId: data.sceneId,
      sceneName: sceneName,
      timestamp: new Date().toISOString()
    })
    
    if (streamState.isStreaming) {
      socket.emit('chat:message', {
        sender: 'System',
        message: `Scene switched to ${sceneName}`,
        timestamp: new Date().toISOString()
      })
    }
  })

  // Handle guest toggle
  socket.on('guest:toggle', (data) => {
    console.log('◎ Guest TOGGLE:', data.guestId)
    
    const guest = mockGuests.find(g => g.id === data.guestId)
    if (!guest) return
    
    if (streamState.selectedGuests.includes(data.guestId)) {
      streamState.selectedGuests = streamState.selectedGuests.filter(id => id !== data.guestId)
      io.emit('guest:removed', {
        guestId: data.guestId,
        guestName: guest.name,
        timestamp: new Date().toISOString()
      })
    } else {
      streamState.selectedGuests.push(data.guestId)
      io.emit('guest:added', {
        guestId: data.guestId,
        guestName: guest.name,
        timestamp: new Date().toISOString()
      })
    }
    
    if (streamState.isStreaming) {
      const action = streamState.selectedGuests.includes(data.guestId) ? 'added' : 'removed'
      socket.emit('chat:message', {
        sender: 'System',
        message: `${guest.name} ${action} to broadcast`,
        timestamp: new Date().toISOString()
      })
    }
  })

  // Handle chat messages
  socket.on('chat:send', (data) => {
    console.log('💬 Chat MESSAGE:', data.message)
    
    streamState.chatMessages.push(data)
    
    // Broadcast to all clients
    io.emit('chat:message', data)
  })

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log(`✗ Client disconnected: ${socket.id}`)
  })
})

server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════╗
║   MOCK STREAMING SERVER RUNNING                ║
║   Testing Interface on ws://localhost:${PORT}   ║
║                                                ║
║   Mock Data Loaded:                            ║
║   • 3 Scenes                                   ║
║   • 4 Guests                                   ║
║   • 4 Sources                                  ║
║   • 3 Chat Messages                            ║
╚════════════════════════════════════════════════╝
  `)
})

module.exports = server
