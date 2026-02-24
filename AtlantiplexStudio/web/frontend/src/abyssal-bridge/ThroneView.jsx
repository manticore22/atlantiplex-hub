import React from 'react';
import { Play, Video, Users, Monitor, Stop } from 'lucide-react';

/**
 * Throne View - Central Display
 * Program feed, preview feed, and scene controls
 */
const ThroneView = ({
  programFeed,
  previewFeed,
  isLive,
  currentScene,
  onSceneSwitch,
  scenes
}) => {
  const getSceneIcon = (iconName) => {
    const icons = {
      play: Play,
      video: Video,
      users: Users,
      monitor: Monitor,
      stop: Stop
    };
    const Icon = icons[iconName] || Video;
    return <Icon size={20} />;
  };
  
  return (
    <div className="throne-view">
      {/* Program Feed */}
      <div className={`program-feed ${isLive ? 'live' : ''}`}>
        <div className={`feed-label ${isLive ? 'live' : ''}`}>
          {isLive ? '● Live' : 'Program'}
        </div>
        
        {programFeed ? (
          <video 
            src={programFeed} 
            autoPlay 
            muted 
            playsInline
          />
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '16px',
            color: 'rgba(255, 255, 255, 0.3)'
          }}>
            <Video size={48} />
            <span style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Program Feed
            </span>
          </div>
        )}
        
        {/* Live Indicator */}
        {isLive && (
          <div style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            background: 'rgba(255, 45, 85, 0.2)',
            border: '1px solid rgba(255, 45, 85, 0.4)',
            borderRadius: '4px'
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              background: '#FF2D55',
              borderRadius: '50%',
              animation: 'pulse 1.5s ease-in-out infinite'
            }} />
            <span style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#FF2D55',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              On Air
            </span>
          </div>
        )}
      </div>
      
      {/* Preview Feed */}
      <div className="preview-feed">
        <div className="feed-label">Preview</div>
        
        {previewFeed ? (
          <video 
            src={previewFeed} 
            autoPlay 
            muted 
            playsInline
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
            color: 'rgba(255, 255, 255, 0.2)'
          }}>
            <Monitor size={24} />
            <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Preview
            </span>
          </div>
        )}
      </div>
      
      {/* Scene Glyph Bar */}
      <div className="scene-glyph-bar">
        {scenes.map((scene) => (
          <button
            key={scene.id}
            className={`scene-glyph ${currentScene === scene.id ? 'active' : ''}`}
            onClick={() => onSceneSwitch(scene.id)}
          >
            <div className="scene-glyph-icon">
              {getSceneIcon(scene.icon)}
            </div>
            <span className="scene-glyph-label">{scene.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ThroneView;