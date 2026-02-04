"""
ATLANTIPLEX MATRIX STUDIO - WORKING VERSION
Guaranteed to work login system
"""

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import hashlib
import socket
import webbrowser
import threading
import time

app = Flask(__name__)
app.secret_key = 'matrix_studio_working_key'

# Database setup
def setup_database():
    conn = sqlite3.connect('matrix_studio.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Check if admin exists, create if not
    cursor.execute('SELECT id FROM users WHERE username = ?', ('manticore',))
    if not cursor.fetchone():
        admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        ''', ('manticore', 'admin@atlantiplex.com', admin_hash, 'admin'))
        print("✓ Admin user created: manticore")
    
    conn.commit()
    conn.close()

setup_database()

def get_user(username):
    conn = sqlite3.connect('matrix_studio.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

# Find available port
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

# Templates
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Matrix Studio</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
        .login-box { background: rgba(22, 33, 62, 0.9); padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); min-width: 350px; }
        h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #667eea; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { opacity: 0.9; }
        .error { background: #ff4444; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .info { background: #4444ff; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-size: 14px; }
        input::placeholder { color: #aaa; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🚀 Matrix Studio</h1>
        
        <div class="info">
            <strong>Test Credentials:</strong><br>
            Username: manticore<br>
            Password: patriot8812
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="post">
            <input type="text" name="username" placeholder="Username" value="manticore" required>
            <input type="password" name="password" placeholder="Password" value="patriot8812" required>
            <button type="submit">LOGIN</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Matrix Studio - Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; margin: 0; min-height: 100vh; }
        .header { background: rgba(22, 33, 62, 0.9); padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: rgba(22, 33, 62, 0.9); padding: 25px; margin: 20px 0; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; margin: 5px; }
        .btn:hover { opacity: 0.9; }
        .success { color: #4ade80; font-weight: bold; }
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🚀 Atlantiplex Matrix Studio</h1>
            <p>Welcome, <span class="success">{{ session.username }}</span>!</p>
        </div>
        <a href="/logout" class="btn">Logout</a>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>✅ LOGIN SUCCESSFUL!</h2>
            <p>Congratulations! You have successfully logged into Atlantiplex Matrix Studio.</p>
            <p><strong>User:</strong> {{ session.username }}</p>
            <p><strong>Status:</strong> <span class="success">Authenticated</span></p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🎬 Stream Control</h3>
                <p>Stream Status: <span style="color: #fbbf24;">● OFFLINE</span></p>
                <button class="btn">Start Stream</button>
                <button class="btn">Test Audio</button>
            </div>
            
            <div class="card">
                <h3>👥 Guest Management</h3>
                <p>Active Guests: 0</p>
                <button class="btn">Invite Guest</button>
                <button class="btn">View Guests</button>
            </div>
            
            <div class="card">
                <h3>⚙️ Settings</h3>
                <p>Platforms: 0 configured</p>
                <button class="btn">Configure</button>
                <button class="btn">Test API</button>
            </div>
        </div>
        
        <div class="card">
            <h3>🔧 System Information</h3>
            <p><strong>Version:</strong> Matrix Studio Professional Edition</p>
            <p><strong>Authentication:</strong> <span class="success">Working</span></p>
            <p><strong>Database:</strong> <span class="success">Connected</span></p>
            <p><strong>Login Time:</strong> {{ session.get('login_time', 'Just now') }}</p>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    print(f"Login attempt: username='{username}', password_length={len(password)}")
    
    if not username or not password:
        return render_template_string(LOGIN_TEMPLATE, error="Username and password are required")
    
    user = get_user(username)
    if not user:
        print(f"User not found: {username}")
        return render_template_string(LOGIN_TEMPLATE, error=f"User '{username}' not found")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    expected_hash = user['password_hash']
    
    print(f"Hash comparison: input={password_hash[:20]}..., expected={expected_hash[:20]}...")
    print(f"Hashes match: {password_hash == expected_hash}")
    
    if password_hash == expected_hash:
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['login_time'] = 'Just now'
        print(f"✓ Login successful: {username}")
        return redirect(url_for('dashboard'))
    else:
        print(f"✗ Password mismatch for: {username}")
        return render_template_string(LOGIN_TEMPLATE, error="Invalid password")

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Find available port
    port = find_free_port()
    
    print("=" * 70)
    print("🚀 ATLANTIPLEX MATRIX STUDIO - WORKING VERSION")
    print("=" * 70)
    print(f"🌐 Server running on: http://127.0.0.1:{port}")
    print(f"🌐 Alternative URL: http://localhost:{port}")
    print()
    print("🔐 LOGIN CREDENTIALS:")
    print("   Username: manticore")
    print("   Password: patriot8812")
    print("=" * 70)
    print()
    
    # Open browser after delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
        except:
            pass
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")