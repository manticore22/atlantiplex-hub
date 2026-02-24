/**
 * The Abyssal Bridge - Command & Ops Centre WebSocket Server
 * 
 * Add this to the existing Node.js server.js file
 * This extends the Socket.io server with the /abyssal-bridge namespace
 */

const { verifyAbyssalBridgeAccess } = require('./auth/abyssal-bridge-auth');

// Abyssal Bridge state
const abyssalBridgeState = {
  stream: {
    isLive: false,
    isRecording: false,
    currentScene: 'intro',
    programFeed: null,
    previewFeed: null,
    startedAt: null
  },
  metrics: {
    bitrate: 4500,
    fps: 60,
    droppedFrames: 0,
    latency: 45,
    liveViewers: 0,
    engagementVelocity: {
      messagesPerMinute: 0,
      reactionsPerMinute: 0
    },
    sentimentTide: 0.5,
    guests: [],
    serverLoad: {
      cpu: 35,
      gpu: 42,
      ram: 58
    },
    webrtcConnections: [],
    apiLatency: 85,
    apiErrors: 0
  },
  chronicle: []
};

// Chronicle entry types
const CHRONICLE_TYPES = {
  SYSTEM: 'system',
  MODERATOR: 'moderator',
  GUEST: 'guest',
  WARNING: 'warning',
  DANGER: 'danger'
};

// Initialize Command Centre namespace
function initializeCommandCentre(io) {
  const abyssalBridge = io.of('/command-centre');
  
  // Middleware: Verify admin/CEO access
  abyssalBridge.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token;
      if (!token) {
        return next(new Error('Authentication required'));
      }
      
      const user = await verifyCommandCentreAccess(token);
      if (!user || !user.isAdmin) {
        return next(new Error('Insufficient permissions'));
      }
      
      socket.user = user;
      next();
    } catch (error) {
      next(new Error('Authentication failed'));
    }
  });
  
  abyssalBridge.on('connection', (socket) => {
    console.log(`[CommandCentre] Admin connected: ${socket.user.username}`);
    
    // Send initial state
    socket.emit('stream:state', abyssalBridgeState.stream);
    socket.emit('metrics:update', abyssalBridgeState.metrics);
    socket.emit('chronicle:batch', abyssalBridgeState.chronicle);
    
    // Handle state requests
    socket.on('request:state', () => {
      socket.emit('stream:state', abyssalBridgeState.stream);
    });
    
    socket.on('request:metrics', () => {
      socket.emit('metrics:update', abyssalBridgeState.metrics);
    });
    
    socket.on('request:chronicle', () => {
      socket.emit('chronicle:batch', abyssalBridgeState.chronicle);
    });
    
    // Handle chronicle filtering
    socket.on('chronicle:filter', ({ filter }) => {
      let filtered = abyssalBridgeState.chronicle;
      if (filter && filter !== 'all') {
        filtered = abyssalBridgeState.chronicle.filter(e => e.type === filter);
      }
      socket.emit('chronicle:batch', filtered);
    });
    
    // Command: Stream controls
    socket.on('command:stream:start', () => {
      abyssalBridgeState.stream.isLive = true;
      abyssalBridgeState.stream.startedAt = new Date().toISOString();
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'stream_start',
        title: 'Stream started',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
      console.log(`[CommandCentre] Stream started by ${socket.user.username}`);
    });
    
    socket.on('command:stream:stop', () => {
      abyssalBridgeState.stream.isLive = false;
      abyssalBridgeState.stream.startedAt = null;
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'stream_stop',
        title: 'Stream ended',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
      console.log(`[CommandCentre] Stream stopped by ${socket.user.username}`);
    });
    
    // Command: Recording controls
    socket.on('command:recording:start', () => {
      abyssalBridgeState.stream.isRecording = true;
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'recording_start',
        title: 'Recording started',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
    });
    
    socket.on('command:recording:stop', () => {
      abyssalBridgeState.stream.isRecording = false;
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'recording_stop',
        title: 'Recording stopped',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
    });
    
    // Command: Scene switching
    socket.on('command:scene:switch', ({ sceneId }) => {
      const oldScene = abyssalBridgeState.stream.currentScene;
      abyssalBridgeState.stream.currentScene = sceneId;
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'scene',
        title: `Scene changed: ${oldScene} → ${sceneId}`,
        target: sceneId,
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
    });
    
    // Command: Emergency fallback
    socket.on('command:scene:fallback', () => {
      abyssalBridgeState.stream.currentScene = 'fallback';
      
      addChronicleEntry({
        type: CHRONICLE_TYPES.DANGER,
        category: 'system',
        action: 'emergency_fallback',
        title: 'EMERGENCY: Fallback scene activated',
        actor: socket.user.username
      });
      
      // Broadcast alert to all
      broadcastToAll(abyssalBridge, 'system:alert', {
        severity: 'critical',
        title: 'Emergency Fallback Activated',
        message: `Fallback scene activated by ${socket.user.username}`
      });
      
      broadcastToAll(abyssalBridge, 'stream:state', abyssalBridgeState.stream);
    });
    
    // Command: Overlay triggers
    socket.on('command:overlay:trigger', ({ overlayId }) => {
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'overlay',
        title: `Overlay triggered: ${overlayId}`,
        target: overlayId,
        actor: socket.user.username
      });
      
      // Broadcast overlay trigger to stage namespace
      io.of('/stage').emit('overlay:trigger', { overlayId });
    });
    
    // Command: Chat controls
    socket.on('command:chat:seal', ({ sealed }) => {
      addChronicleEntry({
        type: CHRONICLE_TYPES.MODERATOR,
        category: 'moderator',
        action: sealed ? 'chat_seal' : 'chat_unseal',
        title: sealed ? 'Chat sealed' : 'Chat unsealed',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'chat:sealed', { sealed });
    });
    
    // Command: Studio lock
    socket.on('command:studio:lock', ({ locked }) => {
      addChronicleEntry({
        type: CHRONICLE_TYPES.MODERATOR,
        category: 'moderator',
        action: locked ? 'studio_lock' : 'studio_unlock',
        title: locked ? 'Studio locked' : 'Studio unlocked',
        actor: socket.user.username
      });
      
      broadcastToAll(abyssalBridge, 'studio:locked', { locked });
    });
    
    // Command: Broadcast announcement
    socket.on('command:broadcast:announce', ({ message }) => {
      addChronicleEntry({
        type: CHRONICLE_TYPES.SYSTEM,
        category: 'system',
        action: 'broadcast',
        title: 'Announcement broadcasted',
        details: message.substring(0, 50) + (message.length > 50 ? '...' : ''),
        actor: socket.user.username
      });
      
      // Broadcast to all namespaces
      io.of('/stage').emit('broadcast:message', { message, from: socket.user.username });
      io.of('/chat').emit('broadcast:message', { message, from: socket.user.username });
    });
    
    socket.on('disconnect', () => {
      console.log(`[CommandCentre] Admin disconnected: ${socket.user.username}`);
    });
  });
  
  // Start metrics update loop
  startMetricsUpdates(abyssalBridge);
  
  return abyssalBridge;
}

