import React from 'react'
import './stream-controls.css'

export default function StreamControls({ isStreaming, onStart, onStop, sceneCount, guestCount }) {
  return (
    <div className="stream-controls">
      <div className="controls-primary">
        <button
          className={`control-btn btn-primary ${isStreaming ? 'active' : ''}`}
          onClick={isStreaming ? onStop : onStart}
        >
          <span className="btn-icon">{isStreaming ? '◾' : '⏺'}</span>
          <span className="btn-label">{isStreaming ? 'Stop Broadcast' : 'Start Broadcast'}</span>
        </button>
      </div>

      <div className="controls-secondary">
        <div className="control-indicator">
          <span className="indicator-label">Scenes:</span>
          <span className="indicator-value">{sceneCount}</span>
        </div>
        <div className="control-indicator">
          <span className="indicator-label">Guests:</span>
          <span className="indicator-value">{guestCount}</span>
        </div>
      </div>

      <div className="controls-tertiary">
        <button className="control-btn secondary">
          <span className="btn-icon">⚙</span>
          Settings
        </button>
        <button className="control-btn secondary">
          <span className="btn-icon">📊</span>
          Analytics
        </button>
      </div>
    </div>
  )
}
