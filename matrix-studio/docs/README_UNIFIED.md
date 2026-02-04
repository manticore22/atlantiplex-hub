# 🌊 Matrix Unified Broadcasting Server

Complete unified broadcasting platform that integrates all streaming functions into a single, dynamic interface.

## ✨ Features

### 🎬 Core Broadcasting
- **Multi-Platform Streaming**: Stream simultaneously to YouTube, Twitch, Facebook, LinkedIn
- **Professional Quality**: Support for 360p, 480p, 720p, 1080p streaming
- **Real-Time Monitoring**: Track viewer counts, bandwidth, and system performance
- **Automatic Failover**: Resume streaming on connection failures

### 👥 Guest Management
- **6 Guest Slots**: Support for up to 6 simultaneous guests
- **Real-Time Controls**: Mute/unmute, camera controls, hand raising
- **Role-Based Permissions**: Host, moderator, guest, spectator roles
- **WebRTC Integration**: Low-latency peer-to-peer connections

### 🎨 Scene Management
- **Dynamic Scene Switching**: Smooth transitions between scenes
- **Video Composition**: Picture-in-picture, split-screen, overlay modes
- **Custom Layouts**: Create and save custom scene layouts
- **Real-Time Preview**: See scene changes before going live

### 📊 Analytics & Monitoring
- **Live Analytics**: Real-time viewer counts and engagement metrics
- **Performance Monitoring**: CPU, memory, bandwidth usage
- **Stream Recording**: Automatic recording with customizable quality
- **Export Reports**: Detailed analytics in JSON, CSV, PDF formats

### 🔧 Advanced Features
- **OBS Integration**: Full OBS Studio control and automation
- **WebRTC Streaming**: Ultra-low latency streaming
- **API-First**: Comprehensive REST API for all functions
- **WebSocket Events**: Real-time updates and notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for some dependencies)
- OBS Studio (optional but recommended)
- FFmpeg (for transcoding)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/matrix-studio.git
cd matrix-studio
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Initialize database**
```bash
python unified_broadcast_server.py --init-db
```

5. **Start the server**
```bash
python unified_broadcast_server.py
```

### 🌐 Access the Interface

- **Main Studio**: http://localhost:8080
- **Guest View**: http://localhost:8080/guest-view/[guest-id]
- **API Documentation**: http://localhost:8080/api/docs
- **Health Check**: http://localhost:8080/api/health

## 📖 Usage Guide

### Starting Your First Stream

1. **Open the Studio Interface**
   - Navigate to http://localhost:8080
   - Login with your credentials

2. **Configure Your Stream**
   - Enter a stream title
   - Select streaming quality (720p recommended)
   - Choose platforms to stream to
   - Configure stream settings

3. **Add Guests (Optional)**
   - Click "Invite Guest" to add participants
   - Share the guest link with participants
   - Guests join via their web browser

4. **Go Live**
   - Click "GO LIVE" to start streaming
   - Monitor real-time stats and viewer count
   - Switch scenes and manage guests during stream

5. **End Stream**
   - Click "END STREAM" to stop
   - View analytics and download recordings

### Guest Experience

Guests receive a link that opens a web-based interface with:
- Video preview and controls
- Real-time chat with host
- Screen sharing capability
- Audio/video quality settings
- Hand raising for participation

### API Integration

The unified server provides comprehensive REST APIs for:
- Stream control and monitoring
- Guest management
- Scene switching
- Analytics retrieval
- Recording management

Example API call:
```bash
curl -X POST http://localhost:8080/api/session/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Stream",
    "platforms": ["youtube", "twitch"],
    "quality": "720p"
  }'
```

## 🏗️ Architecture

### Core Components

1. **UnifiedBroadcastingSystem**: Main orchestrator
2. **BroadcastEngine**: RTMP streaming and transcoding
3. **GuestManagementSystem**: WebRTC guest connections
4. **SceneManager**: Scene composition and transitions
5. **PlatformStreamer**: Multi-platform API integrations
6. **AnalyticsEngine**: Performance and engagement metrics

### Data Flow

