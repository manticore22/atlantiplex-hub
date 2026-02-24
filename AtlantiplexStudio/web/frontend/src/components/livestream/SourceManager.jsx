import React from 'react'
import './source-manager.css'

export default function SourceManager({ sources, isStreaming, onDockMove }) {
  return (
    <div className="source-manager panel-component">
      <div className="panel-header">
        <h3 className="panel-title">
          <span className="panel-icon">◈</span>
          Sources & Media
        </h3>
        <span className="panel-count">{sources.length}</span>
      </div>

      <div className="sources-grid">
        {sources.length === 0 ? (
          <div className="empty-state-horizontal">
            <p>No sources added</p>
            <span className="empty-icon">◇</span>
          </div>
        ) : (
          sources.map((source) => (
            <div key={source.id} className="source-card">
              <div className="source-thumbnail">
                <span className="source-icon">{source.icon || '◈'}</span>
              </div>
              <div className="source-info">
                <span className="source-name">{source.name}</span>
                <span className="source-type">{source.type}</span>
              </div>
              <div className={`source-status ${source.active ? 'active' : ''}`}>
                <span className="status-dot"></span>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="source-actions">
        <button className="action-btn">+ Add Source</button>
        <button className="action-btn secondary">Manage Layers</button>
      </div>
    </div>
  )
}
