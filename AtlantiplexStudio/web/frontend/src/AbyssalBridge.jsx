import React, { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';
import './abyssal-bridge.css';

// Import sub-components
import SovereignAltar from './abyssal-bridge/SovereignAltar';
import ThroneView from './abyssal-bridge/ThroneView';
import SystemsOracle from './abyssal-bridge/SystemsOracle';
import MetricsSpine from './abyssal-bridge/MetricsSpine';
import ChronicleOfHands from './abyssal-bridge/ChronicleOfHands';
import AbyssalEffects from './abyssal-bridge/AbyssalEffects';
import MatrixRain from './abyssal-bridge/MatrixRain';
import HolographicOverlay from './abyssal-bridge/HolographicOverlay';
import DigitalNoise from './abyssal-bridge/DigitalNoise';
import CyberGrid from './abyssal-bridge/CyberGrid';

/**
 * The Abyssal Bridge - Command & Ops Centre
 * The sovereign command interface for Atlantiplex Studio
 * Where the abyssal depths meet the digital matrix
 */
const AbyssalBridge = () => {
  // Connection state
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [bootSequence, setBootSequence] = useState(true);
  const [bootProgress, setBootProgress] = useState(0);
  
  // Stream state
  const [streamState, setStreamState] = useState({
    isLive: false,
    isRecording: false,
    currentScene: 'intro',
    programFeed: null,
    previewFeed: null
  });
  
  // Metrics state
  const [metrics, setMetrics] = useState({
    // Stream vitals
    bitrate: 4500,
    fps: 60,
    droppedFrames: 0,
    latency: 45,
    
    // Audience pulse
    liveViewers: 0,
    engagementVelocity: {
      messagesPerMinute: 0,
      reactionsPerMinute: 0
    },
    sentimentTide: 0.5,
    
    // Guest diagnostics
    guests: [],
    
    // System oracle
    serverLoad: {
      cpu: 35,
      gpu: 42,
      ram: 58
    },
    webrtcConnections: [],
    apiLatency: 85,
    apiErrors: 0,
    
    // Historical data
    history: {
      hourly: [],
      daily: [],
      weekly: []
    }
  });
  
  // Chronicle entries
  const [chronicleEntries, setChronicleEntries] = useState([]);
  
  // WebSocket reference
  const socketRef = useRef(null);
  
  // Boot sequence animation
  useEffect(() => {
    const bootInterval = setInterval(() => {
      setBootProgress(prev => {
        if (prev >= 100) {
          clearInterval(bootInterval);
          setTimeout(() => setBootSequence(false), 500);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 100);
    
    return () => clearInterval(bootInterval);
  }, []);
  
  // Initialize WebSocket connection
  useEffect(() => {
    if (bootSequence) return;
    
    const token = sessionStorage.getItem('token');
    if (!token) {
      setConnectionError('Authentication required');
      return;
    }
    
    // Connect to Abyssal Bridge WebSocket namespace
    const socket = io(`${window.location.origin}/abyssal-bridge`, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });
    
    socketRef.current = socket;
    
    // Connection events
    socket.on('connect', () => {
      console.log('[ABYSSAL_BRIDGE] Neural link established');
      setIsConnected(true);
      setConnectionError(null);
      
      // Request initial state
      socket.emit('request:state');
      socket.emit('request:metrics');
      socket.emit('request:chronicle');
    });
    
    socket.on('disconnect', () => {
      console.log('[ABYSSAL_BRIDGE] Neural link severed');
      setIsConnected(false);
    });
    
    socket.on('connect_error', (error) => {
      console.error('[ABYSSAL_BRIDGE] Connection error:', error);
      setConnectionError(error.message);
      setIsConnected(false);
    });
    
    // Stream state updates
    socket.on('stream:state', (state) => {
      setStreamState(prev => ({ ...prev, ...state }));
    });
    
    // Metrics updates
    socket.on('metrics:update', (newMetrics) => {
      setMetrics(prev => ({
        ...prev,
        ...newMetrics
      }));
    });
    
    // Chronicle entries
    socket.on('chronicle:entry', (entry) => {
      setChronicleEntries(prev => {
        const newEntries = [entry, ...prev].slice(0, 50);
        return newEntries;
      });
    });
    
    // Batch chronicle update
    socket.on('chronicle:batch', (entries) => {
      setChronicleEntries(entries.slice(0, 50));
    });
    
    // Guest diagnostics update
    socket.on('guests:update', (guests) => {
      setMetrics(prev => ({
        ...prev,
        guests
      }));
    });
    
    // System alerts
    socket.on('system:alert', (alert) => {
      const alertEntry = {
        id: `alert-${Date.now()}`,
        type: alert.severity === 'critical' ? 'danger' : 'warning',
        category: 'system',
        title: alert.title,
        message: alert.message,
        timestamp: new Date().toISOString(),
        actor: 'System'
      };
      
      setChronicleEntries(prev => [alertEntry, ...prev].slice(0, 50));
    });
    
    return () => {
      socket.disconnect();
    };
  }, [bootSequence]);
  
  // Command handlers
  const handleCommand = useCallback((command, payload = {}) => {
    if (!socketRef.current || !isConnected) {
      console.error('[ABYSSAL_BRIDGE] Cannot execute command - neural link inactive');
      return;
    }
    
    console.log(`[ABYSSAL_BRIDGE] Executing command: ${command}`, payload);
    socketRef.current.emit(`command:${command}`, payload);
  }, [isConnected]);
  
  // Scene switching
  const handleSceneSwitch = useCallback((sceneId) => {
    handleCommand('scene:switch', { sceneId });
  }, [handleCommand]);
  
  // Stream controls
  const handleStreamToggle = useCallback(() => {
    handleCommand(streamState.isLive ? 'stream:stop' : 'stream:start');
  }, [handleCommand, streamState.isLive]);
  
  const handleRecordingToggle = useCallback(() => {
    handleCommand(streamState.isRecording ? 'recording:stop' : 'recording:start');
  }, [handleCommand, streamState.isRecording]);
  
  // Overlay controls
  const handleOverlayTrigger = useCallback((overlayId) => {
    handleCommand('overlay:trigger', { overlayId });
  }, [handleCommand]);
  
  // Chat controls
  const handleChatSeal = useCallback((sealed) => {
    handleCommand('chat:seal', { sealed });
  }, [handleCommand]);
  
  // Studio lock
  const handleStudioLock = useCallback((locked) => {
    handleCommand('studio:lock', { locked });
  }, [handleCommand]);
  
  // Emergency fallback
  const handleEmergencyFallback = useCallback(() => {
    handleCommand('scene:fallback');
  }, [handleCommand]);
  
  // Broadcast announcement
  const handleBroadcast = useCallback((message) => {
    handleCommand('broadcast:announce', { message });
  }, [handleCommand]);
  
  // Boot sequence overlay
  if (bootSequence) {
    return (
      <div className="abyssal-bridge-boot">
        <MatrixRain intensity="high" />
        <div className="boot-sequence">
          <div className="boot-header">ATLANTIPLEX SYSTEMS</div>
          <div className="boot-subheader">THE ABYSSAL BRIDGE v2.0.77</div>
          <div className="boot-status">
            {bootProgress < 30 && '> Initializing neural pathways...'}
            {bootProgress >= 30 && bootProgress < 60 && '> Synchronizing with abyssal network...'}
            {bootProgress >= 60 && bootProgress < 90 && '> Loading command protocols...'}
            {bootProgress >= 90 && '> Establishing sovereign connection...'}
          </div>
          <div className="boot-progress-container">
            <div 
              className="boot-progress-bar" 
              style={{ width: `${Math.min(bootProgress, 100)}%` }}
            />
          </div>
          <div className="boot-percentage">{Math.min(Math.floor(bootProgress), 100)}%</div>
          <div className="boot-hex">
            {Array.from({ length: 8 }).map((_, i) => (
              <span key={i}>
                {Math.random().toString(16).substr(2, 8).toUpperCase()}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="abyssal-bridge">
      {/* Matrix Digital Rain Background */}
      <MatrixRain intensity="medium" />
      
      {/* Abyssal Bioluminescent Effects */}
      <AbyssalEffects />
      
      {/* Cyber Grid Overlay */}
      <CyberGrid />
      
      {/* Digital Noise/Static */}
      <DigitalNoise intensity={0.03} />
      
      {/* Holographic Overlay */}
      <HolographicOverlay />
      
      {/* Sovereign's Altar - Top Command Bar */}
      <SovereignAltar
        isLive={streamState.isLive}
        isRecording={streamState.isRecording}
        isConnected={isConnected}
        connectionError={connectionError}
        onStreamToggle={handleStreamToggle}
        onRecordingToggle={handleRecordingToggle}
        onSceneSwitch={handleSceneSwitch}
        onOverlayTrigger={handleOverlayTrigger}
        onChatSeal={handleChatSeal}
        onStudioLock={handleStudioLock}
        onEmergencyFallback={handleEmergencyFallback}
        onBroadcast={handleBroadcast}
        currentScene={streamState.currentScene}
      />
      
      {/* Systems Oracle - Left Column */}
      <SystemsOracle
        serverLoad={metrics.serverLoad}
        webrtcConnections={metrics.webrtcConnections}
        apiLatency={metrics.apiLatency}
        apiErrors={metrics.apiErrors}
        history={metrics.history}
      />
      
      {/* Throne View - Center */}
      <ThroneView
        programFeed={streamState.programFeed}
        previewFeed={streamState.previewFeed}
        isLive={streamState.isLive}
        currentScene={streamState.currentScene}
        onSceneSwitch={handleSceneSwitch}
        scenes={[
          { id: 'intro', name: 'Intro', icon: 'play' },
          { id: 'main', name: 'Main', icon: 'video' },
          { id: 'guest', name: 'Guest', icon: 'users' },
          { id: 'screen', name: 'Screen', icon: 'monitor' },
          { id: 'outro', name: 'Outro', icon: 'stop' }
        ]}
      />
      
      {/* Metrics Spine - Right Column */}
      <MetricsSpine
        bitrate={metrics.bitrate}
        fps={metrics.fps}
        droppedFrames={metrics.droppedFrames}
        latency={metrics.latency}
        liveViewers={metrics.liveViewers}
        engagementVelocity={metrics.engagementVelocity}
        sentimentTide={metrics.sentimentTide}
        guests={metrics.guests}
      />
      
      {/* Chronicle of Hands - Bottom Activity Strip */}
      <ChronicleOfHands
        entries={chronicleEntries}
        onFilterChange={(filter) => {
          if (socketRef.current) {
            socketRef.current.emit('chronicle:filter', { filter });
          }
        }}
      />
    </div>
  );
};

export default AbyssalBridge;