// Helper: Add chronicle entry
function addChronicleEntry(entry) {
  const fullEntry = {
    id: `entry-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    ...entry
  };
  
  abyssalBridgeState.chronicle.unshift(fullEntry);
  
  // Keep only last 100 entries
  if (abyssalBridgeState.chronicle.length > 100) {
    abyssalBridgeState.chronicle = abyssalBridgeState.chronicle.slice(0, 100);
  }
  
  return fullEntry;
}

// Helper: Broadcast to all connected sockets
function broadcastToAll(namespace, event, data) {
  namespace.emit(event, data);
}

// Metrics update simulation (replace with real data sources)
function startMetricsUpdates(abyssalBridge) {
  setInterval(() => {
    // Simulate metric fluctuations
    abyssalBridgeState.metrics.bitrate = 4000 + Math.random() * 1000;
    abyssalBridgeState.metrics.fps = 58 + Math.random() * 4;
    abyssalBridgeState.metrics.latency = 40 + Math.random() * 20;
    abyssalBridgeState.metrics.serverLoad.cpu = 30 + Math.random() * 20;
    abyssalBridgeState.metrics.serverLoad.ram = 50 + Math.random() * 15;
    
    // Simulate viewer fluctuations if live
    if (abyssalBridgeState.stream.isLive) {
      const change = Math.floor(Math.random() * 10) - 5;
      abyssalBridgeState.metrics.liveViewers = Math.max(0, 
        abyssalBridgeState.metrics.liveViewers + change
      );
    }
    
    broadcastToAll(abyssalBridge, 'metrics:update', abyssalBridgeState.metrics);
  }, 2000);
}

// API: Get command centre state
function getCommandCentreState() {
  return { ...abyssalBridgeState };
}

// API: Update metrics from external sources
function updateMetrics(metrics) {
  Object.assign(abyssalBridgeState.metrics, metrics);
}

// API: Add guest
function addGuest(guest) {
  abyssalBridgeState.metrics.guests.push(guest);
  
  addChronicleEntry({
    type: CHRONICLE_TYPES.GUEST,
    category: 'guest',
    action: 'join',
    title: `${guest.name} joined the stream`,
    actor: guest.name
  });
}

// API: Remove guest
function removeGuest(guestId) {
  const guest = abyssalBridgeState.metrics.guests.find(g => g.id === guestId);
  if (guest) {
    abyssalBridgeState.metrics.guests = 
      abyssalBridgeState.metrics.guests.filter(g => g.id !== guestId);
    
    addChronicleEntry({
      type: CHRONICLE_TYPES.GUEST,
      category: 'guest',
      action: 'leave',
      title: `${guest.name} left the stream`,
      actor: guest.name
    });
  }
}

// API: Moderator action
function logModeratorAction(action, target, moderator) {
  addChronicleEntry({
    type: CHRONICLE_TYPES.MODERATOR,
    category: 'moderator',
    action: action,
    title: `${action}: ${target}`,
    target: target,
    actor: moderator
  });
}

// API: System warning
function logSystemWarning(title, message) {
  addChronicleEntry({
    type: CHRONICLE_TYPES.WARNING,
    category: 'warning',
    action: 'warning',
    title: title,
    message: message
  });
}

// API: System alert
function logSystemAlert(title, message, severity = 'warning') {
  addChronicleEntry({
    type: severity === 'critical' ? CHRONICLE_TYPES.DANGER : CHRONICLE_TYPES.WARNING,
    category: 'warning',
    action: 'alert',
    title: title,
    message: message
  });
}

module.exports = {
  initializeCommandCentre,
  getCommandCentreState,
  updateMetrics,
  addGuest,
  removeGuest,
  logModeratorAction,
  logSystemWarning,
  logSystemAlert,
  CHRONICLE_TYPES
};