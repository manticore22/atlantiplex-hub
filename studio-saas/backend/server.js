// SERAPHONIX STUDIO - Enhanced Backend Server
// Express + WebSocket + JWT Auth + Streaming Infrastructure
// Hybrid of StreamYards + OBS functionality

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const bodyParser = require('body-parser');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const fs = require('fs-extra');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || 'seraphonix-studio-secret-key-production';
const STRIPE_SECRET = process.env.STRIPE_SECRET || '';

// ============================================
// MIDDLEWARE
// ============================================

// CORS - Allow specific origins
const corsOptions = {
    origin: ['http://localhost:3000', 'http://localhost:80', 'http://76.13.242.128', 'http://76.13.242.128:80', 'http://76.13.242.128:3000'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true
};
app.use(cors(corsOptions));
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '50mb' }));

// Serve static files
app.use(express.static(path.join(__dirname, '../frontend')));
app.use('/streams', express.static(path.join(__dirname, 'streams')));

// ============================================
// DATA STORAGE
// ============================================

const DATA_DIR = path.join(__dirname, 'data');
const STREAMS_DIR = path.join(__dirname, 'streams');

const FILES = {
    USERS: path.join(DATA_DIR, 'users.json'),
    SUBSCRIPTIONS: path.join(DATA_DIR, 'subscriptions.json'),
    PRODUCTS: path.join(DATA_DIR, 'products.json'),
    GUESTS: path.join(DATA_DIR, 'guests.json'),
    STREAMS: path.join(DATA_DIR, 'streams.json'),
    CHAT: path.join(DATA_DIR, 'chat.json'),
    ROOMS: path.join(DATA_DIR, 'rooms.json'),
    SETTINGS: path.join(DATA_DIR, 'settings.json')
};

// Ensure directories exist
fs.ensureDirSync(DATA_DIR);
fs.ensureDirSync(STREAMS_DIR);

// Initialize data files
Object.values(FILES).forEach(file => {
    if (!fs.existsSync(file)) {
        fs.writeFileSync(file, JSON.stringify({}));
    }
});

// Data helpers
async function readData(file) {
    try {
        const data = await fs.readFile(file, 'utf8');
        return JSON.parse(data);
    } catch {
        return {};
    }
}

async function writeData(file, data) {
    await fs.writeFile(file, JSON.stringify(data, null, 2));
}

// ============================================
// AUTHENTICATION
// ============================================

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Authentication required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
}

// ============================================
// WEBSOCKET MANAGEMENT
// ============================================

const rooms = new Map(); // roomId -> { host, guests, chat, streamData }
const clients = new Map(); // ws -> { userId, roomId, role }

wss.on('connection', (ws, req) => {
    console.log('🔌 New WebSocket connection');
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            await handleWebSocketMessage(ws, data);
        } catch (error) {
            console.error('WebSocket message error:', error);
            ws.send(JSON.stringify({ type: 'error', message: error.message }));
        }
    });

    ws.on('close', () => {
        handleClientDisconnect(ws);
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });

    // Send welcome message
    ws.send(JSON.stringify({
        type: 'connected',
        message: 'Connected to Seraphonix Studio'
    }));
});

async function handleWebSocketMessage(ws, data) {
    const { type, payload } = data;

    switch (type) {
        case 'join-room':
            await handleJoinRoom(ws, payload);
            break;
        case 'leave-room':
            await handleLeaveRoom(ws);
            break;
        case 'chat':
            await handleChatMessage(ws, payload);
            break;
        case 'offer':
            await handleWebRTCOffer(ws, payload);
            break;
        case 'answer':
            await handleWebRTCAnswer(ws, payload);
            break;
        case 'ice-candidate':
            await handleICECandidate(ws, payload);
            break;
        case 'start-stream':
            await handleStartStream(ws, payload);
            break;
        case 'stop-stream':
            await handleStopStream(ws);
            break;
        case 'guest-join':
            await handleGuestJoin(ws, payload);
            break;
        case 'guest-leave':
            await handleGuestLeave(ws, payload);
            break;
        case 'update-settings':
            await handleUpdateSettings(ws, payload);
            break;
        case 'scene-change':
            await handleSceneChange(ws, payload);
            break;
        default:
            console.log('Unknown message type:', type);
    }
}

