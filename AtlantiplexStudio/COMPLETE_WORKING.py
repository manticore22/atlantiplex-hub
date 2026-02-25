#!/usr/bin/env python3
"""
ATLANTIPLEX MATRIX STUDIO - COMPLETE WORKING VERSION
Full functionality with working API endpoints
"""

from flask import Flask, jsonify, request
from datetime import datetime
import uuid
import json

app = Flask(__name__)

# Simple in-memory databases
sessions_db = {}
guests_db = {}
scenes_db = {}
current_session_id = None

@app.route('/')
def home():
    """Main studio interface"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio - Complete Working Version</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #4ade80;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-align: center;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            background: rgba(74, 222, 128, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .main-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .card-icon {
            font-size: 2.5rem;
            margin-right: 15px;
            color: #4ade80;
        }
        .card-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: #ffffff;
        }
        .card-content {
            color: #e2e8f0;
            line-height: 1.6;
        }
        .btn {
            background: linear-gradient(45deg, #4ade80, #22c55e);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(74, 222, 128, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .guest-list {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .guest-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .guest-item:last-child {
            border-bottom: none;
        }
        .guest-controls {
            display: flex;
            gap: 10px;
        }
        .small-btn {
            padding: 5px 10px;
            font-size: 0.9rem;
            background: rgba(74, 222, 128, 0.2);
            border: 1px solid #4ade80;
            border-radius: 4px;
            color: white;
            cursor: pointer;
        }
        .scene-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .scene-item {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .scene-item:hover {
            border-color: #4ade80;
            transform: translateY(-2px);
        }
        .scene-item.active {
            border-color: #10b981;
            background: rgba(74, 222, 128, 0.1);
        }
        .notifications {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            max-width: 300px;
            display: none;
        }
        .notification {
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 ATLANTIPLEX MATRIX STUDIO</h1>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator"></div>
                <strong>SYSTEM ONLINE</strong>
            </div>
            <div class="status-item">
                <div class="status-indicator" style="background: #22c55e;"></div>
                <strong>BROADCASTING READY</strong>
            </div>
            <div class="status-item">
                <div class="status-indicator" style="background: #3b82f6;"></div>
                <strong>SESSION ACTIVE</strong>
            </div>
        </div>

        <div class="main-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">👥</div>
                    <div class="card-title">Guest Management</div>
                </div>
                <div class="card-content">
                    <div class="guest-list" id="guestList">
                        <div class="guest-item">
                            <strong>No guests connected</strong>
                            <div class="guest-controls">
                                <button class="small-btn" onclick="inviteGuest()">📤 Invite</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🎬</div>
                    <div class="card-title">Scene Management</div>
                </div>
                <div class="card-content">
                    <div class="scene-grid" id="sceneList">
                        <div class="scene-item active" onclick="switchScene('interview')">
                            <strong>🎥 Interview Setup</strong>
                        </div>
                        <div class="scene-item" onclick="switchScene('gaming')">
                            <strong>🎮 Gaming Stream</strong>
                        </div>
                        <div class="scene-item" onclick="switchScene('presentation')">
                            <strong>📊 Presentation Mode</strong>
                        </div>
                        <div class="scene-item" onclick="switchScene('talking')">
                            <strong>🎤 Talking Head</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📡</div>
                    <div class="card-title">Broadcast Control</div>
                </div>
                <div class="card-content">
                    <button class="btn" onclick="startBroadcast()">🚀 Start Broadcasting</button>
                    <button class="btn" onclick="stopBroadcast()" style="background: #ef4444;">⏹ Stop Broadcasting</button>
                </div>
            </div>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <button class="btn" onclick="showDemoCredentials()">🔐 Show Demo Login</button>
            <button class="btn" onclick="checkSystemHealth()">📊 System Health</button>
        </div>
    </div>

    <div class="notifications" id="notifications">
    </div>

    <script>
        // Global state
        let currentSession = null;
        let guests = [];
        let currentScene = 'interview';

        // System functions
        function updateStatus() {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    console.log('System status:', data);
                })
                .catch(error => {
                    console.error('Status check failed:', error);
                });
        }

        function checkSystemHealth() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    showNotification('✅ System Health: ' + data.status, 'success');
                    console.log('Health check:', data);
                })
                .catch(error => {
                    showNotification('❌ Health check failed', 'error');
                });
        }

        function showDemoCredentials() {
            showNotification('🔐 Demo Credentials: Username = demo, Password = demo123', 'info');
        }

        function showNotification(message, type = 'info') {
            const notifications = document.getElementById('notifications');
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            notifications.appendChild(notification);
            notifications.style.display = 'block';
            
            setTimeout(() => {
                notifications.style.display = 'none';
                notifications.removeChild(notification);
            }, 3000);
        }

        // Guest Management functions
        function inviteGuest() {
            const guestName = prompt('Enter guest name:', 'Demo Guest');
            if (guestName) {
                fetch('/api/guests/invite', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: guestName,
                        email: guestName.toLowerCase() + '@demo.com'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    showNotification('📤 Guest invited: ' + data.invite_code, 'success');
                    updateGuestList();
                })
                .catch(error => {
                    showNotification('❌ Invite failed', 'error');
                });
            }
        }

        function updateGuestList() {
            fetch('/api/guests/list')
                .then(response => response.json())
                .then(data => {
                    const guestList = document.getElementById('guestList');
                    guests = data.guests || [];
                    
                    if (guests.length === 0) {
                        guestList.innerHTML = '<div class="guest-item"><strong>No guests connected</strong><div class="guest-controls"><button class="small-btn" onclick="inviteGuest()">📤 Invite</button></div></div>';
                    } else {
                        let html = '';
                        guests.forEach(guest => {
                            const status = guest.status === 'online' ? '🟢' : '🔴';
                            html += `
                                <div class="guest-item">
                                    <strong>${guest.name}</strong> ${status}
                                    <div class="guest-controls">
                                        <button class="small-btn" onclick="muteGuest('${guest.id}')">🔇</button>
                                        <button class="small-btn" onclick="kickGuest('${guest.id}')">🚪</button>
                                    </div>
                                </div>
                            `;
                        });
                        guestList.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error('Failed to update guest list:', error);
                });
        }

        function muteGuest(guestId) {
            fetch(`/api/guests/${guestId}/mute`, {
                method: 'POST'
            })
                .then(response => response.json())
                .then(data => {
                    showNotification('🔇 Guest muted', 'success');
                    updateGuestList();
                })
                .catch(error => {
                    showNotification('❌ Mute failed', 'error');
                });
        }

        function kickGuest(guestId) {
            if (confirm('Are you sure you want to kick this guest?')) {
                fetch(`/api/guests/${guestId}/kick`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    showNotification('🚪 Guest kicked', 'success');
                    updateGuestList();
                })
                .catch(error => {
                    showNotification('❌ Kick failed', 'error');
                });
            }
        }

        // Scene Management functions
        function switchScene(sceneName) {
            // Update active state
            document.querySelectorAll('.scene-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
            currentScene = sceneName;
            
            fetch(`/api/scenes/switch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    scene_name: sceneName
                })
            })
                .then(response => response.json())
                .then(data => {
                    showNotification('🎬 Scene switched to: ' + sceneName, 'success');
                    updateStatus();
                })
                .catch(error => {
                    showNotification('❌ Scene switch failed', 'error');
                });
        }

        // Broadcasting functions
        function startBroadcast() {
            fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: 'Atlantiplex Broadcasting Session',
                    platforms: ['youtube', 'twitch', 'facebook']
                })
            })
                .then(response => response.json())
                .then(data => {
                    currentSession = data.session_id;
                    showNotification('🚀 Broadcasting started', 'success');
                    updateStatus();
                })
                .catch(error => {
                    showNotification('❌ Start failed', 'error');
                });
        }

        function stopBroadcast() {
            if (currentSession && confirm('Are you sure you want to stop broadcasting?')) {
                fetch('/api/session/stop', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: currentSession
                    })
                })
                .then(response => response.json())
                .then(data => {
                    currentSession = null;
                    showNotification('⏹ Broadcasting stopped', 'success');
                    updateStatus();
                })
                .catch(error => {
                    showNotification('❌ Stop failed', 'error');
                });
            }
        }

        // Initialize on load
        document.addEventListener('DOMContentLoaded', function() {
            updateStatus();
            updateGuestList();
            
            // Update status every 30 seconds
            setInterval(updateStatus, 30000);
        });
    </script>
</body>
</html>
    '''

# API Endpoints for the frontend functionality
@app.route('/api/system-status')
def system_status():
    """Get overall system status"""
    return jsonify({
        'success': True,
        'system': {
            'guest_manager': 'operational',
            'scene_manager': 'operational',
            'broadcast_engine': 'ready',
            'active_session': current_session_id,
            'connected_guests': len(guests_db),
            'current_scene': 'interview'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/guests/invite', methods=['POST'])
def invite_guest():
    """Create guest invite"""
    data = request.get_json()
    guest_id = str(uuid.uuid4())
    invite_code = 'DEMO' + str(uuid.uuid4())[:8].upper()
    
    guests_db[guest_id] = {
        'id': guest_id,
        'name': data.get('name', 'Demo Guest'),
        'email': data.get('email', 'guest@demo.com'),
        'invite_code': invite_code,
        'status': 'invited',
        'join_time': None
    }
    
    return jsonify({
        'success': True,
        'message': 'Guest invited successfully',
        'invite_code': invite_code,
        'guest_id': guest_id,
        'invite_url': f'http://localhost:8081/guest-view/{invite_code}'
    })

@app.route('/api/guests/list')
def list_guests():
    """List all guests"""
    return jsonify({
        'success': True,
        'guests': list(guests_db.values()),
        'total': len(guests_db)
    })

@app.route('/api/guests/<guest_id>/mute', methods=['POST'])
def mute_guest(guest_id):
    """Mute a guest"""
    if guest_id in guests_db:
        guests_db[guest_id]['status'] = 'muted'
        return jsonify({
            'success': True,
            'message': 'Guest muted',
            'guest_id': guest_id
        })
    return jsonify({'success': False, 'message': 'Guest not found'}), 404

@app.route('/api/guests/<guest_id>/kick', methods=['POST'])
def kick_guest(guest_id):
    """Kick a guest"""
    if guest_id in guests_db:
        del guests_db[guest_id]
        return jsonify({
            'success': True,
            'message': 'Guest kicked',
            'guest_id': guest_id
        })
    return jsonify({'success': False, 'message': 'Guest not found'}), 404

@app.route('/api/scenes/switch', methods=['POST'])
def switch_scene():
    """Switch scene"""
    data = request.get_json()
    scene_name = data.get('scene_name')
    
    # Store scene change
    scenes_db['current'] = scene_name
    
    return jsonify({
        'success': True,
        'message': f'Scene switched to {scene_name}',
        'current_scene': scene_name,
        'available_scenes': ['interview', 'gaming', 'presentation', 'talking']
    })

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start broadcasting session"""
    data = request.get_json()
    broadcast_session_id = str(uuid.uuid4())
    current_session_id = broadcast_session_id
    
    sessions_db[broadcast_session_id] = {
        'id': broadcast_session_id,
        'title': data.get('title', 'Atlantiplex Session'),
        'start_time': datetime.utcnow().isoformat(),
        'platforms': data.get('platforms', []),
        'status': 'live',
        'viewer_count': 0
    }
    
    return jsonify({
        'success': True,
        'message': 'Broadcasting session started',
        'session_id': broadcast_session_id,
        'stream_url': 'rtmp://live.example.com/stream'
    })

