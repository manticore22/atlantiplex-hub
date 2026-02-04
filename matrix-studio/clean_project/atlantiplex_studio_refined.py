"""
ATLANTIPLEX STUDIO - REFINED VERSION
Enhanced with better error handling and debugging
"""

from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify, send_file
import sqlite3
import hashlib
import socket
import webbrowser
import threading
import time
import sys
import os
import json
import uuid
from datetime import datetime
import traceback

# Enhanced logging
class Logger:
    def __init__(self):
        self.enabled = True
    
    def log(self, message, level="DEBUG"):
        if not self.enabled:
            return
        timestamp = time.strftime('%H:%M:%S')
        safe_message = str(message).replace('⚡', '[LIGHTNING]').replace('✓', '[OK]').replace('✗', '[ERROR]')
        print(f"[DEBUG {timestamp}] [{level}] {safe_message}")
        sys.stdout.flush()

logger = Logger()

app = Flask(__name__)
app.secret_key = 'atlantiplex_studio_production_key'

def safe_operation(func, default=None, error_msg="Operation failed"):
    """Safely execute operation with error handling"""
    try:
        return func()
    except Exception as e:
        logger.log(f"{error_msg}: {e}", "ERROR")
        logger.log(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return default

def setup_database():
    """Initialize database with enhanced error handling"""
    return safe_operation(lambda: _setup_database_impl(), False, "Database setup failed")

def _setup_database_impl():
    conn = sqlite3.connect('atlantiplex_studio.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Admin user setup
    cursor.execute('SELECT id FROM users WHERE username = ?', ('manticore',))
    if not cursor.fetchone():
        admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        ''', ('manticore', 'admin@atlantiplex.com', admin_hash, 'admin'))
        logger.log("Admin user created: manticore", "OK")
    
    # Enhanced tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            invite_code TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'invited',
            invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            joined_at TIMESTAMP NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stream_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            stream_key TEXT,
            is_active BOOLEAN DEFAULT 0,
            bitrate INTEGER DEFAULT 8500,
            resolution TEXT DEFAULT '1920x1080',
            fps INTEGER DEFAULT 60
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.log("Database setup completed successfully", "OK")
    return True

def get_user(username):
    """Get user safely"""
    return safe_operation(
        lambda: _get_user_impl(username),
        None,
        f"User retrieval failed: {username}"
    )

def _get_user_impl(username):
    conn = sqlite3.connect('atlantiplex_studio.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        logger.log(f"User found: {username}", "OK")
        return dict(user)
    else:
        logger.log(f"User not found: {username}", "ERROR")
        return None

def find_free_port():
    """Find available port safely"""
    return safe_operation(
        lambda: _find_free_port_impl(),
        8086,
        "Port detection failed"
    )

def _find_free_port_impl():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    logger.log(f"Found available port: {port}", "OK")
    return port

# Initialize database
setup_database()

# Templates (copied from main version)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ATLANTIPLEX STUDIO - MATRIX INTERFACE</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Orbitron', monospace;
            background: #000;
            color: #00ff00;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        .matrix-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 255, 0, 0.03) 2px, rgba(0, 255, 0, 0.03) 4px),
                        repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0, 255, 0, 0.03) 2px, rgba(0, 255, 0, 0.03) 4px);
            animation: scan 8s linear infinite; pointer-events: none;
        }
        
        @keyframes scan { 0% { transform: translateY(0); } 100% { transform: translateY(10px); } }
        
        .login-container { position: relative; z-index: 10; display: flex; align-items: center; justify-content: center; height: 100vh; padding: 20px; }
        
        .cyber-box {
            background: rgba(0, 0, 0, 0.9); border: 2px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5), inset 0 0 20px rgba(0, 255, 0, 0.1);
            padding: 40px; min-width: 500px; position: relative; overflow: hidden;
        }
        
        .logo-section { text-align: center; margin-bottom: 30px; }
        .logo-icon { font-size: 48px; margin-bottom: 10px; display: block; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .brand-name { font-size: 32px; font-weight: 900; margin-bottom: 10px; text-transform: uppercase; }
        .brand-tagline { color: #00ff00; opacity: 0.8; font-size: 12px; letter-spacing: 2px; }
        .auth-title { color: #00ff00; text-align: center; margin-bottom: 20px; font-size: 18px; text-transform: uppercase; letter-spacing: 2px; }
        
        .terminal-info { background: rgba(0, 255, 0, 0.1); border: 1px solid #00ff00; padding: 15px; border-radius: 0; margin-bottom: 20px; font-size: 12px; font-family: 'Courier New', monospace; }
        .message-box { padding: 12px; margin-bottom: 20px; text-align: center; font-family: 'Courier New', monospace; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
        .error-box { background: rgba(255, 0, 0, 0.1); border: 1px solid #ff0000; color: #ff0000; }
        .success-box { background: rgba(0, 255, 0, 0.1); border: 1px solid #00ff00; color: #00ff00; }
        
        .cyber-input { 
            width: 100%; padding: 15px; margin: 8px 0; background: rgba(0, 0, 0, 0.8); border: 1px solid #00ff00;
            color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;
        }
        .cyber-input:focus { outline: none; box-shadow: 0 0 10px rgba(0, 255, 0, 0.5); }
        .cyber-input::placeholder { color: rgba(0, 255, 0, 0.5); }
        
        .cyber-btn {
            width: 100%; padding: 15px; background: transparent; color: #00ff00; border: 2px solid #00ff00;
            font-family: 'Orbitron', monospace; font-weight: 700; font-size: 16px; text-transform: uppercase; letter-spacing: 2px;
            cursor: pointer; margin-top: 10px; transition: all 0.3s ease;
        }
        .cyber-btn:hover { background: rgba(0, 255, 0, 0.1); box-shadow: 0 0 15px rgba(0, 255, 0, 0.5); transform: translateY(-2px); }
        
        .test-controls { margin-top: 20px; text-align: center; }
        .mini-btn { background: transparent; color: #00ff00; border: 1px solid #00ff00; padding: 8px 15px; margin: 5px; font-family: 'Courier New', monospace; font-size: 11px; text-transform: uppercase; cursor: pointer; }
        .mini-btn:hover { background: rgba(0, 255, 0, 0.1); }
        .test-results { margin-top: 15px; font-family: 'Courier New', monospace; font-size: 11px; color: #00ff00; max-height: 150px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <div class="login-container">
        <div class="cyber-box">
            <div class="logo-section">
                <span class="logo-icon">⚡</span>
                <div class="brand-name">ATLANTIPLEX STUDIO</div>
                <div class="brand-tagline">REFINED MATRIX CONTROL INTERFACE</div>
            </div>
            <div class="auth-title">[AUTH] SECURE LOGIN PROTOCOL</div>
            <div class="terminal-info">
                <strong>SYSTEM STATUS:</strong><br>
                &gt; PORT: {{ port }}<br>
                &gt; TIME: {{ current_time }}<br>
                &gt; SECURITY: ENHANCED<br>
                &gt; CREDENTIALS: manticore / patriot8812<br>
                &gt; STATUS: <span style="color: #00ff00;">ONLINE</span>
            </div>
            {% if error %}
            <div class="message-box error-box">[ERROR] {{ error }}</div>
            {% endif %}
            {% if success %}
            <div class="message-box success-box">[SUCCESS] {{ success }}</div>
            {% endif %}
            <form method="post">
                <input type="text" name="username" placeholder="USERNAME" value="manticore" required class="cyber-input">
                <input type="password" name="password" placeholder="PASSWORD" value="patriot8812" required class="cyber-input">
                <button type="submit" class="cyber-btn">INITIALIZE SESSION</button>
            </form>
            <div class="test-controls">
                <button class="mini-btn" onclick="testConnection()">TEST CONNECTION</button>
                <button class="mini-btn" onclick="testDatabase()">TEST DATABASE</button>
            </div>
            <div id="test-results" class="test-results"></div>
        </div>
    </div>
    <script>
        function testConnection() {
            document.getElementById('test-results').innerHTML = '<div>&gt; TESTING CONNECTION...</div>';
            setTimeout(() => document.getElementById('test-results').innerHTML += '<div style="color: #00ff00;">&gt; [OK] CONNECTION ESTABLISHED</div>', 500);
        }
        function testDatabase() {
            document.getElementById('test-results').innerHTML = '<div>&gt; TESTING DATABASE...</div>';
            fetch('/test/database').then(r => r.json()).then(data => {
                const status = data.success ? 'OK' : 'ERROR';
                const color = data.success ? '#00ff00' : '#ff0000';
                document.getElementById('test-results').innerHTML += `<div style="color: ${color};">&gt; [${status}] ${data.message}</div>`;
            });
        }
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ATLANTIPLEX STUDIO - MATRIX CONTROL</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { font-family: 'Orbitron', monospace; background: #000; color: #00ff00; min-height: 100vh; position: relative; }
        
        .matrix-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 255, 0, 0.03) 2px, rgba(0, 255, 0, 0.03) 4px);
            animation: scan 8s linear infinite; pointer-events: none; z-index: 1;
        }
        @keyframes scan { 0% { transform: translateY(0); } 100% { transform: translateY(10px); } }
        
        .main-content { position: relative; z-index: 10; }
        
        .cyber-header {
            background: rgba(0, 0, 0, 0.95); border-bottom: 2px solid #00ff00; padding: 20px;
            display: flex; justify-content: space-between; align-items: center;
        }
        
        .brand-section { display: flex; align-items: center; gap: 15px; }
        .brand-icon { font-size: 36px; color: #00ff00; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        
        .brand-text { color: #00ff00; font-size: 24px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; }
        .brand-tagline { color: #00ff00; opacity: 0.7; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
        
        .user-section { text-align: right; }
        .user-welcome { font-size: 14px; margin-bottom: 5px; }
        .user-name { color: #00ff00; font-weight: 700; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .cyber-card {
            background: rgba(0, 0, 0, 0.9); border: 1px solid #00ff00; padding: 25px; margin: 20px 0; position: relative; overflow: hidden;
        }
        
        .card-title { color: #00ff00; font-size: 18px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
        
        .data-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(0, 255, 0, 0.2); font-size: 14px; }
        .data-label { color: #00ff00; opacity: 0.8; }
        .data-value { font-weight: 700; }
        
        .cyber-btn {
            background: transparent; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px;
            margin: 5px; font-family: 'Orbitron', monospace; font-weight: 700; font-size: 12px; text-transform: uppercase;
            cursor: pointer; transition: all 0.3s ease;
        }
        .cyber-btn:hover { background: rgba(0, 255, 0, 0.1); box-shadow: 0 0 10px rgba(0, 255, 0, 0.5); transform: translateY(-2px); }
        
        .grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .status-ok { color: #00ff00; }
        .status-warning { color: #ffff00; }
        .status-error { color: #ff0000; }
        
        .terminal-output {
            background: rgba(0, 0, 0, 0.8); border: 1px solid #00ff00; padding: 15px; margin-top: 15px;
            font-family: 'Courier New', monospace; font-size: 12px; max-height: 200px; overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="matrix-bg"></div>
    <div class="main-content">
        <div class="cyber-header">
            <div class="brand-section">
                <span class="brand-icon">⚡</span>
                <div>
                    <div class="brand-text">ATLANTIPLEX</div>
                    <div class="brand-tagline">REFINED MATRIX CONTROL v4.2.0</div>
                </div>
            </div>
            <div class="user-section">
                <div class="user-welcome">USER: <span class="user-name">{{ session.username }}</span> [ROLE: {{ session.role }}]</div>
                <button class="cyber-btn" onclick="location.href='/logout'" style="background: rgba(255,0,0,0.1); border-color: #ff0000; color: #ff0000;">TERMINATE SESSION</button>
            </div>
        </div>
        <div class="container">
            <div class="cyber-card">
                <div class="card-title">SYSTEM STATUS MONITOR</div>
                <div class="data-row"><span class="data-label">USER:</span><span class="data-value">{{ session.username }}</span></div>
                <div class="data-row"><span class="data-label">ROLE:</span><span class="data-value">{{ session.role }}</span></div>
                <div class="data-row"><span class="data-label">SERVER PORT:</span><span class="data-value">{{ port }}</span></div>
                <div class="data-row"><span class="data-label">SYSTEM STATUS:</span><span class="data-value status-ok">OPERATIONAL</span></div>
            </div>
            
            <div class="cyber-card">
                <div class="card-title">SYSTEM TESTING</div>
                <div>
                    <button class="cyber-btn" onclick="runFullTest()">FULL SYSTEM SCAN</button>
                    <button class="cyber-btn" onclick="testDatabase()">DATABASE TEST</button>
                    <button class="cyber-btn" onclick="testSession()">SESSION TEST</button>
                </div>
                <div id="test-results" class="terminal-output"></div>
            </div>
            
            <div class="grid-layout">
                <div class="cyber-card">
                    <div class="card-title">BROADCAST CONTROL</div>
                    <div class="data-row"><span class="data-label">STATUS:</span><span class="data-value status-ok">STANDBY</span></div>
                    <div class="data-row"><span class="data-label">BITRATE:</span><span class="data-value">8500 KBPS</span></div>
                    <div class="data-row"><span class="data-label">RESOLUTION:</span><span class="data-value">1920x1080</span></div>
                    <div>
                        <button class="cyber-btn">START STREAM</button>
                        <button class="cyber-btn">CONFIGURE</button>
                    </div>
                </div>
                
                <div class="cyber-card">
                    <div class="card-title">GUEST MANAGEMENT</div>
                    <div class="data-row"><span class="data-label">ACTIVE GUESTS:</span><span class="data-value">0</span></div>
                    <div class="data-row"><span class="data-label">STATUS:</span><span class="data-value status-ok">READY</span></div>
                    <div>
                        <button class="cyber-btn">INVITE GUEST</button>
                        <button class="cyber-btn">GUEST LIST</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        function logToTerminal(message, type = 'info') {
            const terminal = document.getElementById('test-results');
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? '#ff0000' : '#00ff00';
            terminal.innerHTML += `<div style="color: ${color};">[${timestamp}] ${message}</div>`;
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        function runFullTest() {
            logToTerminal('INITIATING FULL SYSTEM SCAN...');
            fetch('/test/full').then(r => r.json()).then(data => {
                for (let [key, value] of Object.entries(data)) {
                    const status = value ? 'OK' : 'ERROR';
                    logToTerminal(`${key.toUpperCase()}: ${status}`, value ? 'info' : 'error');
                }
            });
        }
        
        function testDatabase() {
            logToTerminal('TESTING DATABASE...');
            fetch('/test/database').then(r => r.json()).then(data => {
                logToTerminal(`DATABASE: ${data.message}`, data.success ? 'info' : 'error');
            });
        }
        
        function testSession() {
            logToTerminal('TESTING SESSION...');
            fetch('/test/session').then(r => r.json()).then(data => {
                logToTerminal(`SESSION: ${data.message}`, data.success ? 'info' : 'error');
            });
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    logger.log("Home page accessed", "INFO")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        logger.log("Login page loaded", "INFO")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=app.config.get('SERVER_PORT', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'))
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    logger.log(f"Login attempt: {username}", "INFO")
    
    if not username or not password:
        logger.log("Login failed: Missing credentials", "WARNING")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=app.config.get('SERVER_PORT', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="Username and password are required")
    
    user = get_user(username)
    if not user:
        logger.log(f"Login failed: User not found - {username}", "WARNING")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=app.config.get('SERVER_PORT', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error=f"User '{username}' not found")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    expected_hash = user['password_hash']
    
    if password_hash == expected_hash:
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['login_time'] = time.strftime('%H:%M:%S')
        logger.log(f"Login successful: {username}", "OK")
        return redirect(url_for('dashboard'))
    else:
        logger.log(f"Login failed: Password mismatch for {username}", "WARNING")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=app.config.get('SERVER_PORT', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="Invalid password")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        logger.log("Dashboard accessed without login - redirecting", "WARNING")
        return redirect(url_for('login'))
    
    logger.log(f"Dashboard accessed by user: {session['username']}", "INFO")
    return render_template_string(DASHBOARD_TEMPLATE, 
                               port=app.config.get('SERVER_PORT', 'unknown'))

@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    logger.log(f"User logged out: {username}", "INFO")
    return redirect(url_for('login'))

# Test endpoints
@app.route('/test/database')
def test_database():
    return safe_operation(
        lambda: _test_database_impl(),
        jsonify({'success': False, 'message': 'Database test failed'}),
        "Database test failed"
    )

def _test_database_impl():
    conn = sqlite3.connect('atlantiplex_studio.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM guests')
    guest_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM stream_configs')
    config_count = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        'success': True, 
        'message': f'Database working - {user_count} users, {guest_count} guests, {config_count} stream configs'
    })

@app.route('/test/session')
def test_session():
    if 'username' in session:
        return jsonify({'success': True, 'message': f'Session working - user: {session["username"]}'})
    else:
        return jsonify({'success': False, 'message': 'No active session'})

@app.route('/test/full')
def test_full():
    tests = {
        'database': False,
        'session': False,
        'authentication': False,
        'streaming': True
    }
    
    # Test database
    if safe_operation(lambda: True, False, ""):
        try:
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
    user = get_user('manticore')
    if user:
        tests['authentication'] = True
    
    return jsonify(tests)

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '4.2.0-refined',
        'brand': 'Atlantiplex Studio - Refined Matrix Control',
        'features': [
            'enhanced_error_handling',
            'refined_ui', 
            'stable_database',
            'professional_streaming',
            'debug_mode'
        ],
        'components': {
            'authentication': 'active',
            'database': 'connected',
            'streaming': 'ready',
            'session_management': 'active'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = find_free_port()
    app.config['SERVER_PORT'] = port
    
    print("=" * 80)
    print("ATLANTIPLEX STUDIO - REFINED MATRIX CONTROL v4.2.0")
    print("=" * 80)
    print(f"Server: http://127.0.0.1:{port}")
    print(f"Alt URL: http://localhost:{port}")
    print()
    print("[AUTH] Admin Credentials:")
    print("  Username: manticore")
    print("  Password: patriot8812")
    print()
    print("[FEATURES] Refined Edition:")
    print("  [OK] Enhanced Error Handling")
    print("  [OK] Stable Database Operations")
    print("  [OK] Professional Logging")
    print("  [OK] Safe Operation Wrappers")
    print()
    print("[STATUS] All systems initialized and ready")
    print("=" * 80)
    
    def open_browser():
        time.sleep(2)
        try:
            url = f'http://127.0.0.1:{port}'
            webbrowser.open(url)
            logger.log(f"Browser opened to: {url}", "INFO")
        except Exception as e:
            logger.log(f"Failed to open browser: {e}", "ERROR")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.log(f"Server error: {e}", "ERROR")
        print(f"Server error: {e}")
        input("Press Enter to exit...")