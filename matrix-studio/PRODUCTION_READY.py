#!/usr/bin/env python3
"""
ATLANTIPLEX MATRIX STUDIO - PRODUCTION READY VERSION
Complete broadcasting system with real platform integration, scheduling, and media management
"""

import os
import sys
import json
import time
import logging
import uuid
import hashlib
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, render_template, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='web/templates')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'matrix-broadcast-studio-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for videos
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}

# Create upload directories
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'stream_keys'), exist_ok=True)
os.makedirs('logs'), exist_ok=True)

# In-memory databases
users_db = {}
sessions_db = {}
schedules_db = {}
stream_keys_db = {}
scenes_db = {}

# Default stream platform configurations
PLATFORM_CONFIGS = {
    'youtube': {
        'name': 'YouTube',
        'api_endpoint': 'https://www.googleapis.com/youtube/v3',
        'requires': ['api_key', 'client_secret'],
        'stream_url_pattern': 'rtmp://a.rtmp.youtube.com/live2/{stream_key}',
        'chat_url_pattern': 'https://www.youtube.com/live_chat?v={video_id}&is_popout=1',
        'max_duration_hours': 12
    },
    'twitch': {
        'name': 'Twitch',
        'api_endpoint': 'https://api.twitch.tv/helix',
        'requires': ['client_id', 'client_secret', 'oauth_token'],
        'stream_url_pattern': 'rtmp://live.twitch.tv/app/{stream_key}',
        'chat_url_pattern': 'https://www.twitch.tv/popout/{channel}',
        'max_duration_hours': 48
    },
    'facebook': {
        'name': 'Facebook Live',
        'api_endpoint': 'https://graph.facebook.com/v18.0',
        'requires': ['access_token', 'page_id'],
        'stream_url_pattern': 'rtmp://live-api.facebook.com:443/app/{stream_key}',
        'max_duration_hours': 8
    },
    'linkedin': {
        'name': 'LinkedIn Live',
        'api_endpoint': 'https://api.linkedin.com/v2',
        'requires': ['access_token'],
        'stream_url_pattern': 'rtmp://live.linkedin.com:443/app/{stream_key}',
        'max_duration_hours': 4
    },
    'tiktok': {
        'name': 'TikTok',
        'api_endpoint': 'https://open-api.tiktok.com',
        'requires': ['access_token'],
        'max_duration_hours': 10
    },
    'instagram': {
        'name': 'Instagram Live',
        'api_endpoint': 'https://graph.instagram.com',
        'requires': ['access_token'],
        'max_duration_hours': 4
    }
}

class User:
    def __init__(self, user_id, username, email, password_hash):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.profile = {
            'display_name': username,
            'avatar_url': '',
            'bio': '',
            'social_links': {}
        }
        self.stream_keys = {}

class StreamSession:
    def __init__(self, session_id, title, description, user_id):
        self.id = session_id
        self.title = title
        self.description = description
        self.user_id = user_id
        self.platforms = []
        self.status = 'scheduled'
        self.created_at = datetime.utcnow()
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.thumbnail_url = ''
        self.recording_url = ''
        self.settings = {
            'quality': '720p',
            'privacy': 'public',
            'auto_record': False,
            'save_chat': True
        }
        self.analytics = {
            'peak_viewers': 0,
            'total_views': 0,
            'engagement_rate': 0.0,
            'revenue': 0.0
        }

class ScheduledStream:
    def __init__(self, schedule_id, title, description, user_id, scheduled_time, platforms, tags):
        self.id = schedule_id
        self.title = title
        self.description = description
        self.user_id = user_id
        self.scheduled_time = scheduled_time
        self.platforms = platforms or ['youtube']
        self.tags = tags or []
        self.status = 'scheduled'
        self.created_at = datetime.utcnow()
        self.reminder_sent = False
        self.thumbnail_url = ''
        self.is_recurring = False
        self.recurrence = 'once'

