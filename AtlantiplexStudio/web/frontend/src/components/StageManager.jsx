import React, { useState, useEffect } from 'react';
import MatrixCurtain from './MatrixCurtain';
import { Settings, Code, Eye, EyeOff, Zap, Palette } from 'lucide-react';

const StageManager = ({ children, onCurtainToggle }) => {
  const [isCurtainOpen, setIsCurtainOpen] = useState(false);
  const [curtainPosition, setCurtainPosition] = useState('front');
  const [showQuickControls, setShowQuickControls] = useState(false);
  const [curtainConfig, setCurtainConfig] = useState({
    autoOpen: true,
    position: 'front',
    triggerOn: 'idle', // idle, manual, schedule, stream-start
    idleTimeout: 300000, // 5 minutes
    fadeInDuration: 1500,
    fadeOutDuration: 1500
  });

  useEffect(() => {
    // Auto-open curtain based on settings
    if (curtainConfig.autoOpen && curtainConfig.triggerOn === 'idle') {
      const idleTimer = setTimeout(() => {
        setIsCurtainOpen(true);
      }, curtainConfig.idleTimeout);

      return () => clearTimeout(idleTimer);
    }
  }, [curtainConfig]);

  const handleCurtainToggle = () => {
    setIsCurtainOpen(!isCurtainOpen);
    onCurtainToggle?.(!isCurtainOpen);
  };

  const handlePositionChange = (position) => {
    setCurtainPosition(position);
  };

  const CurtainQuickControls = () => (
    <div className="curtain-quick-controls">
      <button
        onClick={handleCurtainToggle}
        className="quick-control-btn"
        title={isCurtainOpen ? 'Close Curtain' : 'Open Curtain'}
      >
        {isCurtainOpen ? <EyeOff size={16} /> : <Eye size={16} />}
        <span>{isCurtainOpen ? 'Hide' : 'Show'}</span>
      </button>
      
      <button
        onClick={() => setShowQuickControls(!showQuickControls)}
        className="quick-control-btn settings"
        title="Curtain Settings"
      >
        <Settings size={16} />
      </button>
    </div>
  );

  const CurtainSettingsPanel = () => {
    if (!showQuickControls) return null;

    return (
      <div className="curtain-settings-panel">
        <h4>Curtain Settings</h4>
        
        <div className="setting-group">
          <label>Position</label>
          <div className="position-options">
            {['front', 'back', 'side'].map(pos => (
              <button
                key={pos}
                className={`position-btn ${curtainPosition === pos ? 'active' : ''}`}
                onClick={() => handlePositionChange(pos)}
              >
                {pos.charAt(0).toUpperCase() + pos.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="setting-group">
          <label>
            <input
              type="checkbox"
              checked={curtainConfig.autoOpen}
              onChange={(e) => setCurtainConfig(prev => ({ ...prev, autoOpen: e.target.checked }))}
            />
            Auto-open on idle
          </label>
        </div>

        <div className="setting-group">
          <label>Auto-open trigger</label>
          <select
            value={curtainConfig.triggerOn}
            onChange={(e) => setCurtainConfig(prev => ({ ...prev, triggerOn: e.target.value }))}
          >
            <option value="idle">After inactivity</option>
            <option value="manual">Manual only</option>
            <option value="schedule">Scheduled</option>
            <option value="stream-start">On stream start</option>
          </select>
        </div>

        <div className="setting-group">
          <label>Idle timeout: {curtainConfig.idleTimeout / 1000}s</label>
          <input
            type="range"
            min="60000"
            max="600000"
            step="30000"
            value={curtainConfig.idleTimeout}
            onChange={(e) => setCurtainConfig(prev => ({ ...prev, idleTimeout: parseInt(e.target.value) }))}
          />
        </div>
      </div>
    );
  };

  return (
    <>
      <div className={`stage-container ${isCurtainOpen ? 'curtain-open' : 'curtain-closed'}`}>
        {/* Main Content */}
        <div className={`stage-content ${isCurtainOpen ? 'behind-curtain' : 'visible'}`}>
          {children}
        </div>

        {/* Matrix Curtain */}
        <MatrixCurtain
          isOpen={isCurtainOpen}
          onToggle={handleCurtainToggle}
          position={curtainPosition}
        />

        {/* Stage Status Indicator */}
        <div className="stage-status">
          <div className="status-indicator">
            <div className={`status-dot ${isCurtainOpen ? 'curtain-open' : 'curtain-closed'}`}></div>
            <span className="status-text">
              Stage: {isCurtainOpen ? 'Behind Curtain' : 'Visible'}
            </span>
          </div>
        </div>

        {/* Quick Controls */}
        <CurtainQuickControls />
        <CurtainSettingsPanel />
      </div>
    </>
  );
};

export default StageManager;