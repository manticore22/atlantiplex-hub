import React, { useState } from 'react'
import './scene-manager.css'

export default function SceneManager({ scenes, currentScene, onSceneSwitch, onDockMove }) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragStart = (e) => {
    setIsDragging(true)
  }

  const handleDragEnd = () => {
    setIsDragging(false)
  }

  return (
    <div className="scene-manager panel-component">
      <div className="panel-header" draggable onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
        <h3 className="panel-title">
          <span className="panel-icon">◆</span>
          Scene Switcher
        </h3>
        <span className="panel-count">{scenes.length}</span>
      </div>

      <div className="scene-list">
        {scenes.length === 0 ? (
          <div className="empty-state">
            <p>No scenes available</p>
            <span className="empty-icon">◇</span>
          </div>
        ) : (
          scenes.map((scene) => (
            <button
              key={scene.id}
              className={`scene-item ${currentScene === scene.id ? 'active' : ''}`}
              onClick={() => onSceneSwitch(scene.id)}
            >
              <span className="scene-thumbnail">
                <span className="thumbnail-icon">◆</span>
              </span>
              <div className="scene-meta">
                <span className="scene-name">{scene.name}</span>
                <span className="scene-sources">{scene.sourceCount || 0} sources</span>
              </div>
              <span className={`scene-indicator ${currentScene === scene.id ? 'live' : ''}`}></span>
            </button>
          ))
        )}
      </div>

      {scenes.length > 0 && (
        <div className="scene-actions">
          <button className="action-btn">+ New Scene</button>
          <button className="action-btn secondary">Duplicate</button>
        </div>
      )}
    </div>
  )
}
