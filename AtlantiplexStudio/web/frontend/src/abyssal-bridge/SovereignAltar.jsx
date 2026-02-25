import React from 'react';
import { 
  Radio, 
  Video, 
  MessageSquare, 
  Shield, 
  AlertTriangle, 
  Megaphone,
  Power,
  Circle,
  Wifi,
  WifiOff
} from 'lucide-react';

/**
 * Sovereign's Altar - Top Command Bar
 * High-authority controls for the CEO/Admin
 */
const SovereignAltar = ({
  isLive,
  isRecording,
  isConnected,
  connectionError,
  onStreamToggle,
  onRecordingToggle,
  onSceneSwitch,
  onOverlayTrigger,
  onChatSeal,
  onStudioLock,
  onEmergencyFallback,
  onBroadcast,
  currentScene
}) => {
  const [chatSealed, setChatSealed] = React.useState(false);
  const [studioLocked, setStudioLocked] = React.useState(false);
  const [showBroadcastModal, setShowBroadcastModal] = React.useState(false);
  const [broadcastMessage, setBroadcastMessage] = React.useState('');
  
  const handleChatSeal = () => {
    const newState = !chatSealed;
    setChatSealed(newState);
    onChatSeal(newState);
  };
  
  const handleStudioLock = () => {
    const newState = !studioLocked;
    setStudioLocked(newState);
    onStudioLock(newState);
  };
  
  const handleBroadcastSubmit = () => {
    if (broadcastMessage.trim()) {
      onBroadcast(broadcastMessage.trim());
      setBroadcastMessage('');
      setShowBroadcastModal(false);
    }
  };
  
  // Generate binary pattern
  const generateBinary = () => {
    return Array.from({ length: 16 }, () => Math.random() > 0.5 ? '1' : '0').join('');
  };

  return (
    <div className="sovereign-altar">
      {/* Binary Data Stream */}
      <div style={{
        position: 'absolute',
        top: '4px',
        left: '20px',
        fontSize: '9px',
        color: 'rgba(0, 255, 138, 0.3)',
        fontFamily: 'Courier New, monospace',
        letterSpacing: '1px'
      }}>
        {generateBinary()}
      </div>

      {/* Title & Connection Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Matrix Icon */}
          <div style={{
            width: '32px',
            height: '32px',
            border: '1px solid rgba(0, 255, 138, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'Courier New, monospace',
            fontSize: '18px',
            color: '#00FF8A',
            textShadow: '0 0 10px #00FF8A',
            background: 'rgba(0, 255, 138, 0.05)'
          }}>
            ◈
          </div>
          <div>
            <h1 className="altar-title" style={{ 
              fontFamily: 'Courier New, monospace',
              letterSpacing: '4px',
              fontSize: '16px'
            }}>
              THE ABYSSAL BRIDGE
            </h1>
            <div style={{
              fontSize: '9px',
              color: 'rgba(0, 246, 255, 0.6)',
              fontFamily: 'Courier New, monospace',
              letterSpacing: '2px',
              textTransform: 'uppercase'
            }}>
              Command & Ops Centre v2.0.77
            </div>
          </div>
        </div>
        
        {/* Connection Indicator */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '6px',
          padding: '4px 10px',
          background: isConnected ? 'rgba(0, 255, 138, 0.1)' : 'rgba(255, 45, 85, 0.1)',
          border: `1px solid ${isConnected ? 'rgba(0, 255, 138, 0.3)' : 'rgba(255, 45, 85, 0.3)'}`,
          borderRadius: '4px'
        }}>
          {isConnected ? (
            <Wifi size={12} style={{ color: '#00FF8A' }} />
          ) : (
            <WifiOff size={12} style={{ color: '#FF2D55' }} />
          )}
          <span style={{ 
            fontSize: '10px', 
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            color: isConnected ? '#00FF8A' : '#FF2D55'
          }}>
            {isConnected ? 'Connected' : connectionError || 'Disconnected'}
          </span>
        </div>
      </div>
      
      {/* Controls */}
      <div className="altar-controls">
        {/* Scene Dropdown */}
        <select 
          value={currentScene}
          onChange={(e) => onSceneSwitch(e.target.value)}
          style={{
            padding: '8px 12px',
            background: 'rgba(0, 246, 255, 0.05)',
            border: '1px solid rgba(0, 246, 255, 0.2)',
            borderRadius: '6px',
            color: '#00F6FF',
            fontSize: '12px',
            cursor: 'pointer',
            outline: 'none'
          }}
        >
          <option value="intro">Intro</option>
          <option value="main">Main</option>
          <option value="guest">Guest</option>
          <option value="screen">Screen Share</option>
          <option value="outro">Outro</option>
        </select>
        
        {/* Overlay Triggers */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="altar-rune"
            onClick={() => onOverlayTrigger('stinger1')}
            title="Trigger Stinger 1"
          >
            <Video size={18} />
          </button>
          <button 
            className="altar-rune"
            onClick={() => onOverlayTrigger('stinger2')}
            title="Trigger Stinger 2"
          >
            <Radio size={18} />
          </button>
        </div>
        
        {/* Chat Seal */}
        <button 
          className={`altar-rune ${chatSealed ? 'active' : ''}`}
          onClick={handleChatSeal}
          title={chatSealed ? 'Unseal Chat' : 'Seal Chat'}
        >
          <MessageSquare size={18} />
        </button>
        
        {/* Studio Lock */}
        <button 
          className={`altar-rune ${studioLocked ? 'active' : ''}`}
          onClick={handleStudioLock}
          title={studioLocked ? 'Unlock Studio' : 'Lock Studio'}
        >
          <Shield size={18} />
        </button>
        
        {/* Broadcast */}
        <button 
          className="altar-rune"
          onClick={() => setShowBroadcastModal(true)}
          title="Broadcast Announcement"
        >
          <Megaphone size={18} />
        </button>
        
        {/* Recording Control */}
        <button 
          className={`altar-rune ${isRecording ? 'active' : ''}`}
          onClick={onRecordingToggle}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          <Circle 
            size={18} 
            fill={isRecording ? '#00FF8A' : 'none'}
          />
        </button>
        
        {/* Stream Control */}
        <button 
          className={`altar-rune ${isLive ? 'active' : ''}`}
          onClick={onStreamToggle}
          title={isLive ? 'End Stream' : 'Go Live'}
        >
          <Power size={18} />
        </button>
        
        {/* Emergency Fallback */}
        <button 
          className="altar-rune danger"
          onClick={onEmergencyFallback}
          title="Emergency Fallback Scene"
        >
          <AlertTriangle size={18} />
        </button>
      </div>
      
      {/* Broadcast Modal */}
      {showBroadcastModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(2, 4, 10, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'rgba(20, 27, 45, 0.98)',
            border: '1px solid rgba(0, 246, 255, 0.2)',
            borderRadius: '12px',
            padding: '24px',
            width: '400px',
            maxWidth: '90%'
          }}>
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '16px',
              color: '#00F6FF',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              Broadcast Announcement
            </h3>
            <textarea
              value={broadcastMessage}
              onChange={(e) => setBroadcastMessage(e.target.value)}
              placeholder="Enter announcement message..."
              style={{
                width: '100%',
                minHeight: '100px',
                padding: '12px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(0, 246, 255, 0.2)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '14px',
                resize: 'vertical',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px',
              marginTop: '16px'
            }}>
              <button
                onClick={() => setShowBroadcastModal(false)}
                style={{
                  padding: '8px 16px',
                  background: 'transparent',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  color: 'rgba(255, 255, 255, 0.7)',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleBroadcastSubmit}
                style={{
                  padding: '8px 16px',
                  background: 'rgba(0, 246, 255, 0.2)',
                  border: '1px solid rgba(0, 246, 255, 0.4)',
                  borderRadius: '6px',
                  color: '#00F6FF',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                Broadcast
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SovereignAltar;