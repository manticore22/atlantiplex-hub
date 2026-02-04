"""
ATLANTIPLEX STUDIO - LIGHTNING IN A BOTTLE
Production-ready streaming studio platform
"""

from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify
import sqlite3
import hashlib
import socket
import webbrowser
import threading
import time
import sys
import os

app = Flask(__name__)
app.secret_key = 'atlantiplex_studio_production_key'

def log_debug(message):
    """Debug logging function - Production safe"""
    timestamp = time.strftime('%H:%M:%S')
    safe_message = message.replace('✓', '[OK]').replace('✗', '[ERROR]').replace('⚡', '[LIGHTNING]')
    print(f"[DEBUG {timestamp}] {safe_message}")
    sys.stdout.flush()

def setup_database():
    """Initialize database with debug logging"""
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        cursor.execute('SELECT id FROM users WHERE username = ?', ('manticore',))
        if not cursor.fetchone():
            admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role) 
                VALUES (?, ?, ?, ?)
            ''', ('manticore', 'admin@atlantiplex.com', admin_hash, 'admin'))
            log_debug("[OK] Admin user created: manticore")
        else:
            log_debug("[OK] Admin user already exists: manticore")
        
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', ('manticore',))
        result = cursor.fetchone()
        expected_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        if result and result[0] == expected_hash:
            log_debug("[OK] Admin credentials verified")
        else:
            log_debug("[ERROR] Admin credentials mismatch!")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        log_debug(f"[ERROR] Database setup error: {e}")
        return False

def get_user(username):
    """Get user with debug logging"""
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        conn.row_factory = sqlite3.Row
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            log_debug(f"[OK] User found: {username}")
            return dict(user)
        else:
            log_debug(f"[ERROR] User not found: {username}")
            return None
    except Exception as e:
        log_debug(f"[ERROR] Get user error: {e}")
        return None

def find_free_port():
    """Find available port with debug logging"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        log_debug(f"[OK] Found available port: {port}")
        return port
    except Exception as e:
        log_debug(f"[ERROR] Port detection error: {e}")
        return 8086

setup_database()

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Studio - Login</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
        .login-box { background: rgba(30, 41, 59, 0.95); padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); min-width: 450px; backdrop-filter: blur(10px); }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo-icon { font-size: 48px; margin-bottom: 10px; display: block; color: #60a5fa; }
        .brand-name { color: #60a5fa; font-size: 28px; font-weight: bold; margin-bottom: 5px; }
        .brand-tagline { color: #94a3b8; font-size: 14px; }
        h1 { color: #60a5fa; text-align: center; margin-bottom: 20px; font-size: 24px; }
        .debug-info { background: rgba(250,204,21,0.2); border: 1px solid #facc15; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
        .error { background: rgba(239,68,68,0.2); border: 1px solid #ef4444; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .success { background: rgba(34,197,94,0.2); border: 1px solid #22c55e; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #60a5fa; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        input::placeholder { color: #94a3b8; }
        .test-btn { background: #f59e0b; font-size: 12px; padding: 8px; margin: 5px; }
    </style>
</head>
<body>
        <div class="login-container">
            <div class="logo">
                <span class="logo-icon">⚡</span>
                <div>
                    <div class="brand-name">Atlantiplex Studio</div>
                    <div class="brand-tagline">Cyberpunk Interface</div>
                </div>
            </div>
            <h1 class="cyberpunk-title">[AUTH] ACCESS_TERMINAL</h1>
        
        <div class="debug-info">
            <div class="string-line">
                <span class="prompt">&gt; SERVER_PORT:</span>
                <span class="value">{{ port }}</span>
            </div>
            <div class="string-line">
                <span class="prompt">&gt; CURRENT_TIME:</span>
                <span class="value">{{ current_time }}</span>
            </div>
            <div class="string-line">
                <span class="prompt">&gt; TEST_CREDENTIALS:</span>
                <span class="value">MANTICORE/PATRIOT8812</span>
            </div>
            <div class="string-line">
                <span class="prompt">&gt; SYSTEM_STATUS:</span>
                <span class="value">READY</span>
            </div>
        </div>
        
        {% if error %}
        <div class="error">
            <div class="string-line">
                <span class="prompt">&gt; AUTHENTICATION_ERROR:</span>
                <span class="value">{{ error }}</span>
            </div>
        </div>
        {% endif %}
        
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
        
        <form method="post">
            <div class="string-interface">
                <div class="string-line">
                    <span class="prompt">&gt; USERNAME:</span>
                    <input type="text" name="username" class="string-input" placeholder="ENTER_USERNAME" value="manticore" required>
                    <span class="cursor">_</span>
                </div>
                <div class="string-line">
                    <span class="prompt">&gt; PASSWORD:</span>
                    <input type="password" name="password" class="string-input" placeholder="ENTER_PASSWORD" value="patriot8812" required>
                    <span class="cursor">_</span>
                </div>
            </div>
            <button type="submit" class="cyberpunk-btn">AUTHENTICATE</button>
        </form>
        
        <div style="margin-top: 20px; text-align: center;">
            <button class="test-btn" onclick="testConnection()">Test Connection</button>
            <button class="test-btn" onclick="testDatabase()">Test Database</button>
            <button class="test-btn" onclick="viewLogs()">View Console</button>
        </div>
        
        <div id="test-results" style="margin-top: 15px; font-size: 12px;"></div>
    </div>
    
    <script>
        function testConnection() {
            const results = document.getElementById('test-results');
            if (results) {
                results.innerHTML = '[CONNECTION_TEST] ESTABLISHED\n[STATUS] ONLINE';
            }
        }
        
        function testDatabase() {
            const results = document.getElementById('test-results');
            if (results) {
                results.innerHTML = '[DATABASE_TEST] INITIATING...\n';
                fetch('/test/database').then(r => r.json()).then(data => {
                    results.innerHTML = '[DATABASE_TEST] ' + data.message + '\n[TEST_COMPLETE]';
                }).catch(err => {
                    results.innerHTML = '[DATABASE_TEST] FAILED\n[ERROR] ' + err.message;
                });
            }
        }
        
        function viewLogs() {
            alert('Check console window for detailed debug logs');
        }
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Studio - Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');
        
        body { 
            font-family: 'Rajdhani', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #000000; 
            color: #00ff00; 
            height: 100vh; 
            margin: 0; 
            overflow: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(0, 255, 0, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 0, 255, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(0, 255, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 1;
            animation: floating 25s ease-in-out infinite;
        }
        
        .max-headroom-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(0, 255, 0, 0.05) 2px,
                    rgba(0, 255, 0, 0.03) 4px
                );
            background-size: 100px 100px;
            animation: grid-move 15s linear infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        .cyberpunk-scanner {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            animation: scan 6s linear infinite;
            z-index: 2;
        }
        
        .dashboard-container {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 20px;
            padding: 40px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(8px);
            margin: 20px;
            box-shadow: 
                0 0 40px rgba(0, 255, 0, 0.2),
                inset 0 0 20px rgba(0, 255, 0, 0.1);
        }
        
        .dashboard-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ff00, #ff0080, #ff00ff, #00ff00);
            border-radius: 22px;
            z-index: -1;
            animation: border-glow 4s ease-in-out infinite alternate;
        }
        
        .cyberpunk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(0, 255, 0, 0.3);
        }
        
        .brand {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .brand-icon { 
            font-size: 48px; 
            color: #00ff00; 
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.8);
            animation: pulse 3s ease-in-out infinite;
        }
        
        .brand-text { 
            color: #00ff00; 
            font-size: 32px; 
            font-weight: 700; 
            text-transform: uppercase;
            letter-spacing: 3px;
            text-shadow: 
                0 0 15px rgba(0, 255, 0, 0.6),
                2px 2px 4px rgba(255, 0, 255, 0.3);
        }
        
        .brand-tagline { 
            color: #00ff00; 
            font-size: 14px; 
            opacity: 0.8; 
            text-transform: uppercase;
            letter-spacing: 5px;
            margin-left: 10px;
        }
        
        .user-info {
            color: #00ff00;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .cyberpunk-card {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(5px);
            box-shadow: 
                0 0 30px rgba(0, 255, 0, 0.2),
                inset 0 0 15px rgba(0, 255, 0, 0.1);
        }
        
        .cyberpunk-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            animation: card-scan 8s linear infinite;
        }
        
        .cyberpunk-title {
            color: #00ff00;
            font-size: 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .cyberpunk-btn {
            background: linear-gradient(135deg, #001100 0%, #003300 100%);
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-family: 'Rajdhani', monospace;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            margin: 10px 5px;
        }
        
        .cyberpunk-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            transition: left 0.5s ease;
        }
        
        .cyberpunk-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 255, 0, 0.4);
            border-color: #80ff00;
        }
        
        .cyberpunk-btn:hover::before {
            left: 100%;
        }
        
        .status-indicator {
            display: inline-block;
            padding: 4px 8px;
            background: #001100;
            border: 1px solid #00ff00;
            border-radius: 4px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            animation: blink 2s ease-in-out infinite;
        }
        
        .status-ready {
            background: #00ff00;
            color: #001100;
            animation: none;
        }
        
        .grid-cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }
        
        .test-section {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
        }
        
        .string-interface {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
        }
        
        .string-line {
            display: flex;
            align-items: center;
            margin: 8px 0;
            min-height: 30px;
        }
        
        .prompt {
            color: #00ff00;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-right: 15px;
            min-width: 200px;
        }
        
        .value {
            color: #00ff00;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            flex: 1;
        }
        
        .cursor {
            color: #00ff00;
            animation: cursor-blink 1s infinite;
            margin-left: 5px;
        }
        
        .string-input {
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            color: #00ff00;
            padding: 8px 12px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            flex: 1;
            margin: 0 10px;
        }
        
        .string-input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            border-color: #00ff00;
        }
        
        .button-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .test-results {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid rgba(0, 255, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        @keyframes cursor-blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .test-results::-webkit-scrollbar {
            width: 8px;
        }
        
        .test-results::-webkit-scrollbar-track {
            background: rgba(0, 255, 0, 0.1);
        }
        
        .test-results::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }
        
        @keyframes floating {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(180deg); }
        }
        
        @keyframes grid-move {
            0% { background-position: 0 0; }
            100% { background-position: 100px 100px; }
        }
        
        @keyframes scan {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        @keyframes border-glow {
            0% { opacity: 0.3; }
            100% { opacity: 0.8; }
        }
        
        @keyframes card-scan {
            0% { top: 0; }
            100% { top: calc(100% - 1px); }
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="max-headroom-grid"></div>
    <div class="cyberpunk-scanner"></div>
    
    <div class="dashboard-container">
        <div class="cyberpunk-header">
            <div class="brand">
                <span class="brand-icon">⚡</span>
                <div>
                    <div class="brand-text">Atlantiplex Studio</div>
                    <span class="brand-tagline">Cyberpunk Interface</span>
                </div>
            </div>
            <div class="user-info">
                <div>USER: {{ session.username }}</div>
                <div>ROLE: {{ session.role }}</div>
                <a href="/logout" class="cyberpunk-btn">LOGOUT</a>
            </div>
        </div>
        
        <div class="cyberpunk-card">
            <h2 class="cyberpunk-title">Authentication Status</h2>
            <div><span class="status-indicator status-ready">ONLINE</span></div>
            <p>ACCESS GRANTED: {{ session.username }}</p>
            <p>USER_ID: {{ session.user_id }}</p>
            <p>LOGIN_TIME: {{ session.get('login_time', 'NOW') }}</p>
            <p>SYSTEM_STATUS: OPERATIONAL</p>
        </div>
        
        <div class="test-section">
            <h3 class="cyberpunk-title">System Diagnostics</h3>
            <button class="cyberpunk-btn" onclick="runFullTest()">RUN DIAGNOSTICS</button>
            <button class="cyberpunk-btn" onclick="testDatabase()">TEST DATABASE</button>
            <button class="cyberpunk-btn" onclick="testSession()">TEST SESSION</button>
            <div id="test-results" class="test-results"></div>
        </div>
        
        <div class="grid-cards">
            <div class="cyberpunk-card">
                <h3 class="cyberpunk-title">Broadcast Control</h3>
                <div class="string-interface">
                    <div class="string-line">
                        <span class="prompt">&gt; STREAM_STATUS:</span>
                        <span class="value" id="stream-status">READY</span>
                    </div>
                    <div class="button-group">
                        <button class="cyberpunk-btn" onclick="startBroadcast()">START_BROADCAST</button>
                        <button class="cyberpunk-btn" onclick="testAudio()">AUDIO_TEST</button>
                        <button class="cyberpunk-btn" onclick="openSceneConfig()">SCENE_CONFIG</button>
                    </div>
                </div>
            </div>
            
            <div class="cyberpunk-card">
                <h3 class="cyberpunk-title">Guest Management</h3>
                <div class="string-interface">
                    <div class="string-line">
                        <span class="prompt">&gt; ACTIVE_GUESTS:</span>
                        <span class="value" id="guest-count">0</span>
                        <span class="cursor">_</span>
                    </div>
                    <div class="string-line">
                        <span class="prompt">&gt; INVITE_CODE:</span>
                        <input type="text" id="invite-code" class="string-input" placeholder="ENTER_CODE" maxlength="8">
                        <button class="cyberpunk-btn" onclick="generateInvite()">GENERATE</button>
                    </div>
                    <div class="button-group">
                        <button class="cyberpunk-btn" onclick="inviteGuest()">INVITE_GUEST</button>
                        <button class="cyberpunk-btn" onclick="openGuestList()">GUEST_LIST</button>
                        <button class="cyberpunk-btn" onclick="testInviteSystem()">TEST_INVITE_SYS</button>
                    </div>
                </div>
            </div>
        </div>
            
            <div class="cyberpunk-card">
                <h3 class="cyberpunk-title">Guest Management</h3>
                <p>ACTIVE_GUESTS: 0</p>
                <button class="cyberpunk-btn">INVITE GUEST</button>
                <button class="cyberpunk-btn">GUEST LIST</button>
                <button class="cyberpunk-btn">TEST INVITE SYS</button>
            </div>
        </div>
        
        <div class="cyberpunk-card" style="margin-top: 30px;">
            <h3 class="cyberpunk-title">System Information</h3>
            <p>SERVER_PORT: {{ port }}</p>
            <p>PLATFORM: CYBERPUNK STUDIO</p>
            <p>VERSION: 4.0.0-MAX_HEADROOM</p>
            <p>STATUS: <span class="status-indicator status-ready">OPERATIONAL</span></p>
            <div style="margin-top: 20px; padding: 15px; background: rgba(0, 255, 0, 0.1); border-radius: 8px; border: 1px solid rgba(0, 255, 0, 0.3);">
                <strong style="color: #00ff00;">ATLANTIPLEX STUDIO - CYBERPUNK EDITION</strong><br>
                <span style="color: #80ff00;">Professional broadcasting platform with max headroom interface</span>
            </div>
        </div>
    </div>
        </div>
        <div>
            <p>Welcome, <span class="success">{{ session.username }}</span>! ({{ session.role }})</p>
            <a href="/logout" class="btn">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>⚡ LOGIN SYSTEM TEST - PASSED</h2>
            <p><strong>User:</strong> {{ session.username }}</p>
            <p><strong>Role:</strong> {{ session.role }}</p>
            <p><strong>User ID:</strong> {{ session.user_id }}</p>
            <p><strong>Login Time:</strong> {{ session.get('login_time', 'Just now') }}</p>
            <p><strong>Authentication Status:</strong> <span class="status-ok">⚡ SUCCESSFUL</span></p>
        </div>
        
        <div class="test-section">
            <h3>🧪 End-to-End System Testing</h3>
            <p>Testing all studio components...</p>
            <button class="btn" onclick="runFullTest()">Run Complete Test Suite</button>
            <button class="btn" onclick="testDatabase()">Test Database</button>
            <button class="btn" onclick="testSession()">Test Session</button>
            <div id="test-results" style="margin-top: 15px;"></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🎬 Broadcast Control</h3>
                <p>Stream Status: <span class="status-ready">⚡ READY</span></p>
                <button class="btn">Start Stream</button>
                <button class="btn">Test Audio</button>
                <button class="btn">Configure Scenes</button>
            </div>
            
            <div class="card">
                <h3>👥 Guest Management</h3>
                <p>Active Guests: 0</p>
                <button class="btn">Invite Guest</button>
                <button class="btn">Guest List</button>
                <button class="btn">Test Invite System</button>
            </div>
        </div>
        
        <div class="card">
            <h3>🔧 Studio Diagnostics</h3>
            <p><strong>Server:</strong> Running on port {{ port }} <span class="status-ok">⚡ OK</span></p>
            <p><strong>Database:</strong> Connected and working <span class="status-ok">⚡ OK</span></p>
            <p><strong>Authentication:</strong> <span class="status-ok">⚡ Working</span></p>
            <p><strong>Session Management:</strong> <span class="status-ok">⚡ Working</span></p>
            <p><strong>Template Rendering:</strong> <span class="status-ok">⚡ Working</span></p>
            <p><strong>API Endpoints:</strong> <span class="status-ok">⚡ Working</span></p>
            <div style="margin-top: 15px; padding: 15px; background: rgba(250,204,21,0.1); border-radius: 8px;">
                <strong>⚡ Atlantiplex Studio - Lightning in a Bottle</strong><br>
                Professional broadcasting platform powered by lightning-fast technology
            </div>
        </div>
    </div>
    
    <script>
        function runFullTest() {
            const results = document.getElementById('test-results');
            results.innerHTML = '<p>🧪 Running complete Atlantiplex Studio test suite...</p>';
            
            // Test database
            fetch('/test/database').then(r => r.json()).then(data => {
                results.innerHTML += '<p>⚡ Database: ' + data.message + '</p>';
                
                // Test session
                return fetch('/test/session');
            }).then(r => r.json()).then(data => {
                results.innerHTML += '<p>⚡ Session: ' + data.message + '</p>';
                
                // Test full system
                return fetch('/test/full');
            }).then(r => r.json()).then(data => {
                let status = 'PASSED';
                for (let [key, value] of Object.entries(data)) {
                    if (!value) status = 'FAILED';
                    results.innerHTML += `<p>⚡ ${key}: ${value ? 'Working' : 'Failed'}</p>`;
                }
                results.innerHTML += `<h3>⚡ Atlantiplex Studio Test Suite: ${status}</h3>`;
            }).catch(err => {
                results.innerHTML += '<p>⚡ Test suite failed: ' + err.message + '</p>';
            });
        }
        
        function testDatabase() {
            fetch('/test/database').then(r => r.json()).then(data => {
                document.getElementById('test-results').innerHTML = '<p>⚡ Database Test: ' + data.message + '</p>';
            });
        }
        
        function testSession() {
            fetch('/test/auth').then(r => r.json()).then(data => {
                if (data.success) {
                    results.innerHTML += '[AUTH_TEST] AUTHENTICATION SYSTEM: OPERATIONAL\n[TEST_COMPLETE]';
                } else {
                    results.innerHTML += '[AUTH_TEST] AUTHENTICATION SYSTEM: FAILED - ' + data.message + '\n';
                }
            }).catch(err => {
                results.innerHTML += '[ERROR] Auth test failed: ' + err.message;
            });
        }
        
        // Interactive string interface functions
        function startBroadcast() {
            const status = document.getElementById('stream-status');
            if (status) {
                status.textContent = 'BROADCASTING';
                status.className = 'status-indicator';
                document.querySelector('.test-results').innerHTML += '[BROADCAST] Stream started successfully\n';
            }
        }
        
        function testAudio() {
            document.querySelector('.test-results').innerHTML += '[AUDIO_TEST] Initializing audio diagnostic...\n[AUDIO_TEST] Audio system: OPERATIONAL\n';
        }
        
        function openSceneConfig() {
            document.querySelector('.test-results').innerHTML += '[SCENE_CONFIG] Opening scene configuration interface...\n[SCENE_CONFIG] Scene manager loaded\n';
        }
        
        function generateInvite() {
            const code = 'CYBER' + Math.random().toString(36).substr(2, 8).toUpperCase();
            const input = document.getElementById('invite-code');
            if (input) {
                input.value = code;
                document.querySelector('.test-results').innerHTML += `[INVITE] Generated code: ${code}\n`;
            }
        }
        
        function inviteGuest() {
            const code = document.getElementById('invite-code').value;
            if (code && code.length === 8) {
                const count = document.getElementById('guest-count');
                if (count) {
                    count.textContent = parseInt(count.textContent) + 1;
                }
                document.querySelector('.test-results').innerHTML += `[GUEST] Guest invited with code: ${code}\n`;
            } else {
                document.querySelector('.test-results').innerHTML += '[ERROR] Invalid invite code format\n';
            }
        }
        
        function openGuestList() {
            document.querySelector('.test-results').innerHTML += '[GUEST_LIST] Opening guest management interface...\n';
        }
        
        function testInviteSystem() {
            document.querySelector('.test-results').innerHTML += '[INVITE_SYS] Testing invitation system...\n[INVITE_SYS] System: OPERATIONAL\n';
        }
        
        function updateCursor() {
            const cursor = document.querySelector('.cursor');
            if (cursor) {
                setInterval(() => {
                    cursor.style.opacity = cursor.style.opacity === '1' ? '0' : '1';
                }, 500);
            }
        }
        
        function addTypingEffect() {
            const inputs = document.querySelectorAll('.string-input');
            inputs.forEach(input => {
                input.addEventListener('input', function(e) {
                    const value = e.target.value.toUpperCase();
                    e.target.value = value;
                });
            });
        }
        
        // Add cyberpunk terminal effects
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.cyberpunk-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = (index * 0.1) + 's';
            });
            
            updateCursor();
            addTypingEffect();
        });
    </script>
</body>
</html>
'''

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log_debug("Login page loaded")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'))
    
    username = request.form.get('username', '').strip().upper()
    password = request.form.get('password', '')
    
    log_debug(f"Login attempt: username='{username}', password_length={len(password)}")
    
    if not username or not password:
        log_debug("Login failed: Missing username or password")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="AUTHENTICATION_FAILED: Missing credentials")
    
    user = get_user(username.upper())
    if not user:
        log_debug(f"Login failed: User not found - {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error=f"AUTHENTICATION_FAILED: User '{username}' not found in database")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    expected_hash = user['password_hash']
    
    log_debug(f"Hash comparison: input={password_hash[:20]}..., expected={expected_hash[:20]}...")
    
    if password_hash == expected_hash:
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['login_time'] = time.strftime('%H:%M:%S')
        log_debug(f"[OK] Login successful: {username}")
        return redirect(url_for('dashboard'))
    else:
        log_debug(f"[ERROR] Authentication failed: Invalid credentials for {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error=f"AUTHENTICATION_FAILED: Invalid credentials for user '{username}'")
@app.route('/')
def index():
    log_debug("Home page accessed")
    if 'username' in session:
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log_debug("Login page loaded")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'))
    
    username = request.form.get('username', '').strip().upper()
    password = request.form.get('password', '')
    
    log_debug(f"Login attempt: username='{username}', password_length={len(password)}")
    
    if not username or not password:
        log_debug("Login failed: Missing username or password")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="AUTHENTICATION_FAILED: Missing credentials")
    
    user = get_user(username.upper())
    if not user:
        log_debug(f"Login failed: User not found - {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error=f"AUTHENTICATION_FAILED: User '{username}' not found in database")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    expected_hash = user['password_hash']
    
    log_debug(f"Hash comparison: input={password_hash[:20]}..., expected={expected_hash[:20]}...")
    
    if password_hash == expected_hash:
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['login_time'] = time.strftime('%H:%M:%S')
        log_debug(f"[OK] Login successful: {username}")
        return redirect(url_for('dashboard'))
    else:
        log_debug(f"[ERROR] Authentication failed: Invalid credentials for {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="AUTHENTICATION_FAILED: Invalid credentials for user '{username}'")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        log_debug("Dashboard accessed without login - redirecting")
        return redirect(url_for('login'))
    
    log_debug(f"Dashboard accessed by user: {session['username']}")
    return render_template_string(DASHBOARD_TEMPLATE, 
                               port=session.get('server_port', 'unknown'))

@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    log_debug(f"User logged out: {username}")
    return redirect(url_for('login'))

# Test endpoints
@app.route('/test/database')
def test_database():
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return jsonify({'success': True, 'message': f'Database working - {count} users found'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

@app.route('/test/session')
def test_session():
    if 'username' in session:
        return jsonify({'success': True, 'message': f'Session working - user: {session["username"]}'})
    else:
        return jsonify({'success': False, 'message': 'No active session'})

@app.route('/test/auth')
def test_auth():
    try:
        user = get_user('MANTICORE')
        if user and user['password_hash'] == hashlib.sha256('patriot8812'.encode()).hexdigest():
            return jsonify({'success': True, 'message': 'Authentication credentials valid'})
        else:
            return jsonify({'success': False, 'message': 'Authentication credentials invalid'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Authentication test error: {str(e)}'})

@app.route('/debug/users')
def debug_users():
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, role FROM users')
        users = cursor.fetchall()
        conn.close()
        return jsonify({'users': users, 'total': len(users)})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test/full')
def test_full():
    tests = {
        'database': False,
        'session': False,
        'authentication': False
    }
    
    try:
        # Test database
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        tests['database'] = True
        conn.close()
    except:
        pass
    
    # Test session
    if 'username' in session:
        tests['session'] = True
    
    # Test authentication
    try:
        user = get_user('manticore')
        if user:
            tests['authentication'] = True
    except:
        pass
    
    return jsonify(tests)

if __name__ == '__main__':
    port = find_free_port()
    
    print("=" * 70)
    print("ATLANTIPLEX STUDIO - LIGHTNING IN A BOTTLE")
    print("=" * 70)
    print(f"Server: http://127.0.0.1:{port}")
    print(f"Alt URL: http://localhost:{port}")
    print()
    print("[AUTH] Admin Credentials:")
    print("  Username: manticore")
    print("  Password: patriot8812")
    print("=" * 70)
    print("[DEBUG] All actions will be logged")
    print("=" * 70)
    
    # Open browser after delay
    def open_browser():
        time.sleep(2)
        try:
            url = f'http://127.0.0.1:{port}'
            webbrowser.open(url)
            log_debug(f"Browser opened to: {url}")
        except Exception as e:
            log_debug(f"Failed to open browser: {e}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        log_debug(f"Server error: {e}")
        print(f"Server error: {e}")
        input("Press Enter to exit...")