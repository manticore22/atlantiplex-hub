// Stage display server with basic signaling (socket.io)
// Serves the stage_display.html on a dedicated port (default 9001)
const express = require('express');
const http = require('http');
const path = require('path');
const jwt = require('jsonwebtoken');

const app = express();
const { Issuer } = require('openid-client');
const crypto = require('crypto');
const OIDC_ISSUER = process.env.OIDC_ISSUER;
const OIDC_CLIENT_ID = process.env.OIDC_CLIENT_ID;
const OIDC_CLIENT_SECRET = process.env.OIDC_CLIENT_SECRET;
let oidcClient = null;
const oidcSessions = new Map();
const port = process.env.STAGE_PORT ? parseInt(process.env.STAGE_PORT, 10) : 9001;
const JWT_SECRET = process.env.JWT_SECRET || 'atlantiplex-secret';
// Simple in-memory user store (demo); replace with real auth in production
const USERS = {
  alice: 'password123',
  bob: 'letmein',
};

// Serve static assets from the shared static folder
app.use('/static', express.static(path.join(__dirname, '../static')));
// Serve the frontend app (web/app) for a full UI experience
app.use('/app', express.static(path.join(__dirname, '../app')));

// Lightweight API endpoints for auth (production should use a proper identity provider)
app.use(express.json());
app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: 'Missing credentials' });
  }
  const pass = USERS[username];
  if (!pass || pass !== password) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '1h' });
  return res.json({ token });
});

// Health check for orchestration
app.get('/health', (req, res) => res.json({ ok: true }));

// Serve the stage page from this directory
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'stage_display.html'));
});

// Serve the stage UI for iframe embedding at /stage
app.get('/stage', (req, res) => {
  // Stage UI also loads via stage_display.html; pass through any query parameters (token/room)
  res.sendFile(path.join(__dirname, 'stage_display.html'));
});

// Setup HTTP server and Socket.IO for signaling
const server = http.createServer(app);
let io;
try {
  io = require('socket.io')(server, {
    cors: {
      origin: '*'
    }
  });
} catch (err) {
  // Fallback for older socket.io versions that expect different init
  io = require('socket.io')(server);
}
// OIDC login flow (production-ready scaffold)
async function ensureOidcClient(req) {
  if (oidcClient) return oidcClient;
  if (!OIDC_ISSUER || !OIDC_CLIENT_ID || !OIDC_CLIENT_SECRET) return null;
  const issuer = await Issuer.discover(OIDC_ISSUER);
  oidcClient = new issuer.Client({
    client_id: OIDC_CLIENT_ID,
    client_secret: OIDC_CLIENT_SECRET,
    redirect_uris: [`${req.protocol}://${req.get('host')}/auth/oidc/callback`],
    response_types: ['code'],
  });
  return oidcClient;
}

app.get('/auth/oidc/login', async (req, res) => {
  const client = await ensureOidcClient(req);
  if (!client) return res.status(500).send('OIDC not configured');
  const state = crypto.randomBytes(16).toString('hex');
  const nonce = crypto.randomBytes(16).toString('hex');
  oidcSessions.set(state, { nonce, client });
  const url = client.authorizationUrl({ scope: 'openid profile email', state, nonce });
  res.redirect(url);
});

app.get('/auth/oidc/callback', async (req, res) => {
  const { code, state } = req.query;
  const sess = oidcSessions.get(state);
  if (!sess) return res.status(400).send('Invalid state');
  oidcSessions.delete(state);
  try {
    const { client } = sess;
    const tokens = await client.callback(`${req.protocol}://${req.get('host')}/auth/oidc/callback`, { code, state }, { nonce: sess.nonce });
    const userinfo = await client.userinfo(tokens.access_token);
    const username = userinfo.preferred_username || userinfo.name || userinfo.email || userinfo.sub;
    const token = jwt.sign({ username, oidc: true }, JWT_SECRET, { expiresIn: '1h' });
    res.redirect('/app/index.html?token=' + encodeURIComponent(token));
  } catch (err) {
    console.error(err);
    res.status(500).send('OIDC login failed');
  }
});
// Optional Redis adapter for horizontal scaling
try {
  if (process.env.REDIS_URL) {
    const redisAdapter = require('socket.io-redis');
    io.adapter(redisAdapter(process.env.REDIS_URL));
    console.log('Stage signaling: using Redis adapter at', process.env.REDIS_URL);
  }
} catch (err) {
  console.warn('Stage signaling: Redis adapter not loaded:', err?.message);
}

// In-memory room management for signaling
const rooms = new Map(); // roomName -> Set(socketId)
const socketRooms = new Map(); // socketId -> Set(roomName)

// Stage signaling namespace
const stageIo = io.of('/stage');

stageIo.on('connection', (socket) => {
  // Authenticate via JWT (passed via socket.auth or query)
  const token = (socket.handshake.auth && socket.handshake.auth.token) || (socket.handshake.query && socket.handshake.query.token);
  if (!token) {
    socket.disconnect(true);
    return;
  }
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    socket.user = decoded.username;
  } catch (e) {
    socket.disconnect(true);
    return;
  }
  console.log(`Stage signaling: ${socket.id} connected as ${socket.user}`);

  socket.on('join-stage', ({ room }) => {
    const rm = room || 'default';
    if (!rooms.has(rm)) rooms.set(rm, new Set());
    const members = rooms.get(rm);
    members.add(socket.id);

    // track membership per socket
    if (!socketRooms.has(socket.id)) socketRooms.set(socket.id, new Set());
    socketRooms.get(socket.id).add(rm);
    socket.join(rm);

    // Notify existing peers
    stageIo.to(rm).emit('user-joined', { id: socket.id, count: members.size });
    // Inform the new peer about other peers in the room
    const peers = Array.from(members).filter(id => id !== socket.id);
    socket.emit('peers', { peers });
  });

  socket.on('offer', ({ room, to, offer }) => {
    if (to) stageIo.to(to).emit('offer', { from: socket.id, offer });
  });

  socket.on('answer', ({ room, to, answer }) => {
    if (to) stageIo.to(to).emit('answer', { from: socket.id, answer });
  });

  socket.on('ice-candidate', ({ room, to, candidate }) => {
    if (to) stageIo.to(to).emit('ice-candidate', { from: socket.id, candidate });
  });

  socket.on('disconnecting', () => {
    // remove from all rooms
    if (socketRooms.has(socket.id)) {
      for (const rm of socketRooms.get(socket.id)) {
        const members = rooms.get(rm);
        if (members) {
          members.delete(socket.id);
          stageIo.to(rm).emit('user-left', { id: socket.id, count: members.size });
        }
      }
      socketRooms.delete(socket.id);
    }
  });
  socket.on('disconnect', () => {
    // ensure cleanup in case disconnect happens
    if (socketRooms.has(socket.id)) {
      for (const rm of socketRooms.get(socket.id)) {
        const members = rooms.get(rm);
        if (members) {
          members.delete(socket.id);
          stageIo.to(rm).emit('user-left', { id: socket.id, count: members.size });
        }
      }
      socketRooms.delete(socket.id);
    }
    console.log(`Stage signaling: ${socket.id} disconnected`);
  });
});

server.listen(port, () => {
  console.log(`Stage display server listening on port ${port}`);
}).on('error', (e) => {
  console.error('Failed to start stage server:', e);
});
