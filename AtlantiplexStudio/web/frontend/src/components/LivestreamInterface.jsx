import React, { useState, useCallback, useRef, useEffect } from 'react'
import io from 'socket.io-client'
import '../styles/livestream-interface.css'
import ModularDockingPanel from './livestream/ModularDockingPanel'
import SceneManager from './livestream/SceneManager'
import GuestManager from './livestream/GuestManager'
import ChatPanel from './livestream/ChatPanel'
import SourceManager from './livestream/SourceManager'
import StreamControls from './livestream/StreamControls'

export default function LivestreamInterface() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [scenes, setScenes] = useState([])
  const [currentScene, setCurrentScene] = useState(null)
  const [guests, setGuests] = useState([])
  const [sources, setSources] = useState([])
  const [chatMessages, setChatMessages] = useState([])
  const [dockingLayout, setDockingLayout] = useState({
    scenes: { position: 'left', width: 25 },
    sources: { position: 'top', height: 30 },
    guests: { position: 'right', width: 25 },
    chat: { position: 'right-bottom', width: 25 },
    preview: { position: 'center', flex: 1 }
  })
  const [selectedGuests, setSelectedGuests] = useState([])
  const socketRef = useRef(null)

  // Initialize WebSocket connection
  useEffect(() => {
    const socketUrl = import.meta.env.VITE_API_URL || 'http://localhost:9001'
    socketRef.current = io(socketUrl, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    })

    socketRef.current.on('connect', () => {
      console.log('Connected to streaming server')
    })

    socketRef.current.on('scene:update', (data) => {
      setScenes(data)
    })

    socketRef.current.on('guest:update', (data) => {
      setGuests(data)
    })

    socketRef.current.on('chat:message', (message) => {
      setChatMessages(prev => [...prev, message])
    })

    socketRef.current.on('source:update', (data) => {
      setSources(data)
    })

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [])

  const handleStartStream = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.emit('stream:start', {
        scene: currentScene,
        guests: selectedGuests,
        timestamp: new Date().toISOString()
      })
      setIsStreaming(true)
    }
  }, [currentScene, selectedGuests])

  const handleStopStream = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.emit('stream:stop', {
        timestamp: new Date().toISOString()
      })
      setIsStreaming(false)
    }
  }, [])

  const handleSceneSwitch = useCallback((sceneId) => {
    setCurrentScene(sceneId)
    if (socketRef.current) {
      socketRef.current.emit('scene:switch', { sceneId })
    }
  }, [])

  const handleGuestToggle = useCallback((guestId) => {
    setSelectedGuests(prev => {
      if (prev.includes(guestId)) {
        return prev.filter(id => id !== guestId)
      } else {
        return [...prev, guestId]
      }
    })
    if (socketRef.current) {
      socketRef.current.emit('guest:toggle', { guestId })
    }
  }, [])

  const handleDockPanelMove = useCallback((panelId, newPosition) => {
    setDockingLayout(prev => ({
      ...prev,
      [panelId]: { ...prev[panelId], position: newPosition }
    }))
  }, [])

  const handleSendChatMessage = useCallback((message) => {
    if (socketRef.current) {
      socketRef.current.emit('chat:send', {
        message,
        timestamp: new Date().toISOString(),
        sender: 'broadcaster'
      })
    }
  }, [])

  return (
    <div className="livestream-interface">
      {/* Header with Stream Title and Status */}
      <div className="livestream-header">
        <div className="livestream-title-section">
          <div className="livestream-logo">
            <span className="atlantean-glyph">◈</span>
          </div>
          <div className="livestream-info">
            <h1 className="livestream-title">Live Broadcasting Control Center</h1>
            <p className="livestream-subtitle">Multi-Participant Livestream Management</p>
          </div>
        </div>
        <div className="livestream-status">
          <div className={`status-indicator ${isStreaming ? 'live' : 'offline'}`}>
            <span className="status-light"></span>
            <span className="status-text">{isStreaming ? 'LIVE' : 'OFFLINE'}</span>
          </div>
        </div>
      </div>

      {/* Main Layout Container */}
      <div className="livestream-main">
        {/* Left Panel: Scene Manager */}
        <aside className="livestream-panel livestream-panel-left">
          <SceneManager
            scenes={scenes}
            currentScene={currentScene}
            onSceneSwitch={handleSceneSwitch}
            onDockMove={(pos) => handleDockPanelMove('scenes', pos)}
          />
        </aside>

        {/* Center: Preview and Main Controls */}
        <div className="livestream-center">
          {/* Preview Canvas */}
          <div className="livestream-preview-container">
            <div className="livestream-preview">
              <div className="preview-grid">
                {/* Main Preview Area */}
                <div className="preview-main">
                  <div className="preview-content">
                    <div className="scene-preview">
                      {currentScene ? (
                        <div className="scene-placeholder">
                          <span className="scene-icon">◆</span>
                          <p>Scene: {currentScene}</p>
                        </div>
                      ) : (
                        <div className="scene-placeholder empty">
                          <p>Select a scene to preview</p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Holographic Overlay Indicators */}
                  <div className="preview-overlay">
                    <div className="overlay-indicator top-left">REC</div>
                    <div className="overlay-indicator top-right">
                      {guests.length > 0 && `${guests.length} Guests`}
                    </div>
                  </div>
                </div>

                {/* Guest Tiles (up to 4) */}
                <div className="preview-guests">
                  {selectedGuests.slice(0, 4).map((guestId, idx) => (
                    <div key={guestId} className="guest-tile">
                      <div className="guest-placeholder">
                        <span className="guest-icon">◎</span>
                      </div>
                      <div className="guest-status">
                        <span className="status-glow"></span>
                        <span className="status-label">Guest {idx + 1}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Source Icons Layer */}
            <div className="source-icons-layer">
              {sources.map((source) => (
                <div key={source.id} className="source-icon" title={source.name}>
                  <span className="icon-glyph">{source.icon || '◇'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Stream Controls */}
          <StreamControls
            isStreaming={isStreaming}
            onStart={handleStartStream}
            onStop={handleStopStream}
            sceneCount={scenes.length}
            guestCount={selectedGuests.length}
          />
        </div>

        {/* Right Panel: Guests and Chat */}
        <aside className="livestream-panel livestream-panel-right">
          <div className="livestream-panel-stack">
            {/* Guest Manager */}
            <GuestManager
              guests={guests}
              selectedGuests={selectedGuests}
              onGuestToggle={handleGuestToggle}
              onDockMove={(pos) => handleDockPanelMove('guests', pos)}
            />

            {/* Chat Panel */}
            <ChatPanel
              messages={chatMessages}
              onSendMessage={handleSendChatMessage}
              isStreaming={isStreaming}
              onDockMove={(pos) => handleDockPanelMove('chat', pos)}
            />
          </div>
        </aside>
      </div>

      {/* Bottom Panel: Source Management */}
      <div className="livestream-panel livestream-panel-bottom">
        <SourceManager
          sources={sources}
          isStreaming={isStreaming}
          onDockMove={(pos) => handleDockPanelMove('sources', pos)}
        />
      </div>

      {/* Performance & System Stats Footer */}
      <div className="livestream-footer">
        <div className="stats-container">
          <div className="stat-item">
            <span className="stat-label">Bitrate:</span>
            <span className="stat-value">6.5 Mbps</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Resolution:</span>
            <span className="stat-value">1920x1080p60</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Latency:</span>
            <span className="stat-value">2.1ms</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Frames:</span>
            <span className="stat-value">60 FPS</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Viewers:</span>
            <span className="stat-value">1,234</span>
          </div>
        </div>
      </div>
    </div>
  )
}