```
User Interface → WebSocket → Unified System → Component Systems
                                            ↓
OBS Studio ← WebRTC ← Media Pipeline ← FFmpeg ← Sources
```

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///matrix_unified.db
JWT_SECRET_KEY=your-jwt-secret

# Streaming Configuration
MAX_STREAM_QUALITY=1080p
DEFAULT_STREAM_QUALITY=720p
MAX_GUESTS=6

# OBS Configuration
OBS_HOST=localhost
OBS_PORT=4444
OBS_PASSWORD=your-obs-password

# Platform Credentials
YOUTUBE_API_KEY=your-youtube-api-key
TWITCH_CLIENT_ID=your-twitch-client-id
FACEBOOK_ACCESS_TOKEN=your-facebook-token
```

### OBS Setup

1. **Install OBS Studio** (version 27+ recommended)
2. **Enable WebSocket** in OBS settings
3. **Set Authentication** with password
4. **Configure Scene Templates** in Matrix interface

### Platform Setup

#### YouTube
- Enable Live Streaming in YouTube Studio
- Generate stream key
- Set up alerts and monetization

#### Twitch
- Get stream key from Twitch Dashboard
- Configure stream settings
- Set up channel points and raids

#### Facebook
- Create Facebook Page
- Enable Live streaming
- Generate stream access token

#### LinkedIn
- Verify account for live streaming
- Set up professional credentials
- Configure stream privacy settings

## 📊 Monitoring & Analytics

### Real-Time Metrics
- Viewer count per platform
- Bandwidth usage
- CPU and memory utilization
- Connection quality indicators
- Guest connection status

### Historical Analytics
- Stream duration and reach
- Peak viewer times
- Engagement patterns
- Revenue tracking
- Performance optimization suggestions

### Alerts & Notifications
- Stream failure alerts
- High resource usage warnings
- Guest connection issues
- Platform-specific notifications

## 🔒 Security

### Authentication
- JWT-based user authentication
- Role-based access control
- Guest invitation codes
- API rate limiting

### Data Protection
- Encrypted WebRTC connections
- Secure API endpoints
- Privacy compliance
- Data retention policies

## 🐛 Troubleshooting

### Common Issues

**Stream Won't Start**
1. Check OBS connection status
2. Verify platform credentials
3. Ensure proper RTMP URLs
4. Check network connectivity

**Guest Can't Connect**
1. Verify guest invitation code
2. Check browser WebRTC support
3. Ensure proper camera/mic permissions
4. Test firewall settings

**Poor Quality**
1. Adjust stream quality settings
2. Check internet bandwidth
3. Optimize encoder settings
4. Verify system resources

### Debug Mode

Enable debug logging:
```bash
DEBUG=1 python unified_broadcast_server.py
```

Check logs:
```bash
tail -f logs/unified_server.log
```

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Create virtual environment
3. Install development dependencies
4. Run tests and linting

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add comprehensive tests
- Document API endpoints

## 📝 API Documentation

### Authentication
```bash
POST /api/auth/login
{
  "username": "your_username",
  "password": "your_password"
}
```

### Stream Control
```bash
POST /api/session/start
{
  "title": "Stream Title",
  "platforms": ["youtube", "twitch"],
  "quality": "720p"
}

POST /api/session/stop
```

### Guest Management
```bash
GET /api/guests
POST /api/guests
PUT /api/guests/{guest_id}
DELETE /api/guests/{guest_id}
```

### Scene Management
```bash
GET /api/scenes
POST /api/scenes
PUT /api/scenes/{scene_id}
POST /api/scenes/transition
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full API Docs](/docs/api.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/matrix-studio/issues)
- **Discord**: [Community Server](https://discord.gg/matrix-studio)
- **Email**: support@matrix.studio

## 🗺️ Roadmap

### v2.1 (Coming Soon)
- [ ] Mobile guest interface
- [ ] Advanced audio processing
- [ ] Custom branding options
- [ ] Cloud deployment support

### v2.2 (Future)
- [ ] AI-powered scene detection
- [ ] Advanced analytics dashboard
- [ ] Multi-host support
- [ ] Plugin system

---

**Built with ❤️ by the Matrix Studio Team**