async function handleJoinRoom(ws, { roomId, token, role }) {
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const userId = decoded.id || decoded.email;
        
        // Create room if it doesn't exist
        if (!rooms.has(roomId)) {
            rooms.set(roomId, {
                id: roomId,
                host: null,
                guests: new Map(),
                chat: [],
                isStreaming: false,
                streamData: null,
                createdAt: new Date().toISOString()
            });
        }

        const room = rooms.get(roomId);
        
        // Store client info
        clients.set(ws, { userId, roomId, role, email: decoded.email });

        if (role === 'host') {
            room.host = { userId, ws, email: decoded.email };
            console.log(`👤 Host joined room: ${roomId}`);
        } else {
            room.guests.set(userId, { userId, ws, email: decoded.email });
            console.log(`👥 Guest joined room: ${roomId}`);
            
            // Notify host
            if (room.host && room.host.ws.readyState === WebSocket.OPEN) {
                room.host.ws.send(JSON.stringify({
                    type: 'guest-joined',
                    guest: { userId, email: decoded.email }
                }));
            }
        }

        // Send room state to client
        ws.send(JSON.stringify({
            type: 'room-joined',
            roomId,
            role,
            guests: Array.from(room.guests.values()).map(g => ({
                userId: g.userId,
                email: g.email
            })),
            isStreaming: room.isStreaming
        }));

        // Broadcast to all clients in room
        broadcastToRoom(roomId, {
            type: 'user-joined',
            userId,
            role,
            email: decoded.email
        }, ws);

    } catch (error) {
        console.error('Join room error:', error);
        ws.send(JSON.stringify({ type: 'error', message: 'Failed to join room' }));
    }
}

async function handleLeaveRoom(ws) {
    const client = clients.get(ws);
    if (!client) return;

    const { roomId, userId, role } = client;
    const room = rooms.get(roomId);

    if (room) {
        if (role === 'host') {
            room.host = null;
        } else {
            room.guests.delete(userId);
        }

        // Notify others
        broadcastToRoom(roomId, {
            type: 'user-left',
            userId,
            role
        }, ws);

        // Clean up empty rooms
        if (!room.host && room.guests.size === 0) {
            rooms.delete(roomId);
            console.log(`🗑️ Room deleted: ${roomId}`);
        }
    }

    clients.delete(ws);
}

async function handleChatMessage(ws, { message, platform = 'all' }) {
    const client = clients.get(ws);
    if (!client) return;

    const { roomId, email } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    const chatMessage = {
        id: uuidv4(),
        author: email.split('@')[0],
        email,
        message,
        platform,
        timestamp: new Date().toISOString()
    };

    room.chat.push(chatMessage);

    // Save to file
    const chatData = await readData(FILES.CHAT);
    if (!chatData[roomId]) chatData[roomId] = [];
    chatData[roomId].push(chatMessage);
    await writeData(FILES.CHAT, chatData);

    // Broadcast to all in room
    broadcastToRoom(roomId, {
        type: 'chat-message',
        message: chatMessage
    });
}

async function handleStartStream(ws, { destinations, settings }) {
    const client = clients.get(ws);
    if (!client || client.role !== 'host') {
        ws.send(JSON.stringify({ type: 'error', message: 'Only host can start stream' }));
        return;
    }

    const { roomId } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    room.isStreaming = true;
    room.streamData = {
        destinations,
        settings,
        startedAt: new Date().toISOString(),
        viewers: 0
    };

    // Save stream info
    const streams = await readData(FILES.STREAMS);
    streams[roomId] = room.streamData;
    await writeData(FILES.STREAMS, streams);

    // Notify all clients
    broadcastToRoom(roomId, {
        type: 'stream-started',
        destinations,
        settings
    });

    console.log(`🔴 Stream started in room: ${roomId}`);
}