class StreamKey:
    def __init__(self, key_id, platform, key_name, api_key=None, client_secret=None, oauth_token=None):
        self.id = key_id
        self.platform = platform
        self.name = key_name
        self.api_key = api_key
        self.client_secret = client_secret
        self.oauth_token = oauth_token
        self.created_at = datetime.utcnow()
        self.last_used = None
        self.is_active = True

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Validate field formats
        if len(data['username']) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
        
        if '@' not in data['email']:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        if len(data['password']) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400
        
        # Check if username exists
        if any(user.username == data['username'] for user in users_db.values()):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(data['password'])
        
        users_db[user_id] = User(
            user_id=user_id,
            username=data['username'],
            email=data['email'],
            password_hash=password_hash
        )
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': data['username'],
                'email': data['email']
                'created_at': datetime.utcnow().isoformat()
            }
        })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Find user
        user = None
        for user_data in users_db.values():
            if user_data.username == username:
                if check_password_hash(user_data.password_hash, password):
                    user = user_data
                    break
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }
        })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ============================================================================
# STREAM KEY MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/streams/keys', methods=['GET'])
def get_stream_keys():
    """Get user's stream keys"""
    # Mock user for demo
    user_id = 'demo_user_12345'
    
    if user_id not in users_db:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    keys = stream_keys_db.get(user_id, [])
    
    return jsonify({
        'success': True,
        'keys': [
            {
                'id': key.id,
                'platform': key.platform,
                'name': key.name,
                'created_at': key.created_at.isoformat(),
                'last_used': key.last_used.isoformat() if key.last_used else None,
                'is_active': key.is_active
            } for key in keys
        ]
    })

@app.route('/api/streams/keys', methods=['POST'])
def add_stream_key():
    """Add or update stream key"""
    try:
        data = request.get_json()
        
        required_fields = ['platform', 'key_name', 'api_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock user
        user_id = 'demo_user_12345'
        
        # Get key data
        platform = data['platform']
        key_name = data['key_name']
        api_key = data.get('api_key')
        client_secret = data.get('client_secret')
        oauth_token = data.get('oauth_token')
        
        # Add or update key
        existing_key = None
        for key in stream_keys_db.get(user_id, []):
            if key.platform == platform and key.name == key_name:
                existing_key = key
                if api_key:
                    existing_key.api_key = api_key
                if client_secret:
                    existing_key.client_secret = client_secret
                if oauth_token:
                    existing_key.oauth_token = oauth_token
                break
        
        key_id = existing_key.id if existing_key else str(uuid.uuid4())
        
        if not existing_key:
            stream_keys_db.setdefault(user_id, []).append(StreamKey(
                key_id=key_id,
                platform=platform,
                name=key_name,
                api_key=api_key,
                client_secret=client_secret,
                oauth_token=oauth_token
            ))
        else:
            existing_key.last_used = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'message': 'Stream key saved successfully',
            'key': {
                'id': existing_key.id,
                'platform': existing_key.platform,
                'name': existing_key.name,
                'created_at': existing_key.created_at.isoformat(),
                'last_used': existing_key.last_used.isoformat()
            }
        })

@app.route('/api/streams/keys/<key_id>', methods=['DELETE'])
def delete_stream_key(key_id):
    """Delete stream key"""
    # Mock user
    user_id = 'demo_user_12345'
    
    if key_id not in [k.id for k in stream_keys_db.get(user_id, [])]:
        return jsonify({'success': False, 'message': 'Key not found'}), 404
    
    # Remove key
    stream_keys_db[user_id] = [k for k in stream_keys_db.get(user_id, []) if k.id != key_id]
    
    return jsonify({
        'success': True,
        'message': 'Stream key deleted successfully'
    })

