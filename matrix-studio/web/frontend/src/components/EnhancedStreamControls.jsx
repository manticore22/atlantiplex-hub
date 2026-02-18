import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, Square, Mic, MicOff, Video, VideoOff, Settings, Users, MessageSquare, Share, Screen, Maximize2, Volume2, VolumeX, Monitor, Camera, CameraOff, Wifi, WifiOff, Zap } from 'lucide-react';

const EnhancedStreamControls = ({ 
  isLive, 
  isRecording, 
  isMuted, 
  isVideoOff, 
  isScreenSharing, 
  onToggleLive, 
  onToggleRecord, 
  onToggleMute, 
  onToggleVideo, 
  onToggleScreenShare,
  viewerCount = 0,
  duration = 0,
  streamQuality = '1080p',
  bitRate = 5000
}) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isParticipantsOpen, setIsParticipantsOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [volume, setVolume] = useState(75);
  const [selectedQuality, setSelectedQuality] = useState(streamQuality);
  const [connectionStatus, setConnectionStatus] = useState('excellent');
  const [streamMetrics, setStreamMetrics] = useState({
    frameRate: 30,
    bitrate: bitRate,
    droppedFrames: 0,
    latency: 25
  });

  const settingsRef = useRef(null);
  const participantsRef = useRef(null);

  useEffect(() => {
    // Simulate real-time stream metrics
    const interval = setInterval(() => {
      setStreamMetrics(prev => ({
        ...prev,
        droppedFrames: Math.floor(Math.random() * 5),
        latency: prev.latency + (Math.random() - 0.5) * 2,
        bitrate: bitRate + (Math.random() - 0.5) * 500
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, [bitRate]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target)) {
        setIsSettingsOpen(false);
      }
      if (participantsRef.current && !participantsRef.current.contains(event.target)) {
        setIsParticipantsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'excellent': return 'text-green-400';
      case 'good': return 'text-yellow-400';
      case 'poor': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'excellent': return <Wifi size={16} className="text-green-400" />;
      case 'good': return <Wifi size={16} className="text-yellow-400" />;
      case 'poor': return <WifiOff size={16} className="text-red-400" />;
      default: return <Wifi size={16} className="text-gray-400" />;
    }
  };

  const ControlButton = ({ 
    icon: Icon, 
    isActive, 
    isDangerous = false, 
    onClick, 
    title, 
    badge = null,
    size = 'medium' 
  }) => (
    <button
      onClick={onClick}
      title={title}
      className={`control-btn ${size} ${isActive ? 'active' : ''} ${isDangerous ? 'danger' : ''}`}
    >
      <Icon size={size === 'small' ? 16 : 20} />
      {badge && <span className="control-badge">{badge}</span>}
    </button>
  );

  const StreamStats = () => (
    <div className="stream-stats">
      <div className="stat-item">
        <span className="stat-label">FPS</span>
        <span className="stat-value">{Math.round(streamMetrics.frameRate)}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Bitrate</span>
        <span className="stat-value">{Math.round(streamMetrics.bitrate / 1000)}k</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Dropped</span>
        <span className="stat-value">{streamMetrics.droppedFrames}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Latency</span>
        <span className="stat-value">{Math.round(streamMetrics.latency)}ms</span>
      </div>
    </div>
  );

  return (
    <div className="enhanced-stream-controls">
      {/* Top Bar - Stream Info */}
      <div className="stream-info-bar">
        <div className="stream-status">
          <div className={`status-indicator ${isLive ? 'live' : 'offline'}`}></div>
          <span className="status-text">{isLive ? 'LIVE' : 'OFFLINE'}</span>
          {isLive && (
            <div className="viewer-count">
              <Users size={16} />
              <span>{viewerCount.toLocaleString()}</span>
            </div>
          )}
        </div>

        <div className="stream-duration">
          {formatDuration(duration)}
        </div>

        <div className="stream-quality">
          <span>{selectedQuality}</span>
        </div>

        <div className="connection-status">
          {getConnectionStatusIcon()}
        </div>
      </div>

      {/* Main Controls */}
      <div className="main-controls">
        <div className="control-group left">
          <ControlButton
            icon={isLive ? Square : Play}
            isActive={isLive}
            isDangerous={isLive}
            onClick={onToggleLive}
            title={isLive ? 'End Stream' : 'Start Stream'}
            size="large"
          />
          
          <ControlButton
            icon={isRecording ? Square : Video}
            isActive={isRecording}
            isDangerous={isRecording}
            onClick={onToggleRecord}
            title={isRecording ? 'Stop Recording' : 'Start Recording'}
            badge={isRecording ? '● REC' : null}
          />
        </div>

        <div className="control-group center">
          <ControlButton
            icon={isMuted ? MicOff : Mic}
            isActive={isMuted}
            onClick={onToggleMute}
            title={isMuted ? 'Unmute' : 'Mute'}
          />
          
          <ControlButton
            icon={isVideoOff ? CameraOff : Camera}
            isActive={isVideoOff}
            onClick={onToggleVideo}
            title={isVideoOff ? 'Start Video' : 'Stop Video'}
          />
          
          <ControlButton
            icon={Screen}
            isActive={isScreenSharing}
            onClick={onToggleScreenShare}
            title={isScreenSharing ? 'Stop Screen Share' : 'Share Screen'}
          />
        </div>

        <div className="control-group right">
          <div className="volume-control">
            <Volume2 size={20} />
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="volume-slider"
            />
            <span className="volume-value">{volume}%</span>
          </div>

          <ControlButton
            icon={Settings}
            isActive={isSettingsOpen}
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
            title="Stream Settings"
          />
          
          <ControlButton
            icon={Users}
            isActive={isParticipantsOpen}
            onClick={() => setIsParticipantsOpen(!isParticipantsOpen)}
            title="Participants"
            badge="3"
          />
          
          <ControlButton
            icon={MessageSquare}
            isActive={isChatOpen}
            onClick={() => setIsChatOpen(!isChatOpen)}
            title="Chat"
            badge="5"
          />
          
          <ControlButton
            icon={Maximize2}
            onClick={() => document.documentElement.requestFullscreen()}
            title="Fullscreen"
          />
        </div>
      </div>

      {/* Stream Metrics Bar */}
      <div className="stream-metrics-bar">
        <StreamStats />
      </div>

      {/* Settings Panel */}
      {isSettingsOpen && (
        <div ref={settingsRef} className="settings-panel">
          <div className="settings-header">
            <h4>Stream Settings</h4>
          </div>
          
          <div className="settings-content">
            <div className="setting-group">
              <label>Video Quality</label>
              <select 
                value={selectedQuality} 
                onChange={(e) => setSelectedQuality(e.target.value)}
                className="quality-select"
              >
                <option value="4K">4K (2160p)</option>
                <option value="1080p">1080p</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Bitrate</label>
              <input
                type="range"
                min="1000"
                max="10000"
                step="500"
                value={bitRate}
                className="bitrate-slider"
              />
              <span className="bitrate-value">{bitRate / 1000} Mbps</span>
            </div>

            <div className="setting-group">
              <label>Frame Rate</label>
              <div className="frame-rate-options">
                {['24', '30', '60'].map(fps => (
                  <button
                    key={fps}
                    className={`frame-rate-btn ${streamMetrics.frameRate === parseInt(fps) ? 'active' : ''}`}
                    onClick={() => setStreamMetrics(prev => ({ ...prev, frameRate: parseInt(fps) }))}
                  >
                    {fps} fps
                  </button>
                ))}
              </div>
            </div>

            <div className="setting-group">
              <label>Audio Input</label>
              <select className="audio-select">
                <option>Default Microphone</option>
                <option>USB Microphone</option>
                <option>Virtual Audio Cable</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Video Input</label>
              <select className="video-select">
                <option>Default Camera</option>
                <option>HD Webcam</option>
                <option>Virtual Camera</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Participants Panel */}
      {isParticipantsOpen && (
        <div ref={participantsRef} className="participants-panel">
          <div className="participants-header">
            <h4>Participants</h4>
            <button className="invite-btn">
              <Users size={16} />
              Invite
            </button>
          </div>
          
          <div className="participants-list">
            {[
              { name: 'John Doe', role: 'Host', status: 'speaking' },
              { name: 'Jane Smith', role: 'Co-host', status: 'muted' },
              { name: 'Bob Wilson', role: 'Guest', status: 'active' }
            ].map((participant, index) => (
              <div key={index} className="participant-item">
                <div className="participant-avatar">
                  <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${participant.name}`} alt={participant.name} />
                </div>
                <div className="participant-info">
                  <span className="participant-name">{participant.name}</span>
                  <span className="participant-role">{participant.role}</span>
                </div>
                <div className="participant-status">
                  {participant.status === 'speaking' && <Mic size={14} />}
                  {participant.status === 'muted' && <MicOff size={14} />}
                  {participant.status === 'active' && <div className="status-dot"></div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat Panel - Simplified for this component */}
      {isChatOpen && (
        <div className="chat-panel">
          <div className="chat-header">
            <h4>Live Chat</h4>
            <button className="close-chat" onClick={() => setIsChatOpen(false)}>
              ×
            </button>
          </div>
          
          <div className="chat-messages">
            <div className="chat-message">
              <span className="chat-user">User123:</span>
              <span className="chat-text">Great stream!</span>
            </div>
            <div className="chat-message">
              <span className="chat-user">Viewer456:</span>
              <span className="chat-text">What software are you using?</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedStreamControls;