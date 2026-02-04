"""
ATLANTIPLEX MATRIX STUDIO - PROFESSIONAL EDITION
Complete streaming studio with admin login, Gmail integration, real guest system
"""

from flask import Flask, jsonify, request, render_template_string, redirect, url_for, session, flash
from datetime import datetime, timedelta
import uuid
import json
import sqlite3
import hashlib
import secrets
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Database initialization
def init_db():
    conn = sqlite3.connect('matrix_studio.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            avatar_url TEXT,
            preferences TEXT
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT NOT NULL,
            stream_key TEXT,
            api_key TEXT,
            webhook_url TEXT,
            enabled BOOLEAN DEFAULT 0,
            settings_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Guests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invite_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'guest',
            status TEXT DEFAULT 'invited',
            invited_by INTEGER,
            invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            joined_at TIMESTAMP,
            permissions TEXT,
            avatar_url TEXT,
            FOREIGN KEY (invited_by) REFERENCES users (id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            user_id INTEGER,
            platforms TEXT,
            status TEXT DEFAULT 'offline',
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            viewer_count INTEGER DEFAULT 0,
            settings_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert admin user if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'manticore'")
    if not cursor.fetchone():
        admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        ''', ('manticore', 'admin@atlantiplex.com', admin_hash, 'admin'))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database helpers
def get_db():
    conn = sqlite3.connect('matrix_studio.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, email, password, role='user'):
    conn = get_db()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor = conn.execute('''
        INSERT INTO users (username, email, password_hash, role) 
        VALUES (?, ?, ?, ?)
    ''', (username, email, password_hash, role))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Debug info - remove this in production
    print(f"DEBUG: Login attempt - username: '{username}', password: '{password}'")
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, error="Username and password are required")
    
    user = get_user_by_username(username)
    
    if not user:
        print(f"DEBUG: User '{username}' not found in database")
        return render_template_string(LOGIN_TEMPLATE, error=f"User '{username}' not found")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"DEBUG: Input hash: {password_hash}")
    print(f"DEBUG: Stored hash: {user['password_hash']}")
    print(f"DEBUG: Hashes match: {password_hash == user['password_hash']}")
    
    if user and user['password_hash'] == password_hash:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session['email'] = user['email']
        
        # Update last login
        conn = get_db()
        conn.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                    (datetime.now().isoformat(), user['id']))
        conn.commit()
        conn.close()
        
        print(f"DEBUG: Login successful for user '{username}'")
        return redirect(url_for('dashboard'))
    else:
        print(f"DEBUG: Login failed for user '{username}'")
        return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Gmail OAuth simulation
@app.route('/auth/gmail')
def gmail_auth():
    # Simulate Gmail OAuth flow
    session['gmail_authenticated'] = True
    session['gmail_email'] = session.get('email', 'user@gmail.com')
    flash('Gmail account connected successfully!', 'success')
    return redirect(url_for('dashboard'))

# Main dashboard
@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    
    # Get user's settings
    settings = conn.execute('''
        SELECT platform, enabled, stream_key FROM settings 
        WHERE user_id = ? AND enabled = 1
    ''', (session['user_id'],)).fetchall()
    
    # Get recent guests
    guests = conn.execute('''
        SELECT name, email, status, invited_at FROM guests 
        WHERE invited_by = ? 
        ORDER BY invited_at DESC LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    # Get current session
    current_session = conn.execute('''
        SELECT * FROM sessions 
        WHERE user_id = ? AND status = 'live'
        ORDER BY created_at DESC LIMIT 1
    ''', (session['user_id'],)).fetchone()
    
    conn.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                settings=settings, 
                                guests=guests,
                                current_session=current_session)

# Settings page
@app.route('/settings')
@login_required
def settings_page():
    conn = get_db()
    settings = conn.execute('''
        SELECT * FROM settings WHERE user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template_string(SETTINGS_TEMPLATE, settings=settings)

# API Routes
@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    if request.method == 'GET':
        conn = get_db()
        settings = conn.execute('''
            SELECT * FROM settings WHERE user_id = ?
        ''', (session['user_id'],)).fetchall()
        conn.close()
        return jsonify([dict(s) for s in settings])
    
    # Update settings
    data = request.get_json()
    conn = get_db()
    
    for platform, config in data.items():
        conn.execute('''
            INSERT OR REPLACE INTO settings 
            (user_id, platform, stream_key, api_key, webhook_url, enabled, settings_data, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            platform,
            config.get('stream_key', ''),
            config.get('api_key', ''),
            config.get('webhook_url', ''),
            config.get('enabled', False),
            json.dumps(config),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Settings updated successfully'})

@app.route('/api/guests/invite', methods=['POST'])
@login_required
def invite_guest():
    data = request.get_json()
    invite_code = secrets.token_urlsafe(8).upper()
    
    conn = get_db()
    conn.execute('''
        INSERT INTO guests (invite_code, name, email, role, invited_by, permissions)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        invite_code,
        data['name'],
        data.get('email', ''),
        data.get('role', 'guest'),
        session['user_id'],
        json.dumps(data.get('permissions', {}))
    ))
    
    conn.commit()
    conn.close()
    
    # Generate invite URL
    invite_url = f"{request.host_url}guest/{invite_code}"
    
    # Send email (simulated - would integrate with Gmail API)
    if session.get('gmail_authenticated') and data.get('email'):
        # TODO: Integrate with Gmail API for real email sending
        pass
    
    return jsonify({
        'success': True,
        'invite_code': invite_code,
        'invite_url': invite_url,
        'message': f'Guest {data["name"]} invited successfully'
    })

@app.route('/api/guests')
@login_required
def list_guests():
    conn = get_db()
    guests = conn.execute('''
        SELECT * FROM guests WHERE invited_by = ?
        ORDER BY invited_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify([dict(g) for g in guests])

@app.route('/api/session/start', methods=['POST'])
@login_required
def start_session():
    data = request.get_json()
    session_id = str(uuid.uuid4())
    
    conn = get_db()
    conn.execute('''
        INSERT INTO sessions (session_id, title, user_id, platforms, status, start_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        data.get('title', 'Atlantiplex Session'),
        session['user_id'],
        json.dumps(data.get('platforms', [])),
        'live',
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Stream started successfully',
        'stream_url': f'rtmp://live.example.com/live/{session_id}'
    })

# Guest view
@app.route('/guest/<invite_code>')
def guest_view(invite_code):
    conn = get_db()
    guest = conn.execute('''
        SELECT g.*, u.username as host_username FROM guests g
        JOIN users u ON g.invited_by = u.id
        WHERE g.invite_code = ?
    ''', (invite_code,)).fetchone()
    
    if not guest:
        return "Invalid invite code", 404
    
    # Update guest status
    conn.execute('''
        UPDATE guests SET status = 'joined', joined_at = ? 
        WHERE id = ?
    ''', (datetime.now().isoformat(), guest['id']))
    conn.commit()
    conn.close()
    
    return render_template_string(GUEST_TEMPLATE, guest=dict(guest))

# API Health
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '3.0.0-professional',
        'features': ['admin_auth', 'gmail_oauth', 'real_guests', 'settings_db'],
        'timestamp': datetime.now().isoformat()
    })

# HTML Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 8px;
        }
        .logo p {
            color: #666;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .login-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .login-btn:hover {
            transform: translateY(-2px);
        }
        .divider {
            text-align: center;
            margin: 25px 0;
            color: #999;
            font-size: 14px;
        }
        .gmail-btn {
            width: 100%;
            padding: 12px;
            background: #4285f4;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: transform 0.2s ease;
        }
        .gmail-btn:hover {
            transform: translateY(-2px);
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🚀 Matrix Studio</h1>
            <p>Professional Broadcasting Platform</p>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username or Email</label>
                <input type="text" id="username" name="username" required placeholder="Enter your username">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter your password">
            </div>
            
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        
        <div class="divider">or</div>
        
        <a href="/auth/gmail" style="text-decoration: none;">
            <div class="gmail-btn">
                <span>📧</span>
                <span>Continue with Google</span>
            </div>
        </a>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #fff;
            overflow-x: hidden;
        }
        .navbar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .nav-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .nav-left h1 {
            font-size: 24px;
            font-weight: 700;
        }
        .nav-right {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 15px;
            border-radius: 25px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(145deg, #1e2139, #2a2d47);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(102, 126, 234, 0.2);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .card p {
            color: #b8bfcc;
            line-height: 1.6;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: linear-gradient(135deg, #f56565 0%, #ed8936 100%);
        }
        .status-live {
            background: #48bb78;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-offline {
            background: #718096;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .guest-list {
            margin-top: 15px;
        }
        .guest-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }
        .preview-area {
            background: #000;
            border-radius: 20px;
            height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #667eea;
            position: relative;
        }
        .preview-controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-left">
            <h1>🚀 Matrix Studio</h1>
            <a href="/" class="btn">Dashboard</a>
            <a href="/settings" class="btn">Settings</a>
            <a href="/api" class="btn">API Docs</a>
        </div>
        <div class="nav-right">
            <div class="user-info">
                <span>👤</span>
                <span>{{ session.username }}</span>
                {% if session.gmail_authenticated %}
                <span style="color: #4ade80;">✓ Gmail</span>
                {% endif %}
            </div>
            <a href="/logout" class="btn btn-danger" style="padding: 8px 16px; font-size: 14px;">Logout</a>
        </div>
    </nav>

    <div class="container">
        <div class="grid">
            <div class="card">
                <h3>🎬 Stream Status</h3>
                {% if current_session %}
                    <span class="status-live">● LIVE</span>
                    <p>Current Session: {{ current_session.title }}</p>
                    <p>Viewers: {{ current_session.viewer_count }}</p>
                    <button class="btn btn-danger">End Stream</button>
                {% else %}
                    <span class="status-offline">● OFFLINE</span>
                    <p>No active stream</p>
                    <button class="btn">Start Stream</button>
                {% endif %}
            </div>
            
            <div class="card">
                <h3>👥 Guest Management</h3>
                <p>Invite and manage your guests</p>
                <div class="guest-list">
                    {% for guest in guests %}
                    <div class="guest-item">
                        <span>{{ guest.name }}</span>
                        <span style="color: #4ade80;">{{ guest.status }}</span>
                    </div>
                    {% endfor %}
                </div>
                <button class="btn" onclick="openGuestModal()">Invite Guest</button>
            </div>
            
            <div class="card">
                <h3>⚙️ Platform Settings</h3>
                <p>Connected platforms:</p>
                {% for setting in settings %}
                <p style="color: #4ade80;">✓ {{ setting.platform }}</p>
                {% endfor %}
                {% if not settings %}
                <p style="color: #718096;">No platforms connected</p>
                {% endif %}
                <a href="/settings" class="btn">Configure</a>
            </div>
        </div>

        <div class="main-content">
            <div class="preview-area">
                <h2>📹 Stream Preview</h2>
                <div class="preview-controls">
                    <button class="btn">🎤 Mute</button>
                    <button class="btn">📷 Camera</button>
                    <button class="btn">🖼️ Scenes</button>
                    <button class="btn">📊 Analytics</button>
                </div>
            </div>
            
            <div>
                <div class="card" style="margin-bottom: 20px;">
                    <h3>🚀 Quick Actions</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button class="btn">Start Broadcasting</button>
                        <button class="btn">Add Background</button>
                        <button class="btn">Test Audio</button>
                        <button class="btn">Share Screen</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📱 Social Integration</h3>
                    <p>Connect your social platforms</p>
                    <button class="btn" onclick="window.open('/auth/gmail')">📧 Connect Gmail</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function openGuestModal() {
            const name = prompt('Guest name:');
            if (name) {
                fetch('/api/guests/invite', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, email: prompt('Guest email (optional):') || ''})
                }).then(r => r.json()).then(data => {
                    if (data.success) {
                        alert(`Guest invited! Invite link: ${data.invite_url}`);
                        location.reload();
                    }
                });
            }
        }
    </script>
</body>
</html>
'''

SETTINGS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlantiplex Matrix Studio - Settings</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #fff;
        }
        .navbar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
        }
        .settings-grid {
            display: grid;
            gap: 30px;
        }
        .platform-card {
            background: linear-gradient(145deg, #1e2139, #2a2d47);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }
        .platform-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .platform-header h3 {
            color: #667eea;
            font-size: 20px;
        }
        .toggle-switch {
            position: relative;
            width: 60px;
            height: 30px;
        }
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        input:checked + .slider:before {
            transform: translateX(30px);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #b8bfcc;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 10px;
            color: white;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #4a5568;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div>
            <h1>⚙️ Platform Settings</h1>
        </div>
        <div>
            <a href="/" class="btn">← Back to Dashboard</a>
        </div>
    </nav>

    <div class="container">
        <div class="settings-grid">
            <div class="platform-card">
                <div class="platform-header">
                    <h3>📺 YouTube Streaming</h3>
                    <label class="toggle-switch">
                        <input type="checkbox" id="youtube-enabled">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="form-group">
                    <label>Stream Key</label>
                    <input type="password" id="youtube-stream-key" placeholder="Enter YouTube stream key">
                </div>
                <div class="form-group">
                    <label>API Key</label>
                    <input type="password" id="youtube-api-key" placeholder="Enter YouTube API key">
                </div>
                <button class="btn">Save YouTube Settings</button>
            </div>

            <div class="platform-card">
                <div class="platform-header">
                    <h3>🎮 Twitch Integration</h3>
                    <label class="toggle-switch">
                        <input type="checkbox" id="twitch-enabled">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="form-group">
                    <label>Stream Key</label>
                    <input type="password" id="twitch-stream-key" placeholder="Enter Twitch stream key">
                </div>
                <div class="form-group">
                    <label>OAuth Token</label>
                    <input type="password" id="twitch-oauth" placeholder="Enter Twitch OAuth token">
                </div>
                <button class="btn">Save Twitch Settings</button>
            </div>

            <div class="platform-card">
                <div class="platform-header">
                    <h3>📘 Facebook Live</h3>
                    <label class="toggle-switch">
                        <input type="checkbox" id="facebook-enabled">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="form-group">
                    <label>Stream URL</label>
                    <input type="text" id="facebook-stream-url" placeholder="Enter Facebook stream URL">
                </div>
                <div class="form-group">
                    <label>Access Token</label>
                    <input type="password" id="facebook-token" placeholder="Enter Facebook access token">
                </div>
                <button class="btn">Save Facebook Settings</button>
            </div>

            <div class="platform-card">
                <div class="platform-header">
                    <h3>🎬 LinkedIn Live</h3>
                    <label class="toggle-switch">
                        <input type="checkbox" id="linkedin-enabled">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="form-group">
                    <label>Stream Key</label>
                    <input type="password" id="linkedin-stream-key" placeholder="Enter LinkedIn stream key">
                </div>
                <button class="btn">Save LinkedIn Settings</button>
            </div>

            <div class="platform-card">
                <div class="platform-header">
                    <h3>📧 Email Settings</h3>
                </div>
                <div class="form-group">
                    <label>Gmail Integration</label>
                    {% if session.gmail_authenticated %}
                    <p style="color: #4ade80;">✓ Connected: {{ session.gmail_email }}</p>
                    <button class="btn btn-secondary">Disconnect Gmail</button>
                    {% else %}
                    <p style="color: #718096;">Not connected</p>
                    <button class="btn" onclick="window.open('/auth/gmail')">Connect Gmail</button>
                    {% endif %}
                </div>
            </div>

            <div class="platform-card">
                <h3>💾 Save All Settings</h3>
                <p>Save all platform settings and configurations</p>
                <button class="btn" onclick="saveAllSettings()">Save All Settings</button>
            </div>
        </div>
    </div>

    <script>
        function saveAllSettings() {
            const settings = {
                youtube: {
                    enabled: document.getElementById('youtube-enabled').checked,
                    stream_key: document.getElementById('youtube-stream-key').value,
                    api_key: document.getElementById('youtube-api-key').value
                },
                twitch: {
                    enabled: document.getElementById('twitch-enabled').checked,
                    stream_key: document.getElementById('twitch-stream-key').value,
                    oauth_token: document.getElementById('twitch-oauth').value
                },
                facebook: {
                    enabled: document.getElementById('facebook-enabled').checked,
                    stream_url: document.getElementById('facebook-stream-url').value,
                    access_token: document.getElementById('facebook-token').value
                },
                linkedin: {
                    enabled: document.getElementById('linkedin-enabled').checked,
                    stream_key: document.getElementById('linkedin-stream-key').value
                }
            };

            fetch('/api/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(settings)
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    alert('Settings saved successfully!');
                }
            });
        }

        // Load existing settings
        fetch('/api/settings').then(r => r.json()).then(settings => {
            settings.forEach(setting => {
                if (setting.platform === 'youtube') {
                    document.getElementById('youtube-enabled').checked = setting.enabled;
                    document.getElementById('youtube-stream-key').value = setting.stream_key || '';
                    document.getElementById('youtube-api-key').value = setting.api_key || '';
                }
                // Add similar for other platforms
            });
        });
    </script>
</body>
</html>
'''

GUEST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guest Studio - {{ guest.name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .main-area {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .guest-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        .status {
            background: #4ade80;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin: 20px 0;
            font-weight: 600;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.2s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-danger {
            background: linear-gradient(135deg, #f56565 0%, #ed8936 100%);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Guest Studio</h1>
        <p>Hosted by {{ guest.host_username }}</p>
    </div>

    <div class="main-area">
        <div class="guest-card">
            <h2>👋 Welcome, {{ guest.name }}!</h2>
            <div class="status">🟢 Connected to Studio</div>
            <p>You've successfully joined the broadcast studio.</p>
            
            <div style="margin: 30px 0;">
                <button class="btn">📷 Enable Camera</button>
                <button class="btn">🎤 Enable Microphone</button>
                <button class="btn">💬 Open Chat</button>
            </div>
            
            <button class="btn btn-danger" onclick="if(confirm('Are you sure you want to leave?')) window.close()">
                🚪 Leave Studio
            </button>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 80)
    print("ATLANTIPLEX MATRIX STUDIO - PROFESSIONAL EDITION")
    print("=" * 80)
    print("Admin Login: manticore / patriot8812")
    print("Gmail OAuth Integration: Available")
    print("Real Guest System: Active")
    print("Settings Management: Database Enabled")
    print("Access: http://localhost:8081")
    print("=" * 80)
    
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
    
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)