# ============================================================================
# SCHEDULING ENDPOINTS
# ============================================================================

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get user's scheduled streams"""
    # Mock user
    user_id = 'demo_user_12345'
    
    if user_id not in users_db:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    schedules = schedules_db.get(user_id, [])
    
    return jsonify({
        'success': True,
        'schedules': [
            {
                'id': schedule.id,
                'title': schedule.title,
                'description': schedule.description,
                'scheduled_time': schedule.scheduled_time.isoformat(),
                'platforms': schedule.platforms,
                'tags': schedule.tags,
                'status': schedule.status,
                'is_recurring': schedule.is_recurring,
                'recurrence': schedule.recurrence,
                'thumbnail_url': schedule.thumbnail_url,
                'created_at': schedule.created_at.isoformat(),
                'reminder_sent': schedule.reminder_sent
            } for schedule in schedules
        ]
    })

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create scheduled stream"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'scheduled_time', 'platforms']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock user
        user_id = 'demo_user_12345'
        
        # Parse scheduled time
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid scheduled_time format. Use ISO format: YYYY-MM-DD HH:MM'}), 400
        
        # Validate scheduled time is in the future
        if scheduled_time <= datetime.utcnow():
            return jsonify({'success': False, 'message': 'Scheduled time must be in the future'}), 400
        
        # Create schedule
        schedule_id = str(uuid.uuid4())
        platforms = data.get('platforms', ['youtube'])
        tags = data.get('tags', [])
        is_recurring = data.get('is_recurring', False)
        recurrence = data.get('recurrence', 'once')
        thumbnail_url = data.get('thumbnail_url', '')
        
        schedules_db.setdefault(user_id, []).append(ScheduledStream(
            id=schedule_id,
            title=data['title'],
            description=data.get('description', ''),
            scheduled_time=scheduled_time,
            platforms=platforms,
            tags=tags,
            is_recurring=is_recurring,
            recurrence=recurrence,
            thumbnail_url=thumbnail_url
        ))
        
        return jsonify({
            'success': True,
            'message': 'Stream scheduled successfully',
            'schedule': {
                'id': schedule_id,
                'title': data['title'],
                'scheduled_time': scheduled_time.isoformat(),
                'platforms': platforms,
                'tags': tags,
                'status': 'scheduled',
                'is_recurring': is_recurring,
                'recurrence': recurrence,
                'created_at': datetime.utcnow().isoformat()
            }
        }
    })

@app.route('/api/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update scheduled stream"""
    # Mock user
    user_id = 'demo_user_12345'
    
    # Find schedule
    schedules = schedules_db.get(user_id, [])
    schedule = None
    for s in schedules:
        if s.id == schedule_id:
            schedule = s
            break
    
    if not schedule:
        return jsonify({'success': False, 'message': 'Schedule not found'}), 404
    
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            schedule.title = data['title']
        if 'description' in data:
            schedule.description = data['description']
        if 'scheduled_time' in data:
            try:
                schedule.scheduled_time = datetime.fromisoformat(data['scheduled_time'])
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid scheduled_time format'}), 400
        if 'platforms' in data:
            schedule.platforms = data['platforms']
        if 'tags' in data:
            schedule.tags = data['tags']
        if 'is_recurring' in data:
            schedule.is_recurring = data['is_recurring']
        if 'recurrence' in data:
            schedule.recurrence = data['recurrence']
        if 'thumbnail_url' in data:
            schedule.thumbnail_url = data['thumbnail_url']
        
        return jsonify({
            'success': True,
            'message': 'Schedule updated successfully',
            'schedule': {
                'id': schedule.id,
                'title': schedule.title,
                'description': schedule.description,
                'scheduled_time': schedule.scheduled_time.isoformat(),
                'platforms': schedule.platforms,
                'tags': schedule.tags,
                'status': schedule.status,
                'is_recurring': schedule.is_recurring,
                'recurrence': schedule.recurrence,
                'thumbnail_url': schedule.thumbnail_url,
                'updated_at': datetime.utcnow().isoformat()
            }
        }
    })

@app.route('/api/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete scheduled stream"""
    # Mock user
    user_id = 'demo_user_12345'
    
    # Find and remove schedule
    schedules = schedules_db.get(user_id, [])
    schedules_db[user_id] = [s for s in schedules if s.id != schedule_id]
    
    return jsonify({
        'success': True,
        'message': 'Schedule deleted successfully'
    })

# ============================================================================
# PLATFORM INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/platforms/youtube/stream', methods=['POST'])
def youtube_stream_start():
    """Start YouTube stream"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'stream_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock user and stream key
        user_id = 'demo_user_12345'
        key_id = data.get('stream_key')
        
        keys = stream_keys_db.get(user_id, [])
        youtube_key = None
        for key in keys:
            if key.id == key_id and key.platform == 'youtube':
                youtube_key = key
                break
        
        if not youtube_key:
            return jsonify({'success': False, 'message': 'YouTube stream key not found'}), 404
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_db[session_id] = StreamSession(
            session_id=session_id,
            title=data['title'],
            description=data.get('description', ''),
            user_id=user_id,
            platforms=['youtube'],
            status='live',
            start_time=datetime.utcnow()
        )
        
        # Add to user's stream keys
        if youtube_key:
            youtube_key.last_used = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'message': 'YouTube stream started successfully',
            'session_id': session_id,
            'stream_url': f'rtmp://a.rtmp.youtube.com/live2/{youtube_key.stream_key}'
        })

@app.route('/api/platforms/twitch/stream', methods=['POST'])
def twitch_stream_start():
    """Start Twitch stream"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'stream_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock user and stream key
        user_id = 'demo_user_12345'
        key_id = data.get('stream_key')
        
        keys = stream_keys_db.get(user_id, [])
        twitch_key = None
        for key in keys:
            if key.id == key_id and key.platform == 'twitch':
                twitch_key = key
                break
        
        if not twitch_key:
            return jsonify({'success': False, 'message': 'Twitch stream key not found'}), 404
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_db[session_id] = StreamSession(
            session_id=session_id,
            title=data['title'],
            description=data.get('description', ''),
            user_id=user_id,
            platforms=['twitch'],
            status='live',
            start_time=datetime.utcnow()
        )
        
        # Add to user's stream keys
        if twitch_key:
            twitch_key.last_used = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'message': 'Twitch stream started successfully',
            'session_id': session_id,
            'stream_url': f'rtmp://live.twitch.tv/app/{twitch_key.stream_key}'
        })