async function handleStopStream(ws) {
    const client = clients.get(ws);
    if (!client || client.role !== 'host') return;

    const { roomId } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    room.isStreaming = false;
    
    if (room.streamData) {
        room.streamData.endedAt = new Date().toISOString();
        
        // Save final stream data
        const streams = await readData(FILES.STREAMS);
        streams[roomId] = room.streamData;
        await writeData(FILES.STREAMS, streams);
    }

    // Notify all clients
    broadcastToRoom(roomId, {
        type: 'stream-stopped'
    });

    console.log(`⏹️ Stream stopped in room: ${roomId}`);
}

// WebRTC signaling
async function handleWebRTCOffer(ws, { targetUserId, offer }) {
    const client = clients.get(ws);
    if (!client) return;

    const { roomId } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    // Find target client
    let targetWs = null;
    
    if (room.host && room.host.userId === targetUserId) {
        targetWs = room.host.ws;
    } else {
        const guest = room.guests.get(targetUserId);
        if (guest) targetWs = guest.ws;
    }

    if (targetWs && targetWs.readyState === WebSocket.OPEN) {
        targetWs.send(JSON.stringify({
            type: 'offer',
            from: client.userId,
            offer
        }));
    }
}

async function handleWebRTCAnswer(ws, { targetUserId, answer }) {
    const client = clients.get(ws);
    if (!client) return;

    const { roomId } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    // Find target client
    let targetWs = null;
    
    if (room.host && room.host.userId === targetUserId) {
        targetWs = room.host.ws;
    } else {
        const guest = room.guests.get(targetUserId);
        if (guest) targetWs = guest.ws;
    }

    if (targetWs && targetWs.readyState === WebSocket.OPEN) {
        targetWs.send(JSON.stringify({
            type: 'answer',
            from: client.userId,
            answer
        }));
    }
}

async function handleICECandidate(ws, { targetUserId, candidate }) {
    const client = clients.get(ws);
    if (!client) return;

    const { roomId } = client;
    const room = rooms.get(roomId);

    if (!room) return;

    // Find target client
    let targetWs = null;
    
    if (room.host && room.host.userId === targetUserId) {
        targetWs = room.host.ws;
    } else {
        const guest = room.guests.get(targetUserId);
        if (guest) targetWs = guest.ws;
    }

    if (targetWs && targetWs.readyState === WebSocket.OPEN) {
        targetWs.send(JSON.stringify({
            type: 'ice-candidate',
            from: client.userId,
            candidate
        }));
    }
}

function broadcastToRoom(roomId, message, excludeWs = null) {
    const room = rooms.get(roomId);
    if (!room) return;

    const messageStr = JSON.stringify(message);

    // Send to host
    if (room.host && room.host.ws !== excludeWs && room.host.ws.readyState === WebSocket.OPEN) {
        room.host.ws.send(messageStr);
    }

    // Send to guests
    room.guests.forEach(guest => {
        if (guest.ws !== excludeWs && guest.ws.readyState === WebSocket.OPEN) {
            guest.ws.send(messageStr);
        }
    });
}

function handleClientDisconnect(ws) {
    handleLeaveRoom(ws);
}

// ============================================
// HTTP API ROUTES
// ============================================

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        activeRooms: rooms.size,
        activeConnections: wss.clients.size
    });
});

