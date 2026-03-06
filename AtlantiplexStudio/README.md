# Atlantiplex Studio

Professional multi-platform broadcasting studio with guest management, scene control, and real-time streaming capabilities.

## 🎯 STATUS: 100% PRODUCTION READY - v1.1.0

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```

### Option 2: Direct Python Launch
```bash
pip install -r requirements_enhanced.txt
python COMPLETE_WORKING.py
```

## 📱 Access Points

Once launched, access the system at:
- **Studio Interface**: http://localhost:8081
- **API Documentation**: http://localhost:8081/api
- **Health Check**: http://localhost:8081/api/health
- **Guest View**: http://localhost:8081/guest-view/[INVITE_CODE]

## 🔐 Demo Credentials

- **Username**: `demo`
- **Password**: `demo123`

## 📁 Project Structure

```
atlantiplex-studio/
├── web/
│   ├── frontend/          # React + Vite frontend
│   └── stage/             # Node.js WebSocket server
├── config/                # Configuration files
├── core/                  # Core components
├── tests/                 # Test suites
├── .github/               # CI/CD workflows
├── Dockerfile             # Frontend container
├── docker-compose.yml     # Docker orchestration
├── requirements_enhanced.txt    # Python dependencies
└── requirements_payments.txt  # Payment dependencies
```

## ✅ System Status

**Status**: 🟢 PRODUCTION READY - v1.1.0

### Core Features
- ✅ Guest Management (8 concurrent guests)
- ✅ Professional Scene Templates
- ✅ Avatar & Profile Management
- ✅ Multi-Platform Streaming (RTMP, WebRTC)
- ✅ Real-time WebSocket Communication
- ✅ OBS Studio Integration
- ✅ Secure Authentication
- ✅ Analytics & Monitoring
- ✅ Payment Integration (Stripe)

## 🛠️ Tech Stack

### Frontend
- React 18.3.1
- Vite 6.0.7
- Socket.io Client 4.8.1
- Stripe React

### Backend
- Python 3.11+ (Flask 3.1.0)
- Node.js 22 (Express 4.21.2)
- Socket.io 4.8.1

### Infrastructure
- Docker & Docker Compose
- GitHub Actions CI/CD
- Trivy Security Scanning

## 🔧 Requirements

- **Python**: 3.11+ 
- **Node.js**: 22+
- **Operating System**: Windows/Linux/macOS
- **Optional**: OBS Studio, FFmpeg, Docker

## 📦 Dependencies

### Python
```bash
pip install -r requirements_enhanced.txt
pip install -r requirements_payments.txt
```

### Node.js
```bash
cd web/frontend && npm install
cd web/stage && npm install
```

## 🧪 Development

### Running Tests
```bash
# Python tests
cd tests
python test_core_components.py

# Node tests
cd web/frontend && npm test

# Run all with coverage
pytest --cov=. --cov-report=xml
```

### Docker Development
```bash
# Build images
docker build -t atlantiplex/studio:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Guest Management
- `GET /api/guests` - List all guests
- `POST /api/guests` - Add new guest
- `DELETE /api/guests/{id}` - Remove guest

### Scene Management
- `GET /api/scenes` - List all scenes
- `POST /api/scenes/{scene}/switch` - Switch scene

### Streaming
- `POST /api/session/start` - Start streaming session
- `POST /api/session/stop` - Stop streaming session
- `GET /api/stream/status` - Get stream status

## 📞 Support

For issues:
1. Check logs in `logs/` directory
2. Verify Python 3.11+ and Node.js 22+ are installed
3. Run with administrator privileges if needed

## 📄 License

Atlantiplex Studio - Production Ready
Last Updated: February 26, 2026