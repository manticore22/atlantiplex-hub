#!/usr/bin/env python3
"""
🌊 MATRIX BROADCAST STUDIO - UNIFIED SERVER
Complete unified broadcasting server integrating all functions into a single dynamic interface
Features: Multi-platform streaming, guest management, scene control, real-time monitoring
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import base64
from io import BytesIO

# Import existing components
from broadcast_engine import BroadcastEngine, StreamQuality, VideoCompositor, AudioMixer
from guest_management import GuestManager, StreamGuest, GuestRole, GuestStatus, MediaState
from scene_manager import SceneManager, BroadcastScene, SceneSource
from platform_integrations import MultiPlatformStreamer
from analytics import StreamAnalytics as AnalyticsEngine
from scheduler import StreamScheduler
import obs_integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'matrix-unified-server-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///matrix_unified.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'matrix-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm'}

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # user, admin, moderator
    preferences = db.Column(db.JSON, default={})

class StreamSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='offline')  # offline, live, starting, stopping
    platforms = db.Column(db.JSON, default=[])
    current_scene = db.Column(db.String(100), default='main')
    quality = db.Column(db.String(10), default='720p')
    is_recording = db.Column(db.Boolean, default=False)
    viewer_count = db.Column(db.Integer, default=0)
    max_viewers = db.Column(db.Integer, default=0)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)
    settings = db.Column(db.JSON, default={})

class StreamAnalytics(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('stream_session.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    viewer_count = db.Column(db.Integer, default=0)
    bandwidth_kbps = db.Column(db.Integer, default=0)
    dropped_frames = db.Column(db.Integer, default=0)
    metrics = db.Column(db.JSON, default={})

# Core Systems
class UnifiedBroadcastingSystem:
    """Main unified broadcasting system that coordinates all components"""
    
    def __init__(self):
        self.broadcast_engine = BroadcastEngine()
        self.guest_manager = GuestManager()
        self.scene_manager = SceneManager()
        self.platform_streamer = MultiPlatformStreamer()
        self.analytics_engine = AnalyticsEngine()
        self.scheduler = StreamScheduler()
        self.obs_controller = obs_integration.OBSWebSocketManager()
        
        # System state
        self.start_time = time.time()
        self.current_session_id = None
        self.active_platforms = {}
        self.connected_clients = set()
        self.system_stats = {
            'uptime': 0,
            'total_streams': 0,
            'active_guests': 0,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'network_bandwidth': 0.0
        }
        
        # Background tasks
        self.monitoring_thread = None
        self.stats_thread = None
        self.is_running = False
        
        logger.info("🌊 Unified Broadcasting System initialized")
        
        # Initialize system components
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize all system components"""
        try:
            # Initialize OBS connection
            if self.obs_controller.connect():
                logger.info("✅ OBS connected successfully")
            
            # Initialize broadcast engine
            self.broadcast_engine.initialize_streaming('720p')
            
            # Start background monitoring
            self._start_background_tasks()
            
            logger.info("🚀 All system components initialized")
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        if not self.is_running:
            self.is_running = True
            
            # Monitoring thread for streams
            self.monitoring_thread = threading.Thread(
                target=self._monitor_streams,
                daemon=True
            )
            self.monitoring_thread.start()
            
            # Stats collection thread
            self.stats_thread = threading.Thread(
                target=self._collect_stats,
                daemon=True
            )
            self.stats_thread.start()
            
            logger.info("📊 Background tasks started")
    
    def _monitor_streams(self):
        """Monitor all active streams and handle issues"""
        while self.is_running:
            try:
                # Check broadcast engine status
                if self.current_session_id:
                    status = self.broadcast_engine.get_stream_status()
                    
                    # Update system stats
                    self.system_stats.update({
                        'total_streams': len(status.get('active_platforms', {})),
                        'viewer_count': sum(p.get('viewer_count', 0) for p in status.get('active_platforms', {}).values())
                    })
                    
                    # Emit status to connected clients
                    socketio.emit('stream_status_update', status)
                
                # Check guest connections
                guest_status = [guest.to_dict() for guest in self.guest_manager.get_active_guests()]
                online_guests = len([g for g in guest_status if g['status'] in ['online', 'in_studio', 'on_air']])
                self.system_stats['active_guests'] = online_guests
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Stream monitoring error: {e}")
                time.sleep(5)
    
    def _collect_stats(self):
        """Collect system statistics"""
        while self.is_running:
            try:
                # Calculate uptime
                if hasattr(self, 'start_time'):
                    self.system_stats['uptime'] = int(time.time() - self.start_time)
                
                # Collect performance metrics (simplified)
                import psutil
                self.system_stats.update({
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'network_bandwidth': 0.0  # Would require more detailed monitoring
                })
                
                # Emit stats to dashboard
                socketio.emit('system_stats', self.system_stats)
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Stats collection error: {e}")
                time.sleep(30)
    
    def start_stream_session(self, session_data: Dict) -> Dict:
        """Start a new streaming session"""
        try:
            # Create session in database
            session = StreamSession()
            session.title = session_data['title']
            session.description = session_data.get('description', '')
            session.platforms = session_data.get('platforms', [])
            session.quality = session_data.get('quality', '720p')
            session.user_id = session_data['user_id']
            session.settings = session_data.get('settings', {})
            
            db.session.add(session)
            db.session.flush()
            
            # Update session status
            session.status = 'starting'
            session.started_at = datetime.utcnow()
            self.current_session_id = session.id
            
            # Initialize broadcast with selected quality
            self.broadcast_engine.initialize_streaming(session.quality)
            
            # Start platform streams
            platform_results = {}
            for platform in session.platforms:
                platform_config = session_data.get('platform_configs', {}).get(platform, {})
                result = self.broadcast_engine.start_platform_stream(platform, platform_config)
                platform_results[platform] = result
                
                if result.get('success'):
                    self.active_platforms[platform] = result
            
            # Update session status to live
            session.status = 'live'
            
            # Initialize scene
            self.scene_manager.switch_scene(session_data.get('initial_scene', 'main'))
            
            # Start recording if requested
            if session_data.get('record', False):
                session.is_recording = True
                # self.obs_controller.start_recording()
            
            db.session.commit()
            
            # Emit session start event
            socketio.emit('session_started', {
                'session_id': session.id,
                'title': session.title,
                'platforms': session.platforms,
                'platform_results': platform_results
            })
            
            logger.info(f"🎬 Stream session started: {session.title}")
            
            return {
                'success': True,
                'session_id': session.id,
                'platform_results': platform_results,
                'stream_url': self._generate_stream_url()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start stream session: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    def stop_stream_session(self) -> Dict:
        """Stop the current streaming session"""
        try:
            if not self.current_session_id:
                return {'error': 'No active stream session'}
            
            session = StreamSession.query.get(self.current_session_id)
            if not session:
                return {'error': 'Session not found'}
            
            # Update session status
            session.status = 'stopping'
            
            # Stop all platform streams
            stop_results = self.broadcast_engine.stop_all_streams()
            self.active_platforms.clear()
            
            # Stop recording if active
            if session.is_recording:
                session.is_recording = False
                # self.obs_controller.stop_recording()
            
            # Calculate duration
            if session.started_at:
                session.ended_at = datetime.utcnow()
                session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
            
            session.status = 'offline'
            db.session.commit()
            
            # Emit session stop event
            socketio.emit('session_stopped', {
                'session_id': session.id,
                'duration': session.duration_seconds,
                'final_stats': self.broadcast_engine.get_stream_status()
            })
            
            # Clear current session
            self.current_session_id = None
            
            logger.info(f"🛑 Stream session stopped: {session.title}")
            
            return {
                'success': True,
                'session_id': session.id,
                'duration': session.duration_seconds,
                'stop_results': stop_results
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to stop stream session: {e}")
            return {'error': str(e)}
    
    def _generate_stream_url(self) -> str:
        """Generate a public stream URL"""
        if self.current_session_id:
            return f"https://stream.matrix.studio/{self.current_session_id}"
        return ""
    
    def get_comprehensive_status(self) -> Dict:
        """Get comprehensive system status"""
        try:
            # Get broadcast status
            broadcast_status = self.broadcast_engine.get_stream_status()
            
            # Get guest status
            guest_status = [guest.to_dict() for guest in self.guest_manager.get_active_guests()]
            
            # Get scene status
            scene_status = self.scene_manager.get_active_scene()
            
            # Get current session info
            session_info = None
            if self.current_session_id:
                session = StreamSession.query.get(self.current_session_id)
                if session:
                    session_info = {
                        'id': session.id,
                        'title': session.title,
                        'status': session.status,
                        'platforms': session.platforms,
                        'viewer_count': session.viewer_count,
                        'duration': session.duration_seconds
                    }
            
            return {
                'system': {
                    'status': 'online' if self.is_running else 'offline',
                    'uptime': self.system_stats['uptime'],
                    'stats': self.system_stats
                },
                'broadcast': broadcast_status,
                'guests': {
                    'total': len(guest_status),
                    'online': len([g for g in guest_status if g['status'] in ['online', 'in_studio', 'on_air']]),
                    'details': guest_status
                },
                'scenes': {
                    'current': scene_status.name if scene_status else None,
                    'total_sources': len(scene_status.sources) if scene_status else 0
                },
                'session': session_info
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting comprehensive status: {e}")
            return {'error': str(e)}
    
    def handle_websocket_event(self, event_type: str, data: Dict):
        """Handle WebSocket events from web interface"""
        try:
            if event_type == 'join_studio':
                user_id = data.get('user_id')
                if user_id:
                    join_room(f'studio_{user_id}')
                    logger.info(f"👤 User {user_id} joined studio")
            
            elif event_type == 'switch_scene':
                scene_name = data.get('scene_name')
                if scene_name:
                    self.scene_manager.switch_scene(scene_name)
                    socketio.emit('scene_switched', {'scene': scene_name})
            
            elif event_type == 'update_guest':
                guest_id = data.get('guest_id')
                guest_data = data.get('guest_data', {})
                if guest_id:
                    # Update guest media state if specified
                    result = {'success': True}
                    if 'camera' in guest_data or 'microphone' in guest_data:
                        camera_state = MediaState.ON if guest_data.get('camera', True) else MediaState.OFF
                        mic_state = MediaState.ON if guest_data.get('microphone', True) else MediaState.OFF
                        result = self.guest_manager.set_guest_media_state(guest_id, camera_state, mic_state)
                    socketio.emit('guest_updated', {'guest_id': guest_id, 'result': result})
            
            elif event_type == 'add_platform':
                platform_name = data.get('platform_name')
                platform_config = data.get('config', {})
                if platform_name:
                    result = self.broadcast_engine.start_platform_stream(platform_name, platform_config)
                    socketio.emit('platform_added', {'platform': platform_name, 'result': result})
            
            elif event_type == 'update_quality':
                quality = data.get('quality')
                if quality:
                    result = self.broadcast_engine.update_stream_quality(quality)
                    socketio.emit('quality_updated', {'quality': quality, 'result': result})
            
            else:
                logger.warning(f"⚠️ Unknown WebSocket event type: {event_type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling WebSocket event: {e}")

# Initialize unified system
unified_system = UnifiedBroadcastingSystem()

# API Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/system/status', methods=['GET'])
@jwt_required()
def get_system_status():
    """Get comprehensive system status"""
    return jsonify(unified_system.get_comprehensive_status())

@app.route('/api/session/start', methods=['POST'])
@jwt_required()
def start_session():
    """Start a new streaming session"""
    user_id = get_jwt_identity()
    data = request.get_json()
    data['user_id'] = user_id
    
    result = unified_system.start_stream_session(data)
    return jsonify(result)

@app.route('/api/session/stop', methods=['POST'])
@jwt_required()
def stop_session():
    """Stop the current streaming session"""
    result = unified_system.stop_stream_session()
    return jsonify(result)

# Guest Management API
@app.route('/api/guests', methods=['GET'])
@jwt_required()
def get_guests():
    """Get all guests"""
    guests = [guest.to_dict() for guest in unified_system.guest_manager.get_active_guests()]
    return jsonify({'guests': guests})

@app.route('/api/guests', methods=['POST'])
@jwt_required()
def add_guest():
    """Add a new guest"""
    data = request.get_json()
    # Create guest invite as the proper way to add guests
    result = unified_system.guest_manager.create_guest_invite(
        data.get('name', 'New Guest'),
        data.get('email', 'guest@example.com'),
        GuestRole.GUEST
    )
    return jsonify(result)

# Scene Management API
@app.route('/api/scenes', methods=['GET'])
@jwt_required()
def get_scenes():
    """Get all scenes"""
    scenes = unified_system.scene_manager.get_all_scenes()
    return jsonify({'scenes': [scene.to_dict() for scene in scenes]})

@app.route('/api/scenes/<scene_name>/switch', methods=['POST'])
@jwt_required()
def switch_scene(scene_name):
    """Switch to a specific scene"""
    result = unified_system.scene_manager.switch_scene(scene_name)
    return jsonify({'success': result})

# Platform Management API
@app.route('/api/platforms/add', methods=['POST'])
@jwt_required()
def add_platform():
    """Add a new platform to current stream"""
    data = request.get_json()
    platform_name = data.get('platform_name')
    platform_config = data.get('config', {})
    
    result = unified_system.broadcast_engine.start_platform_stream(platform_name, platform_config)
    return jsonify(result)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {
        'message': 'Connected to Matrix Unified Server',
        'server_time': datetime.utcnow().isoformat()
    })

@socketio.on('join_studio')
def handle_join_studio(data):
    """Handle joining studio room"""
    unified_system.handle_websocket_event('join_studio', data)

@socketio.on('studio_action')
def handle_studio_action(data):
    """Handle studio actions"""
    action_type = data.get('action')
    action_data = data.get('data', {})
    
    unified_system.handle_websocket_event(action_type, action_data)

# Web Interface Routes
@app.route('/')
def index():
    """Main studio interface"""
    return render_template('unified_studio.html')

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')

@app.route('/guest-view/<guest_id>')
def guest_view(guest_id):
    """Guest view interface"""
    return render_template('guest_view.html', guest_id=guest_id)

# Static files and uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Health check
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'system': unified_system.get_comprehensive_status()
    })

# Initialize database
@app.before_request
def ensure_db():
    """Create database tables"""
    db.create_all()

# Main entry point
if __name__ == '__main__':
    logger.info("🌊 Starting Matrix Unified Broadcasting Server")
    logger.info("=" * 60)
    
    # Set start time for uptime calculation
    unified_system.start_time = time.time()
    
    # Start the server
    socketio.run(
        app,
        host='0.0.0.0',
        port=8080,
        debug=False,
        allow_unsafe_werkzeug=True
    )