// Auth Routes
app.post('/api/auth/signup', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const users = await readData(FILES.USERS);

        if (users[email]) {
            return res.status(400).json({ error: 'Email already registered' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const trialEndsAt = Date.now() + 16 * 60 * 60 * 1000;

        users[email] = {
            id: uuidv4(),
            email,
            password: hashedPassword,
            createdAt: new Date().toISOString(),
            trialEndsAt,
            plan: 'free',
            subscriptionStatus: 'trial'
        };

        await writeData(FILES.USERS, users);

        // Create subscription
        const subscriptions = await readData(FILES.SUBSCRIPTIONS);
        subscriptions[email] = {
            tier: 'free',
            status: 'trial',
            createdAt: new Date().toISOString(),
            expiresAt: new Date(trialEndsAt).toISOString()
        };
        await writeData(FILES.SUBSCRIPTIONS, subscriptions);

        const role = email === 'admin@seraphonix.studio' ? 'admin' : 'user';
        const token = jwt.sign({ id: users[email].id, email, role }, JWT_SECRET, { expiresIn: '7d' });

        res.json({ token, user: { id: users[email].id, email, role } });
    } catch (error) {
        console.error('Signup error:', error);
        res.status(500).json({ error: 'Signup failed' });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password required' });
        }

        const users = await readData(FILES.USERS);
        const user = users[email];

        if (!user) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const role = email === 'admin@seraphonix.studio' ? 'admin' : 'user';
        const token = jwt.sign({ id: user.id, email, role }, JWT_SECRET, { expiresIn: '7d' });

        res.json({ token, user: { id: user.id, email, role } });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Login failed' });
    }
});

app.get('/api/auth/me', authenticateToken, (req, res) => {
    res.json({ user: req.user });
});

// Room Management
app.post('/api/rooms/create', authenticateToken, async (req, res) => {
    try {
        const roomId = uuidv4().slice(0, 8);
        const rooms = await readData(FILES.ROOMS);
        
        rooms[roomId] = {
            id: roomId,
            host: req.user.email,
            createdAt: new Date().toISOString(),
            status: 'active'
        };

        await writeData(FILES.ROOMS, rooms);

        const API_BASE = `http://76.13.242.128:${PORT}`;
        res.json({
            roomId,
            inviteLink: `${API_BASE}/guest.html?room=${roomId}`,
            wsUrl: `ws://76.13.242.128:${PORT}`
        });
    } catch (error) {
        console.error('Create room error:', error);
        res.status(500).json({ error: 'Failed to create room' });
    }
});

app.get('/api/rooms/:roomId', authenticateToken, async (req, res) => {
    try {
        const { roomId } = req.params;
        const roomsData = await readData(FILES.ROOMS);
        const room = roomsData[roomId];

        if (!room) {
            return res.status(404).json({ error: 'Room not found' });
        }

        // Get live room data from in-memory Map
        const liveRoom = rooms.has(roomId) ? rooms.get(roomId) : null;
        
        res.json({
            ...room,
            isLive: !!liveRoom,
            guestCount: liveRoom ? liveRoom.guests.size : 0,
            isStreaming: liveRoom ? liveRoom.isStreaming : false
        });
    } catch (error) {
        console.error('Get room error:', error);
        res.status(500).json({ error: 'Failed to get room' });
    }
});

// Guest Management
app.post('/api/guests/invite', authenticateToken, async (req, res) => {
    try {
        const { roomId, email } = req.body;
        
        if (!roomId || !email) {
            return res.status(400).json({ error: 'Room ID and guest email required' });
        }

        const guests = await readData(FILES.GUESTS);
        
        if (!guests[roomId]) {
            guests[roomId] = [];
        }

        // Check guest limit (2 per month for free tier)
        const now = new Date();
        const monthKey = now.toISOString().slice(0, 7);
        const monthlyInvites = guests[roomId].filter(g => 
            g.inviter === req.user.email && 
            g.invitedAt.startsWith(monthKey)
        ).length;

        if (monthlyInvites >= 2) {
            return res.status(429).json({ error: 'Guest invite limit reached for this month' });
        }

        const invite = {
            id: uuidv4(),
            roomId,
            inviter: req.user.email,
            guestEmail: email,
            invitedAt: new Date().toISOString(),
            status: 'pending'
        };

        guests[roomId].push(invite);
        await writeData(FILES.GUESTS, guests);

        res.json({ success: true, invite });
    } catch (error) {
        console.error('Guest invite error:', error);
        res.status(500).json({ error: 'Failed to invite guest' });
    }
});