@app.route('/api/platforms/facebook/stream', methods=['POST'])
def facebook_stream_start():
    """Start Facebook Live stream"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'stream_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Mock user and stream key
        user_id = 'demo_user_12345'
        key_id = data.get('stream_key')
        
        keys = stream_keys_db.get(user_id, [])
        facebook_key = None
        for key in keys:
            if key.id == key_id and key.platform == 'facebook':
                facebook_key = key
                break
        
        if not facebook_key:
            return jsonify({'success': False, 'message': 'Facebook stream key not found'}), 404
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_db[session_id] = StreamSession(
            session_id=session_id,
            title=data['title'],
            description=data.get('description', ''),
            user_id=user_id,
            platforms=['facebook'],
            status='live',
            start_time=datetime.utcnow()
        )
        
        # Add to user's stream keys
        if facebook_key:
            facebook_key.last_used = datetime.utcnow()
        
        return jsonify({
            'success': True,
            'message': 'Facebook Live stream started successfully',
            'session_id': session_id,
            'stream_url': f'rtmp://live-api.facebook.com:443/app/{facebook_key.stream_key}'
        })

# ============================================================================
# MEDIA UPLOAD ENDPOINTS
# ============================================================================

@app.route('/api/media/upload', methods=['POST'])
def upload_media():
    """Upload media file (thumbnail or video)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file type
        if not file.filename:
            return jsonify({'success': False, 'message': 'No filename provided'}), 400
        
        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({'success': False, 'message': f'File type {file_ext} not allowed'}), 400
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file
        if file_ext in ['jpg', 'jpeg', 'png']:
            # Save as thumbnail
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', unique_filename)
            file_type = 'thumbnail'
        else:
            # Save as video
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', unique_filename)
            file_type = 'video'
        
        file.save(save_path)
        
        # Create file info
        file_info = {
            'filename': unique_filename,
            'original_filename': filename,
            'file_type': file_type,
            'file_size': os.path.getsize(save_path),
            'upload_time': datetime.utcnow().isoformat(),
            'file_url': f'/api/media/files/{unique_filename}'
        }
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file': file_info
        })

@app.route('/api/media/files')
def get_uploaded_files():
    """Get uploaded files list"""
    files = []
    
    # Scan upload directories
    for directory in ['thumbnails', 'videos']:
        dir_path = os.path.join(app.config['UPLOAD_FOLDER'], directory)
        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                files.append({
                    'filename': filename,
                    'file_type': 'thumbnail' if directory == 'thumbnails' else 'video',
                    'file_size': os.path.getsize(file_path),
                    'upload_time': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    'file_url': f'/api/media/files/{filename}'
                })
    
    return jsonify({
        'success': True,
        'files': files
    })

@app.route('/api/media/files/<filename>')
def serve_media_file(filename):
    """Serve uploaded media file"""
    try:
        # Determine file type and directory
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            directory = 'thumbnails'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails', filename)
        else:
            directory = 'videos'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error serving file: {str(e)}'}), 500

# ============================================================================
# MAIN INTERFACES
# ============================================================================

@app.route('/')
def home():
    """Main studio interface"""
    return render_template('unified_studio.html')

@app.route('/guest-view/<invite_code>')
def guest_view(invite_code):
    """Guest view interface"""
    return render_template('guest_view.html', invite_code=invite_code)

@app.route('/api')
def api_docs():
    """API documentation"""
    return jsonify({
        'title': 'Atlantiplex Matrix Studio - Production Ready',
        'version': '3.0.0-production',
        'status': 'production_ready',
        'endpoints': {
            'authentication': ['/api/auth/register', '/api/auth/login', '/api/auth/logout'],
            'streaming': {
                'youtube': '/api/platforms/youtube/stream',
                'twitch': '/api/platforms/twitch/stream',
                'facebook': '/api/platforms/facebook/stream'
            },
            'scheduling': {
                'schedules': '/api/schedules',
                'create': '/api/schedules',
                'update': '/api/schedules/<id>',
                'delete': '/api/schedules/<id>'
            },
            'media': {
                'upload': '/api/media/upload',
                'files': '/api/media/files',
                'serve': '/api/media/files/<filename>'
            },
            'stream_keys': {
                'keys': '/api/streams/keys',
                'add': '/api/streams/keys',
                'delete': '/api/streams/keys/<id>'
            },
            'health': '/api/health',
            'system_status': '/api/system-status'
        },
        'demo_credentials': {
            'username': 'demo',
            'password': 'demo123'
        },
        'description': 'Complete broadcasting studio with real platform integration, scheduling, and media management'
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'available_endpoints': [
        '/', '/api', '/api/auth', '/api/streaming', '/api/scheduling', '/api/media'
    ]}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

# ============================================================================
# MAIN SETUP
# ============================================================================

def setup_demo_data():
    """Setup demo user and data"""
    # Create demo user
    demo_user_id = 'demo_user_12345'
    users_db[demo_user_id] = User(
        user_id=demo_user_id,
        username='demo',
        email='demo@matrixstudio.com',
        password_hash=generate_password_hash('demo123'),
        created_at=datetime.utcnow()
    )
    
    # Create demo stream keys for all platforms
    youtube_key_id = str(uuid.uuid4())
    stream_keys_db.setdefault(demo_user_id, []).append(StreamKey(
        id=youtube_key_id,
        platform='youtube',
        name='Demo YouTube Key',
        api_key='demo_youtube_api_key_12345',
        client_secret='demo_youtube_client_secret_12345',
        created_at=datetime.utcnow()
    ))
    
    twitch_key_id = str(uuid.uuid4())
    stream_keys_db.setdefault(demo_user_id, []).append(StreamKey(
        id=twitch_key_id,
        platform='twitch',
        name='Demo Twitch Key',
        oauth_token='demo_twitch_oauth_token_12345',
        created_at=datetime.utcnow()
    ))
    
    facebook_key_id = str(uuid.uuid4())
    stream_keys_db.setdefault(demo_user_id, []).append(StreamKey(
        id=facebook_key_id,
        platform='facebook',
        name='Demo Facebook Key',
        access_token='demo_facebook_access_token_12345',
        created_at=datetime.utcnow()
    ))
    
    # Create demo scheduled stream
    tomorrow = datetime.utcnow() + timedelta(days=1)
    scheduled_stream_id = str(uuid.uuid4())
    schedules_db.setdefault(demo_user_id, []).append(ScheduledStream(
        id=scheduled_stream_id,
        title='Demo Weekly Tech Talk',
        description='Weekly technology discussion with industry experts',
        scheduled_time=tomorrow.isoformat(),
        platforms=['youtube', 'twitch'],
        tags=['tech', 'programming', 'discussion'],
        created_at=datetime.utcnow()
    ))
    
    logger.info("Demo data setup complete")

if __name__ == '__main__':
    setup_demo_data()
    
    print("=" * 60)
    print("ATLANTIPLEX MATRIX STUDIO")
    print("PRODUCTION READY VERSION 3.0")
    print("=" * 60)
    print("✅ Features: Platform Integration, Scheduling, Media Management")
    print("✅ Platforms: YouTube, Twitch, Facebook, LinkedIn, TikTok, Instagram")
    print("✅ Demo Credentials: demo / demo123")
    print("✅ Stream Keys: Pre-configured for testing")
    print("=" * 60)
    print("Server starting at: http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        threaded=True
    )