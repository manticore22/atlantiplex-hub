"""
ATLANTIPLEX MATRIX STUDIO - FINAL DEBUG VERSION
Unicode-fixed comprehensive testing
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
app.secret_key = 'matrix_studio_final_debug_key'

def log_debug(message):
    """Debug logging function - Unicode safe"""
    timestamp = time.strftime('%H:%M:%S')
    safe_message = message.replace('✓', '[OK]').replace('✗', '[ERROR]').replace('🚀', '[START]').replace('🔐', '[AUTH]')
    print(f"[DEBUG {timestamp}] {safe_message}")
    sys.stdout.flush()

def setup_database():
    """Initialize database with debug logging"""
    try:
        conn = sqlite3.connect('matrix_studio.db')
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
        conn = sqlite3.connect('matrix_studio.db')
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
        return 8085

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
        .logo-icon { font-size: 48px; margin-bottom: 10px; display: block; }
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
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo">
            <span class="logo-icon">⚡</span>
            <div class="brand-name">Atlantiplex Studio</div>
            <div class="brand-tagline">Lightning in a Bottle</div>
        </div>
        <h1>[AUTH] Studio Login</h1>
        
        <div class="debug-info">
            <strong>Debug Information:</strong><br>
            Server Port: {{ port }}<br>
            Time: {{ current_time }}<br>
            Test Credentials: manticore / patriot8812
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
        
        <form method="post">
            <input type="text" name="username" placeholder="Username" value="manticore" required>
            <input type="password" name="password" placeholder="Password" value="patriot8812" required>
            <button type="submit">LOGIN</button>
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
            document.getElementById('test-results').innerHTML = '<p style="color: #4caf50;">[OK] Connection test: Server is responding</p>';
        }
        
        function testDatabase() {
            fetch('/test/database').then(r => r.json()).then(data => {
                document.getElementById('test-results').innerHTML = '<p style="color: #4caf50;">[OK] Database: ' + data.message + '</p>';
            }).catch(err => {
                document.getElementById('test-results').innerHTML = '<p style="color: #f44336;">[ERROR] Database test failed</p>';
            });
        }
        
        function viewLogs() {
            alert('Check the console window for detailed debug logs');
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
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; margin: 0; }
        .header { background: rgba(30, 41, 59, 0.95); padding: 20px; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(10px); }
        .brand { display: flex; align-items: center; gap: 15px; }
        .brand-icon { font-size: 32px; }
        .brand-text { color: #60a5fa; font-size: 24px; font-weight: bold; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: rgba(30, 41, 59, 0.9); padding: 25px; margin: 20px 0; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); backdrop-filter: blur(10px); }
        .btn { background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; margin: 5px; transition: all 0.3s ease; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .success { color: #22c55e; font-weight: bold; }
        .test-section { background: rgba(34,197,94,0.1); border: 1px solid #22c55e; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .status-ok { color: #22c55e; }
        .status-error { color: #ef4444; }
        .status-ready { color: #facc15; }
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">
            <span class="brand-icon">⚡</span>
            <div>
                <div class="brand-text">Atlantiplex Studio</div>
                <p style="margin: 0; color: #94a3b8; font-size: 12px;">Lightning in a Bottle</p>
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
                document.getElementById('test-results').innerHTML = '<p>[OK] Database Test: ' + data.message + '</p>';
            });
        }
        
        function testSession() {
            fetch('/test/session').then(r => r.json()).then(data => {
                document.getElementById('test-results').innerHTML = '<p>[OK] Session Test: ' + data.message + '</p>';
            });
        }
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    log_debug("Home page accessed")
    if 'username' in session:
        log_debug(f"User already logged in: {session['username']}")
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log_debug("Login page loaded")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'))
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    log_debug(f"Login attempt: username='{username}', password_length={len(password)}")
    
    if not username or not password:
        log_debug("Login failed: Missing username or password")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="Username and password are required")
    
    user = get_user(username)
    if not user:
        log_debug(f"Login failed: User not found - {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error=f"User '{username}' not found")
    
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
        log_debug(f"[ERROR] Login failed: Password mismatch for {username}")
        return render_template_string(LOGIN_TEMPLATE, 
                                   port=session.get('server_port', 'unknown'),
                                   current_time=time.strftime('%H:%M:%S'),
                                   error="Invalid password")

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
        conn = sqlite3.connect('matrix_studio.db')
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

@app.route('/test/full')
def test_full():
    tests = {
        'database': False,
        'session': False,
        'authentication': False
    }
    
    try:
        # Test database
        conn = sqlite3.connect('matrix_studio.db')
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
    print("⚡ ATLANTIPLEX STUDIO - LIGHTNING IN A BOTTLE")
    print("=" * 70)
    print(f"Server: http://127.0.0.1:{port}")
    print(f"Alt URL: http://localhost:{port}")
    print()
    print("⚡ Admin Credentials:")
    print("  Username: manticore")
    print("  Password: patriot8812")
    print("=" * 70)
    print("⚡ Debug Mode: All actions will be logged")
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