// Streaming Endpoints
app.post('/api/stream/start', authenticateToken, async (req, res) => {
    try {
        const { roomId, destinations, settings } = req.body;
        
        const streams = await readData(FILES.STREAMS);
        streams[roomId] = {
            roomId,
            host: req.user.email,
            destinations,
            settings,
            startedAt: new Date().toISOString(),
            status: 'live'
        };

        await writeData(FILES.STREAMS, streams);

        res.json({ success: true, stream: streams[roomId] });
    } catch (error) {
        console.error('Start stream error:', error);
        res.status(500).json({ error: 'Failed to start stream' });
    }
});

app.post('/api/stream/stop', authenticateToken, async (req, res) => {
    try {
        const { roomId } = req.body;
        
        const streams = await readData(FILES.STREAMS);
        if (streams[roomId]) {
            streams[roomId].status = 'ended';
            streams[roomId].endedAt = new Date().toISOString();
            await writeData(FILES.STREAMS, streams);
        }

        res.json({ success: true });
    } catch (error) {
        console.error('Stop stream error:', error);
        res.status(500).json({ error: 'Failed to stop stream' });
    }
});

app.get('/api/stream/:roomId/status', authenticateToken, async (req, res) => {
    try {
        const { roomId } = req.params;
        const streams = await readData(FILES.STREAMS);
        const stream = streams[roomId];

        if (!stream) {
            return res.status(404).json({ error: 'Stream not found' });
        }

        res.json(stream);
    } catch (error) {
        console.error('Get stream status error:', error);
        res.status(500).json({ error: 'Failed to get stream status' });
    }
});

// Chat History
app.get('/api/chat/:roomId', authenticateToken, async (req, res) => {
    try {
        const { roomId } = req.params;
        const chatData = await readData(FILES.CHAT);
        const messages = chatData[roomId] || [];

        res.json({ messages: messages.slice(-100) }); // Last 100 messages
    } catch (error) {
        console.error('Get chat error:', error);
        res.status(500).json({ error: 'Failed to get chat history' });
    }
});

// Settings Management
app.get('/api/settings', authenticateToken, async (req, res) => {
    try {
        const settings = await readData(FILES.SETTINGS);
        const userSettings = settings[req.user.email] || {};
        
        res.json(userSettings);
    } catch (error) {
        console.error('Get settings error:', error);
        res.status(500).json({ error: 'Failed to get settings' });
    }
});

app.post('/api/settings', authenticateToken, async (req, res) => {
    try {
        const settings = await readData(FILES.SETTINGS);
        settings[req.user.email] = {
            ...settings[req.user.email],
            ...req.body,
            updatedAt: new Date().toISOString()
        };
        
        await writeData(FILES.SETTINGS, settings);
        res.json({ success: true, settings: settings[req.user.email] });
    } catch (error) {
        console.error('Save settings error:', error);
        res.status(500).json({ error: 'Failed to save settings' });
    }
});

// Subscription Management
app.get('/api/subscription', authenticateToken, async (req, res) => {
    try {
        const subscriptions = await readData(FILES.SUBSCRIPTIONS);
        const subscription = subscriptions[req.user.email];

        if (!subscription) {
            return res.json({ tier: 'free', status: 'trial' });
        }

        res.json(subscription);
    } catch (error) {
        console.error('Get subscription error:', error);
        res.status(500).json({ error: 'Failed to get subscription' });
    }
});

