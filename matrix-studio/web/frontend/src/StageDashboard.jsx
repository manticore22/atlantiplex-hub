import React, { useEffect, useState } from 'react'
import { getBrandLabel, getPalette } from './branding.ts'
import StageLayoutEditor from './StageLayoutEditor.jsx'
import WebRTCPanel from './WebRTCPanel.jsx'
import io from 'socket.io-client'

const initialParticipants = [
  { id: 'p1', name: 'Panelist A', muted: false },
  { id: 'p2', name: 'Panelist B', muted: false },
  { id: 'ai', name: 'AI Co‑Host', muted: false },
]

export default function StageDashboard() {
  const [participants, setParticipants] = useState(initialParticipants)
  const [messages, setMessages] = useState([{ from: 'system', text: `Welcome to ${getBrandLabel('brandName')}` }])
  const [socket, setSocket] = useState(null)
  const [editorOpen, setEditorOpen] = useState(false)
  const [rtcEnabled, setRtcEnabled] = useState(false)
  const palette = getPalette()

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token') || sessionStorage.getItem('token')
    if (!token) return
    const s = io('/stage', { transports: ['websocket'], auth: { token } })
    setSocket(s)
    s.on('user-joined', (d) => pushMsg(`Peer joined: ${d.id} (${d.count})`))
    s.on('user-left', (d) => pushMsg(`Peer left: ${d.id} (${d.count})`))
    s.on('offer', (d) => pushMsg(`Offer from ${d.from}`))
    s.on('answer', (d) => pushMsg(`Answer from ${d.from}`))
    s.on('ice-candidate', (d) => pushMsg(`ICE candidate from ${d.from}`))
    return () => s.disconnect()
  }, [])

  function pushMsg(text) {
    setMessages((m) => [...m, { from: 'system', text }])
  }

  return (
    <div className="dashboard fade-in">
      <div className="dashboard-grid">
        <aside className="dashboard-sidebar">
          <div className="sidebar-section">
            <h3 className="section-title">Participants</h3>
            <div className="participants-list">
              {participants.map((p) => (
                <div key={p.id} className="participant-item">
                  <div className="participant-avatar">
                    <span className="avatar-initial">{p.name.charAt(0)}</span>
                  </div>
                  <div className="participant-info">
                    <span className="participant-name">{p.name}</span>
                    <span className="participant-status">
                      {p.muted ? '🔇 Muted' : '🎤 Active'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="section-title">Studio Controls</h3>
            <div className="control-buttons">
              <button 
                className={`btn btn-primary ${rtcEnabled ? 'btn-active' : ''}`}
                onClick={() => setRtcEnabled(!rtcEnabled)}
              >
                {rtcEnabled ? '🟢 WebRTC Active' : '🔴 Enable WebRTC'}
              </button>
              <button 
                className="btn btn-accent"
                onClick={() => setEditorOpen(!editorOpen)}
              >
                ⚡ Layout Editor
              </button>
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="section-title">System Messages</h3>
            <div className="messages-container">
              {messages.map((m, i) => (
                <div key={i} className="message-item">
                  <span className="message-source">{m.from}:</span>
                  <span className="message-text">{m.text}</span>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="dashboard-main">
          {editorOpen && (
            <div className="editor-panel slide-up">
              <StageLayoutEditor />
            </div>
          )}
          
          {!editorOpen && rtcEnabled && (
            <div className="rtc-panel scale-in">
              <WebRTCPanel />
            </div>
          )}
          
          {!editorOpen && !rtcEnabled && (
            <div className="welcome-card">
              <div className="welcome-content">
                <h2 className="welcome-title">Welcome to Lightning Studio</h2>
                <p className="welcome-description">
                  Your professional broadcasting platform with real-time collaboration and 
                  advanced scene management capabilities.
                </p>
                <div className="welcome-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={() => setRtcEnabled(true)}
                  >
                    🎥 Start Broadcasting
                  </button>
                  <button 
                    className="btn btn-accent"
                    onClick={() => setEditorOpen(true)}
                  >
                    🎨 Design Layout
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}