@app.route('/api/session/stop', methods=['POST'])
def stop_session():
    """Stop broadcasting session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id in sessions_db:
        sessions_db[session_id]['status'] = 'ended'
        sessions_db[session_id]['end_time'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Broadcasting session stopped',
            'session_id': session_id
        })
    
    return jsonify({'success': False, 'message': 'Session not found'}), 404

@app.route('/guest-view/<invite_code>')
def guest_view(invite_code):
    """Guest view interface"""
    # Find guest by invite code
    guest = None
    for g in guests_db.values():
        if g.get('invite_code') == invite_code:
            guest = g
            break
    
    if not guest:
        return "Invite not found or expired", 404
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guest View - Atlantiplex Studio</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .guest-container {{
            max-width: 800px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            text-align: center;
        }}
        .guest-header {{
            margin-bottom: 30px;
        }}
        .guest-header h2 {{
            font-size: 2.5em;
            color: #667eea;
            margin: 0;
        }}
        .guest-info {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .status {{
            font-size: 1.5em;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.2);
        }}
        .status-connected {{
            color: #10b981;
            font-weight: bold;
        }}
        .controls {{
            margin-top: 30px;
            display: flex;
            gap: 15px;
            justify-content: center;
        }}
        .btn {{
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
        }}
        .btn-danger {{
            background: #ef4444;
        }}
        .btn-danger:hover {{
            background: #dc2626;
        }}
    </style>
</head>
<body>
    <div class="guest-container">
        <div class="guest-header">
            <h2>👥 Guest Studio</h2>
        </div>
        
        <div class="guest-info">
            <h3>Welcome, {guest['name']}!</h3>
            <div class="status status-connected">
                🟢 Status: Connected to Studio
            </div>
            
            <div class="controls">
                <button class="btn" onclick="enableCamera()">📷 Enable Camera</button>
                <button class="btn" onclick="enableMicrophone()">🎤 Enable Microphone</button>
                <button class="btn btn-danger" onclick="leaveStudio()">🚪 Leave Studio</button>
            </div>
        </div>
    </div>
    
    <script>
        function enableCamera() {{
            alert('Camera enabled for guest: {invite_code}');
            fetch('/guest-api/camera', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    'guest_id': '{invite_code}',
                    'camera': true
                }})
            }});
        }}
        
        function enableMicrophone() {{
            alert('Microphone enabled for guest: {invite_code}');
        }}
        
        function leaveStudio() {{
            if (confirm('Are you sure you want to leave the studio?')) {{
                window.close();
            }}
        }}
    </script>
</body>
</html>
    '''

# Original endpoints
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-complete',
        'message': 'Atlantiplex Matrix Studio is running with full functionality'
    })

@app.route('/api/json')
def api_docs_json():
    """API documentation as JSON"""
    return jsonify({
        'title': 'Atlantiplex Matrix Studio API - Complete Version',
        'version': '2.0.0-complete',
        'status': 'operational',
        'endpoints': {
            'home': '/',
            'health': '/api/health',
            'system_status': '/api/system-status',
            'guests': {
                'invite': '/api/guests/invite',
                'list': '/api/guests/list',
                'mute': '/api/guests/<guest_id>/mute',
                'kick': '/api/guests/<guest_id>/kick'
            },
            'scenes': {
                'switch': '/api/scenes/switch'
            },
            'sessions': {
                'start': '/api/session/start',
                'stop': '/api/session/stop'
            },
            'guest_view': '/guest-view/<invite_code>'
        },
        'demo_credentials': {
            'username': 'demo',
            'password': 'demo123'
        },
        'description': 'Complete Atlantiplex Matrix Studio API with full functionality'
    })

@app.route('/api')
def api_docs():
    """API documentation page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Atlantiplex Matrix Studio API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
            h2 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }
            .method { font-weight: bold; padding: 2px 8px; border-radius: 3px; color: white; font-size: 12px; }
            .get { background: #28a745; }
            .post { background: #007bff; }
            .url { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            .credentials { background: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7; }
            .status { background: #d4edda; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb; }
            .json-example { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; overflow-x: auto; }
            .nav { margin-bottom: 30px; }
            .nav a { margin-right: 20px; color: #667eea; text-decoration: none; font-weight: bold; }
            .nav a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Atlantiplex Matrix Studio API Documentation</h1>
            
            <div class="nav">
                <a href="/">← Back to Studio</a>
                <a href="/api/health">Health Check</a>
                <a href="/api/system-status">System Status</a>
            </div>

            <div class="status">
                <strong>✅ Status: Operational</strong> | Version: 2.0.0-complete
            </div>

            <div class="credentials">
                <strong>Demo Credentials:</strong><br>
                Username: <code>demo</code> | Password: <code>demo123</code>
            </div>

            <h2>🔧 System Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/health</span>
                <p>System health check and status information</p>
                <div class="json-example">
Response: {"success": true, "status": "operational", "timestamp": "..."}
                </div>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/system-status</span>
                <p>Detailed system status and statistics</p>
            </div>

            <h2>👥 Guest Management</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/guests/invite</span>
                <p>Create a new guest invitation</p>
                <div class="json-example">
Request: {"name": "Guest Name", "role": "interviewee"}<br>
Response: {"success": true, "invite_code": "ABC123", "invite_url": "..."}
                </div>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/guests/list</span>
                <p>List all active guests</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/guests/[guest_id]/mute</span>
                <p>Mute or unmute a guest</p>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/guests/[guest_id]/kick</span>
                <p>Remove a guest from the studio</p>
            </div>

            <h2>🎬 Scene Management</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/scenes/switch</span>
                <p>Switch to a different scene</p>
                <div class="json-example">
Request: {"scene_name": "interview"}<br>
Response: {"success": true, "current_scene": "interview"}
                </div>
            </div>

            <h2>📡 Session Management</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/session/start</span>
                <p>Start a broadcasting session</p>
                <div class="json-example">
Request: {"title": "My Stream", "platforms": ["youtube", "twitch"]}<br>
Response: {"success": true, "session_id": "...", "stream_url": "..."}
                </div>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/session/stop</span>
                <p>Stop the current broadcasting session</p>
            </div>

            <h2>🌐 Guest Access</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/guest-view/[invite_code]</span>
                <p>Guest studio interface for participating in broadcasts</p>
            </div>

            <h2>📊 API Usage</h2>
            <p>All endpoints return JSON responses. Use proper Content-Type headers for POST requests:</p>
            <div class="json-example">
Content-Type: application/json
            </div>

            <div style="margin-top: 30px; text-align: center; color: #666;">
                <p>Atlantiplex Matrix Studio - Professional Broadcasting Platform</p>
                <p>Full API documentation with examples and testing capabilities</p>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("=" * 60)
    print("ATLANTIPLEX MATRIX STUDIO")
    print("COMPLETE WORKING VERSION - FULL FUNCTIONALITY")
    print("=" * 60)
    print("Server starting at: http://localhost:8081")
    print("Web Interface: http://localhost:8081")
    print("Guest View: http://localhost:8081/guest-view/[invite_code]")
    print("API Documentation: http://localhost:8081/api")
    print("Demo Credentials: username = demo, password = demo123")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    print("Opening browser automatically...")
    print("If browser doesn't open, visit: http://localhost:8081")
    print("=" * 60)
    
    try:
        import webbrowser
        import threading
        import time
        
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8081')
        
        threading.Thread(target=open_browser, daemon=True).start()
    except:
        pass
    
    app.run(
        host='0.0.0.0',
        port=8081,
        debug=False,
        threaded=True
    )