"""
ATLANTIPLEX MATRIX STUDIO - SIMPLIFIED LOGIN VERSION
"""

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'matrix_studio_secret_key_2024'

def init_database():
    if not os.path.exists('matrix_studio.db'):
        conn = sqlite3.connect('matrix_studio.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Insert admin user
        admin_hash = hashlib.sha256('patriot8812'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        ''', ('manticore', 'admin@atlantiplex.com', admin_hash, 'admin'))
        
        conn.commit()
        conn.close()
        print("Database created with admin user")
    else:
        print("Database already exists")

# Initialize database
init_database()

def get_user(username):
    conn = sqlite3.connect('matrix_studio.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

# Simple login template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Matrix Studio - Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: white; margin: 50px; }
        .container { max-width: 400px; margin: 0 auto; background: #16213e; padding: 40px; border-radius: 10px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: none; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .error { background: #ff4444; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Atlantiplex Studio</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="post">
            <input type="text" name="username" placeholder="Username" value="manticore" required>
            <input type="password" name="password" placeholder="Password" value="patriot8812" required>
            <button type="submit">Login</button>
        </form>
        <p style="text-align: center; margin-top: 20px; font-size: 14px;">
            Admin: manticore / patriot8812
        </p>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Atlantiplex Matrix Studio - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: white; margin: 20px; }
        .header { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: #16213e; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Atlantiplex Matrix Studio</h1>
        <p>Welcome, {{ session.username }}! <a href="/logout" class="btn">Logout</a></p>
    </div>
    
    <div class="card">
        <h2>🎬 Stream Status</h2>
        <p>Stream: <span style="color: #4ade80;">● OFFLINE</span></p>
        <button class="btn">Start Stream</button>
    </div>
    
    <div class="card">
        <h2>👥 Guest Management</h2>
        <p>Invite guests to your broadcast</p>
        <button class="btn">Invite Guest</button>
    </div>
    
    <div class="card">
        <h2>⚙️ Settings</h2>
        <p>Configure streaming platforms</p>
        <button class="btn">Open Settings</button>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    print(f"Login attempt: {username}")
    
    user = get_user(username)
    if not user:
        print(f"User not found: {username}")
        return render_template_string(LOGIN_TEMPLATE, error="User not found")
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] == password_hash:
        session['username'] = user['username']
        session['user_id'] = user['id']
        session['role'] = user['role']
        print(f"Login successful: {username}")
        return redirect(url_for('dashboard'))
    else:
        print(f"Password mismatch for: {username}")
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
    print("=" * 60)
    print("ATLANTIPLEX MATRIX STUDIO - SIMPLIFIED VERSION")
    print("=" * 60)
    print("Server: http://127.0.0.1:8083")
    print("Login: manticore / patriot8812")
    print("=" * 60)
    
    try:
        app.run(host='127.0.0.1', port=8083, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        input("Press Enter to exit...")