app.get('/api/plans', (req, res) => {
    const plans = [
        {
            id: 'free',
            name: 'Free Trial',
            price: 0,
            features: ['16 hours streaming', '2 guests/month', '720p quality', 'Basic overlays'],
            limits: { hours: 16, guests: 2, quality: '720p' }
        },
        {
            id: 'ascendant',
            name: 'Ascendant',
            price: 9.99,
            features: ['70 hours streaming', '4 guests', '1080p quality', 'Custom overlays', 'Priority support'],
            limits: { hours: 70, guests: 4, quality: '1080p' }
        },
        {
            id: 'covenant',
            name: 'Covenant',
            price: 29,
            features: ['Unlimited streaming', '8 guests', '1080p60 quality', 'Multi-platform', 'Analytics', 'Priority support'],
            limits: { hours: Infinity, guests: 8, quality: '1080p60' }
        },
        {
            id: 'infinite',
            name: 'Infinite',
            price: 70,
            features: ['Unlimited everything', 'Unlimited guests', '4K quality', 'API access', 'White-label', 'Dedicated support'],
            limits: { hours: Infinity, guests: Infinity, quality: '4K' }
        }
    ];

    res.json(plans);
});

// Recording Management
app.get('/api/recordings', authenticateToken, async (req, res) => {
    try {
        const recordingsDir = path.join(STREAMS_DIR, req.user.email);
        
        if (!fs.existsSync(recordingsDir)) {
            return res.json({ recordings: [] });
        }

        const files = await fs.readdir(recordingsDir);
        const recordings = files
            .filter(f => f.endsWith('.webm'))
            .map(f => ({
                filename: f,
                createdAt: fs.statSync(path.join(recordingsDir, f)).mtime,
                url: `/streams/${req.user.email}/${f}`
            }))
            .sort((a, b) => b.createdAt - a.createdAt);

        res.json({ recordings });
    } catch (error) {
        console.error('Get recordings error:', error);
        res.status(500).json({ error: 'Failed to get recordings' });
    }
});

// Admin Routes
app.get('/api/admin/stats', authenticateToken, async (req, res) => {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Admin access required' });
    }

    try {
        const users = await readData(FILES.USERS);
        const subscriptions = await readData(FILES.SUBSCRIPTIONS);
        const rooms = await readData(FILES.ROOMS);
        const streams = await readData(FILES.STREAMS);

        res.json({
            users: Object.keys(users).length,
            activeSubscriptions: Object.values(subscriptions).filter(s => s.status === 'active').length,
            totalRooms: Object.keys(roomsData).length,
            activeStreams: Object.values(streams).filter(s => s.status === 'live').length,
            liveConnections: wss.clients.size,
            activeLiveRooms: rooms.size,
            uptime: process.uptime()
        });
    } catch (error) {
        console.error('Admin stats error:', error);
        res.status(500).json({ error: 'Failed to get stats' });
    }
});

// Explicit routes for HTML files
app.get('/dashboard.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/dashboard.html'));
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// Serve frontend for all other routes
app.get('*', (req, res) => {
    if (!req.path.startsWith('/api') && !req.path.startsWith('/streams')) {
        res.sendFile(path.join(__dirname, '../frontend/index.html'));
    }
});

// ============================================
// START SERVER
// ============================================

server.listen(PORT, '0.0.0.0', () => {
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║          🎬 SERAPHONIX STUDIO SERVER                   ║');
    console.log('║     Hybrid Streaming Platform - StreamYards + OBS      ║');
    console.log('╠════════════════════════════════════════════════════════╣');
    console.log(`║  HTTP API:     http://76.13.242.128:${PORT}             ║`);
    console.log(`║  WebSocket:    ws://76.13.242.128:${PORT}               ║`);
    console.log(`║  Environment:  ${process.env.NODE_ENV || 'development'}                    ║`);
    console.log('╚════════════════════════════════════════════════════════╝');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});