"""
MINIMAL ATLANTIPLEX STUDIO - Direct Fix
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
import sqlite3
import hashlib
import socket
import webbrowser
import threading
import time

app = Flask(__name__)
app.secret_key = 'minimal_key'

def find_port():
    """Find a working port"""
    for port in [8080, 8081, 8082, 8083, 8084, 8085, 8086]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except:
            continue
    return 8087

def setup_db():
    """Setup minimal database"""
    conn = sqlite3.connect('atlantiplex_studio.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Create admin user
    admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                 ('manticore', admin_hash, 'admin'))
    conn.commit()
    conn.close()

# Setup database
setup_db()

# Simple template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Studio</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: monospace; 
            background: #000; 
            color: #00ff00; 
            padding: 50px;
            text-align: center;
        }
        .login-box {
            background: rgba(0,255,0,0.1);
            border: 2px solid #00ff00;
            padding: 30px;
            max-width: 400px;
            margin: 0 auto;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            background: #111;
            border: 1px solid #00ff00;
            color: #00ff00;
            font-family: monospace;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #00ff00;
            color: #000;
            border: none;
            font-family: monospace;
            font-weight: bold;
            cursor: pointer;
        }
        .error { color: #ff0000; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>⚡ ATLANTIPLEX STUDIO</h1>
    <div class="login-box">
        <h3>MATRIX CONTROL INTERFACE</h3>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="post">
            <input type="text" name="username" placeholder="Username" value="manticore" required>
            <input type="password" name="password" placeholder="Password" value="patriot8812" required>
            <button type="submit">LOGIN</button>
        </form>
        <p><small>Server: {{ port }}</small></p>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Studio - Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: monospace; 
            background: #000; 
            color: #00ff00; 
            padding: 20px;
        }
        .header {
            background: rgba(0,255,0,0.1);
            border: 1px solid #00ff00;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(0,255,0,0.05);
            border: 1px solid #00ff00;
            padding: 20px;
            margin: 20px 0;
        }
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-family: monospace;
            cursor: pointer;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ ATLANTIPLEX STUDIO - DASHBOARD</h1>
        <p>Welcome {{ session.username }} | <a href="/logout" style="color:#00ff00;">Logout</a></p>
    </div>
    
    <div class="card">
        <h2>System Status</h2>
        <p>✓ Server: Running on port {{ port }}</p>
        <p>✓ Database: Connected</p>
        <p>✓ Authentication: Active</p>
        <p>✓ Interface: Operational</p>
    </div>
    
    <div class="card">
        <h2>Quick Tests</h2>
        <button onclick="testDB()">Test Database</button>
        <button onclick="testAPI()">Test API</button>
        <div id="results" style="margin-top: 10px;"></div>
    </div>
    
    <script>
        function testDB() {
            fetch('/test/db').then(r => r.json()).then(data => {
                document.getElementById('results').innerHTML = 
                    '<p>Database Test: ' + (data.success ? 'SUCCESS' : 'FAILED') + '</p>';
            });
        }
        
        function testAPI() {
            fetch('/api/health').then(r => r.json()).then(data => {
                document.getElementById('results').innerHTML = 
                    '<p>API Test: ' + data.status + '</p>';
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verify credentials
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash, role FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash, role = result
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == stored_hash:
                session['username'] = username
                session['role'] = role
                return redirect(url_for('dashboard'))
        
        return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials", port=port)
    
    return render_template_string(LOGIN_TEMPLATE, port=port)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE, port=port)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/test/db')
def test_db():
    try:
        conn = sqlite3.connect('atlantiplex_studio.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return {'success': True, 'users': count}
    except:
        return {'success': False}

@app.route('/api/health')
def health():
    return {
        'status': 'healthy',
        'version': 'minimal-test',
        'port': port,
        'user': session.get('username', 'anonymous')
    }

if __name__ == '__main__':
    port = find_port()
    
    print("=" * 60)
    print("ATLANTIPLEX STUDIO - MINIMAL TEST VERSION")
    print("=" * 60)
    print(f"Starting server on: http://127.0.0.1:{port}")
    print(f"Login: manticore / patriot8812")
    print("=" * 60)
    
    # Open browser
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://127.0.0.1:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)