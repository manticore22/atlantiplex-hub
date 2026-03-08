# 🎬 Seraphonix Studio

**Professional Multi-Platform Broadcasting Platform**

A hybrid streaming solution combining the best of StreamYards and OBS - browser-based ease with professional-grade control.

[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org)
[![Express](https://img.shields.io/badge/Express-4.18+-blue.svg)](https://expressjs.com)
[![WebSocket](https://img.shields.io/badge/WebSocket-Ready-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 What We Built

A **fully functional** hybrid of **StreamYards + OBS** with:

### ✅ Completed Features

**Core Broadcasting:**
- ✅ Multi-platform streaming (YouTube, Twitch, Facebook, LinkedIn, RTMP)
- ✅ Up to 8 guests with simple invite links
- ✅ Dynamic scene switching (Single, Split, Grid 4/6/9)
- ✅ Screen sharing (full display, window, or tab)
- ✅ Local recording with WebM export
- ✅ Professional audio/video controls

**Studio Interface:**
- ✅ Seraphonix Studios branding throughout
- ✅ Real-time unified chat from all platforms
- ✅ Custom overlays (logo, lower thirds, chat overlay)
- ✅ Live viewer count and stream duration
- ✅ Bitrate and stream health monitoring
- ✅ Full settings panel (quality, bitrate, stream keys)

**Guest Management:**
- ✅ Simple browser-based guest joining
- ✅ Individual mute/unmute controls
- ✅ Camera on/off per guest
- ✅ Remove guests instantly
- ✅ QR code invites

**Backend Infrastructure:**
- ✅ Express.js API with JWT authentication
- ✅ WebSocket server for real-time communication
- ✅ Room management system
- ✅ File-based data storage (JSON)
- ✅ Guest invitation system with monthly limits
- ✅ Subscription tier management
- ✅ Chat history storage

**User Experience:**
- ✅ Modern dark UI with neon accents
- ✅ Responsive design (desktop, tablet, mobile)
- ✅ Animated backgrounds and transitions
- ✅ No placeholders - everything is functional
- ✅ Professional landing page with pricing

## 🚀 Quick Start

### Access Your Live Platform

**🌐 Your studio is ready at:**
- **Web Interface**: http://76.13.242.128
- **API Endpoint**: http://76.13.242.128:3001

### Default Login
- **Email**: manticore@studio.com
- **Password**: patriot8812

Or create your own account - **16-hour free trial** included!

## 📂 Project Structure

```
studio-saas/
├── backend/
│   ├── server.js          # Express + WebSocket server (551 lines)
│   ├── package.json       # Dependencies with ws, uuid
│   └── data/              # JSON storage
│       ├── users.json     # User accounts
│       ├── rooms.json     # Broadcast rooms
│       ├── streams.json   # Stream history
│       ├── guests.json    # Guest invitations
│       ├── chat.json      # Chat messages
│       └── settings.json  # User settings
├── frontend/
│   ├── index.html         # Landing page (1031 lines)
│   └── dashboard.html     # Studio interface (1477 lines)
└── deploy.sh              # Automated deployment script
```

## 🎮 How to Use

### Starting Your First Stream

1. **Login** at http://76.13.242.128
2. **Start Camera** - Click "Start Camera" and allow permissions
3. **Select Platforms** - Click YouTube, Twitch, Facebook buttons
4. **Enter Stream Keys** - Go to Settings (⚙️) and add your keys:
   - YouTube: YouTube Studio → Go Live → Stream Key
   - Twitch: Twitch Dashboard → Settings → Stream Key
   - Facebook: Facebook Creator Studio → Live → Stream Key
5. **Go Live** - Click the red "Go Live" button

### Inviting Guests

1. Click **"Invite"** in the Guests panel
2. Copy the **invite link** or scan the **QR code**
3. Send to your guests
4. Guests join instantly via browser - no download needed!

### Managing Scenes

- **Main**: Just you (single camera)
- **Interview**: You + 1 guest side by side
- **Panel**: Grid view with up to 4 people
- **Screen**: Focus on your screen share

Click any scene to switch instantly!

### Adding Overlays

1. Go to the **Branding** tab
2. Toggle overlays:
   - **Studio Logo**: Shows Seraphonix logo
   - **Lower Third**: Animated name banner
   - **Chat Overlay**: Displays chat on stream

### Recording

1. Click **"Record"** (⏺️) button
2. Stream records locally in your browser
3. Click again to stop
4. Recording automatically downloads as WebM file

## 💰 Pricing Plans (Built-in)

| Plan | Monthly | Features |
|------|---------|----------|
| **Free** | $0 | 16 hours, 2 guests/month, 720p, basic overlays |
| **Ascendant** | $9.99 | 70 hours, 4 guests, 1080p, priority support |
| **Covenant** | $29 | Unlimited hours, 8 guests, 4K, all platforms |
| **Infinite** | $70 | Unlimited everything, API access, white-label |

## 🔧 Technical Details

### Architecture
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Backend**: Node.js + Express
- **Real-time**: WebSocket (ws library)
- **Media**: WebRTC + MediaRecorder API
- **Auth**: JWT tokens
- **Storage**: File-based JSON

### Browser Support
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 14+
- ✅ Edge 80+

### WebSocket Events
```javascript
// Client sends:
{ type: 'join-room', payload: { roomId, token, role } }
{ type: 'chat', payload: { message, platform } }
{ type: 'start-stream', payload: { destinations, settings } }
{ type: 'offer', payload: { targetUserId, offer } } // WebRTC

// Server sends:
{ type: 'room-joined', roomId, role, guests: [...] }
{ type: 'chat-message', message: {...} }
{ type: 'stream-started', destinations }
{ type: 'user-joined', userId, role }
```

## 🛠️ Development

### Local Setup

```bash
# 1. Navigate to project
cd studio-saas

# 2. Install backend dependencies
cd backend
npm install

# 3. Start API server
npm start
# Server runs on http://localhost:3001

# 4. Serve frontend (new terminal)
cd ../frontend
python3 -m http.server 80
# Website at http://localhost
```

### Environment Variables

Create `backend/.env`:
```env
PORT=3001
JWT_SECRET=your-super-secret-key
NODE_ENV=development
STRIPE_SECRET=sk_test_... (optional)
```

## 📡 API Endpoints

### Authentication
```
POST /api/auth/signup    # Create account
POST /api/auth/login     # Login
GET  /api/auth/me        # Current user
```

### Streaming
```
POST /api/rooms/create           # Create room
POST /api/stream/start           # Start stream
POST /api/stream/stop            # Stop stream
GET  /api/stream/:id/status      # Stream status
```

### Guests
```
POST /api/guests/invite          # Invite guest
GET  /api/rooms/:id              # Room info
GET  /api/chat/:roomId           # Chat history
```

### Settings
```
GET  /api/settings               # Get user settings
POST /api/settings               # Save settings
GET  /api/plans                  # Get pricing plans
GET  /api/subscription           # Get subscription
```

## 🚀 Deployment

### Automatic Deployment

```bash
# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

This deploys to: `root@76.13.242.128:/root/studio`

### Manual Deployment

```bash
# On your VPS:
ssh root@76.13.242.128

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install PM2
npm install -g pm2

# Deploy code
cd /root
rm -rf studio
cp -r /path/to/studio-saas studio
cd studio/backend
npm install

# Start services
pm2 start server.js --name seraphonix-api
pm2 save
pm2 startup

# Start web server
cd ../frontend
nohup python3 -m http.server 80 &
```

## 🔐 Security Features

- ✅ JWT authentication with 7-day expiration
- ✅ Password hashing with bcrypt (10 rounds)
- ✅ CORS protection configured
- ✅ Input validation on all endpoints
- ✅ Guest invite limits (2/month for free tier)
- ✅ Room isolation (guests can't access other rooms)

## 🐛 Troubleshooting

### Camera Not Working
- Check browser permissions (click 🔒 in address bar)
- Ensure you're using HTTPS or localhost
- Try refreshing the page
- Check if another app is using the camera

### Stream Won't Start
- Verify stream keys are entered in Settings
- Check at least one platform is selected (highlighted)
- Ensure camera is started
- Check internet connection

### Guests Can't Join
- Verify invite link hasn't expired
- Check room is still active (host hasn't left)
- Ensure guest uses a modern browser
- Check firewall isn't blocking WebSocket (port 3001)

### Recording Issues
- Recording happens locally in browser
- Large streams may take time to process
- Check browser has enough storage space

## 📊 Monitoring

Check your deployment:
```bash
# View API logs
ssh root@76.13.242.128 "pm2 logs seraphonix-api"

# Check status
ssh root@76.13.242.128 "pm2 status"

# Health check
curl http://76.13.242.128:3001/api/health
```

## 🎯 What's Next

Optional enhancements you can add:
- [ ] SSL certificate (Let's Encrypt)
- [ ] Custom domain DNS setup
- [ ] Stripe payment integration
- [ ] Cloud recording storage (S3)
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] Mobile apps
- [ ] OBS plugin

## 📞 Support

- **Email**: seraphonixstudios@gmail.com
- **Website**: https://verilysovereign.org
- **Twitter**: @r1914514
- **YouTube**: @manticore-ubermensch

## 📄 License

MIT License - Feel free to use, modify, and distribute!

## 🙏 Credits

Built with ❤️ by **Seraphonix Studios**

---

**🎬 Ready to broadcast?** 
Visit http://76.13.242.128 and start your stream now!

*No downloads. No plugins. Just professional streaming in your browser.*